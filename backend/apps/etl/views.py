import os
import uuid
from pathlib import Path

from django.conf import settings
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets

from apps.authentication.permissions import IsAdminOrMedico, IsReadOnlyClinicalRole

from .forms import UploadCSVForm
from .models import ETLLog, Patient
from .serializers import ETLLogSerializer, PatientSerializer, UploadCSVSerializer
from .services import run_etl


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsReadOnlyClinicalRole]

    def get_permissions(self):
        if self.action in {'create', 'update', 'partial_update', 'destroy'}:
            return [IsAdminOrMedico()]
        return [IsReadOnlyClinicalRole()]


class ETLLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ETLLog.objects.all().order_by('-fecha_ejecucion')
    serializer_class = ETLLogSerializer
    permission_classes = [IsReadOnlyClinicalRole]

    def get_permissions(self):
        if self.action == 'run':
            return [IsAdminOrMedico()]
        return [IsReadOnlyClinicalRole()]

    @action(detail=False, methods=['post'])
    def run(self, request):
        result = run_etl(user_id=request.user.id)

        return Response(
            {
                'status': 'ETL ejecutado',
                'log_id': result.log.id,
                'estado': result.log.estado,
                'registros_procesados': result.registros_procesados,
                'registros_invalidos': result.registros_invalidos,
                'source_type': result.log.source_type,
            },
            status=status.HTTP_200_OK,
        )


class UploadCSVView(APIView):
    permission_classes = [IsAdminOrMedico]
    serializer_class = UploadCSVSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        form = UploadCSVForm(data=request.data, files=request.FILES)
        if not form.is_valid():
            return Response({'errors': form.errors}, status=status.HTTP_400_BAD_REQUEST)

        archivo = form.cleaned_data['archivo']
        upload_dir = Path(settings.MEDIA_ROOT) / 'etl_uploads'
        upload_dir.mkdir(parents=True, exist_ok=True)
        safe_name = f"{uuid.uuid4().hex}_{archivo.name}"
        destination_path = upload_dir / safe_name

        try:
            with destination_path.open('wb') as destination:
                for chunk in archivo.chunks():
                    destination.write(chunk)
        except Exception as exc:
            if destination_path.exists():
                destination_path.unlink()
            return Response({'error': f'No fue posible guardar el archivo: {exc}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            result = run_etl(file_path=str(destination_path), user_id=request.user.id)
            if os.path.exists(destination_path):
                os.remove(destination_path)
        except Exception as exc:
            if os.path.exists(destination_path):
                os.remove(destination_path)
            return Response({'error': f'Error ejecutando ETL: {exc}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(
            {
                'status': 'ETL ejecutado',
                'archivo': archivo.name,
                'log_id': result.log.id,
                'estado': result.log.estado,
                'registros_procesados': result.registros_procesados,
                'registros_invalidos': result.registros_invalidos,
                'source_type': result.log.source_type,
            },
            status=status.HTTP_200_OK,
        )
