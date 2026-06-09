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


class AnalyticsStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        qs = ClinicalRecord.objects.all()

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

        imc_vals = list(qs.exclude(imc__isnull=True).values_list('imc', flat=True))
        edad_vals = list(qs.exclude(age__isnull=True).values_list('age', flat=True))
        gluc_vals = list(qs.exclude(glucosa__isnull=True).values_list('glucosa', flat=True))

        return Response({
            'total_records': qs.count(),
            'media_mediana_moda_desv_std': {
                'imc': stats(imc_vals),
                'edad': stats(edad_vals),
                'glucosa': stats(gluc_vals),
            },
        })

