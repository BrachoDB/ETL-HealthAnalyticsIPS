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


class ExportAuditSerializer(serializers.Serializer):
    """Serializa el histórico de descargas (ExportAudit) para el dashboard."""

    id = serializers.IntegerField()
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    export_format = serializers.CharField()
    export_format_display = serializers.CharField(source='get_export_format_display')
    total_rows = serializers.IntegerField()
    usuario = serializers.SerializerMethodField()

    def get_usuario(self, obj):
        if not obj.usuario:
            return 'Sistema'
        return getattr(obj.usuario, 'email', None) or obj.usuario.get_username()
