import unicodedata
from difflib import get_close_matches


class CorrectorLinguisticoClinico:
    """Sanea de forma no destructiva las inconsistencias en los diagnosticos clinicos."""

    def __init__(self, catalogo_oficial=None):
        self.catalogo_oficial = catalogo_oficial or [
            "hipertensión arterial",
            "diabetes mellitus tipo 2",
            "asma bronquial",
            "obesidad mórbida",
            "insuficiencia renal crónica",
            "sano",
        ]

    @staticmethod
    def normalizar_texto(texto: str) -> str:
        """Remueve tildes, convierte a minusculas y elimina espacios en blanco extras."""
        if not isinstance(texto, str):
            return ""
        texto_descompuesto = unicodedata.normalize("NFKD", texto)
        texto_limpio = "".join([c for c in texto_descompuesto if not unicodedata.combining(c)])
        return texto_limpio.strip().lower()

    def corregir_diagnostico(self, diagnostico: str, cutoff: float = 0.80) -> str:
        """Mapea un diagnostico mal escrito al termino oficial mas cercano en español."""
        if not diagnostico or str(diagnostico).strip().lower() in ["nan", "null", "none"]:
            return "sin diagnóstico preliminar"

        limpio = self.normalizar_texto(diagnostico)
        mapeo_catalogo = {self.normalizar_texto(diag): diag for diag in self.catalogo_oficial}

        if limpio in mapeo_catalogo:
            return mapeo_catalogo[limpio]

        coincidencias = get_close_matches(limpio, mapeo_catalogo.keys(), n=1, cutoff=cutoff)
        if coincidencias:
            return mapeo_catalogo[coincidencias[0]]

        return str(diagnostico).strip().capitalize()

