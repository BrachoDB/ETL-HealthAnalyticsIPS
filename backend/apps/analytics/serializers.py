from rest_framework import serializers


class KPISerializer(serializers.Serializer):
    total_pacientes = serializers.IntegerField()
    riesgo_distribucion = serializers.ListField(child=serializers.DictField())
    edad_riesgo = serializers.DictField()
    pacientes_criticos = serializers.IntegerField()
    hipertensos = serializers.IntegerField()
    diabeticos = serializers.IntegerField()
    imc_promedio = serializers.FloatField()


class DashboardExtrasSerializer(serializers.Serializer):
    tendencias = serializers.DictField()
    heatmap = serializers.DictField()
    diagnosticos = serializers.DictField()
    mensual = serializers.DictField()
    estadistica = serializers.ListField(child=serializers.DictField())
    pacientes = serializers.ListField(child=serializers.DictField())
    criticos = serializers.ListField(child=serializers.DictField())
    segmentacion = serializers.DictField()
    ml_metricas = serializers.DictField(allow_null=True)


class PatientExportFormatSerializer(serializers.Serializer):
    export_format = serializers.ChoiceField(choices=['xlsx', 'csv', 'pdf'])
