from django.db import models


class Paciente(models.Model):
    sexo = models.CharField(max_length=20, blank=True, default='')
    edad = models.IntegerField(null=True, blank=True)
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

    antecedentes_familiares = models.BooleanField(default=False)
    fumador = models.BooleanField(default=False)
    consumo_alcohol = models.BooleanField(default=False)
    actividad_fisica = models.CharField(max_length=100, blank=True, default='')

    diagnostico_preliminar = models.CharField(max_length=255, blank=True, default='')
    riesgo_enfermedad = models.CharField(max_length=20, blank=True, default='')
    fecha_consulta = models.DateField(null=True, blank=True)

    # Identidad (dado el dataset)
    id_paciente = models.IntegerField(unique=True)
    nombres = models.CharField(max_length=100, blank=True, default='')
    apellidos = models.CharField(max_length=100, blank=True, default='')

    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pacientes'

