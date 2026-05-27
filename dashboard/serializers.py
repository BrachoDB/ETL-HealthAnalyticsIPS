from rest_framework import serializers


class DashboardChartRequestSerializer(serializers.Serializer):
    # placeholder for future filters (fecha, sexo, etc.)
    dummy = serializers.CharField(required=False)

