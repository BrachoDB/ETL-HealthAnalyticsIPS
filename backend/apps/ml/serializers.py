from rest_framework import serializers

from apps.ml.validators import ClampedFloatField


class AtipicoFlagMixin:
    """Mixin para inyectar flags es_dato_atipico_<campo> cuando el valor
    llega fuera de rango y se clampa."""

    def validate(self, attrs):
        # Recorremos campos numéricos definidos en el serializer.
        # Si el campo se clampo por rango, el campo guardó _is_atipico_for_last.
        for field_name, field in self.fields.items():
            if isinstance(field, ClampedFloatField):
                # Si el valor no estaba atipico, no añadimos flag.
                if getattr(field, '_is_atipico_for_last', False):
                    attrs[f'es_dato_atipico_{field_name}'] = True
        return attrs


class PredictionInputSerializer(AtipicoFlagMixin, serializers.Serializer):
    edad = ClampedFloatField(min_value=0, max_value=120)
    imc = ClampedFloatField(min_value=10, max_value=80)
    presion_sistolica = ClampedFloatField(min_value=70, max_value=220)
    presion_diastolica = ClampedFloatField(min_value=40, max_value=140)
    frecuencia_cardiaca = ClampedFloatField(min_value=30, max_value=220)
    glucosa = ClampedFloatField(min_value=40, max_value=400)
    colesterol = ClampedFloatField(min_value=80, max_value=500)
    saturacion_oxigeno = ClampedFloatField(min_value=70, max_value=100)
    temperatura = ClampedFloatField(min_value=35, max_value=42)

    antecedentes_familiares = serializers.BooleanField()
    fumador = serializers.BooleanField()
    consumo_alcohol = serializers.BooleanField()


class BatchPredictionSerializer(serializers.Serializer):
    records = serializers.ListField(
        child=PredictionInputSerializer(),
        allow_empty=False,
        max_length=1000,
    )

