from __future__ import annotations

import io
from datetime import datetime

import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from etl.models import ClinicalRecord


def records_queryset_dataframe():
    qs = ClinicalRecord.objects.all()
    return pd.DataFrame(list(qs.values()))


class PDFExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        df = records_queryset_dataframe()

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        title = f"Clinical Records Export ({datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC)"
        c.setFont('Helvetica-Bold', 12)
        c.drawString(40, height - 50, title)

        c.setFont('Helvetica', 8)
        y = height - 70

        # limit lines to keep PDF readable
        max_rows = 30
        cols = list(df.columns)[:10]
        header = ' | '.join(cols)
        c.drawString(40, y, header)
        y -= 12

        for i, row in enumerate(df.head(max_rows).itertuples(index=False)):
            line = ' | '.join([str(x) for x in row[:10]])
            if y < 40:
                c.showPage()
                y = height - 50
            c.drawString(40, y, line)
            y -= 10

        c.showPage()
        c.save()

        filename = f"clinical_records_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
        resp = Response(buffer.getvalue(), content_type='application/pdf')
        resp['Content-Disposition'] = f'attachment; filename="{filename}"'
        return resp

