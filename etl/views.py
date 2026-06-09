from __future__ import annotations

import os
import time

from django.core.files.uploadedfile import UploadedFile
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .etl_engine import run_etl
from .models import ClinicalRecord, ETLRun


class ETLRunView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        start = time.time()

        file_obj = request.FILES.get('file') if hasattr(request, 'FILES') else None

        default_path = os.path.join(os.getcwd(), 'dataset_clinico_etl_1800_registros.xlsx')
        source_filename = ''
        excel_bytes = None
        csv_bytes = None

        if file_obj and isinstance(file_obj, UploadedFile):
            source_filename = getattr(file_obj, 'name', '') or 'upload'
            name_lower = source_filename.lower()
            excel_bytes = file_obj.read() if name_lower.endswith(('.xlsx', '.xls')) else None
            csv_bytes = file_obj.read() if name_lower.endswith('.csv') else None
        else:
            # fallback dataset del repo
            with open(default_path, 'rb') as f:
                excel_bytes = f.read()
            source_filename = 'dataset_clinico_etl_1800_registros.xlsx'

        etl_run = ETLRun.objects.create(
            user=user,
            source_filename=source_filename,
            status=ETLRun.Status.PENDING,
        )

        try:
            df, _ = run_etl(excel_bytes=excel_bytes, csv_bytes=csv_bytes, source_filename=source_filename)

            # LOAD: insertar limpios
            bulk = []
            for _, r in df.iterrows():
                bulk.append(
                    ClinicalRecord(
                        sex=r.get('sexo') or r.get('sexo') if 'sexo' in df.columns else None,
                        names=r.get('nombres') if 'nombres' in df.columns else None,
                        last_names=r.get('apellidos') if 'apellidos' in df.columns else None,
                        age=int(r.get('edad')) if r.get('edad') is not None and str(r.get('edad')) != 'nan' else None,
                        peso=float(r.get('peso')) if 'peso' in df.columns else None,
                        altura=float(r.get('altura')) if 'altura' in df.columns else None,
                        imc=float(r.get('imc')) if 'imc' in df.columns else None,
                        presion_sistolica=int(r.get('presion_sistolica')) if 'presion_sistolica' in df.columns else None,
                        presion_diastolica=int(r.get('presion_diastolica')) if 'presion_diastolica' in df.columns else None,
                        frecuencia_cardiaca=int(r.get('frecuencia_cardiaca')) if 'frecuencia_cardiaca' in df.columns else None,
                        glucosa=float(r.get('glucosa')) if 'glucosa' in df.columns else None,
                        colesterol=float(r.get('colesterol')) if 'colesterol' in df.columns else None,
                        saturacion_oxigeno=float(r.get('saturacion_oxigeno')) if 'saturacion_oxigeno' in df.columns else None,
                        temperatura=float(r.get('temperatura')) if 'temperatura' in df.columns else None,
                        antecedentes_familiares=bool(r.get('antecedentes_familiares')) if 'antecedentes_familiares' in df.columns else None,
                        fumador=bool(r.get('fumador')) if 'fumador' in df.columns else None,
                        consumo_alcohol=bool(r.get('consumo_alcohol')) if 'consumo_alcohol' in df.columns else None,
                        actividad_fisica=r.get('actividad_física') if 'actividad_física' in df.columns else (r.get('actividad_fisica') if 'actividad_fisica' in df.columns else None),
                        diagnostico_preliminar=r.get('diagnostico_preliminar') if 'diagnostico_preliminar' in df.columns else None,
                        riesgo_enfermedad=r.get('riesgo_enfermedad') if 'riesgo_enfermedad' in df.columns else None,
                    )
                )

            ClinicalRecord.objects.bulk_create(bulk, batch_size=1000)
            loaded = len(bulk)

            etl_run.status = ETLRun.Status.SUCCESS
            etl_run.duration_ms = int((time.time() - start) * 1000)
            etl_run.records_processed = int(len(df))
            etl_run.records_loaded = loaded
            etl_run.error_detail = ''
            etl_run.save()

            return Response({'etl_run_id': etl_run.id, 'records_loaded': loaded}, status=201)

        except Exception as e:
            etl_run.status = ETLRun.Status.FAILED
            etl_run.duration_ms = int((time.time() - start) * 1000)
            etl_run.error_detail = str(e)
            etl_run.save()
            return Response({'detail': str(e)}, status=500)


class PacientesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        qs = ClinicalRecord.objects.all()

        # filtros simples (opcional)
        riesgo = request.query_params.get('riesgo_enfermedad')
        if riesgo:
            qs = qs.filter(riesgo_enfermedad__iexact=riesgo)

        sexo = request.query_params.get('sexo')
        if sexo:
            qs = qs.filter(sex__iexact=sexo)

        fumador = request.query_params.get('fumador')
        if fumador is not None:
            t = str(fumador).strip().lower()
            if t in {'true', '1', 'si', 'sí'}:
                qs = qs.filter(fumador=True)
            elif t in {'false', '0', 'no'}:
                qs = qs.filter(fumador=False)

        limit = int(request.query_params.get('limit', '50'))
        limit = max(1, min(limit, 200))

        data = list(
            qs.values(
                'id',
                'sex',
                'names',
                'last_names',
                'age',
                'imc',
                'glucosa',
                'colesterol',
                'presion_sistolica',
                'presion_diastolica',
                'frecuencia_cardiaca',
                'fumador',
                'diagnostico_preliminar',
                'riesgo_enfermedad',
            )
        )[:limit]

        return Response({'count': qs.count(), 'results': data})

