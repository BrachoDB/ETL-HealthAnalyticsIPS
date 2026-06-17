RANGOS_FISIOLOGICOS = {
    # Nota: rangos según ETL_CONTEXT.md / reto técnico
    'frecuencia_cardiaca': (30, 220),
    'temperatura': (34, 42),
    'presion_sistolica': (60, 250),
    'presion_diastolica': (40, 150),
    'glucosa': (40, 500),
    'colesterol': (50, 400),
    # Campos clínicos adicionales pueden agregarse aquí de forma aditiva.
}


def validar_datos_clinicos(data: dict) -> None:
    """Valida rangos fisiológicos de un diccionario de entrada.

    Si un valor está fuera de rango, lanza ValueError con el mensaje requerido.
    """
    if not isinstance(data, dict):
        raise ValueError('Payload inválido: se esperaba un objeto/diccionario.')

    for campo, (min_val, max_val) in RANGOS_FISIOLOGICOS.items():
        if campo not in data:
            # si no viene el campo, se ignora (DRF ya maneja campos requeridos)
            continue

        valor = data.get(campo)
        try:
            valor_num = float(valor)
        except (TypeError, ValueError):
            raise ValueError(f'El valor de {campo} es inválido: {valor}')

        if valor_num < min_val or valor_num > max_val:
            # Mensaje exacto solicitado en el prompt
            raise ValueError(f'El valor de {campo} está fuera de rango fisiológico: {valor_num}')

