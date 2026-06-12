# HealthAnalytics IPS - Plataforma Inteligente de Analítica Clínica

Este proyecto es una solución integral para el procesamiento, análisis y predicción de riesgo médico basado en datos clínicos.

## Características
- **ETL Automatizado:** limpieza y transformación de datos desde Excel o CSV a MySQL usando Pandas.
- **Validaciones Clínicas:** omisión controlada de registros fuera de rango para temperatura, presión sistólica, glucosa y saturación de oxígeno.
- **Carga Manual CSV:** endpoint `POST /api/pacientes/upload-csv/` y formulario en el dashboard.
- **Machine Learning:** modelo Random Forest para predicción individual y batch de riesgo de enfermedades.
- **Métricas ML:** registro de accuracy, precision, recall, F1 y matriz de confusión en `MLModelMetrics`.
- **Dashboard Interactivo:** KPIs, distribución de riesgo, edad vs riesgo, predicción ML, histórico ETL y exportaciones.
- **Exportaciones:** Excel, CSV y PDF desde `/api/analytics/export/<formato>/`.
- **Seguridad:** autenticación JWT, roles Admin/Médico/Analista y permisos read-only para Analista.
- **API Documentada:** documentación interactiva con Swagger/OpenAPI.

## Estructura del Proyecto
```
backend/
├── apps/
│   ├── authentication/   # Gestión de usuarios, roles y JWT
│   ├── etl/              # Proceso de extracción, limpieza, validación y carga
│   ├── analytics/        # KPIs, edad vs riesgo y exportaciones
│   ├── ml/               # Entrenamiento, predicción y métricas del modelo
│   └── dashboard/        # Plantilla principal del dashboard
├── config/               # Configuración de Django
├── media/models/         # Modelos entrenados en formato joblib
└── manage.py

docs/
├── diagrams/             # Diagramas Mermaid de arquitectura, flujo ETL y ERD
└── sql_migrate.ps1       # Script para generar SQL de migraciones
```

## Guía de Inicio Rápido
1. Clonar el repositorio.
2. Configurar el archivo `backend/.env` con su conexión MySQL.
3. Instalar dependencias: `pip install -r backend/requirements.txt`.
4. Ejecutar migraciones: `python backend/manage.py migrate`.
5. Ejecutar ETL inicial: `python backend/manage.py run_etl`.
6. Ejecutar ETL con archivo manual: `python backend/manage.py run_etl --file ruta/al/archivo.csv`.
7. Entrenar el modelo ML: `python backend/manage.py train_ml`.
8. Iniciar el servidor: `python backend/manage.py runserver`.

## Endpoints principales
- `POST /api/pacientes/logs/run/`: ejecuta el ETL por defecto en segundo plano.
- `POST /api/pacientes/upload-csv/`: sube un CSV clínico y ejecuta el ETL en segundo plano.
- `GET /api/analytics/kpis/`: retorna KPIs, distribución de riesgo y datos para edad vs riesgo.
- `GET /api/analytics/export/xlsx/`, `/csv/`, `/pdf/`: exporta pacientes.
- `POST /api/ml/predict/`: predicción individual.
- `POST /api/ml/predict/batch/`: predicción batch con una lista de registros.

## Roles
- **ADMIN:** acceso completo.
- **MEDICO:** uso clínico del dashboard y predicción.
- **ANALISTA:** permisos read-only para consultar pacientes, logs ETL, KPIs y exportar datos analíticos.

## Documentación técnica
- Manual técnico: `docs/Manual_Tecnico.md`
- Manual de usuario: `docs/Manual_Usuario.md`
- Diagramas Mermaid: `docs/diagrams/`
- Script SQL de migraciones: `docs/sql_migrate.ps1`

## Acceso
- **Dashboard:** http://localhost:8000/
- **Documentación API:** http://localhost:8000/api/docs/
- **Credenciales por defecto:** admin / admin123
