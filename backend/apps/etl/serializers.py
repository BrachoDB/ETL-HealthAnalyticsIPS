from rest_framework import serializers
from .models import Patient, ETLLog

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'

class UploadCSVSerializer(serializers.Serializer):
    archivo = serializers.FileField(label='Archivo CSV clínico')

class ETLLogSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)
    
    class Meta:
        model = ETLLog
        fields = '__all__'
