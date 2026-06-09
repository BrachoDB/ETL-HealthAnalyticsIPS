# TODO_VALIDACION_FINAL

## Objetivo
Cumplir lo marcado en `VALIDACION_FINAL_PARTE3.md` corrigiendo/implementando lo necesario.

## Checklist (Paso a Paso)
- [ ] Revisar y alinear rutas de Reportes/ETL/Docs con el documento.
- [x] Implementar **Historial ETL**:
  - [x] Agregar endpoint de listado de `ETLRun` (filtrado por usuario) en `backend/apps/etl/urls.py`.
  - [x] Implementar vista correspondiente en `backend/apps/etl/views.py`.

- [ ] Implementar **Exportación PDF/Excel/CSV** según requisitos del reto:
  - [ ] Identificar endpoints requeridos desde el documento técnico.
  - [ ] Implementar en `backend/apps/reports/views.py` (o crear vistas específicas) export CSV/Excel/PDF.
  - [ ] Registrar rutas en `backend/apps/reports/urls.py`.
- [ ] Ajustar **Roles/Permisos** si el documento exige control por rol:
  - [ ] Revisar `permissions.py` y uso en vistas.
  - [ ] Aplicar permisos por rol donde sea obligatorio (sin cambiar comportamiento de endpoints no requeridos).
- [ ] Revisar consistencia de `ROOT_URLCONF` y estructura de import con `backend/config/healthcare_etl_platform/settings.py`.
- [ ] Ejecutar en entorno con dependencias:
  - [ ] `python manage.py check`
  - [ ] `python manage.py makemigrations --check`
  - [ ] `python manage.py migrate`
- [ ] Probar endpoints con JWT (mínimo los obligatorios del reto).

