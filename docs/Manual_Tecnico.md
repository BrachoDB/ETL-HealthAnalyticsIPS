# Manual Técnico - HealthAnalytics IPS

## Arquitectura del Sistema

El sistema usa un backend en **Django**, Django REST Framework y plantillas Django con **Bootstrap 5**, **Chart.js** y **Axios** para el dashboard.

![Arquitectura del sistema](diagrams/arquitectura_sistema.md)

### Componentes principales

1. **Módulo Authentication:** gestiona usuarios, JWT, roles y permisos.
2. **Módulo ETL:** `backend/apps/etl` procesa Excel/CSV, aplica validaciones clínicas, carga `Patient` y registra `ETLLog`.
3. **Módulo Analytics:** `backend/apps/analytics` calcula KPIs, datos para gráficos, segmentación, pacientes recientes, exportaciones y auditoría de exportaciones.
4. **Módulo ML:** `backend/apps/ml` entrena Random Forest, guarda artefactos en `backend/media/models/*.joblib`, registra métricas y expone predicción individual/batch.
5. **Módulo Reports:** `backend/apps/reports` genera reportes PDF, Excel y CSV usando ReportLab, Matplotlib y Pandas.
6. **Dashboard y templates:** `backend/templates` consolida Dashboard, Analítica, Reportes, Pacientes, ML y login.

## Diagramas

- Arquitectura del sistema: [docs/diagrams/arquitectura_sistema.md](diagrams/arquitectura_sistema.md)
- Flujo ETL: [docs/diagrams/flujo_etl.md](diagrams/flujo_etl.md)
- ERD de base de datos: [docs/diagrams/erd_bd.md](diagrams/erd_bd.md)

## Tecnologías utilizadas

- **Backend:** Python 3.13, Django, Django REST Framework, Pandas, NumPy, Scikit-Learn.
- **Base de datos:** MySQL.
- **Frontend:** HTML5, CSS3, Bootstrap 5, Chart.js, Axios.
- **Reportes:** ReportLab, Matplotlib, Pandas.
- **ML:** Random Forest, joblib, LabelEncoder.
- **Documentación API:** drf-spectacular/Swagger.

## Proceso ETL

El comando `run_etl` realiza:

1. Extracción desde:
   - Archivo por defecto: `dataset_clinico_etl_1800_registros.xlsx`.
   - Archivo manual: `python backend/manage.py run_etl --file ruta/al/archivo.csv`.
2. Validación de columnas requeridas, incluyendo `imc`.
3. Normalización de columnas con variaciones de acentos o mayúsculas en Excel.
4. Detección de duplicados por `id_paciente` + `fecha_consulta`.
5. Limpieza de duplicados por `id_paciente`.
6. Corrección de tipos y valores textuales en edad y presión sistólica.
7. Normalización de diagnósticos.
8. Imputación de nulos usando mediana.
9. Validaciones clínicas:
   - Temperatura: 35-42 °C.
   - Presión sistólica: 70-220 mmHg.
   - Presión diastólica: 40-140 mmHg.
   - Glucosa: 40-400 mg/dL.
   - Saturación de oxígeno: 70-100 %.
   - IMC consistente con peso/altura.
   - Presión sistólica mayor que diastólica.
10. Carga con `update_or_create` en `Patient`.
11. Registro de ejecución, duración, estado y detalles en `ETLLog`.

Los registros fuera de rango o inconsistentes se omiten de forma controlada y se reportan en `ETLLog.detalles` con fila, paciente, campo y motivo.

## Carga manual CSV/Excel

- Endpoint: `POST /api/pacientes/upload-csv/`.
- Formatos esperados: CSV UTF-8, XLSX o XLS con las columnas clínicas del dataset.
- Validación: extensión `.csv`, columnas requeridas y rangos clínicos.
- Ejecución: directa mediante `run_etl(file_path=..., user_id=...)`.

## Machine Learning

El entrenamiento usa `backend/apps/ml/training.py` y guarda:

