from datetime import date, timedelta
from io import BytesIO

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from django.http import HttpResponse
from django.utils import timezone

from reportlab.lib.pagesizes import landscape, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

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

        # --- ReportLab (paginación automática) ---
        output = BytesIO()
        doc = SimpleDocTemplate(
            output,
            pagesize=landscape(letter),
            rightMargin=18,
            leftMargin=18,
            topMargin=18,
            bottomMargin=18,
        )

        styles = getSampleStyleSheet()
        title_style = styles['Title']
        title_style.fontSize = 16

        elements = []
        elements.append(Paragraph('HealthAnalytics IPS - Reporte Ejecutivo', title_style))
        elements.append(Paragraph(f'Fecha: {date.today().strftime("%d/%m/%Y")}', styles['Normal']))
        elements.append(Spacer(1, 8))

        elements.append(Paragraph(f'Periodo solicitado: {periodo}', styles['Normal']))
        elements.append(Paragraph(f'Total pacientes en periodo: {len(df)}', styles['Normal']))
        elements.append(Spacer(1, 12))

        if include_kpis:
            riesgo_counts = df.get('riesgo_enfermedad', pd.Series(dtype=str)).value_counts(dropna=True).to_dict()
            imc_prom = float(pd.to_numeric(df.get('imc', pd.Series([0])), errors='coerce').mean())
            elements.append(Paragraph('KPIs Principales', styles['Heading2']))
            elements.append(Paragraph(f'IMC promedio: {imc_prom:.2f}', styles['Normal']))
            elements.append(Paragraph(f'Distribución riesgo: {riesgo_counts}', styles['Normal']))
            elements.append(Spacer(1, 12))

        # --- Gráficas (Matplotlib) -> PNG en memoria -> ReportLab Image ---
        # IMPORTANTE: la imagen se agrega SOLO UNA VEZ al principio del story.
        img = None
        if include_charts or include_kpis:
            fig = plt.figure(figsize=(12, 6))

            # Fondo/estilo liviano
            ax = fig.add_subplot(111)
            ax.axis('off')

            cursor_y = 0.95
            # Título secundario
            if include_kpis:
                riesgo_counts = df.get('riesgo_enfermedad', pd.Series(dtype=str)).value_counts(dropna=True).to_dict()
                imc_prom = float(pd.to_numeric(df.get('imc', pd.Series([0])), errors='coerce').mean())

                ax.text(0.02, cursor_y, 'KPIs Principales', fontsize=14, fontweight='bold', transform=ax.transAxes)
                cursor_y -= 0.06
                ax.text(0.02, cursor_y, f'IMC promedio: {imc_prom:.2f}', fontsize=12, transform=ax.transAxes)
                cursor_y -= 0.04
                ax.text(0.02, cursor_y, f'Distribución riesgo: {riesgo_counts}', fontsize=10, transform=ax.transAxes)
                cursor_y -= 0.06

            if include_charts:
                # Gráfico: distribución de riesgo
                try:
                    riesgo_col = 'riesgo_enfermedad' if 'riesgo_enfermedad' in df.columns else None
                    if riesgo_col:
                        series = df[riesgo_col]
                        vc = series.value_counts().sort_index()

                        ax_bar = fig.add_axes([0.55, 0.25, 0.40, 0.55])
                        ax_bar.bar(vc.index.astype(str), vc.values)
                        ax_bar.set_title('Riesgo - Conteo', fontsize=10)
                        ax_bar.set_xticklabels(vc.index.astype(str), rotation=45, ha='right', fontsize=8)
                        ax_bar.tick_params(axis='y', labelsize=8)
                except Exception:
                    pass

            fig.tight_layout()
            png_buffer = BytesIO()
            fig.savefig(png_buffer, format='png', dpi=200, bbox_inches='tight')
            plt.close(fig)
            png_buffer.seek(0)

            # Convertir a Image de ReportLab
            from reportlab.platypus import Image
            img = Image(png_buffer)

            # Restricción de tamaño máxima para evitar LayoutError
            img.drawWidth = 600
            img.drawHeight = 300

            # Agregar AL PRINCIPIO (antes de cualquier tabla)
            elements.append(img)
            elements.append(Spacer(1, 12))



        if include_table:
            columnas_esenciales = [
                'id_paciente',
                'nombres',
                'apellidos',
                'edad',
                'riesgo_enfermedad',
                'diagnostico_preliminar',
                'imc',
                'fecha_consulta',
            ]

            tabla_df = df.copy()
            columnas_existentes = [c for c in columnas_esenciales if c in tabla_df.columns]
            tabla_df = tabla_df[columnas_existentes]

            # Convertir a listas de listas para Table
            # Primera fila: encabezado
            headers = list(tabla_df.columns)
            data_rows = tabla_df.fillna('').values.tolist()
            table_data = [headers] + data_rows

            table = Table(table_data, repeatRows=1)
            table_style = TableStyle(
                [
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('ROWHEIGHT', (0, 1), (-1, -1), 20),
                    ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 2),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                ]
            )
            table.setStyle(table_style)

            elements.append(table)

        doc.build(elements)

        pdf_bytes = output.getvalue()
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
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


