from __future__ import annotations

from collections import Counter

import numpy as np

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from etl.models import ClinicalRecord


def _mode(values: list[float | int]) -> float | int | None:
    if not values:
        return None
    c = Counter(values)
    return c.most_common(1)[0][0]


class ReportsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        qs = ClinicalRecord.objects.all()
        total = qs.count()

        imc_vals = list(qs.exclude(imc__isnull=True).values_list('imc', flat=True))
        age_vals = list(qs.exclude(age__isnull=True).values_list('age', flat=True))
        gluc_vals = list(qs.exclude(glucosa__isnull=True).values_list('glucosa', flat=True))

        def stats(vals):
            if not vals:
                return {'media': 0, 'mediana': 0, 'moda': None, 'desv_std': 0}
            arr = np.array(vals, dtype=float)
            return {
                'media': float(arr.mean()),
                'mediana': float(np.median(arr)),
                'moda': _mode([float(v) if '.' in str(v) else int(v) for v in vals]) if vals else None,
                'desv_std': float(arr.std(ddof=0)),
            }

        stats_payload = {
            'imc': stats(imc_vals),
            'edad': stats(age_vals),
            'glucosa': stats(gluc_vals),
        }

        sexo = dict(Counter(qs.exclude(sex__isnull=True).values_list('sex', flat=True)))
        diagnostico = dict(
            Counter(
                qs.exclude(diagnostico_preliminar__isnull=True).values_list(
                    'diagnostico_preliminar', flat=True
                )
            )
        )
        riesgo = dict(
            Counter(qs.exclude(riesgo_enfermedad__isnull=True).values_list('riesgo_enfermedad', flat=True))
        )

        imc_bins = {'<18.5': 0, '18.5-24.9': 0, '25-29.9': 0, '>=30': 0}
        for v in imc_vals:
            v = float(v)
            if v < 18.5:
                imc_bins['<18.5'] += 1
            elif v < 25:
                imc_bins['18.5-24.9'] += 1
            elif v < 30:
                imc_bins['25-29.9'] += 1
            else:
                imc_bins['>=30'] += 1

        age_bins = {'<30': 0, '30-44': 0, '45-59': 0, '>=60': 0}
        for v in age_vals:
            v = int(v)
            if v < 30:
                age_bins['<30'] += 1
            elif v < 45:
                age_bins['30-44'] += 1
            elif v < 60:
                age_bins['45-59'] += 1
            else:
                age_bins['>=60'] += 1

        return Response(
            {
                'total_records': total,
                'stats': stats_payload,
                'segmentaciones': {
                    'edad': age_bins,
                    'sexo': sexo,
                    'diagnostico': diagnostico,
                    'imc': imc_bins,
                    'riesgo': riesgo,
                },
            }
        )

