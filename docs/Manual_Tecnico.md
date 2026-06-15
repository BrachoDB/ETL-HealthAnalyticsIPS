# Manual Técnico - HealthAnalytics IPS

## Arquitectura del Sistema
El sistema usa un backend en **Django 6**, Django REST Framework y plantillas Django con **Bootstrap 5**, **Chart.js** y **Axios** para el dashboard.

![Arquitectura del sistema](diagrams/arquitectura_sistema.md)

### Componentes principales
1. **Módulo ETL:** `backend/apps/etl` procesa Excel/CSV, aplica validaciones clínicas y carga `Patient` y `ETLLog`.
2. **Módulo ML:** `backend/apps/ml` entrena Random Forest, guarda artefactos en `backend/media/models/*.joblib`, registra métricas y expone predicción individual/batch.
3. **Módulo Analytics:** `backend/apps/analytics` calcula KPIs, edad vs riesgo y exportaciones Excel/CSV/PDF.
4. **Módulo Authentication:** gestiona usuarios, JWT y permisos de rol Analista.
5. **Dashboard:** `backend/templates/dashboard.html` consolida KPIs, gráficos, carga CSV/Excel, ML y logs ETL.

## Diagramas
- Arquitectura del sistema: [docs/diagrams/arquitectura_sistema.md](diagrams/arquitectura_sistema.md)
- Flujo ETL: [docs/diagrams/flujo_etl.md](diagrams/flujo_etl.md)
- ERD de base de datos: [docs/diagrams/erd_bd.md](diagrams/erd_bd.md)

## Tecnologías utilizadas
- **Backend:** Python 3.13, Django 6, DRF, Pandas, NumPy, Scikit-Learn.
- **Base de datos:** MySQL.
- **Frontend:** HTML5, CSS3, Bootstrap 5, Chart.js.
- **ML:** Random Forest, joblib, LabelEncoder.
- **Documentación API:** drf-spectacular/Swagger.

## Proceso ETL
El comando `run_etl` realiza:

1. Extracción desde:
   - Archivo por defecto: `dataset_clinico_etl_1800_registros.xlsx`.
   - Archivo manual: `python backend/manage.py run_etl --file ruta/al/archivo.csv`.
3. Validación de columnas requeridas, incluyendo `imc`.
4. Normalización de columnas con variaciones de acentos o mayúsculas en Excel.
5. Detección de duplicados por `id_paciente` + `fecha_consulta`.
6. Limpieza de duplicados por `id_paciente`.
7. Corrección de tipos y valores textuales en edad y presión sistólica.
5. Normalización de diagnósticos.
6. Imputación de nulos usando mediana.
8. Validaciones clínicas:
   - Temperatura: 35-42 °C.
   - Presión sistólica: 70-220 mmHg.
   - Presión diastólica: 40-140 mmHg.
   - Glucosa: 40-400 mg/dL.
   - Saturación de oxígeno: 70-100 %.
   - IMC consistente con peso/altura.
   - Presión sistólica mayor que diastólica.
9. Carga con `update_or_create` en `Patient`.
10. Registro de ejecución, duración, estado y detalles en `ETLLog`.

Los registros fuera de rango o inconsistentes se omiten de forma controlada y se reportan en `ETLLog.detalles` con fila, paciente, campo y motivo.

## Carga manual CSV/Excel

- Endpoint: `POST /api/pacientes/upload-csv/`.
- Formatos esperados: CSV UTF-8, XLSX o XLS con las columnas clínicas del dataset.
- Validación: extension `.csv`, columnas requeridas y rangos clínicos.
- Ejecución: directa mediante `run_etl(file_path=..., user_id=...)`.

## Machine Learning
El entrenamiento usa `backend/apps/ml/training.py` y guarda:

- `backend/media/models/random_forest_model.joblib`
- `backend/media/models/label_encoder.joblib`
- `backend/media/models/feature_names.joblib`

Cada entrenamiento registra una fila en `MLModelMetrics` con:

- `model_name`
- `model_path`
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

Exportaciones:

| Formato | Endpoint |
| --- | --- |
| Excel | `GET /api/analytics/export/xlsx/` |
| CSV | `GET /api/analytics/export/csv/` |
| PDF | `GET /api/analytics/export/pdf/` |

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
| `ADMIN` | pacientes, ETL, analytics, ML. |
| `MEDICO` | pacientes, ETL, analytics, ML. |
| `ANALISTA` | lectura de pacientes/logs, KPIs y exportaciones. |

## SQL de migraciones
El script `docs/sql_migrate.ps1` genera archivos SQL con `python manage.py sqlmigrate` para cada aplicación relevante.

## Instalación local
1. Instalar dependencias: `pip install -r backend/requirements.txt`.
2. Configurar `backend/.env`.
3. Ejecutar migraciones: `python backend/manage.py migrate`.
4. Ejecutar ETL: `python backend/manage.py run_etl`.
5. Entrenar ML: `python backend/manage.py train_ml`.
6. Iniciar servidor: `python backend/manage.py runserver`.

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
El dashboard mantiene las mismas rutas y IDs, pero separa assets estáticos:

- `backend/static/css/base.css`
- `backend/static/css/dashboard.css`
- `backend/static/css/login.css`
- `backend/static/js/api-client.js`
- `backend/static/js/auth.js`
- `backend/static/js/charts.js`
- `backend/static/js/dashboard.js`

Los templates `base.html`, `dashboard.html` y `login.html` cargan estos assets con `{% load static %}` y conservan compatibilidad con el frontend actual.

## Permisos por rol
Roles implementados:

- `ADMIN`: acceso completo.
- `MEDICO`: lectura clínica, escritura de pacientes, ETL y predicción ML.
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
