from __future__ import annotations

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from etl.models import ClinicalRecord


class KPIsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        qs = ClinicalRecord.objects.all()

        total_records = qs.count()

        # Riesgo (valores provienen del ETL)
        critical_patients = qs.filter(riesgo_enfermedad__iexact='Crítico').count()

        # Hipertensos (regla simple por presión sistólica/diastólica)

        # Nota: si tu dataset ya incluye otro campo de hipertensión, ajusta aquí.
        hypertensive_patients = qs.filter(
            presion_sistolica__isnull=False,
            presion_diastolica__isnull=False,
        ).filter(
            presion_sistolica__gte=140,
        ).union(
            qs.filter(presion_sistolica__isnull=False, presion_diastolica__gte=90)
        ).count()

        # Diabéticos (regla simple por glucosa)
        # Ajustable según criterio de tu documento.
        diabetic_patients = qs.filter(glucosa__isnull=False).filter(glucosa__gte=126).count()

        # Fumadores
        smoker_patients = qs.filter(fumador=True).count()

        # Riesgo promedio: map de categorías a numérico
        risk_map = {'Bajo': 0, 'Medio': 1, 'Alto': 2, 'Crítico': 3}
        risks = list(qs.values_list('riesgo_enfermedad', flat=True))
        numeric = [risk_map.get(str(r).strip().title().replace('Crítico', 'Crítico'), None) for r in risks]
        numeric = [v for v in numeric if v is not None]
        avg_risk = (sum(numeric) / len(numeric)) if numeric else 0

        return Response({
            'total_records': total_records,
            'critical_patients': critical_patients,
            'hypertensive_patients': hypertensive_patients,
            'diabetic_patients': diabetic_patients,
            'smoker_patients': smoker_patients,
            'avg_risk': avg_risk,
        })


