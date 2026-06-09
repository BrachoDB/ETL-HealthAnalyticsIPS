from django.conf import settings
from django.db import models


class ETLRun(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING'
        SUCCESS = 'SUCCESS'
        FAILED = 'FAILED'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    source_filename = models.CharField(max_length=255, blank=True, default='')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    duration_ms = models.IntegerField(null=True, blank=True)
    records_processed = models.IntegerField(default=0)
    records_loaded = models.IntegerField(default=0)
    error_detail = models.TextField(blank=True, default='')


class ClinicalRecord(models.Model):
    sex = models.CharField(max_length=20, null=True, blank=True)
    names = models.CharField(max_length=100, null=True, blank=True)
    last_names = models.CharField(max_length=100, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)

    peso = models.FloatField(null=True, blank=True)
    altura = models.FloatField(null=True, blank=True)
    imc = models.FloatField(null=True, blank=True)

    presion_sistolica = models.IntegerField(null=True, blank=True)
    presion_diastolica = models.IntegerField(null=True, blank=True)
    frecuencia_cardiaca = models.IntegerField(null=True, blank=True)

    glucosa = models.FloatField(null=True, blank=True)
    colesterol = models.FloatField(null=True, blank=True)
    saturacion_oxigeno = models.FloatField(null=True, blank=True)
    temperatura = models.FloatField(null=True, blank=True)

    antecedentes_familiares = models.BooleanField(null=True, blank=True)
    fumador = models.BooleanField(null=True, blank=True)
    consumo_alcohol = models.BooleanField(null=True, blank=True)
    actividad_fisica = models.CharField(max_length=100, null=True, blank=True)

    diagnostico_preliminar = models.CharField(max_length=255, null=True, blank=True)
    riesgo_enfermedad = models.CharField(max_length=20, null=True, blank=True)
    fecha_consulta = models.DateField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=['age'])]


