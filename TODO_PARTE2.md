# TODO - PARTE 2 (CORRECCIÓN AUTOMÁTICA DE ESTRUCTURA)

## Estado
- [ ] Plan aprobado y listo para ejecutar reestructuración.

## Checklist de ejecución
- [ ] Crear carpetas: backend/, backend/config/, backend/apps/, frontend/, datasets/, docs/.
- [ ] Mover proyecto Django: healthcare_etl_platform/ -> backend/config/.
- [ ] Mover apps Django: authentication/, etl/, analytics/, ml/, dashboard/, reports/ -> backend/apps/.
- [ ] Crear archivos __init__.py necesarios en backend/ y subcarpetas (para que importen como paquetes).
- [ ] Mover frontend: dashboard/templates/* -> frontend/templates/*; dashboard/static/* -> frontend/static/*.
- [ ] Mover dataset_clinico_etl_1800_registros.xlsx -> datasets/.
- [ ] Mover documentación .md -> docs/ (excepto README.md).
- [ ] Actualizar manage.py (DJANGO_SETTINGS_MODULE).
- [ ] Actualizar settings.py (INSTALLED_APPS con rutas backend.apps.*; TEMPLATES DIRS; STATICFILES_DIRS).
- [ ] Actualizar urls.py si aplica (imports).
- [ ] Actualizar etl/views.py para dataset default path apuntando a datasets/.
- [ ] Actualizar referencias a plantillas/static si quedaron rutas relativas.
- [ ] Verificar consistencia: que los módulos importan y que compile (runserver / makemigrations si aplica).

## Resultado final
- [ ] Generar el reporte con:
  - # Cambios realizados
  - # Archivos movidos
  - # Archivos renombrados
  - # Carpetas creadas
  - # Carpetas eliminadas
  - # Nueva estructura final

