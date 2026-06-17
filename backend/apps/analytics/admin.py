from django.contrib import admin

from apps.analytics.models import ExportAudit


@admin.register(ExportAudit)
class ExportAuditAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'usuario', 'export_format', 'total_rows', 'ip_address')
    list_filter = ('export_format', 'created_at')
    search_fields = ('usuario__username', 'ip_address')
