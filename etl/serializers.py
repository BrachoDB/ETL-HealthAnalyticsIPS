from rest_framework import serializers

from .models import ETLRun, ClinicalRecord


class ETLRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = ETLRun
        fields = '__all__'


class ClinicalRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicalRecord
        fields = '__all__'

