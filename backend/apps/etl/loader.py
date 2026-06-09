from __future__ import annotations

from typing import Any

import pandas as pd

from .models import ClinicalRecord  # type: ignore


def _to_int_or_none(v: Any) -> int | None:
    if v is None:
        return None
    try:
        if str(v) == 'nan':
            return None
        return int(v)
    except Exception:
        return None


def _to_float_or_none(v: Any) -> float | None:
    if v is None:
        return None
    try:
        if str(v) == 'nan':
            return None
        return float(v)
    except Exception:
        return None


def load_to_db(df: pd.DataFrame, *, batch_size: int = 1000) -> int:
    """Carga registros limpios hacia ClinicalRecord usando bulk_create.

    Asume que el df ya viene transformado y con columnas esperadas.
    """
    bulk: list[ClinicalRecord] = []

    for _, r in df.iterrows():
        bulk.append(
            ClinicalRecord(
                sex=r.get('sexo') if 'sexo' in df.columns else r.get('sex') if 'sex' in df.columns else None,
                names=r.get('nombres') if 'nombres' in df.columns else r.get('names') if 'names' in df.columns else None,
                last_names=r.get('apellidos') if 'apellidos' in df.columns else r.get('last_names') if 'last_names' in df.columns else None,
                age=_to_int_or_none(r.get('edad')),
                peso=_to_float_or_none(r.get('peso')),
                altura=_to_float_or_none(r.get('altura')),
                imc=_to_float_or_none(r.get('imc')),
                presion_sistolica=_to_int_or_none(r.get('presion_sistolica')),
                presion_diastolica=_to_int_or_none(r.get('presion_diastolica')),
                frecuencia_cardiaca=_to_int_or_none(r.get('frecuencia_cardiaca')),
                glucosa=_to_float_or_none(r.get('glucosa')),
                colesterol=_to_float_or_none(r.get('colesterol')),
                saturacion_oxigeno=_to_float_or_none(r.get('saturacion_oxigeno')),
                temperatura=_to_float_or_none(r.get('temperatura')),
                antecedentes_familiares=bool(r.get('antecedentes_familiares')) if 'antecedentes_familiares' in df.columns else None,
                fumador=bool(r.get('fumador')) if 'fumador' in df.columns else None,
                consumo_alcohol=bool(r.get('consumo_alcohol')) if 'consumo_alcohol' in df.columns else None,
                actividad_fisica=r.get('actividad_fisica') if 'actividad_fisica' in df.columns else (r.get('actividad_física') if 'actividad_física' in df.columns else None),
                diagnostico_preliminar=r.get('diagnostico_preliminar') if 'diagnostico_preliminar' in df.columns else None,
                riesgo_enfermedad=r.get('riesgo_enfermedad') if 'riesgo_enfermedad' in df.columns else None,
            )
        )

    ClinicalRecord.objects.bulk_create(bulk, batch_size=batch_size)
    return len(bulk)

