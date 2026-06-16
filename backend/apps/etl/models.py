from django.db import models

class Patient(models.Model):
    SEX_CHOICES = [
        ('Masculino', 'Masculino'),
        ('Femenino', 'Femenino'),
        ('Otro', 'Otro'),
    ]
    
    RIESGO_CHOICES = [
        ('Bajo', 'Bajo'),
        ('Medio', 'Medio'),
        ('Alto', 'Alto'),
        ('Crítico', 'Crítico'),
    ]

    id_paciente = models.IntegerField(unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    edad = models.IntegerField()
    sexo = models.CharField(max_length=20, choices=SEX_CHOICES)
    peso = models.FloatField()
    altura = models.FloatField()
    imc = models.FloatField()
    presion_sistolica = models.IntegerField()
    presion_diastolica = models.IntegerField()
    frecuencia_cardiaca = models.IntegerField()
    glucosa = models.FloatField()
    colesterol = models.FloatField()
    saturacion_oxigeno = models.FloatField()
    temperatura = models.FloatField()
    antecedentes_familiares = models.BooleanField()
    fumador = models.BooleanField()
    consumo_alcohol = models.BooleanField()
    actividad_fisica = models.CharField(max_length=50)
    diagnostico_preliminar = models.CharField(max_length=200)
    riesgo_enfermedad = models.CharField(max_length=20, choices=RIESGO_CHOICES)
    fecha_consulta = models.DateField()
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = [
            ('run_etl', 'Puede ejecutar procesos ETL'),
            ('upload_etl', 'Puede cargar archivos ETL'),
        ]

    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.id_paciente})"

class ETLLog(models.Model):
    ESTADO_CHOICES = [
        ('Exitoso', 'Exitoso'),
        ('Fallido', 'Fallido'),
    ]

    fecha_ejecucion = models.DateTimeField(auto_now_add=True)
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    usuario = models.ForeignKey('authentication.User', on_delete=models.SET_NULL, null=True)
    source_file = models.CharField(max_length=500, blank=True, null=True)
    source_hash = models.CharField(max_length=64, blank=True, null=True)
    source_type = models.CharField(max_length=20, blank=True, null=True)
    schema_version = models.CharField(max_length=20, default='1.0')
    validation_rules_version = models.CharField(max_length=20, default='1.0')
    registros_extraidos = models.IntegerField(default=0)
    registros_validos = models.IntegerField(default=0)
    registros_procesados = models.IntegerField(default=0)
    registros_invalidos = models.IntegerField(default=0)
    registros_actualizados = models.IntegerField(default=0)
    registros_creados = models.IntegerField(default=0)
    tiempo_ejecucion = models.FloatField()  # en segundos
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    detalles = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"ETL {self.fecha_ejecucion} - {self.estado}"


# Auditoría transaccional (aditiva)
# Nota: se mantiene el core de ETLLog sin cambios; este modelo es adicional.
from .utils_audit import AuditoriaTransaccionalETL


