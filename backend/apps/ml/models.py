from django.db import models


class MLModelMetrics(models.Model):
    model_name = models.CharField(max_length=100)
    model_path = models.CharField(max_length=255)
    accuracy = models.FloatField()
    precision = models.FloatField()
    recall = models.FloatField()
    f1_score = models.FloatField()
    confusion_matrix = models.JSONField()
    feature_names = models.JSONField()
    trained_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-trained_at']
        verbose_name = 'Métrica del modelo ML'
        verbose_name_plural = 'Métricas del modelo ML'

    def __str__(self):
        return f'{self.model_name} - accuracy {self.accuracy:.4f}'
