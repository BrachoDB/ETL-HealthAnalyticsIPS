import pandas as pd
import numpy as np
import time
from django.core.management.base import BaseCommand
from apps.etl.models import Patient, ETLLog
from apps.authentication.models import User
from django.utils import timezone

class Command(BaseCommand):
    help = 'Ejecuta el proceso ETL para cargar datos clínicos desde Excel a MySQL'

    def handle(self, *args, **options):
        start_time = time.time()
        self.stdout.write(self.style.SUCCESS('Iniciando proceso ETL...'))
        
        try:
            import os
            from django.conf import settings
            file_path = os.path.join(settings.BASE_DIR.parent, 'dataset_clinico_etl_1800_registros.xlsx')
            df = pd.read_excel(file_path)
            self.stdout.write(f'Registros extraídos: {len(df)}')

            # 2. TRANSFORM
            # Eliminar duplicados
            df.drop_duplicates(subset=['id_paciente'], keep='first', inplace=True)
            
            # Limpieza de edad
            def clean_edad(val):
                if isinstance(val, str):
                    val = val.strip().lower()
                    mapping = {
                        'dieciocho': 18, 'veinte': 20, 'treinta': 30, 'cuarenta': 40, 
                        'cincuenta': 50, 'sesenta': 60, 'setenta': 70, 'ochenta': 80, 'noventa': 90
                    }
                    return mapping.get(val, np.nan)
                return val

            df['edad'] = df['edad'].apply(clean_edad)
            df['edad'] = pd.to_numeric(df['edad'], errors='coerce')
            df['edad'] = df['edad'].fillna(df['edad'].median())

            # Limpieza de presión sistólica
            def clean_presion(val):
                if isinstance(val, str):
                    val = val.strip().lower()
                    if 'alta' in val: return 140
                    if 'media' in val: return 120
                    if 'baja' in val: return 100
                    return np.nan
                return val

            df['presión_sistólica'] = df['presión_sistólica'].apply(clean_presion)
            df['presión_sistólica'] = pd.to_numeric(df['presión_sistólica'], errors='coerce')
            df['presión_sistólica'] = df['presión_sistólica'].fillna(df['presión_sistólica'].median())

            # Corregir diagnósticos
            typo_map = {
                'hipertencion': 'Hipertensión',
                'hipertensíon': 'Hipertensión',
                'hipertensión': 'Hipertensión'
            }
            df['diagnóstico_preliminar'] = df['diagnóstico_preliminar'].replace(typo_map)

            # Tratamiento de nulos en otras columnas
            numeric_cols = ['peso', 'glucosa', 'colesterol', 'temperatura', 'saturación_oxígeno']
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                df[col] = df[col].fillna(df[col].median())

            # Valores atípicos
            # Peso > 250 -> median
            df.loc[df['peso'] > 250, 'peso'] = df['peso'].median()
            # Temperatura < 30 -> 36.5
            df.loc[df['temperatura'] < 30, 'temperatura'] = 36.5

            # Cálculo de IMC
            df['IMC'] = df['peso'] / (df['altura'] ** 2)

            # Estandarizar riesgo (Asegurar que sea Bajo, Medio, Alto, Crítico)
            # Si hay valores extraños, los mapeamos o calculamos.
            # Por ahora aseguramos capitalización.
            df['riesgo_enfermedad'] = df['riesgo_enfermedad'].str.capitalize()

            # 3. LOAD
            # Limpiar tabla actual antes de cargar si se desea, o usar update_or_create
            # Para este reto, cargaremos todo de nuevo o actualizaremos.
            
            registros_procesados = 0
            for _, row in df.iterrows():
                Patient.objects.update_or_create(
                    id_paciente=row['id_paciente'],
                    defaults={
                        'nombres': row['nombres'],
                        'apellidos': row['apellidos'],
                        'edad': int(row['edad']),
                        'sexo': row['sexo'],
                        'peso': row['peso'],
                        'altura': row['altura'],
                        'imc': row['IMC'],
                        'presion_sistolica': int(row['presión_sistólica']),
                        'presion_diastolica': int(row['presión_diastólica']),
                        'frecuencia_cardiaca': int(row['frecuencia_cardiaca']),
                        'glucosa': row['glucosa'],
                        'colesterol': row['colesterol'],
                        'saturacion_oxigeno': row['saturación_oxígeno'],
                        'temperatura': row['temperatura'],
                        'antecedentes_familiares': bool(row['antecedentes_familiares']),
                        'fumador': bool(row['fumador']),
                        'consumo_alcohol': bool(row['consumo_alcohol']),
                        'actividad_fisica': row['actividad_física'],
                        'diagnostico_preliminar': row['diagnóstico_preliminar'],
                        'riesgo_enfermedad': row['riesgo_enfermedad'],
                        'fecha_consulta': row['fecha_consulta'],
                    }
                )
                registros_procesados += 1

            end_time = time.time()
            duration = end_time - start_time
            
            # Registrar Log
            admin_user = User.objects.filter(is_superuser=True).first()
            ETLLog.objects.create(
                usuario=admin_user,
                registros_procesados=registros_procesados,
                tiempo_ejecucion=duration,
                estado='Exitoso',
                detalles=f'ETL completado exitosamente. {len(df)} registros únicos procesados.'
            )

            self.stdout.write(self.style.SUCCESS(f'ETL finalizado. {registros_procesados} registros cargados en {duration:.2f}s'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error en ETL: {str(e)}'))
            ETLLog.objects.create(
                tiempo_ejecucion=time.time() - start_time,
                estado='Fallido',
                detalles=str(e)
            )
