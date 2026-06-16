import hashlib
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from django.conf import settings
from django.utils import timezone

from apps.authentication.models import User
from apps.etl.models import ETLLog, Patient
from apps.etl.models import AuditoriaTransaccionalETL

from apps.etl.utils_linguistic import CorrectorLinguisticoClinico
from apps.etl.utils_numerical_spanish import ParserNumericoEspanol



REQUIRED_COLUMNS = [
    'id_paciente',
    'nombres',
    'apellidos',
    'edad',
    'sexo',
    'peso',
    'altura',
    'imc',
    'presión_sistólica',
    'presión_diastólica',
    'frecuencia_cardiaca',
    'glucosa',
    'colesterol',
    'saturación_oxígeno',
    'temperatura',
    'antecedentes_familiares',
    'fumador',
    'consumo_alcohol',
    'actividad_física',
    'diagnóstico_preliminar',
    'riesgo_enfermedad',
    'fecha_consulta',
]

CLINICAL_RANGES = {
    'edad': (0, 120),
    'peso': (2, 300),
    'altura': (0.3, 2.5),
    'imc': (10, 80),
    'presion_sistolica': (70, 220),
    'presion_diastolica': (40, 140),
    'frecuencia_cardiaca': (30, 220),
    'glucosa': (40, 400),
    'colesterol': (80, 500),
    'saturacion_oxigeno': (70, 100),
    'temperatura': (35, 42),
}

SCHEMA_VERSION = '1.0'
VALIDATION_RULES_VERSION = '1.0'


@dataclass
class ETLResult:
    log: ETLLog
    registros_extraidos: int
    registros_validos: int
    registros_procesados: int
    registros_invalidos: int
    registros_actualizados: int
    registros_creados: int


