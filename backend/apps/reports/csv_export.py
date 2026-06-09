from __future__ import annotations

import csv
import io
from datetime import datetime

import pandas as pd
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from etl.models import ClinicalRecord


def records_queryset_dataframe():
    qs = ClinicalRecord.objects.all()
    return pd.DataFrame(list(qs.values()))


class CSVExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        df = records_queryset_dataframe()

        buff = io.StringIO()
        writer = csv.writer(buff)
        # header
        writer.writerow(list(df.columns))
        # rows
        for row in df.itertuples(index=False):
            writer.writerow(list(row))

        filename = f"clinical_records_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        resp = Response(buff.getvalue(), content_type='text/csv; charset=utf-8')
        resp['Content-Disposition'] = f'attachment; filename="{filename}"'
        return resp

