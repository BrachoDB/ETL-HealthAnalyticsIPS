# Manual Técnico - HealthAnalytics IPS

## Arquitectura del Sistema
El sistema usa un backend en **Django 6**, Django REST Framework y plantillas Django con **Bootstrap 5**, **Chart.js** y **Axios** para el dashboard.

![Arquitectura del sistema](diagrams/arquitectura_sistema.md)

### Componentes principales
1. **Módulo ETL:** `backend/apps/etl` procesa Excel/CSV, aplica validaciones clínicas y carga `Patient` y `ETLLog`.
2. **Módulo ML:** `backend/apps/ml` entrena Random Forest, guarda artefactos en `backend/media/models/*.joblib`, registra métricas y expone predicción individual/batch.
3. **Módulo Analytics:** `backend/apps/analytics` calcula KPIs, edad vs riesgo y exportaciones Excel/CSV/PDF.
4. **Módulo Authentication:** gestiona usuarios, JWT y permisos de rol Analista.
5. **Dashboard:** `backend/templates/dashboard.html` consolida KPIs, gráficos, carga CSV, ML y logs ETL.

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
2. Validación de columnas requeridas.
3. Limpieza de duplicados por `id_paciente`.
4. Corrección de tipos y valores textuales en edad y presión sistólica.
5. Normalización de diagnósticos.
6. Imputación de nulos usando mediana.
7. Cálculo automático de IMC.
8. Validaciones clínicas:
   - Temperatura: 35-42 °C.
   - Presión sistólica: 70-220 mmHg.
   - Glucosa: 40-400 mg/dL.
   - Saturación de oxígeno: 70-100 %.
9. Carga con `update_or_create` en `Patient`.
10. Registro de ejecución, duración, estado y detalles en `ETLLog`.

Los registros fuera de rango se omiten de forma controlada y se reportan en `ETLLog.detalles`.

## Carga manual CSV
- Formulario: dashboard principal.
- Endpoint: `POST /api/pacientes/upload-csv/`.
- Formato esperado: CSV UTF-8 con las mismas columnas clínicas del Excel.
- Validación: extension `.csv`, columnas requeridas y rangos clínicos.
- Ejecución: segundo plano mediante `call_command('run_etl', file_path=..., user_id=...)`.

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
| POST | `/api/ml/predict/` | Predicción individual. |
| POST | `/api/ml/predict/batch/` | Predicción masiva con lista de registros. |

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
