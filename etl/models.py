from django.conf import settings
from django.db import models


class ETLRun(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'PENDING'),
        ('SUCCESS', 'SUCCESS'),
        ('FAILED', 'FAILED'),
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='etl_runs',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    fuente = models.CharField(max_length=255, blank=True, default='')
    registros_extraccion = models.IntegerField(null=True, blank=True)
    registros_transformados = models.IntegerField(null=True, blank=True)
    tiempo_ejecucion_ms = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'etl_runs'
        ordering = ['-created_at']


class ETLLog(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    etl_run = models.ForeignKey(ETLRun, on_delete=models.CASCADE, related_name='logs')

    nivel = models.CharField(max_length=20, blank=True, default='INFO')
    mensaje = models.TextField()

    class Meta:
        db_table = 'etl_logs'
        ordering = ['created_at']

