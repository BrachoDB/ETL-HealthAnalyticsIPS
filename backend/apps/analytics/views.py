from datetime import date
from io import BytesIO
from statistics import mean, median, mode, stdev
from xml.sax.saxutils import escape

import pandas as pd
from django.http import HttpResponse
from django.db.models import Avg, Count, Q
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.analytics.models import ExportAudit
from apps.analytics.serializers import DashboardExtrasSerializer, ExportAuditSerializer, KPISerializer, PatientExportFormatSerializer
from apps.authentication.permissions import CanExportAnalytics, IsReadOnlyClinicalRole
from apps.etl.models import Patient
from apps.ml.models import MLModelMetrics


RISK_ORDER = ['Bajo', 'Medio', 'Alto', 'Crítico']


class KPIView(APIView):
    permission_classes = [IsReadOnlyClinicalRole]
    serializer_class = KPISerializer

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
    permission_classes = [IsReadOnlyClinicalRole]
    serializer_class = DashboardExtrasSerializer

    def get(self, request):
        return Response({
            'tendencias': self._tendencias(),
            'heatmap': self._heatmap(),
            'diagnosticos': self._diagnosticos(),
            'mensual': self._mensual(),
            'estadistica': self._estadistica_descriptiva(),
            'pacientes': self._pacientes(),
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

    def _diagnosticos(self):
        rows = (
            Patient.objects
            .values('diagnostico_preliminar')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )
        return {
            'labels': [row['diagnostico_preliminar'] for row in rows],
            'data': [row['count'] for row in rows],
        }

    def _mensual(self):
        grouped = {}
        risk_scores = {'Bajo': 1, 'Medio': 2, 'Alto': 3, 'Crítico': 4}
        for paciente in Patient.objects.values('fecha_consulta', 'riesgo_enfermedad'):
            month = paciente['fecha_consulta'].strftime('%Y-%m')
            grouped.setdefault(month, {'total': 0, 'risk_sum': 0, 'criticos': 0})
            grouped[month]['total'] += 1
            grouped[month]['risk_sum'] += risk_scores.get(paciente['riesgo_enfermedad'], 1)
            if paciente['riesgo_enfermedad'] == 'Crítico':
                grouped[month]['criticos'] += 1

        labels = sorted(grouped.keys())
        return {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Riesgo promedio',
                    'data': [round(grouped[label]['risk_sum'] / grouped[label]['total'], 2) for label in labels],
                    'borderColor': '#0d6efd',
                    'backgroundColor': 'rgba(13, 110, 253, 0.15)',
                    'yAxisID': 'y',
                },
                {
                    'label': 'Casos críticos',
                    'data': [grouped[label]['criticos'] for label in labels],
                    'borderColor': '#dc3545',
                    'backgroundColor': 'rgba(220, 53, 69, 0.15)',
                    'yAxisID': 'y1',
                },
            ],
        }

    def _estadistica_descriptiva(self):
        fields = [
            ('edad', 'Edad'),
            ('imc', 'IMC'),
            ('presion_sistolica', 'Presión sistólica'),
            ('presion_diastolica', 'Presión diastólica'),
            ('frecuencia_cardiaca', 'Frecuencia cardiaca'),
            ('glucosa', 'Glucosa'),
            ('colesterol', 'Colesterol'),
            ('saturacion_oxigeno', 'Saturación O2'),
            ('temperatura', 'Temperatura'),
        ]
        stats = []
        for field, label in fields:
            values = list(Patient.objects.values_list(field, flat=True))
            if not values:
                continue
            stats.append({
                'variable': label,
                'media': round(mean(values), 2),
                'mediana': round(median(values), 2),
                'moda': mode(values) if values else None,
                'desviacion': round(stdev(values), 2) if len(values) > 1 else 0,
                'min': min(values),
                'max': max(values),
            })
        return stats

    def _pacientes(self):
        rows = Patient.objects.all().order_by('-fecha_consulta', '-id_paciente')
        return [
            {
                'id_paciente': row.id_paciente,
                'nombres': row.nombres,
                'apellidos': row.apellidos,
                'edad': row.edad,
                'sexo': row.sexo,
                'diagnostico_preliminar': row.diagnostico_preliminar,
                'riesgo_enfermedad': row.riesgo_enfermedad,
                'presion_sistolica': row.presion_sistolica,
                'glucosa': row.glucosa,
                'saturacion_oxigeno': row.saturacion_oxigeno,
                'fecha_consulta': row.fecha_consulta.isoformat(),
            }
            for row in rows
        ]

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

        classes = []
        try:
            from apps.ml.services import load_model_bundle
            model, label_encoder, _, _ = load_model_bundle()
            classes = list(label_encoder.classes_)
        except Exception:
            pass

        return {
            'model_name': metrica.model_name,
            'model_version': getattr(metrica, 'model_version', 'random_forest_v1'),
            'model_hash': getattr(metrica, 'model_hash', None),
            'accuracy': round(metrica.accuracy, 4),
            'precision': round(metrica.precision, 4),
            'recall': round(metrica.recall, 4),
            'f1_score': round(metrica.f1_score, 4),
            'confusion_matrix': metrica.confusion_matrix,
            'classes': classes,
            'trained_at': metrica.trained_at.strftime('%Y-%m-%d %H:%M:%S'),
            'dataset': f'{Patient.objects.count()} registros clínicos',
        }


