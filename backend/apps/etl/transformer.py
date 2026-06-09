from __future__ import annotations

import re
from typing import Any

import numpy as np
import pandas as pd


RISK_LABELS = {'BAJO': 'Bajo', 'MEDIO': 'Medio', 'ALTO': 'Alto', 'CRITICO': 'Crítico'}


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
    for k, v in corrections.items():
        if k in d:
            return v
    return d


def _classify_risk(row: pd.Series) -> str:
    sys = row.get('presión_sistólica') or row.get('presion_sistolica')
    gluc = row.get('glucosa')
    sat = row.get('saturación_oxígeno') or row.get('saturacion_oxigeno')
    imc = row.get('IMC') or row.get('imc')

    if pd.isna(sys) and pd.isna(gluc) and pd.isna(sat):
        return 'Medio'

    if (not pd.isna(sys) and sys > 180) or (not pd.isna(gluc) and gluc > 300) or (not pd.isna(sat) and sat < 85):
        return 'Crítico'

    if (not pd.isna(gluc) and gluc >= 180) or (not pd.isna(imc) and imc >= 30):
        return 'Alto'

    return 'Medio'


def transform(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Normalización de nombres de columnas con acentos
    rename: dict[str, str] = {}
    for c in df.columns:
        if c == 'presión_sistólica':
            rename[c] = 'presion_sistolica'
        elif c == 'presión_diastólica':
            rename[c] = 'presion_diastolica'
        elif c == 'frecuencia_cardiaca':
            rename[c] = 'frecuencia_cardiaca'
        elif c == 'saturación_oxígeno':
            rename[c] = 'saturacion_oxigeno'
        elif c == 'IMC':
            rename[c] = 'IMC'

    if rename:
        df = df.rename(columns=rename)

    # Eliminar duplicados por id_paciente si existe
    if 'id_paciente' in df.columns:
        df = df.drop_duplicates(subset=['id_paciente'], keep='first')

    # Nulos: mediana numéricos, moda para categóricos
    for col in df.columns:
        # Numérico por tipo
        try:
            kind = df[col].dtype.kind
        except Exception:
            kind = None

        if kind in {'i', 'u', 'f'}:
            numeric = pd.to_numeric(df[col], errors='coerce')
            median = numeric.median()
            df[col] = numeric.fillna(median)
        else:
            if df[col].isna().any():
                mode = df[col].mode().iloc[0] if not df[col].mode().empty else ''
                df[col] = df[col].fillna(mode)

    # Diagnósticos
    if 'diagnóstico_preliminar' in df.columns:
        df = df.rename(columns={'diagnóstico_preliminar': 'diagnostico_preliminar'})

    if 'diagnostico_preliminar' in df.columns:
        df['diagnostico_preliminar'] = df['diagnostico_preliminar'].apply(_correct_diagnosis)

    # Conversión de tipos
    numeric_cols = [
        'edad', 'peso', 'altura',
        'presion_sistolica', 'presion_diastolica', 'frecuencia_cardiaca',
        'glucosa', 'colesterol', 'saturacion_oxigeno', 'temperatura',
        'presion_sistolica', 'presion_diastolica',
    ]

    for col in numeric_cols:
        if col in df.columns:
            ser = pd.to_numeric(df[col], errors='coerce')
            if ser.isna().any():
                ser = ser.fillna(ser.median())
            df[col] = ser

    # IMC cálculo si no existe o está nulo
    if 'peso' in df.columns and 'altura' in df.columns:
        df['imc'] = df['peso'] / (df['altura'] ** 2)
    elif 'IMC' in df.columns:
        df['imc'] = pd.to_numeric(df['IMC'], errors='coerce')

    # Clasificación de riesgo (si existe columna)
    if 'riesgo_enfermedad' in df.columns:
        df['riesgo_enfermedad'] = df.apply(_classify_risk, axis=1)
    elif 'presion_sistolica' in df.columns or 'glucosa' in df.columns or 'saturacion_oxigeno' in df.columns or 'imc' in df.columns:
        df['riesgo_enfermedad'] = df.apply(_classify_risk, axis=1)

    # Normalizar fumador a bool si llega como string
    if 'fumador' in df.columns:
        def _to_bool(v):
            if pd.isna(v):
                return np.nan
            if isinstance(v, bool):
                return v
            t = str(v).strip().lower()
            if t in {'true', '1', 'si', 'sí', 'y', 'yes'}:
                return True
            if t in {'false', '0', 'no', 'n'}:
                return False
            return np.nan

        df['fumador'] = df['fumador'].apply(_to_bool)

    return df

