from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class AuditoriaTransaccionalETL(models.Model):
    """Modelo para guardar de manera persistente los logs e historicos del pipeline ETL."""

    ESTADOS = [
        ("EXITOSO", "EXITOSO"),
        ("FALLIDO", "FALLIDO"),
    ]

    fecha_ejecucion = models.DateTimeField(auto_now_add=True, db_index=True)
    usuario_responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="logs_etl")
    archivo_fuente = models.CharField(max_length=255, blank=True, null=True)
    registros_saneados = models.IntegerField(default=0)
    tiempo_ejecucion_segundos = models.FloatField(default=0.0)
    estado_finalizacion = models.CharField(max_length=15, choices=ESTADOS, default="EXITOSO")
    informe_errores = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "auditoria_procesos_etl"
        ordering = ["-fecha_ejecucion"]

    def __str__(self):
        return f"ETL {self.id} - {self.estado_finalizacion} - {self.fecha_ejecucion}"

