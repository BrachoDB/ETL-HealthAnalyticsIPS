import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from django.db import transaction
from django.utils import timezone

from analytics.models import Paciente
from etl.models import ETLLog


DATASET_XLSX_DEFAULT = 'dataset_clinico_etl_1800_registros.xlsx'


def _log(etl_run, mensaje: str, nivel: str = 'INFO'):
    ETLLog.objects.create(etl_run=etl_run, mensaje=mensaje, nivel=nivel)


def _normalize_text(s: str) -> str:
    if s is None:
        return ''
    s = str(s).strip().lower()
    s = ' '.join(s.split())
    return s


def _standardize_sex(sexo: str) -> str:
    s = _normalize_text(sexo)
    if s in {'m', 'male', 'h', 'hombre', 'masculino'}:
        return 'M'
    if s in {'f', 'female', 'mujer', 'mujeres', 'hembra', 'femenino'}:
        return 'F'
    return ''


def _standardize_diagnosis(diag: str) -> str:
    d = _normalize_text(diag)
    if not d:
        return ''

    # Correcciones ortográficas mínimas exigidas por el enunciado
    if 'hipertens' in d:
        return 'hipertensión'
    if 'diabet' in d:
        return 'diabetes'
    if 'card' in d and 'arr' in d:
        return 'arritmia'

    return diag.strip() if diag else d


def _parse_bool(x) -> bool:
    if pd.isna(x):
        return False
    if isinstance(x, bool):
        return x
    s = str(x).strip().lower()
    return s in {'true', '1', 'si', 'sí', 'y', 'yes'}


def _coerce_numeric(series, dtype=float):
    return pd.to_numeric(series, errors='coerce').astype(dtype)


def _risk_from_row(row) -> str:
    """Reglas simples (alineadas al PDF) para etiquetar Bajo/Medio/Alto/Crítico."""

    def _is_valid_num(v):
        return v is not None and not pd.isna(v)

    ps = row.get('presion_sistolica')
    glu = row.get('glucosa')
    spo2 = row.get('saturacion_oxigeno')
    temp = row.get('temperatura')
    edad = row.get('edad')
    imc = row.get('imc')

    # Triggers de crítico (ejemplo del PDF)
    crit = (
        (_is_valid_num(ps) and ps > 180)
        or (_is_valid_num(glu) and glu > 300)
        or (_is_valid_num(spo2) and spo2 < 85)
        or (_is_valid_num(temp) and temp > 40)
    )
    if crit:
        return 'Crítico'

    alto = (
        (_is_valid_num(ps) and ps >= 140)
        or (_is_valid_num(glu) and glu >= 160)
        or (_is_valid_num(imc) and imc >= 30)
    )
    if alto:
        return 'Alto'

    medio = (
        (_is_valid_num(edad) and edad >= 45)
        or (_is_valid_num(glu) and 100 <= glu < 160)
        or (_is_valid_num(imc) and 25 <= imc < 30)
    )
    if medio:
        return 'Medio'

    return 'Bajo'



