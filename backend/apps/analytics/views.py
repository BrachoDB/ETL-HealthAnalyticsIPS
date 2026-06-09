from __future__ import annotations

from collections import Counter

import numpy as np

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from etl.models import ClinicalRecord

from .statistics import mean, median, mode, std_deviation


class AnalyticsStatsView(APIView):
    permission_classes = [IsAuthenticated]


    def get(self, request, *args, **kwargs):
        qs = ClinicalRecord.objects.all()

        def stats(vals):
            normalized = [float(v) if '.' in str(v) else int(v) for v in vals] if vals else []
            return {
                'media': mean(normalized),
                'mediana': median(normalized),
                'moda': mode(normalized),
                'desv_std': std_deviation(normalized),
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


