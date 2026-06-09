from __future__ import annotations

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


class ExcelExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        df = records_queryset_dataframe()

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='clinical_records')

        filename = f"clinical_records_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
        resp = Response(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        resp['Content-Disposition'] = f'attachment; filename="{filename}"'
        return resp

