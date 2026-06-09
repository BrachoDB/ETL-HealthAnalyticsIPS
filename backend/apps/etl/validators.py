from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass
class ValidationErrorDetail:
    field: str
    message: str


def validate_ranges(record: dict) -> list[ValidationErrorDetail]:
    """Valida rangos clínicos básicos. No detiene el ETL; devuelve errores encontrados."""
    errs: list[ValidationErrorDetail] = []

    def _num(v):
        try:
            if v is None:
                return None
            return float(v)
        except Exception:
            return None

    age = _num(record.get('edad') or record.get('age'))
    if age is not None and not (0 <= age <= 120):
        errs.append(ValidationErrorDetail('edad', 'edad fuera de rango (0-120)'))

    peso = _num(record.get('peso'))
    if peso is not None and not (0 <= peso <= 400):
        errs.append(ValidationErrorDetail('peso', 'peso fuera de rango (0-400)'))

    altura = _num(record.get('altura'))
    if altura is not None and not (0.3 <= altura <= 2.5):
        errs.append(ValidationErrorDetail('altura', 'altura fuera de rango (0.3-2.5)'))

    glucosa = _num(record.get('glucosa'))
    if glucosa is not None and not (0 <= glucosa <= 600):
        errs.append(ValidationErrorDetail('glucosa', 'glucosa fuera de rango (0-600)'))

    t_sis = _num(record.get('presion_sistolica'))
    t_dia = _num(record.get('presion_diastolica'))
    if t_sis is not None and not (60 <= t_sis <= 260):
        errs.append(ValidationErrorDetail('presion_sistolica', 'presión sistólica fuera de rango (60-260)'))
    if t_dia is not None and not (30 <= t_dia <= 160):
        errs.append(ValidationErrorDetail('presion_diastolica', 'presión diastólica fuera de rango (30-160)'))

    return errs


def summarize_errors(errors: Iterable[ValidationErrorDetail]) -> str:
    lst = list(errors)
    if not lst:
        return ''
    # Compacto para guardar en error_detail
    return '; '.join(f"{e.field}: {e.message}" for e in lst)