- `backend/media/models/random_forest_model.joblib`
- `backend/media/models/label_encoder.joblib`
- `backend/media/models/feature_names.joblib`

Cada entrenamiento registra una fila en `MLModelMetrics` con:

- `model_name`
- `model_version`
- `model_path`
- `model_hash`
- `label_encoder_hash`
- `feature_names_hash`
- `accuracy`
- `precision`
- `recall`
- `f1_score`
- `confusion_matrix`
- `feature_names`
- `trained_at`

End puntos ML:

| Método | Endpoint | Descripción |
| --- | --- | --- |
| POST | `/api/ml/predict/` | Predicción individual. Devuelve riesgo, probabilidades, explicación básica y advertencia clínica. |
| POST | `/api/ml/predict/batch/` | Predicción masiva con lista de registros. |

La respuesta incluye `explicacion` con las variables más importantes del modelo y `advertencia_clinica` indicando que la predicción no reemplaza el juicio clínico profesional.

## Analytics y exportaciones

KPIs disponibles en `GET /api/analytics/kpis/`:

- Total de pacientes.
- Pacientes críticos.
- Hipertensos.
- Diabéticos.
- IMC promedio.
- Distribución de riesgo.
- Datos agrupados por edad y riesgo para gráfico de barras.

Datos adicionales disponibles en `GET /api/analytics/dashboard-extras/`:

- Tendencias clínicas.
- Heatmap edad vs riesgo.
- Diagnósticos preliminares.
- Tendencia mensual de riesgo.
- Estadística descriptiva.
- Pacientes recientes.
- Alertas críticas.
- Segmentación de pacientes.
- Métricas ML.

Exportaciones:

| Formato | Endpoint | Descripción |
| --- | --- | --- |
| Excel | `GET /api/analytics/export/xlsx/` | Exporta pacientes desde `Patient` usando Pandas/OpenPyXL. |
| CSV | `GET /api/analytics/export/csv/` | Exporta pacientes en CSV UTF-8. |
| PDF | `GET /api/analytics/export/pdf/` | Genera PDF con ReportLab e incluye tabla de registros clínicos. |

El PDF de Analítica incluye estas columnas:

- ID.
- Paciente.
- Edad.
- Sexo.
- Diagnóstico.
- Riesgo.
- PAS.
- Glucosa.
- Sat. O2.
- Fecha.

## Reportes

El módulo `reports` expone:

| Método | Endpoint | Descripción |
| --- | --- | --- |
| GET | `/api/reportes/export/pdf/` | PDF ejecutivo con ReportLab, Matplotlib y tabla de pacientes. |
| GET | `/api/reportes/export/xlsx/` | Excel de pacientes, ETL, analytics o completo según `export_type`. |
| GET | `/api/reportes/export/csv/` | CSV equivalente al Excel según `export_type`. |

El PDF de reportes acepta los parámetros:

- `periodo`: `semana`, `mes`, `trimestre` o `anio`.
- `include_kpis`: incluye KPIs principales.
- `include_charts`: incluye gráfico generado con Matplotlib.
- `include_table`: incluye tabla de pacientes con ReportLab.

## Roles y permisos

El modelo `User` define roles `ADMIN`, `MEDICO` y `ANALISTA`. Para Analista se agregaron permisos read-only:

- `view_patient`: consultar pacientes del ETL.
- `view_etllog`: consultar logs ETL.
- `view_kpi`: consultar indicadores analíticos.
- `export_analytics`: exportar datos analíticos.

Sincronizar grupos de Django con los permisos del proyecto:

```powershell
python backend/manage.py sync_role_permissions
```

Grupos creados:

| Grupo | Permisos principales |
| --- | --- |
| `ADMIN` | pacientes, ETL, analytics, reports y ML. |
| `MEDICO` | pacientes, ETL, analytics, reports y ML. |
| `ANALISTA` | lectura de pacientes/logs, KPIs y exportaciones. |

