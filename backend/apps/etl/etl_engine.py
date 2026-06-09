from __future__ import annotations

import io
import time
import re
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


RISK_MAP = {
    'BAJO': 'Bajo',
    'MEDIO': 'Medio',
    'ALTO': 'Alto',
    'CRITICO': 'Crítico',
}


def _normalize_text(s: Any) -> Any:
    if pd.isna(s):
        return np.nan
    s = str(s).strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s


def _correct_diagnosis(diag: Any) -> Any:
    d = _normalize_text(diag)
    if pd.isna(d):
        return np.nan

    corrections = {
        'hipertencion': 'hipertensión',
        'hipertensión': 'hipertensión',
        'hipertensíon': 'hipertensión',
        'hipertensíon.': 'hipertensión',
        'diabetes': 'diabetes',
    }
    # simple fuzzy via substring
    for k, v in corrections.items():
        if k in d:
            return v
    return d


def _to_bool(s: Any) -> Any:
    if pd.isna(s):
        return np.nan
    if isinstance(s, bool):
        return s
    t = str(s).strip().lower()
    if t in {'true', '1', 'si', 'sí', 'y', 'yes'}:
        return True
    if t in {'false', '0', 'no', 'n'}:
        return False
    return np.nan


def _classify_risk(row: pd.Series) -> str:
    # Basado en reglas clínicas del enunciado (ejemplos)
    sys = row.get('presión_sistólica') or row.get('presion_sistolica')
    gluc = row.get('glucosa')
    sat = row.get('saturación_oxígeno') or row.get('saturacion_oxigeno')
    imc = row.get('IMC') or row.get('imc')
    if pd.isna(sys) and pd.isna(gluc) and pd.isna(sat):
        return 'Medio'

    if (not pd.isna(sys) and sys > 180) or (not pd.isna(gluc) and gluc > 300) or (not pd.isna(sat) and sat < 85):
        return 'Crítico'

    # IMC / glucosa / presiones como heurística
    if (not pd.isna(gluc) and gluc >= 180) or (not pd.isna(imc) and imc >= 30):
        return 'Alto'

    return 'Medio'


@dataclass
class ETLResult:
    records_processed: int
    records_loaded: int
    extracted_source: str


def run_etl(excel_bytes: bytes | None, csv_bytes: bytes | None, source_filename: str = '') -> tuple[pd.DataFrame, ETLResult]:
    start = time.time()
    df: pd.DataFrame

    if excel_bytes:
        excel_file = io.BytesIO(excel_bytes)
        df = pd.read_excel(excel_file)
        source = source_filename or 'excel'
    elif csv_bytes:
        csv_file = io.BytesIO(csv_bytes)
        df = pd.read_csv(csv_file)
        source = source_filename or 'csv'
    else:
        raise ValueError('No input file provided')

    records_processed = int(len(df))

    # --- TRANSFORM ---
    # estandarizar nombres de columnas si vienen con acentos
    rename = {}
    for c in df.columns:
        if c == 'presión_sistólica':
            rename[c] = 'presion_sistolica'
        if c == 'presión_diastólica':
            rename[c] = 'presion_diastolica'
        if c == 'frecuencia_cardiaca':
            rename[c] = 'frecuencia_cardiaca'
        if c == 'saturación_oxígeno':
            rename[c] = 'saturacion_oxigeno'
        if c == 'IMC':
            rename[c] = 'IMC'
    if rename:
        df = df.rename(columns=rename)

    # eliminación duplicados por id_paciente
    if 'id_paciente' in df.columns:
        df = df.drop_duplicates(subset=['id_paciente'], keep='first')

    # nulos: median para numéricos, moda para categóricos
    for col in df.columns:
        if df[col].dtype.kind in {'i', 'u', 'f'}:
            median = pd.to_numeric(df[col], errors='coerce').median()
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(median)
        else:
            if df[col].isna().any():
                mode = df[col].mode().iloc[0] if not df[col].mode().empty else ''
                df[col] = df[col].fillna(mode)

    # corrección ortográfica básica en diagnóstico_preliminar
    if 'diagnóstico_preliminar' in df.columns:
        df = df.rename(columns={'diagnóstico_preliminar': 'diagnostico_preliminar'})
    if 'diagnostico_preliminar' in df.columns:
        df['diagnostico_preliminar'] = df['diagnostico_preliminar'].apply(_correct_diagnosis)

    # corrección de tipos
    numeric_cols = ['edad', 'peso', 'altura', 'presion_sistolica', 'presion_diastolica', 'frecuencia_cardiaca', 'glucosa', 'colesterol', 'saturacion_oxigeno', 'temperatura']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            if df[col].isna().any():
                df[col] = df[col].fillna(df[col].median())

    # IMC cálculo si no existe o está nulo
    if 'peso' in df.columns and 'altura' in df.columns:
        df['imc'] = df['peso'] / (df['altura'] ** 2)
    elif 'IMC' in df.columns:
        df['imc'] = pd.to_numeric(df['IMC'], errors='coerce')

    # clasificación riesgo
    if 'riesgo_enfermedad' in df.columns:
        df['riesgo_enfermedad'] = df['riesgo_enfermedad'].astype(str).str.strip().replace({'nan': ''})
    df['riesgo_enfermedad'] = df.apply(_classify_risk, axis=1)

    elapsed = int((time.time() - start) * 1000)
    result = ETLResult(
        records_processed=records_processed,
        records_loaded=0,
        extracted_source=source,
    )
    return df, result

