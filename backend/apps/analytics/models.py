from django.db import models


class ExportAudit(models.Model):
    FORMAT_CHOICES = [
        ('xlsx', 'Excel'),
        ('csv', 'CSV'),
        ('pdf', 'PDF'),
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey('authentication.User', on_delete=models.SET_NULL, null=True, blank=True)
    export_format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    total_rows = models.IntegerField(default=0)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        permissions = [
            ('export_analytics', 'Puede exportar datos analíticos'),
        ]
        verbose_name = 'Auditoría de exportación'
        verbose_name_plural = 'Auditorías de exportación'

    def __str__(self):
        return f'{self.export_format} - {self.created_at}'