def run_etl(etl_run, fuente: str = 'default'):
    """Motor ETL: EXTRACT -> TRANSFORM -> LOAD con Pandas/NumPy."""

    start = time.time()
    base_dir = Path(__file__).resolve().parent.parent
    datasets_dir = base_dir / 'datasets'
    datasets_dir.mkdir(parents=True, exist_ok=True)

    xlsx_path = base_dir / DATASET_XLSX_DEFAULT
    if not xlsx_path.exists():
        raise FileNotFoundError(f'No se encontró el dataset Excel: {xlsx_path}')

    # Si pediste recargar (opción A): limpiar y recargar.
    with transaction.atomic():
        _log(etl_run, f'Inicio ETL. Fuente={fuente}. Archivo={xlsx_path}', 'INFO')

        # ---- EXTRACT ----
        t0 = time.time()
        df = pd.read_excel(xlsx_path)

        # Exportar CSV (evidencia)
        csv_path = datasets_dir / 'dataset_clinico_etl_1800_registros.csv'
        df.to_csv(csv_path, index=False, encoding='utf-8')
        _log(etl_run, f'Extract OK: registros={len(df)}. CSV generado en {csv_path}', 'INFO')

        # ---- TRANSFORM ----
        # Normalizar nombres de columnas (por si vienen con espacios/variantes)
        df.columns = [str(c).strip() for c in df.columns]

        required = [
            'id_paciente', 'nombres', 'apellidos', 'edad', 'sexo', 'peso', 'altura', 'IMC',
            'presión_sistólica', 'presión_diastólica', 'frecuencia_cardiaca', 'glucosa',
            'colesterol', 'saturación_oxígeno', 'temperatura', 'antecedentes_familiares',
            'fumador', 'consumo_alcohol', 'actividad_física', 'diagnóstico_preliminar',
            'riesgo_enfermedad', 'fecha_consulta',
        ]

        # Resolver mapeo de nombres con tildes (si el dataset no coincide exactamente)
        colmap = {
            'presión_sistólica': 'presion_sistolica',
            'presión_diastólica': 'presion_diastolica',
            'saturación_oxígeno': 'saturacion_oxigeno',
            'actividad_física': 'actividad_fisica',
            'diagnóstico_preliminar': 'diagnostico_preliminar',
            'riesgo_enfermedad': 'riesgo_enfermedad',
        }

        rename = {}
        for k, v in colmap.items():
            if k in df.columns:
                rename[k] = v
        df = df.rename(columns=rename)

        # IMC puede venir como 'IMC' o 'imc'
        if 'IMC' in df.columns and 'imc' not in df.columns:
            df = df.rename(columns={'IMC': 'imc'})
        if 'imc' not in df.columns:
            df['imc'] = np.nan

        # Presiones pueden venir con nombres sin tilde
        if 'presión_sistólica' in df.columns:
            df = df.rename(columns={'presión_sistólica': 'presion_sistolica'})
        if 'presión_diastólica' in df.columns:
            df = df.rename(columns={'presión_diastólica': 'presion_diastolica'})
        if 'saturación_oxígeno' in df.columns:
            df = df.rename(columns={'saturación_oxígeno': 'saturacion_oxigeno'})
        if 'actividad_física' in df.columns:
            df = df.rename(columns={'actividad_física': 'actividad_fisica'})
        if 'diagnóstico_preliminar' in df.columns:
            df = df.rename(columns={'diagnóstico_preliminar': 'diagnostico_preliminar'})

        # Tipos coerción
        df['id_paciente'] = _coerce_numeric(df['id_paciente'], dtype=int)
        df['edad'] = _coerce_numeric(df['edad'], dtype='Int64')

        for c in ['peso', 'altura', 'imc', 'glucosa', 'colesterol', 'saturacion_oxigeno', 'temperatura']:
            if c in df.columns:
                df[c] = _coerce_numeric(df[c], dtype=float)

        for c in ['presion_sistolica', 'presion_diastolica', 'frecuencia_cardiaca']:
            if c in df.columns:
                df[c] = _coerce_numeric(df[c], dtype='Int64')

        # Booleans
        for c in ['antecedentes_familiares', 'fumador', 'consumo_alcohol']:
            if c in df.columns:
                df[c] = df[c].apply(_parse_bool)

        # Texto normalizado
        if 'sexo' in df.columns:
            df['sexo'] = df['sexo'].apply(_standardize_sex)
        if 'diagnostico_preliminar' in df.columns:
            df['diagnostico_preliminar'] = df['diagnostico_preliminar'].apply(_standardize_diagnosis)
        if 'actividad_fisica' in df.columns:
            df['actividad_fisica'] = df['actividad_fisica'].fillna('').astype(str).str.strip()

        # Fecha
        if 'fecha_consulta' in df.columns:
            df['fecha_consulta'] = pd.to_datetime(df['fecha_consulta'], errors='coerce').dt.date

        # Eliminar duplicados por id_paciente
        before = len(df)
        df = df.drop_duplicates(subset=['id_paciente'], keep='first')
        _log(etl_run, f'Transform: duplicados eliminados. Antes={before}, Después={len(df)}', 'INFO')

        # Tratamiento de nulos (media/mediana según campo)
        # Reglas simples para cumplir el PDF.
        numeric_cols = ['peso', 'altura', 'glucosa', 'colesterol', 'saturacion_oxigeno', 'temperatura']
        for c in numeric_cols:
            if c in df.columns:
                if df[c].isna().all():
                    continue
                median = df[c].median(skipna=True)
                df[c] = df[c].fillna(median)

        if 'edad' in df.columns:
            df['edad'] = df['edad'].fillna(int(df['edad'].median(skipna=True)) if not df['edad'].isna().all() else 0)

        # Validar rangos clínicos (outliers): recortar a rangos plausibles
        # (si el dataset trae valores atípicos intencionales)
        def clip(col, lo, hi):
            if col in df.columns:
                df[col] = df[col].clip(lower=lo, upper=hi)

        clip('peso', 30, 250)
        clip('altura', 1.0, 2.5)
        clip('glucosa', 40, 500)
        clip('colesterol', 50, 400)
        clip('saturacion_oxigeno', 50, 100)
        clip('temperatura', 34, 42)
        clip('presion_sistolica', 70, 260)
        clip('presion_diastolica', 40, 160)
        clip('frecuencia_cardiaca', 30, 220)

        # Calcular IMC = peso/altura^2
        df['imc'] = (df['peso'] / (df['altura'] ** 2)).replace([np.inf, -np.inf], np.nan)
        df['imc'] = df['imc'].fillna(df['imc'].median(skipna=True))

        # Clasificación riesgo (Bajo/Medio/Alto/Crítico)
        # Además: clasificar por IMC (no se guarda la etiqueta, solo imc; riesgo se deriva)
        df['riesgo_enfermedad'] = df.apply(_risk_from_row, axis=1)

        # Si el dataset trae riesgo_enfermedad pero viene mal, igual lo reemplazamos con reglas

        # ---- LOAD ----
        # Limpieza total (opción A)
        _log(etl_run, 'Load: limpiando tabla pacientes (TRUNCATE lógico en SQLite).', 'INFO')
        Paciente.objects.all().delete()

        pacientes = []
        for _, r in df.iterrows():
            pacientes.append(
                Paciente(
                    id_paciente=int(r['id_paciente']),
                    nombres=str(r.get('nombres', '') or '').strip(),
                    apellidos=str(r.get('apellidos', '') or '').strip(),
                    edad=int(r['edad']) if not pd.isna(r.get('edad')) else None,
                    sexo=str(r.get('sexo', '') or ''),
                    peso=float(r.get('peso')) if not pd.isna(r.get('peso')) else None,
                    altura=float(r.get('altura')) if not pd.isna(r.get('altura')) else None,
                    imc=float(r.get('imc')) if not pd.isna(r.get('imc')) else None,
                    presion_sistolica=int(r.get('presion_sistolica')) if not pd.isna(r.get('presion_sistolica')) else None,
                    presion_diastolica=int(r.get('presion_diastolica')) if not pd.isna(r.get('presion_diastolica')) else None,
                    frecuencia_cardiaca=int(r.get('frecuencia_cardiaca')) if not pd.isna(r.get('frecuencia_cardiaca')) else None,
                    glucosa=float(r.get('glucosa')) if not pd.isna(r.get('glucosa')) else None,
                    colesterol=float(r.get('colesterol')) if not pd.isna(r.get('colesterol')) else None,
                    saturacion_oxigeno=float(r.get('saturacion_oxigeno')) if not pd.isna(r.get('saturacion_oxigeno')) else None,
                    temperatura=float(r.get('temperatura')) if not pd.isna(r.get('temperatura')) else None,
                    antecedentes_familiares=bool(r.get('antecedentes_familiares', False)),
                    fumador=bool(r.get('fumador', False)),
                    consumo_alcohol=bool(r.get('consumo_alcohol', False)),
                    actividad_fisica=str(r.get('actividad_fisica', '') or '').strip(),
                    diagnostico_preliminar=str(r.get('diagnostico_preliminar', '') or ''),
                    riesgo_enfermedad=str(r.get('riesgo_enfermedad', '') or ''),
                    fecha_consulta=r.get('fecha_consulta'),
                )
            )

        Paciente.objects.bulk_create(pacientes, batch_size=500)

        transform_ms = int((time.time() - start) * 1000)
        _log(etl_run, f'Load OK: pacientes_insertados={len(pacientes)}. Tiempo_ms={transform_ms}', 'INFO')

    result = {
        'registros_extraccion': int(len(df)),
        'registros_transformados': int(len(df)),
        'tiempo_ejecucion_ms': int((time.time() - start) * 1000),
        'fuente': fuente,
    }
    return result


