from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html

from apps.ml.models import MLModelMetrics
from apps.ml.training import train_model


@admin.register(MLModelMetrics)
class MLModelMetricsAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'model_version', 'accuracy', 'precision', 'recall', 'f1_score', 'trained_at', 'retrain_link')
    list_filter = ('model_name', 'model_version', 'trained_at')
    readonly_fields = ('model_name', 'model_version', 'model_path', 'model_hash', 'label_encoder_hash', 'feature_names_hash', 'accuracy', 'precision', 'recall', 'f1_score', 'confusion_matrix', 'feature_names', 'trained_at')
    actions = ['reentrenar_modelo']

    def retrain_link(self, obj):
        url = reverse('admin:ml_mlmodelmetrics_retrain', args=[obj.pk])
        return format_html('<a href="{}">Re-entrenar desde esta versión</a>', url)
    retrain_link.short_description = 'Acciones'

    def reentrenar_modelo(self, request, queryset):
        metrics = train_model()
        if not metrics:
            self.message_user(request, 'No fue posible re-entrenar el modelo. Revise que existan datos suficientes.', level='ERROR')
            return

        self.message_user(
            request,
            f'Modelo re-entrenado. Accuracy: {metrics["accuracy"]:.4f}. Nueva métrica registrada.',
            level='SUCCESS',
        )

    reentrenar_modelo.short_description = 'Re-entrenar modelo y registrar métricas'

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:pk>/retrain/',
                self.admin_site.admin_view(self.retrain_view),
                name='ml_mlmodelmetrics_retrain',
            ),
        ]
        return custom_urls + urls

    def retrain_view(self, request, pk):
        metrics = train_model()
        if not metrics:
            self.message_user(request, 'No fue posible re-entrenar el modelo.', level='ERROR')
        else:
            self.message_user(request, f'Modelo re-entrenado. Accuracy: {metrics["accuracy"]:.4f}.', level='SUCCESS')
        return HttpResponseRedirect(self._get_changelist_url())

    def _get_changelist_url(self):
        opts = self.model._meta
        return reverse(f'admin:{opts.app_label}_{opts.model_name}_changelist')
