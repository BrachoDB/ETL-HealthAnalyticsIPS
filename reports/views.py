import pandas as pd
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from analytics.models import Paciente
from ml.models import Prediccion
from etl.models import ETLRun

from .exporters import df_to_csv_bytes, df_to_excel_bytes, df_to_pdf_bytes


class ReportesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {
                'endpoints': {
                    'csv': '/api/reportes/export/csv/',
                    'excel': '/api/reportes/export/excel/',
                    'pdf': '/api/reportes/export/pdf/',
                }
            }
        )


class ExportReportBase(APIView):
    permission_classes = [IsAuthenticated]

    export_format: str = 'csv'  # override

    def build_df(self) -> pd.DataFrame:
        pac = Paciente.objects.all().values(
            'id_paciente',
            'nombres',
            'apellidos',
            'edad',
            'sexo',
            'imc',
            'presion_sistolica',
            'presion_diastolica',
            'glucosa',
            'colesterol',
            'saturacion_oxigeno',
            'temperatura',
            'fumador',
            'riesgo_enfermedad',
            'fecha_consulta',
        )
        pred = Prediccion.objects.all().values('paciente_id', 'riesgo_probabilidad', 'riesgo_clase')
        pred_map = {p['paciente_id']: p for p in pred}

        rows = []
        for p in pac:
            pp = pred_map.get(p['id_paciente'])
            rows.append(
                {
                    **p,
                    'riesgo_probabilidad': None if not pp else pp.get('riesgo_probabilidad'),
                    'riesgo_predicho': None if not pp else pp.get('riesgo_clase'),
                }
            )
        df = pd.DataFrame(rows)
        return df


class ExportCSVView(ExportReportBase):
    export_format = 'csv'

    def get(self, request):
        df = self.build_df()
        payload = df_to_csv_bytes(df)
        resp = HttpResponse(payload, content_type='text/csv; charset=utf-8')
        resp['Content-Disposition'] = 'attachment; filename="healthanalytics_reporte.csv"'
        return resp


class ExportExcelView(ExportReportBase):
    export_format = 'excel'

    def get(self, request):
        df = self.build_df()
        payload = df_to_excel_bytes(df)
        resp = HttpResponse(payload, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        resp['Content-Disposition'] = 'attachment; filename="healthanalytics_reporte.xlsx"'
        return resp


class ExportPDFView(ExportReportBase):
    export_format = 'pdf'

    def get(self, request):
        df = self.build_df()
        payload = df_to_pdf_bytes(df, title='HealthAnalytics IPS - Reporte Clínico')
        resp = HttpResponse(payload, content_type='application/pdf')
        resp['Content-Disposition'] = 'attachment; filename="healthanalytics_reporte.pdf"'
        return resp


