from django.db import models


class MLModelMetrics(models.Model):
    model_name = models.CharField(max_length=100)
    model_version = models.CharField(max_length=100, default='random_forest_v1')
    model_path = models.CharField(max_length=255)
    model_hash = models.CharField(max_length=64, blank=True, null=True)
    label_encoder_hash = models.CharField(max_length=64, blank=True, null=True)
    feature_names_hash = models.CharField(max_length=64, blank=True, null=True)
    accuracy = models.FloatField()
    precision = models.FloatField()
    recall = models.FloatField()
    f1_score = models.FloatField()
    confusion_matrix = models.JSONField()
    feature_names = models.JSONField()
    trained_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-trained_at']
        permissions = [
            ('predict_ml', 'Puede ejecutar predicciones ML'),
        ]
        verbose_name = 'Métrica del modelo ML'
        verbose_name_plural = 'Métricas del modelo ML'

    def __str__(self):
        return f'{self.model_name} - {self.model_version} - accuracy {self.accuracy:.4f}'


class PredictionAudit(models.Model):
    user = models.ForeignKey('authentication.User', on_delete=models.SET_NULL, null=True, blank=True)
    model_name = models.CharField(max_length=100)
    model_version = models.CharField(max_length=100)
    model_path = models.CharField(max_length=255)
    model_hash = models.CharField(max_length=64, blank=True, null=True)
    input_data = models.JSONField()
    prediction = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Auditoría de predicción ML'
        verbose_name_plural = 'Auditorías de predicción ML'

    def __str__(self):
        return f'{self.model_name} {self.model_version} - {self.created_at}'
