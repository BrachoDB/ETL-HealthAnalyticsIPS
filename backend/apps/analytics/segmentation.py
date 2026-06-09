from __future__ import annotations

from collections import Counter
from typing import Any

from etl.models import ClinicalRecord


def _age_bucket(age: int | None) -> str | None:
    if age is None:
        return None
    try:
        a = int(age)
    except Exception:
        return None
    if a < 30:
        return '<30'
    if a < 45:
        return '30-44'
    if a < 60:
        return '45-59'
    return '>=60'


def segmentation_payload() -> dict[str, Any]:
    qs = ClinicalRecord.objects.all()

    sexo = dict(Counter(qs.exclude(sex__isnull=True).values_list('sex', flat=True)))
    diagnostico = dict(
        Counter(
            qs.exclude(diagnostico_preliminar__isnull=True).values_list(
                'diagnostico_preliminar', flat=True
            )
        )
    )
    riesgo = dict(Counter(qs.exclude(riesgo_enfermedad__isnull=True).values_list('riesgo_enfermedad', flat=True)))

    imc_bins = {'<18.5': 0, '18.5-24.9': 0, '25-29.9': 0, '>=30': 0}
    for v in qs.exclude(imc__isnull=True).values_list('imc', flat=True):
        try:
            x = float(v)
        except Exception:
            continue
        if x < 18.5:
            imc_bins['<18.5'] += 1
        elif x < 25:
            imc_bins['18.5-24.9'] += 1
        elif x < 30:
            imc_bins['25-29.9'] += 1
        else:
            imc_bins['>=30'] += 1

    age_bins = {'<30': 0, '30-44': 0, '45-59': 0, '>=60': 0}
    for v in qs.exclude(age__isnull=True).values_list('age', flat=True):
        b = _age_bucket(v)
        if not b:
            continue
        if b in age_bins:
            age_bins[b] += 1

    return {
        'edad': age_bins,
        'sexo': sexo,
        'diagnostico': diagnostico,
        'imc': imc_bins,
        'riesgo': riesgo,
    }

