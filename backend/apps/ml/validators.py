from rest_framework import serializers


class ClampedFloatField(serializers.FloatField):
    """FloatField que no rechaza valores fuera de rango.

    - Si el valor viene por encima del max, se ajusta al max.
    - Si el valor viene por debajo del min, se ajusta al min.

    Además marca flags en los datos validados:
    - es_dato_atipico_<campo> = True
    """

    default_error_messages = {
        **serializers.FloatField.default_error_messages,
    }

    def __init__(self, *args, **kwargs):
        self.flag_suffix = kwargs.pop('flag_suffix', '_atipico')
        super().__init__(*args, **kwargs)

    def _clamp(self, value: float) -> float:
        min_value = getattr(self, 'min_value', None)
        max_value = getattr(self, 'max_value', None)

        if min_value is not None and value < min_value:
            return min_value
        if max_value is not None and value > max_value:
            return max_value
        return value

    def to_internal_value(self, data):
        value = super().to_internal_value(data)

        min_value = getattr(self, 'min_value', None)
        max_value = getattr(self, 'max_value', None)
        is_atipico = False

        if min_value is not None and value < min_value:
            is_atipico = True
        if max_value is not None and value > max_value:
            is_atipico = True

        if is_atipico:
            value = self._clamp(value)

            # Nota: no podemos garantizar el nombre del campo aquí,
            # por eso el flag se registra desde el Serializer usando el key.
            # Este flag se guarda como atributo temporal.
            self._is_atipico_for_last = True
        else:
            self._is_atipico_for_last = False

        return value