class ExportAuditListView(APIView):
    """Ruta de lectura del Histórico de Descargas.

    Expone los registros ya persistidos en ExportAudit (no genera nada nuevo).
    El frontend (reportes.js) consume esta vista para poblar #tableDownloads.
    """

    permission_classes = [IsReadOnlyClinicalRole]
    serializer_class = ExportAuditSerializer

    def get(self, request):
        try:
            limit = int(request.GET.get('limit', 25))
        except (TypeError, ValueError):
            limit = 25
        limit = max(1, min(limit, 200))

        queryset = ExportAudit.objects.select_related('usuario').all()[:limit]
        data = ExportAuditSerializer(queryset, many=True).data
        return Response({'total': len(data), 'resultados': data})


class PatientExportView(APIView):
    permission_classes = [CanExportAnalytics]
    serializer_class = PatientExportFormatSerializer

    def get(self, request, export_format):
        export_format = export_format.lower()
        pacientes = list(Patient.objects.all().values())
        if not pacientes:
            return Response({'error': 'No hay datos para exportar'}, status=status.HTTP_404_NOT_FOUND)

        ExportAudit.objects.create(
            usuario=request.user,
            export_format=export_format,
            total_rows=len(pacientes),
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
        )

        df = self._prepare_export_dataframe(pd.DataFrame(pacientes))
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
            styles = getSampleStyleSheet()
            styles['Title'].fontSize = 16
            styles['Heading2'].fontSize = 12
            styles['Normal'].fontSize = 8
            styles['Normal'].leading = 9

            def cell(value):
                if value is None:
                    value = ''
                if hasattr(value, 'strftime'):
                    value = value.strftime('%Y-%m-%d')
                return Paragraph(escape(str(value)), styles['Normal'])

            table_data = [[
                'ID',
                'Paciente',
                'Edad',
                'Sexo',
                'Diagnóstico',
                'Riesgo',
                'PAS',
                'Glucosa',
                'Sat. O2',
                'Fecha',
            ]]

            for row in pacientes:
                table_data.append([
                    row.get('id_paciente', ''),
                    f"{row.get('nombres', '')} {row.get('apellidos', '')}".strip(),
                    row.get('edad', ''),
                    row.get('sexo', ''),
                    row.get('diagnostico_preliminar', ''),
                    row.get('riesgo_enfermedad', ''),
                    row.get('presion_sistolica', ''),
                    row.get('glucosa', ''),
                    row.get('saturacion_oxigeno', ''),
                    row.get('fecha_consulta', ''),
                ])

            table_data = [[cell(item) for item in row] for row in table_data]
            table = Table(table_data, repeatRows=1, colWidths=[35, 115, 35, 55, 130, 55, 45, 55, 55, 75])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('ROWHEIGHT', (0, 1), (-1, -1), 20),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 3),
                ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ]))

            output = BytesIO()
            doc = SimpleDocTemplate(
                output,
                pagesize=landscape(letter),
                rightMargin=18,
                leftMargin=18,
                topMargin=18,
                bottomMargin=18,
            )
            elements = [
                Paragraph('HealthAnalytics IPS - Analítica de Pacientes', styles['Title']),
                Paragraph(f'Fecha: {date.today().strftime("%d/%m/%Y")}', styles['Normal']),
                Paragraph(f'Total registros: {len(df)}', styles['Normal']),
                Spacer(1, 8),
                Paragraph('Registros clínicos', styles['Heading2']),
                Spacer(1, 8),
                table,
            ]
            doc.build(elements)

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
