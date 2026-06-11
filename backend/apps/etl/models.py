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

    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.id_paciente})"

class ETLLog(models.Model):
    ESTADO_CHOICES = [
        ('Exitoso', 'Exitoso'),
        ('Fallido', 'Fallido'),
    ]
    
    fecha_ejecucion = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey('authentication.User', on_delete=models.SET_NULL, null=True)
    registros_procesados = models.IntegerField(default=0)
    tiempo_ejecucion = models.FloatField() # en segundos
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    detalles = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"ETL {self.fecha_ejecucion} - {self.estado}"
