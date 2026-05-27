from django.db import models


class Prediccion(models.Model):
    # Para simplificar: se asocia al paciente por su id_paciente
    paciente_id = models.IntegerField(db_index=True)
    riesgo_probabilidad = models.FloatField(null=True, blank=True)
    riesgo_clase = models.CharField(max_length=20, blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'predicciones'
        ordering = ['-created_at']


class MLMetric(models.Model):
    modelo = models.CharField(max_length=100, blank=True, default='')
    accuracy = models.FloatField(null=True, blank=True)
    precision = models.FloatField(null=True, blank=True)
    recall = models.FloatField(null=True, blank=True)
    f1_score = models.FloatField(null=True, blank=True)
    confusion_matrix_json = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ml_metrics'
        ordering = ['-created_at']

