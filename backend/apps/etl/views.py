import os
import tempfile
import threading

from django.core.management import call_command
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets

from .forms import UploadCSVForm
from .models import ETLLog, Patient
from .serializers import ETLLogSerializer, PatientSerializer


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
        def run_etl_thread():
            call_command('run_etl', user_id=request.user.id)

        thread = threading.Thread(target=run_etl_thread)
        thread.start()

        return Response({'status': 'ETL iniciado en segundo plano'}, status=status.HTTP_202_ACCEPTED)


class UploadCSVView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        form = UploadCSVForm(data=request.data, files=request.FILES)
        if not form.is_valid():
            return Response({'errors': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        archivo = form.cleaned_data['archivo']
        fd, temp_path = tempfile.mkstemp(suffix='.csv')
        os.close(fd)

        try:
            with open(temp_path, 'wb') as destination:
                for chunk in archivo.chunks():
                    destination.write(chunk)
        except Exception as exc:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return Response({'error': f'No fue posible guardar el archivo CSV: {exc}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        def run_etl_thread():
            try:
                call_command('run_etl', file_path=temp_path, user_id=request.user.id)
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        thread = threading.Thread(target=run_etl_thread)
        thread.start()

        return Response(
            {
                'status': 'ETL CSV iniciado en segundo plano',
                'archivo': archivo.name,
            },
            status=status.HTTP_202_ACCEPTED,
        )
