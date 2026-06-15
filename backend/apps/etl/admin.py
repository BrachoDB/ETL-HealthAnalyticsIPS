from django.contrib import admin

from apps.etl.models import ETLLog, Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('id_paciente', 'nombres', 'apellidos', 'edad', 'riesgo_enfermedad', 'fecha_consulta')
    list_filter = ('riesgo_enfermedad', 'sexo', 'fecha_consulta')
    search_fields = ('id_paciente', 'nombres', 'apellidos', 'diagnostico_preliminar')


@admin.register(ETLLog)
class ETLLogAdmin(admin.ModelAdmin):
    list_display = ('fecha_ejecucion', 'usuario', 'estado', 'registros_procesados', 'tiempo_ejecucion', 'source_type')
    list_filter = ('estado', 'source_type', 'fecha_ejecucion')
    search_fields = ('source_file', 'detalles')
