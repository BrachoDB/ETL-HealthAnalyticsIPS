import re


class ParserNumericoEspanol:
    """Transforma representaciones textuales de numeros en español a sus digitos enteros."""

    UNIDADES = {
        "cero": 0,
        "un": 1,
        "uno": 1,
        "dos": 2,
        "tres": 3,
        "cuatro": 4,
        "cinco": 5,
        "seis": 6,
        "siete": 7,
        "ocho": 8,
        "nueve": 9,
        "diez": 10,
        "once": 11,
        "doce": 12,
        "trece": 13,
        "catorce": 14,
        "quince": 15,
        "dieciseis": 16,
        "diecisiete": 17,
        "dieciocho": 18,
        "diecinueve": 19,
        "veinte": 20,
        "veintiuno": 21,
        "veintidos": 22,
        "veintitres": 23,
        "veinticuatro": 24,
        "veinticinco": 25,
        "veintiseis": 26,
        "veintisiete": 27,
        "veintiocho": 28,
        "veintinueve": 29,
    }

    DECENAS = {
        "treinta": 30,
        "cuarenta": 40,
        "cincuenta": 50,
        "sesenta": 60,
        "setenta": 70,
        "ochenta": 80,
        "noventa": 90,
    }

    @classmethod
    def limpiar_palabra(cls, palabra: str) -> str:
        palabra = str(palabra).lower().replace("í", "i").replace("é", "e").replace("á", "a")
        return re.sub(r"\[^a-z\]", "", palabra)

    @classmethod
    def palabra_a_entero(cls, texto: str):
        """Parsea cadenas como 'treinta y dos' o '45' a un entero valido."""
        if not texto:
            return None

        texto_limpio = str(texto).strip().lower()
        if texto_limpio.isdigit():
            return int(texto_limpio)

        tokens = [cls.limpiar_palabra(p) for p in texto_limpio.split() if p not in ["y", "con"]]
        acumulado = 0

        for token in tokens:
            if token in cls.UNIDADES:
                acumulado += cls.UNIDADES[token]
            elif token in cls.DECENAS:
                acumulado += cls.DECENAS[token]

        return acumulado if acumulado > 0 else None

