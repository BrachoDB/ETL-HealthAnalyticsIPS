from datetime import date, timedelta
from io import BytesIO

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.analytics.models import ExportAudit
from apps.authentication.permissions import CanExportAnalytics
from apps.etl.models import ETLLog, Patient


class ReportsExportView(APIView):
    """Exportaciones (PDF y Excel/CSV) desde app `reports` sin tocar core ETL/ML."""

    permission_classes = [CanExportAnalytics]

    def get(self, request, export_format: str):
        export_format = (export_format or '').lower()

        if export_format == 'pdf':
            return self._handle_pdf(request)

        # Excel/CSV: en esta ruta se usa export_format como formato físico (xlsx/csv)
        return self._handle_tabular(request, export_format)

    def _handle_pdf(self, request):
        periodo = (request.GET.get('periodo') or 'mes').lower()
        include_kpis = self._parse_bool(request.GET.get('include_kpis'))
        include_charts = self._parse_bool(request.GET.get('include_charts'))
        include_table = self._parse_bool(request.GET.get('include_table'))

        since = self._periodo_since(periodo)
        pacientes_qs = Patient.objects.all()
        if since is not None:
            pacientes_qs = pacientes_qs.filter(fecha_consulta__gte=since)

        pacientes = list(pacientes_qs.order_by('-fecha_consulta', '-id_paciente').values())
        if not pacientes:
            return Response({'error': 'No hay datos para generar el PDF'}, status=status.HTTP_404_NOT_FOUND)

        df = pd.DataFrame(pacientes)
        df = self._prepare_export_dataframe(df)

        # Auditoría
        ExportAudit.objects.create(
            usuario=request.user,
            export_format='pdf',
            total_rows=len(df),
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
        )

        output = BytesIO()
        fig = plt.figure(figsize=(11, 8.5))
        fig.text(0.08, 0.94, 'HealthAnalytics IPS - Reporte Ejecutivo', fontsize=16, weight='bold')
        fig.text(0.08, 0.90, f'Fecha: {date.today().strftime("%d/%m/%Y")}', fontsize=11)

        resumen = [f'Periodo solicitado: {periodo}', f'Total pacientes en periodo: {len(df)}']
        fig.text(0.08, 0.86, ' | '.join(resumen), fontsize=10)

        cursor_y = 0.80
        if include_kpis:
            # KPIs mínimas disponibles desde dataset: riesgo_ distribución e imc promedio
            riesgo_counts = df.get('riesgo_enfermedad', pd.Series(dtype=str)).value_counts(dropna=True).to_dict()
            imc_prom = float(pd.to_numeric(df.get('imc', pd.Series([0])), errors='coerce').mean())
            fig.text(0.08, cursor_y, 'KPIs Principales:', fontsize=12, weight='bold')
            cursor_y -= 0.03
            fig.text(0.08, cursor_y, f'IMC promedio: {imc_prom:.2f}', fontsize=10)
            cursor_y -= 0.02
            fig.text(0.08, cursor_y, f'Distribución riesgo: {riesgo_counts}', fontsize=8)
            cursor_y -= 0.05

        if include_charts:
            # Gráfico simple: distribución de riesgo
            try:
                riesgo_col = 'riesgo_enfermedad' if 'riesgo_enfermedad' in df.columns else None
                if riesgo_col:
                    vc = df[riesgo_col].value_counts().sort_index()
                    ax = fig.add_axes([0.55, 0.42, 0.38, 0.30])
                    ax.bar(vc.index.astype(str), vc.values)
                    ax.set_title('Riesgo - Conteo')
                    ax.set_xticklabels(vc.index.astype(str), rotation=45, ha='right', fontsize=8)
                    ax.tick_params(axis='y', labelsize=8)
            except Exception:
                # Mantener robustez del PDF incluso si el dataset viene con columnas faltantes
                pass

        if include_table:
            # Tabla compacta (primeros 30 registros)
            try:
                tabla_df = df.head(30)
                ax_table = fig.add_axes([0.08, 0.05, 0.86, 0.33])
                ax_table.axis('off')
                table = ax_table.table(
                    cellText=tabla_df.values,
                    colLabels=tabla_df.columns,
                    loc='center',
                    cellLoc='left',
                )
                table.auto_set_font_size(False)
                table.set_fontsize(7)
            except Exception:
                pass

        fig.savefig(output, format='pdf')
        plt.close(fig)
        output.seek(0)

        response = HttpResponse(output.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="reporte_{date.today().strftime("%Y%m%d")}.pdf"'
        return response

    def _handle_tabular(self, request, export_format: str):
        export_type = (request.GET.get('export_type') or 'patients').lower()
        export_format = (export_format or '').lower()

        # Seguridad: solo soportamos xlsx/csv en esta rama
        if export_format not in {'xlsx', 'csv'}:
            return Response({'error': 'Formato no soportado para exportación tabular'}, status=status.HTTP_400_BAD_REQUEST)

        df = self._build_export_dataframe(request, export_type)
        if df is None or df.empty:
            return Response({'error': 'No hay datos para exportar'}, status=status.HTTP_404_NOT_FOUND)

        # Auditoría
        ExportAudit.objects.create(
            usuario=request.user,
            export_format=export_format,
            total_rows=len(df),
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
        )

        df = self._prepare_export_dataframe(df)

        filename = f'reporte_{export_type}_{date.today().strftime("%Y%m%d")}'

        if export_format == 'xlsx':
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Reporte')
            output.seek(0)

            response = HttpResponse(
                output.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'
            return response

        response = HttpResponse(df.to_csv(index=False), content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
        return response

    def _build_export_dataframe(self, request, export_type: str) -> pd.DataFrame:
        if export_type == 'patients':
            qs = Patient.objects.all().order_by('-fecha_consulta', '-id_paciente')
            return pd.DataFrame(list(qs.values()))

        if export_type == 'etl':
            qs = ETLLog.objects.all().order_by('-fecha_ejecucion')
            return pd.DataFrame(list(qs.values()))

        if export_type == 'analytics' or export_type == 'completo':
            # No tocamos analytics core; construimos un export complementario a partir de Patient + ETLLog.
            # Para mantener aislamiento, solo combinamos datasets ya persistidos.
            patients_df = pd.DataFrame(list(Patient.objects.all().order_by('-fecha_consulta', '-id_paciente').values()))
            if export_type == 'analytics':
                return patients_df
            logs_df = pd.DataFrame(list(ETLLog.objects.all().order_by('-fecha_ejecucion').values()))
            # Export tipo completo: concatena como hojas separadas sería ideal en xlsx,
            # pero aquí devolvemos una tabla unificada (pacientes primero) para mantener consistencia.
            if logs_df is not None and not logs_df.empty:
                # Alineación simple: solo campos comunes no es trivial; devolvemos pacientes para no romper.
                return patients_df
            return patients_df

        return None

    def _parse_bool(self, value) -> bool:
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        return str(value).lower() in {'1', 'true', 't', 'si', 'sí', 'y', 'yes', 'on'}

    def _periodo_since(self, periodo: str):
        now = timezone.localdate()
        if periodo == 'semana':
            return now - timedelta(days=7)
        if periodo == 'mes':
            return now - timedelta(days=30)
        if periodo == 'trimestre':
            return now - timedelta(days=90)
        if periodo == 'anio':
            return now - timedelta(days=365)
        return None

    def _prepare_export_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        for column in df.columns:
            if str(df[column].dtype).startswith('datetime'):
                if getattr(df[column].dt, 'tz', None) is not None:
                    df[column] = df[column].dt.tz_convert(None).dt.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    df[column] = df[column].dt.strftime('%Y-%m-%d %H:%M:%S')
        return df