## Modelos relevantes

- `authentication.User`: usuario con rol.
- `etl.Patient`: registro clínico normalizado.
- `etl.ETLLog`: histórico de ejecuciones ETL.
- `etl.utils_audit.AuditoriaTransaccionalETL`: utilidad de auditoría transaccional ETL.
- `analytics.ExportAudit`: auditoría de exportaciones.
- `ml.MLModelMetrics`: métricas e hashes del modelo.
- `ml.PredictionAudit`: auditoría de predicciones ML.

## SQL de migraciones

El script `docs/sql_migrate.ps1` genera archivos SQL con `python manage.py sqlmigrate` para cada aplicación relevante.

## Instalación local

1. Instalar dependencias: `pip install -r backend/requirements.txt`.
2. Configurar `backend/.env`.
3. Ejecutar migraciones: `python backend/manage.py migrate`.
4. Sincronizar permisos: `python backend/manage.py sync_role_permissions`.
5. Ejecutar ETL: `python backend/manage.py run_etl`.
6. Entrenar ML: `python backend/manage.py train_ml`.
7. Iniciar servidor: `python backend/manage.py runserver`.

## Variables de entorno

El archivo `backend/.env` debe contener al menos:

```env
SECRET_KEY=clave_segura_local
DEBUG=True
DATABASE_URL=mysql://usuario:contrasena@localhost:3306/nombre_bd
ALLOWED_HOSTS=localhost,127.0.0.1
```

No subir `.env` al repositorio.

## Separación frontend

El frontend mantiene las rutas y IDs principales, con assets estáticos separados:

- `backend/static/css/base.css`
- `backend/static/css/dashboard.css`
- `backend/static/css/login.css`
- `backend/static/js/api-client.js`
- `backend/static/js/auth.js`
- `backend/static/js/charts.js`
- `backend/static/js/dashboard.js`
- `backend/static/js/reportes.js`

Los templates cargan estos assets con `{% load static %}` y conservan compatibilidad con el frontend actual.

## Permisos por rol

- `ADMIN`: acceso completo.
- `MEDICO`: lectura clínica, escritura de pacientes, ETL, reportes y predicción ML.
- `ANALISTA`: lectura de pacientes, logs, KPIs y exportación; no puede escribir pacientes, ejecutar ETL ni usar ML.

## Operación en producción

### Ejecución ETL

El ETL se ejecuta de forma directa en los endpoints o mediante:

```powershell
python backend/manage.py run_etl
```

Para un archivo específico:

```powershell
python backend/manage.py run_etl --file ruta/al/archivo.xlsx
```

### Backup y restore MySQL

Backup:

```powershell
mysqldump -h 127.0.0.1 -P 3307 -u usuario -p healthanalyticsips_db > backup.sql
```

Restore:

```powershell
mysql -h 127.0.0.1 -P 3307 -u usuario -p healthanalyticsips_db < backup.sql
```

### Variables críticas de producción

- `SECRET_KEY` única y secreta.
- `DEBUG=False`.
- `ALLOWED_HOSTS` restringido al dominio real.
- `CORS_ALLOW_ALL_ORIGINS=False`.
- `SESSION_COOKIE_SECURE=True` y `CSRF_COOKIE_SECURE=True` bajo HTTPS.
- `OPEN_REGISTRATION=False`, salvo aprobación explícita.

### Modelo ML alterado

Si cambia `random_forest_model.joblib`, `label_encoder.joblib` o `feature_names.joblib`, la predicción retorna `503`. Para corregir:

1. Eliminar artefactos inconsistentes.
2. Ejecutar `python backend/manage.py train_ml`.
3. Verificar `MLModelMetrics` y probar `/api/ml/predict/`.

## Auditoría ML

Las predicciones ML se registran en `PredictionAudit` con usuario, modelo, versión, hash, payload de entrada y resultado. Los artefactos ML tienen hash registrado en `MLModelMetrics`; si el archivo cambia, la predicción retorna 503.