class ETLService:
    def run(self, file_path=None, user_id=None):
        start_time = time.time()
        started_at = timezone.now()
        source_label = 'archivo por defecto'
        source_type = None
        source_hash = None

        try:
            resolved_path = self._resolve_file_path(file_path)
            source_label = str(resolved_path)
            source_type = resolved_path.suffix.lower().lstrip('.')
            source_hash = self._hash_file(resolved_path)
            df = self._read_source(resolved_path)

            df = self._normalize_columns(df)
            missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
            if missing_columns:
                raise ValueError(f'Columnas faltantes en el archivo: {", ".join(missing_columns)}')

            duplicate_keys, duplicate_details = self._find_duplicate_rows(df)
            registros_invalidos = len(duplicate_details)
            invalid_details = duplicate_details
            df['_raw_imc'] = pd.to_numeric(df['imc'], errors='coerce')
            registros_extraidos = len(df)

            df = self._transform(df)
            registros_procesados = 0
            registros_actualizados = 0
            registros_creados = 0

            for original_index, row in df.iterrows():
                row_number = int(original_index) + 2
                validation_errors = self._validate_clinical_ranges(row)
                if validation_errors:
                    registros_invalidos += 1
                    patient_id = row.get('id_paciente', 'sin_id')
                    for error in validation_errors:
                        invalid_details.append(self._validation_error(row_number, patient_id, error))
                    continue

                patient_id = int(row['id_paciente'])
                duplicate_key = (patient_id, self._row_date_key(row['fecha_consulta']))
                if duplicate_key in duplicate_keys:
                    continue

                existed = Patient.objects.filter(id_paciente=patient_id).exists()
                Patient.objects.update_or_create(
                    id_paciente=patient_id,
                    defaults=self._patient_defaults(row),
                )
                registros_procesados += 1
                if existed:
                    registros_actualizados += 1
                else:
                    registros_creados += 1

            end_time = time.time()
            finished_at = timezone.now()
            duration = end_time - start_time
            detalles = self._success_details(
                source_label=source_label,
                registros_extraidos=registros_extraidos,
                registros_procesados=registros_procesados,
                registros_invalidos=registros_invalidos,
                invalid_details=invalid_details,
            )
            user = self._get_user(user_id)

            # Auditoría transaccional (aditiva)
            AuditoriaTransaccionalETL.objects.create(
                usuario_responsable=user,
                archivo_fuente=source_label,
                registros_saneados=registros_procesados,
                tiempo_ejecucion_segundos=duration,
                estado_finalizacion='EXITOSO',
                informe_errores=None,
            )

            log = ETLLog.objects.create(

                usuario=user,
                fecha_inicio=started_at,
                fecha_fin=finished_at,
                source_file=source_label,
                source_hash=source_hash,
                source_type=source_type,
                schema_version=SCHEMA_VERSION,
                validation_rules_version=VALIDATION_RULES_VERSION,
                registros_extraidos=registros_extraidos,
                registros_validos=registros_extraidos - registros_invalidos,
                registros_procesados=registros_procesados,
                registros_invalidos=registros_invalidos,
                registros_actualizados=registros_actualizados,
                registros_creados=registros_creados,
                tiempo_ejecucion=duration,
                estado='Exitoso',
                detalles=detalles,
            )
            return ETLResult(
                log=log,
                registros_extraidos=registros_extraidos,
                registros_validos=registros_extraidos - registros_invalidos,
                registros_procesados=registros_procesados,
                registros_invalidos=registros_invalidos,
                registros_actualizados=registros_actualizados,
                registros_creados=registros_creados,
            )

        except Exception as exc:
            duration = time.time() - start_time
            finished_at = timezone.now()
            user = self._get_user(user_id)

            # Auditoría transaccional (aditiva) - fallido
            AuditoriaTransaccionalETL.objects.create(
                usuario_responsable=user,
                archivo_fuente=source_label,
                registros_saneados=0,
                tiempo_ejecucion_segundos=duration,
                estado_finalizacion='FALLIDO',
                informe_errores=str(exc),
            )

            log = ETLLog.objects.create(

                usuario=user,
                fecha_inicio=started_at,
                fecha_fin=finished_at,
                source_file=source_label,
                source_hash=source_hash,
                source_type=source_type,
                schema_version=SCHEMA_VERSION,
                validation_rules_version=VALIDATION_RULES_VERSION,
                tiempo_ejecucion=duration,
                estado='Fallido',
                detalles=f'Fuente: {source_label}\n{str(exc)}',
            )
            return ETLResult(
                log=log,
                registros_extraidos=0,
                registros_validos=0,
                registros_procesados=0,
                registros_invalidos=0,
                registros_actualizados=0,
                registros_creados=0,
            )

    def _resolve_file_path(self, file_path):
        if file_path:
            path = Path(file_path)
            if not path.is_absolute():
                path = settings.BASE_DIR / file_path
            return path

        return settings.BASE_DIR.parent / 'dataset_clinico_etl_1800_registros.xlsx'

    def _normalize_columns(self, df):
        column_map = {}
        for column in df.columns:
            key = str(column).strip().lower()
            if key == 'imc':
                mapped = 'imc'
            elif 'sist' in key:
                mapped = 'presión_sistólica'
            elif 'diast' in key:
                mapped = 'presión_diastólica'
            elif 'satur' in key and 'ox' in key:
                mapped = 'saturación_oxígeno'
            elif 'diagn' in key:
                mapped = 'diagnóstico_preliminar'
            elif 'activ' in key:
                mapped = 'actividad_física'
            else:
                mapped = column
            column_map[column] = mapped

        return df.rename(columns=column_map)

    def _read_source(self, file_path):
        if not file_path.exists():
            raise FileNotFoundError(f'Archivo no encontrado: {file_path}')

        suffix = file_path.suffix.lower()
        if suffix == '.csv':
            return pd.read_csv(file_path, encoding='utf-8-sig')
        if suffix in {'.xlsx', '.xls'}:
            return pd.read_excel(file_path)
        raise ValueError('El archivo debe tener extensión .csv, .xlsx o .xls')

    def _hash_file(self, file_path):
        sha256 = hashlib.sha256()
        with file_path.open('rb') as file_obj:
            for chunk in iter(lambda: file_obj.read(1024 * 1024), b''):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _transform(self, df):
        df = df.drop_duplicates(subset=['id_paciente'], keep='first').copy()

        # Parser numérico en español (aditivo)
        parser_edad = ParserNumericoEspanol()

        def _parse_edad(value):
            if isinstance(value, str):
                parsed = parser_edad.palabra_a_entero(value)
                if parsed is not None:
                    return parsed
            return self._clean_edad(value)

        df['edad'] = df['edad'].apply(_parse_edad)
        df['edad'] = pd.to_numeric(df['edad'], errors='coerce')
        df['edad'] = df['edad'].fillna(df['edad'].median()).fillna(0)


        df['presión_sistólica'] = df['presión_sistólica'].apply(self._clean_presion)
        df['presión_sistólica'] = pd.to_numeric(df['presión_sistólica'], errors='coerce')
        df['presión_sistólica'] = df['presión_sistólica'].fillna(df['presión_sistólica'].median()).fillna(0)

        numeric_cols = [
            'peso',
            'altura',
            'presión_diastólica',
            'frecuencia_cardiaca',
            'glucosa',
            'colesterol',
            'temperatura',
            'saturación_oxígeno',
        ]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = df[col].fillna(df[col].median()).fillna(0)

        df.loc[df['peso'] > 300, 'peso'] = df['peso'].median()
        df.loc[df['altura'] <= 0, 'altura'] = df['altura'].median()
        df.loc[df['altura'] <= 0, 'altura'] = 1

        df['imc'] = df['peso'] / (df['altura'] ** 2)
        df['imc'] = df['imc'].replace([np.inf, -np.inf], np.nan).fillna(df['imc'].median()).fillna(0)

        # Corrección léxica de diagnósticos (aditivo)
        corrector = CorrectorLinguisticoClinico()
        df['diagnóstico_preliminar'] = df['diagnóstico_preliminar'].apply(
            lambda v: corrector.corregir_diagnostico(self._clean_text(v))
        )


        df['sexo'] = df['sexo'].apply(lambda value: value if value in {'Masculino', 'Femenino', 'Otro'} else 'Otro')
        df['riesgo_enfermedad'] = df['riesgo_enfermedad'].apply(self._clean_riesgo).fillna('Bajo')
        df['actividad_física'] = df['actividad_física'].apply(self._clean_text).fillna('No especificada')
        df['fecha_consulta'] = pd.to_datetime(df['fecha_consulta'], errors='coerce').dt.date.fillna(timezone.localdate())

        return df.rename(columns={
            'presión_sistólica': 'presion_sistolica',
            'presión_diastólica': 'presion_diastolica',
            'saturación_oxígeno': 'saturacion_oxigeno',
            'actividad_física': 'actividad_fisica',
            'diagnóstico_preliminar': 'diagnostico_preliminar',
        })

    def _patient_defaults(self, row):
        return {
            'nombres': row['nombres'],
            'apellidos': row['apellidos'],
            'edad': int(row['edad']),
            'sexo': row['sexo'],
            'peso': float(row['peso']),
            'altura': float(row['altura']),
            'imc': float(row['imc']),
            'presion_sistolica': int(row['presion_sistolica']),
            'presion_diastolica': int(row['presion_diastolica']),
            'frecuencia_cardiaca': int(row['frecuencia_cardiaca']),
            'glucosa': float(row['glucosa']),
            'colesterol': float(row['colesterol']),
            'saturacion_oxigeno': float(row['saturacion_oxigeno']),
            'temperatura': float(row['temperatura']),
            'antecedentes_familiares': self._clean_bool(row['antecedentes_familiares']),
            'fumador': self._clean_bool(row['fumador']),
            'consumo_alcohol': self._clean_bool(row['consumo_alcohol']),
            'actividad_fisica': row['actividad_fisica'],
            'diagnostico_preliminar': row['diagnostico_preliminar'],
            'riesgo_enfermedad': row['riesgo_enfermedad'],
            'fecha_consulta': row['fecha_consulta'],
        }

    def _validate_clinical_ranges(self, row):
        errors = []
        for column, (minimum, maximum) in CLINICAL_RANGES.items():
            value = pd.to_numeric(row[column], errors='coerce')
            if pd.isna(value) or value < minimum or value > maximum:
                errors.append(f'{column}={value} fuera del rango válido {minimum}-{maximum}')

        if row['fecha_consulta'] > timezone.localdate():
            errors.append(f"fecha_consulta={row['fecha_consulta']} es futura")

        errors.extend(self._validate_advanced_consistency(row))
        return errors

    def _find_duplicate_rows(self, df):
        duplicate_keys = set()
        duplicate_details = []
        seen = set()

        for original_index, row in df.iterrows():
            row_number = int(original_index) + 2
            patient_id = pd.to_numeric(row.get('id_paciente'), errors='coerce')
            fecha_consulta = self._row_date_key(row.get('fecha_consulta'))
            if pd.isna(patient_id) or not fecha_consulta:
                continue

            key = (int(patient_id), fecha_consulta)
            if key in seen:
                duplicate_keys.add(key)
                duplicate_details.append(self._validation_error(row_number, int(patient_id), 'duplicado_paciente_fecha'))
            else:
                seen.add(key)

        return duplicate_keys, duplicate_details

    def _row_date_key(self, value):
        if value is None or pd.isna(value):
            return None
        if hasattr(value, 'date') and not isinstance(value, str):
            return value.date().isoformat()
        parsed = pd.to_datetime(value, errors='coerce')
        if pd.isna(parsed):
            return str(value)
        return parsed.date().isoformat()

    def _validate_advanced_consistency(self, row):
        errors = []
        peso = pd.to_numeric(row['peso'], errors='coerce')
        altura = pd.to_numeric(row['altura'], errors='coerce')
        imc = pd.to_numeric(row.get('_raw_imc', row['imc']), errors='coerce')
        presion_sistolica = pd.to_numeric(row['presion_sistolica'], errors='coerce')
        presion_diastolica = pd.to_numeric(row['presion_diastolica'], errors='coerce')

        if not any(pd.isna(value) for value in [peso, altura, imc]) and altura > 0:
            imc_calculado = peso / (altura ** 2)
            tolerancia = max(1.0, imc_calculado * 0.1)
            if abs(imc - imc_calculado) > tolerancia:
                errors.append(f'imc={imc} inconsistente con peso/altura; IMC calculado {imc_calculado:.2f}')

        if not any(pd.isna(value) for value in [presion_sistolica, presion_diastolica]):
            if presion_sistolica <= presion_diastolica:
                errors.append(f'presión sistólica {presion_sistolica} debe ser mayor que diastólica {presion_diastolica}')
            if presion_sistolica - presion_diastolica > 120:
                errors.append(f'diferencial de presión {presion_sistolica - presion_diastolica} fuera de rango clínico')

        return errors

    def _success_details(self, source_label, registros_extraidos, registros_procesados, registros_invalidos, invalid_details):
        details = (
            f'ETL completado exitosamente. Fuente: {source_label}. '
            f'{registros_extraidos} registros únicos procesados en transformación, '
            f'{registros_procesados} cargados/actualizados, '
            f'{registros_invalidos} omitidos por validaciones clínicas.'
        )
        if invalid_details:
            details += '\nDetalles de omisión:\n' + '\n'.join(self._format_invalid_details(invalid_details[:200]))
        return details

    def _format_invalid_details(self, invalid_details):
        formatted = []
        for detail in invalid_details:
            if isinstance(detail, dict):
                formatted.append(
                    f"Fila {detail.get('row_number')}, id_paciente {detail.get('id_paciente')}: "
                    f"{detail.get('field')} - {detail.get('message')}"
                )
            else:
                formatted.append(str(detail))
        return formatted

    def _validation_error(self, row_number, patient_id, message, field='validacion'):
        return {
            'row_number': row_number,
            'id_paciente': patient_id,
            'field': field,
            'message': message,
        }

    def _clean_edad(self, value):
        if isinstance(value, str):
            value = value.strip().lower()
            mapping = {
                'dieciocho': 18,
                'veinte': 20,
                'treinta': 30,
                'cuarenta': 40,
                'cincuenta': 50,
                'sesenta': 60,
                'setenta': 70,
                'ochenta': 80,
                'noventa': 90,
            }
            return mapping.get(value, np.nan)
        return value

    def _clean_presion(self, value):
        if isinstance(value, str):
            value = value.strip().lower()
            if 'alta' in value:
                return 140
            if 'media' in value:
                return 120
            if 'baja' in value:
                return 100
            return np.nan
        return value

    def _clean_bool(self, value):
        if isinstance(value, bool):
            return value
        if pd.isna(value):
            return False
        if isinstance(value, str):
            return value.strip().lower() in {'1', 'true', 'verdadero', 'si', 'sí', 's', 'y', 'yes'}
        return bool(value)

    def _clean_text(self, value):
        if pd.isna(value):
            return ''
        return str(value).strip()

    def _clean_riesgo(self, value):
        text = self._clean_text(value).lower()
        mapping = {
            'bajo': 'Bajo',
            'medio': 'Medio',
            'alto': 'Alto',
            'crítico': 'Crítico',
            'critico': 'Crítico',
        }
        return mapping.get(text, 'Bajo')

    def _get_user(self, user_id):
        if user_id:
            user = User.objects.filter(id=user_id).first()
            if user:
                return user

        admin_username = getattr(settings, 'BOOTSTRAP_ADMIN_USERNAME', 'admin')
        admin_email = getattr(settings, 'BOOTSTRAP_ADMIN_EMAIL', 'admin@example.com')
        admin_password = getattr(settings, 'BOOTSTRAP_ADMIN_PASSWORD', 'admin123')
        admin_role = getattr(settings, 'BOOTSTRAP_ADMIN_ROLE', 'ADMIN')

        admin_user = User.objects.filter(is_superuser=True).first()
        if admin_user is None:
            admin_user, _ = User.objects.get_or_create(
                username=admin_username,
                defaults={
                    'email': admin_email,
                    'role': admin_role,
                },
            )
            admin_user.set_password(admin_password)
            admin_user.is_staff = True
            admin_user.is_superuser = True
            if hasattr(User, 'ADMIN'):
                admin_user.role = User.ADMIN
            admin_user.save()

        return admin_user


def run_etl(file_path=None, user_id=None):
    return ETLService().run(file_path=file_path, user_id=user_id)
