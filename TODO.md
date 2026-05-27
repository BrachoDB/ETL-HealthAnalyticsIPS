# TODO - HealthAnalytics IPS

## Plan aprobado (resumen)
- Crear proyecto Django + DRF (estructura desacoplada con apps: authentication, etl, analytics, ml, dashboard, reports).
- Configurar PostgreSQL, JWT, roles/permiso.
- Implementar ETL (EXTRACT/TRANSFORM/LOAD) con Pandas: limpiar nulos, tipos, duplicados, rangos; normalizar diagnósticos/sexo; calcular IMC y clasificación riesgo; registrar logs e historial ETL; exportar CSV.
- Implementar ML: pipeline con preprocesamiento, entrenamiento con mínimo 1 modelo (Regresión logística y/o RandomForest); métricas (accuracy, precision, recall, f1, matriz confusión) guardadas y expuestas.
- Implementar endpoints REST obligatorios: login, pacientes, etl/run, reportes, predicciones, dashboard/kpis.
- Implementar dashboard web con Bootstrap + Chart.js: KPIs, segmentación, gráficas (barras, líneas, torta, heatmap/tendencias) consumiendo la API.
- Implementar exportación (CSV/Excel/PDF) para reportes.
- Agregar documentación técnica básica (README + swagger si aplica).

## Progreso
### Paso 1
[x] Crear esqueleto del repositorio (backend + apps)
[x] Crear entorno virtual .venv e instalar dependencias base
[x] Ejecutar migraciones del esqueleto Django
[x] Levantar servidor dev

### Paso 2
[ ] Actualizar settings.py (PostgreSQL, DRF, JWT, CORS, OpenAPI)
[ ] Agregar apps a INSTALLED_APPS
[ ] Configurar urls (API + swagger si aplica)

### Paso 3
[ ] Crear modelos BD (roles/permisos, pacientes, tablas ETL logs/historial, predicciones, métricas)

### Paso 4
[ ] Implementar ETL engine (extract/generate dataset -> CSV, transform rules, load -> BD)

### Paso 5
[ ] Implementar ML module (entrenamiento, evaluación, guardado artefactos, predicción)

### Paso 6
[ ] Implementar APIs REST obligatorias + permisos por rol

### Paso 7
[ ] Implementar frontend (login + dashboard) con Chart.js

### Paso 8
[ ] Implementar exportaciones (CSV/Excel/PDF)

### Paso 9
[ ] Documentación y scripts de arranque (requirements, .env.example, README)

