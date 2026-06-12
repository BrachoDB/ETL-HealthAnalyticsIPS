from datetime import date
from io import BytesIO

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from django.http import HttpResponse
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count, Avg
from matplotlib.backends.backend_pdf import PdfPages

from apps.etl.models import Patient


RISK_ORDER = ['Bajo', 'Medio', 'Alto', 'Crítico']


class KPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        total_pacientes = Patient.objects.count()
        if total_pacientes == 0:
            return Response({'error': 'No hay datos'}, status=status.HTTP_404_NOT_FOUND)

        riesgo_dist = (
            Patient.objects
            .values('riesgo_enfermedad')
            .annotate(count=Count('id'))
            .order_by('riesgo_enfermedad')
        )

        criticos = Patient.objects.filter(riesgo_enfermedad='Crítico').count()
        hipertensos = Patient.objects.filter(presion_sistolica__gt=140).count()
        diabeticos = Patient.objects.filter(glucosa__gt=126).count()
        imc_avg = Patient.objects.aggregate(avg_imc=Avg('imc'))['avg_imc']

        return Response({
            'total_pacientes': total_pacientes,
            'riesgo_distribucion': list(riesgo_dist),
            'edad_riesgo': self._edad_riesgo(),
            'pacientes_criticos': criticos,
            'hipertensos': hipertensos,
            'diabeticos': diabeticos,
            'imc_promedio': imc_avg,
        })

    def _edad_riesgo(self):
        grouped = {}
        for paciente in Patient.objects.values('edad', 'riesgo_enfermedad'):
            grupo = self._edad_grupo(paciente['edad'])
            riesgo = paciente['riesgo_enfermedad'] or 'Bajo'
            grouped.setdefault(grupo, {risk: 0 for risk in RISK_ORDER})
            grouped[grupo][riesgo] = grouped[grupo].get(riesgo, 0) + 1

        labels = sorted(grouped.keys(), key=lambda value: int(value.split('-')[0]))
        datasets = []
        for risk in RISK_ORDER:
            datasets.append({
                'label': risk,
                'data': [grouped[label].get(risk, 0) for label in labels],
            })

        return {
            'labels': labels,
            'datasets': datasets,
        }

    def _edad_grupo(self, edad):
        edad = int(edad or 0)
        if edad < 18:
            return '0-17'
        if edad < 30:
            return '18-29'
        if edad < 45:
            return '30-44'
        if edad < 60:
            return '45-59'
        if edad < 75:
            return '60-74'
        return '75+'


class PatientExportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, export_format):
        pacientes = list(Patient.objects.all().values())
        if not pacientes:
            return Response({'error': 'No hay datos para exportar'}, status=status.HTTP_404_NOT_FOUND)

        df = pd.DataFrame(pacientes)
        export_format = export_format.lower()
        filename = f'pacientes_{date.today().strftime("%Y%m%d")}'

        if export_format == 'xlsx':
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Pacientes')
            output.seek(0)
            response = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'
            return response

        if export_format == 'csv':
            response = HttpResponse(df.to_csv(index=False), content_type='text/csv; charset=utf-8')
            response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
            return response

        if export_format == 'pdf':
            output = BytesIO()
            with PdfPages(output) as pdf:
                fig = plt.figure(figsize=(11, 8.5))
                fig.text(0.08, 0.94, 'HealthAnalytics IPS - Exportación de Pacientes', fontsize=16, weight='bold')
                fig.text(0.08, 0.90, f'Fecha: {date.today().strftime("%d/%m/%Y")}', fontsize=11)
                fig.text(0.08, 0.86, f'Total pacientes: {len(df)}', fontsize=11)
                fig.text(0.08, 0.80, 'Columnas exportadas: ' + ', '.join(df.columns), fontsize=9, wrap=True)
                fig.axis('off')
                pdf.savefig(fig)
                plt.close(fig)
            response = HttpResponse(output.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
            return response

        return Response({'error': 'Formato no soportado'}, status=status.HTTP_400_BAD_REQUEST)
