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
from django.db.models import Avg, Count, Q
from matplotlib.backends.backend_pdf import PdfPages

from apps.etl.models import Patient
from apps.ml.models import MLModelMetrics


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

        labels = sorted(grouped.keys(), key=self._edad_grupo_sort_key)
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

    def _edad_grupo_sort_key(self, value):
        if value.endswith('+'):
            return int(value[:-1])
        return int(value.split('-')[0])

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


class DashboardExtrasView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({
            'tendencias': self._tendencias(),
            'heatmap': self._heatmap(),
            'criticos': self._criticos(),
            'segmentacion': self._segmentacion(),
            'ml_metricas': self._ml_metricas(),
        })

    def _edad_grupo_sort_key(self, value):
        if value.endswith('+'):
            return int(value[:-1])
        return int(value.split('-')[0])

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

    def _tendencias(self):
        rows = (
            Patient.objects
            .values('fecha_consulta')
            .annotate(
                total=Count('id'),
                criticos=Count('id', filter=Q(riesgo_enfermedad='Crítico')),
                promedio_glucosa=Avg('glucosa'),
                promedio_presion=Avg('presion_sistolica'),
            )
            .order_by('fecha_consulta')
        )
        return {
            'labels': [row['fecha_consulta'].isoformat() for row in rows],
            'datasets': [
                {
                    'label': 'Total pacientes',
                    'data': [row['total'] for row in rows],
                    'borderColor': '#0d6efd',
                    'backgroundColor': 'rgba(13, 110, 253, 0.15)',
                },
                {
                    'label': 'Críticos',
                    'data': [row['criticos'] for row in rows],
                    'borderColor': '#dc3545',
                    'backgroundColor': 'rgba(220, 53, 69, 0.15)',
                },
                {
                    'label': 'Glucosa promedio',
                    'data': [round(row['promedio_glucosa'] or 0, 2) for row in rows],
                    'borderColor': '#198754',
                    'backgroundColor': 'rgba(25, 135, 84, 0.15)',
                    'yAxisID': 'y1',
                },
            ],
        }

    def _heatmap(self):
        grouped = {}
        for paciente in Patient.objects.values('edad', 'riesgo_enfermedad'):
            edad_grupo = self._edad_grupo(paciente['edad'])
            riesgo = paciente['riesgo_enfermedad'] or 'Bajo'
            grouped.setdefault(edad_grupo, {risk: 0 for risk in RISK_ORDER})
            grouped[edad_grupo][riesgo] = grouped[edad_grupo].get(riesgo, 0) + 1

        labels = sorted(grouped.keys(), key=self._edad_grupo_sort_key)
        matrix = [[grouped[label].get(risk, 0) for risk in RISK_ORDER] for label in labels]
        return {
            'labels': labels,
            'risks': RISK_ORDER,
            'matrix': matrix,
        }

    def _criticos(self):
        queryset = Patient.objects.filter(
            Q(presion_sistolica__gt=180) |
            Q(glucosa__gt=300) |
            Q(saturacion_oxigeno__lt=85) |
            Q(riesgo_enfermedad='Crítico')
        ).order_by('-presion_sistolica', '-glucosa')[:10]

        return [
            {
                'id_paciente': paciente['id_paciente'],
                'nombres': paciente['nombres'],
                'apellidos': paciente['apellidos'],
                'riesgo_enfermedad': paciente['riesgo_enfermedad'],
                'presion_sistolica': paciente['presion_sistolica'],
                'glucosa': paciente['glucosa'],
                'saturacion_oxigeno': paciente['saturacion_oxigeno'],
            }
            for paciente in queryset.values(
                'id_paciente',
                'nombres',
                'apellidos',
                'riesgo_enfermedad',
                'presion_sistolica',
                'glucosa',
                'saturacion_oxigeno',
            )
        ]

    def _segmentacion(self):
        return {
            'sexo': self._segmentar_por('sexo'),
            'riesgo': self._segmentar_por('riesgo_enfermedad'),
            'diagnostico': self._segmentar_por('diagnostico_preliminar')[:8],
        }

    def _segmentar_por(self, campo):
        rows = (
            Patient.objects
            .values(campo)
            .annotate(
                total=Count('id'),
                criticos=Count('id', filter=Q(riesgo_enfermedad='Crítico')),
                imc_promedio=Avg('imc'),
            )
            .order_by('-total')
        )
        return [
            {
                'label': row[campo] or 'Sin dato',
                'total': row['total'],
                'criticos': row['criticos'],
                'imc_promedio': round(row['imc_promedio'] or 0, 2),
            }
            for row in rows
        ]

    def _ml_metricas(self):
        metrica = MLModelMetrics.objects.order_by('-trained_at').first()
        if not metrica:
            return None
        return {
            'model_name': metrica.model_name,
            'accuracy': round(metrica.accuracy, 4),
            'precision': round(metrica.precision, 4),
            'recall': round(metrica.recall, 4),
            'f1_score': round(metrica.f1_score, 4),
            'trained_at': metrica.trained_at.strftime('%Y-%m-%d %H:%M:%S'),
        }


class PatientExportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, export_format):
        pacientes = list(Patient.objects.all().values())
        if not pacientes:
            return Response({'error': 'No hay datos para exportar'}, status=status.HTTP_404_NOT_FOUND)

        df = self._prepare_export_dataframe(pd.DataFrame(pacientes))
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
                pdf.savefig(fig)
                plt.close(fig)
            response = HttpResponse(output.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
            return response

        return Response({'error': 'Formato no soportado'}, status=status.HTTP_400_BAD_REQUEST)

    def _prepare_export_dataframe(self, df):
        df = df.copy()
        for column in df.columns:
            if str(df[column].dtype).startswith('datetime'):
                if getattr(df[column].dt, 'tz', None) is not None:
                    df[column] = df[column].dt.tz_convert(None).dt.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    df[column] = df[column].dt.strftime('%Y-%m-%d %H:%M:%S')
        return df
