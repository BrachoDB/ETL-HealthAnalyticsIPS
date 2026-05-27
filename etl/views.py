from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .etl_engine import run_etl
from .models import ETLRun


class ETRunView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        fuente = request.data.get('fuente', 'default')
        etl_run = ETLRun.objects.create(usuario=request.user, fuente=fuente, status='PENDING')
        try:
            result = run_etl(etl_run=etl_run, fuente=fuente)
            etl_run.status = 'SUCCESS'
            etl_run.registros_extraccion = result.get('registros_extraccion')
            etl_run.registros_transformados = result.get('registros_transformados')
            etl_run.tiempo_ejecucion_ms = result.get('tiempo_ejecucion_ms')
            etl_run.save()
            return Response({'detail': 'ETL ejecutado correctamente', 'result': result})
        except Exception as e:
            etl_run.status = 'FAILED'
            etl_run.save()
            return Response({'detail': 'Error al ejecutar ETL', 'error': str(e)}, status=400)

