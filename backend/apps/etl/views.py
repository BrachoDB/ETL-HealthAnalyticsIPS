from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.management import call_command
from .models import Patient, ETLLog
from .serializers import PatientSerializer, ETLLogSerializer
import threading

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

class ETLLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ETLLog.objects.all().order_by('-fecha_ejecucion')
    serializer_class = ETLLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def run(self, request):
        # Trigger ETL in background to not block the response
        # In a real production app, use Celery.
        def run_etl_thread():
            call_command('run_etl')
            
        thread = threading.Thread(target=run_etl_thread)
        thread.start()
        
        return Response({'status': 'ETL iniciado en segundo plano'}, status=status.HTTP_202_ACCEPTED)
