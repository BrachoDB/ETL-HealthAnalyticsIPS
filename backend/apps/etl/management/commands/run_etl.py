import os
import time
from pathlib import Path

import numpy as np
import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import close_old_connections
from django.utils import timezone

from apps.authentication.models import User
from apps.etl.models import ETLLog, Patient


REQUIRED_COLUMNS = [
    'id_paciente',
    'nombres',
    'apellidos',
    'edad',
    'sexo',
    'peso',
    'altura',
    'presión_sistólica',
    'presion_diastolica',
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
    'temperatura': (35, 42),
    'presión_sistólica': (70, 220),
    'glucosa': (40, 400),
    'saturación_oxígeno': (70, 100),
}


class Command(BaseCommand):
    help = 'Ejecuta el proceso ETL para cargar datos clínicos desde Excel o CSV a MySQL'

    def add_arguments(self, parser):
        parser.add_argument('--file', dest='file_path', type=str, help='Ruta del archivo Excel o CSV a procesar')
        parser.add_argument('--user-id', dest='user_id', type=int, help='ID del usuario que ejecuta el ETL')

    def handle(self, *args, **options):
        start_time = time.time()
        user_id = options.get('user_id')
        source_label = 'archivo manual'
        self.stdout.write(self.style.SUCCESS('Iniciando proceso ETL...'))

        try:
            file_path = self._resolve_file_path(options.get('file_path'))
            source_label = str(file_path)
            df = self._read_source(file_path)
            self.stdout.write(f'Registros extraídos: {len(df)}')

            missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
            if missing_columns:
                raise ValueError(f'Columnas faltantes en el archivo: {", ".join(missing_columns)}')

            df = self._transform(df)
            registros_extraidos = len(df)
            registros_invalidos = 0
            registros_procesados = 0
            invalid_details = []

            for original_index, row in df.iterrows():
                row_number = int(original_index) + 2
                validation_errors = self._validate_clinical_ranges(row)
                if validation_errors:
                    registros_invalidos += 1
                    patient_id = row.get('id_paciente', 'sin_id')
                    for error in validation_errors:
                        invalid_details.append(f'Fila {row_number}, id_paciente {patient_id}: {error}')
                    continue

                Patient.objects.update_or_create(
                    id_paciente=int(row['id_paciente']),
                    defaults={
                        'nombres': row['nombres'],
                        'apellidos': row['apellidos'],
                        'edad': int(row['edad']),
                        'sexo': row['sexo'],
                        'peso': float(row['peso']),
                        'altura': float(row['altura']),
                        'imc': float(row['imc']),
                        'presion_sistolica': int(row['presión_sistólica']),
                        'presion_diastolica': int(row['presion_diastolica']),
                        'frecuencia_cardiaca': int(row['frecuencia_cardiaca']),
                        'glucosa': float(row['glucosa']),
                        'colesterol': float(row['colesterol']),
                        'saturacion_oxigeno': float(row['saturación_oxígeno']),
                        'temperatura': float(row['temperatura']),
                        'antecedentes_familiares': self._clean_bool(row['antecedentes_familiares']),
                        'fumador': self._clean_bool(row['fumador']),
                        'consumo_alcohol': self._clean_bool(row['consumo_alcohol']),
                        'actividad_fisica': row['actividad_física'],
                        'diagnostico_preliminar': row['diagnóstico_preliminar'],
                        'riesgo_enfermedad': row['riesgo_enfermedad'],
                        'fecha_consulta': row['fecha_consulta'],
                    }
                )
                registros_procesados += 1

            end_time = time.time()
            duration = end_time - start_time
            details = (
                f'ETL completado exitosamente. Fuente: {source_label}. '
                f'{registros_extraidos} registros únicos procesados en transformación, '
                f'{registros_procesados} cargados/actualizados, '
                f'{registros_invalidos} omitidos por validaciones clínicas.'
            )
            if invalid_details:
                details += '\nDetalles de omisión:\n' + '\n'.join(invalid_details[:200])

            user = self._get_user(user_id)
            ETLLog.objects.create(
                usuario=user,
                registros_procesados=registros_procesados,
                tiempo_ejecucion=duration,
                estado='Exitoso',
                detalles=details,
            )

            self.stdout.write(self.style.SUCCESS(f'ETL finalizado. {registros_procesados} registros cargados en {duration:.2f}s'))

        except Exception as exc:
            duration = time.time() - start_time
            self.stdout.write(self.style.ERROR(f'Error en ETL: {str(exc)}'))
            ETLLog.objects.create(
                usuario=self._get_user(user_id),
                tiempo_ejecucion=duration,
                estado='Fallido',
                detalles=f'Fuente: {source_label}\n{str(exc)}',
            )
        finally:
            close_old_connections()

    def _resolve_file_path(self, file_path):
        if file_path:
            path = Path(file_path)
            if not path.is_absolute():
                path = settings.BASE_DIR / file_path
            return path

        return settings.BASE_DIR.parent / 'dataset_clinico_etl_1800_registros.xlsx'

    def _read_source(self, file_path):
        if not file_path.exists():
            raise FileNotFoundError(f'Archivo no encontrado: {file_path}')

        suffix = file_path.suffix.lower()
        if suffix == '.csv':
            return pd.read_csv(file_path, encoding='utf-8-sig')
        if suffix in {'.xlsx', '.xls'}:
            return pd.read_excel(file_path)
        raise ValueError('El archivo debe tener extensión .csv, .xlsx o .xls')

    def _transform(self, df):
        df = df.drop_duplicates(subset=['id_paciente'], keep='first').copy()

        df['edad'] = df['edad'].apply(self._clean_edad)
        df['edad'] = pd.to_numeric(df['edad'], errors='coerce')
        df['edad'] = df['edad'].fillna(df['edad'].median()).fillna(0)

        df['presión_sistólica'] = df['presión_sistólica'].apply(self._clean_presion)
        df['presión_sistólica'] = pd.to_numeric(df['presión_sistólica'], errors='coerce')
        df['presión_sistólica'] = df['presión_sistólica'].fillna(df['presión_sistólica'].median()).fillna(0)

        numeric_cols = [
            'peso',
            'altura',
            'presion_diastolica',
            'frecuencia_cardiaca',
            'glucosa',
            'colesterol',
            'temperatura',
            'saturación_oxígeno',
        ]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = df[col].fillna(df[col].median()).fillna(0)

        df.loc[df['peso'] > 250, 'peso'] = df['peso'].median()
        df.loc[df['altura'] <= 0, 'altura'] = df['altura'].median()
        df.loc[df['altura'] <= 0, 'altura'] = 1

        df['imc'] = df['peso'] / (df['altura'] ** 2)
        df['imc'] = df['imc'].replace([np.inf, -np.inf], np.nan).fillna(df['imc'].median()).fillna(0)

        df['diagnóstico_preliminar'] = df['diagnóstico_preliminar'].replace({
            'hipertencion': 'Hipertensión',
            'hipertensíon': 'Hipertensión',
            'hipertensión': 'Hipertensión',
        })
        df['diagnóstico_preliminar'] = df['diagnóstico_preliminar'].apply(self._clean_text).fillna('Sin diagnóstico')

        df['sexo'] = df['sexo'].apply(lambda value: value if value in {'Masculino', 'Femenino', 'Otro'} else 'Otro')
        df['riesgo_enfermedad'] = df['riesgo_enfermedad'].apply(self._clean_riesgo).fillna('Bajo')
        df['actividad_física'] = df['actividad_física'].apply(self._clean_text).fillna('No especificada')
        df['fecha_consulta'] = pd.to_datetime(df['fecha_consulta'], errors='coerce').dt.date.fillna(timezone.localdate())

        return df

    def _validate_clinical_ranges(self, row):
        errors = []
        for column, (minimum, maximum) in CLINICAL_RANGES.items():
            value = pd.to_numeric(row[column], errors='coerce')
            if pd.isna(value) or value < minimum or value > maximum:
                errors.append(f'{column}={value} fuera del rango válido {minimum}-{maximum}')
        return errors

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
