from __future__ import annotations

from collections import Counter

from etl.models import ClinicalRecord


def kpis_clinical() -> dict:
    qs = ClinicalRecord.objects.all()

    total_records = qs.count()

    critical_patients = qs.filter(riesgo_enfermedad__iexact='Crítico').count()

    hypertensive_patients = qs.filter(
        presion_sistolica__isnull=False,
        presion_diastolica__isnull=False,
    ).filter(
        presion_sistolica__gte=140,
    ).union(
        qs.filter(presion_sistolica__isnull=False, presion_diastolica__gte=90)
    ).count()

    diabetic_patients = qs.filter(glucosa__isnull=False, glucosa__gte=126).count()

    smoker_patients = qs.filter(fumador=True).count()

    risk_map = {'Bajo': 0, 'Medio': 1, 'Alto': 2, 'Crítico': 3}
    risks = list(qs.values_list('riesgo_enfermedad', flat=True))
    numeric = []
    for r in risks:
        if r is None:
            continue
        key = str(r).strip().title().replace('Crítico', 'Crítico')
        if key in risk_map:
            numeric.append(risk_map[key])

    avg_risk = (sum(numeric) / len(numeric)) if numeric else 0

    return {
        'total_records': total_records,
        'critical_patients': critical_patients,
        'hypertensive_patients': hypertensive_patients,
        'diabetic_patients': diabetic_patients,
        'smoker_patients': smoker_patients,
        'avg_risk': avg_risk,
    }

