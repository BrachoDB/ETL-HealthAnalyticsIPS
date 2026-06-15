from rest_framework import serializers


class PredictionInputSerializer(serializers.Serializer):
    edad = serializers.FloatField(min_value=0, max_value=120)
    imc = serializers.FloatField(min_value=10, max_value=80)
    presion_sistolica = serializers.FloatField(min_value=70, max_value=220)
    presion_diastolica = serializers.FloatField(min_value=40, max_value=140)
    frecuencia_cardiaca = serializers.FloatField(min_value=30, max_value=220)
    glucosa = serializers.FloatField(min_value=40, max_value=400)
    colesterol = serializers.FloatField(min_value=80, max_value=500)
    saturacion_oxigeno = serializers.FloatField(min_value=70, max_value=100)
    temperatura = serializers.FloatField(min_value=35, max_value=42)
    antecedentes_familiares = serializers.BooleanField()
    fumador = serializers.BooleanField()
    consumo_alcohol = serializers.BooleanField()


class BatchPredictionSerializer(serializers.Serializer):
    records = serializers.ListField(
        child=PredictionInputSerializer(),
        allow_empty=False,
        max_length=1000,
    )
