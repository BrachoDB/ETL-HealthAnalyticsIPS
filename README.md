# ETL-HealthAnalyticsIPS (FASE 4)

Dashboard moderno estilo SaaS + documentación completa.

> Proyecto backend: Django + DRF + JWT (SimpleJWT) + PostgreSQL + drf-spectacular.
> 
> Frontend: HTML5/CSS3/JavaScript sin Bootstrap + Chart.js.

## Características del Dashboard
- **Login** (JWT)
- **Dashboard KPIs**: total pacientes, críticos, riesgo promedio, diabéticos, hipertensos, predicciones realizadas, ETLs ejecutados.
- **Módulos**: Pacientes, ETL, Predicciones, Reportes.
- **Gráficas (Chart.js)**: barras, líneas, torta, heatmap y tendencias.
- **Responsive + Dark Mode**.

## Requisitos
- Python 3.10+
- PostgreSQL
- pip

## Configuración (variables de entorno)
Este proyecto usa configuración directa en `settings.py` (por ahora: PostgreSQL con usuario `postgres` y password `postgres`).

Para producción, se recomienda externalizar variables.

## Instalación (local)
### 1) Crear entorno virtual
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 2) Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3) Migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4) Crear superusuario
```bash
python manage.py createsuperuser
```

### 5) Ejecutar servidor
```bash
python manage.py runserver
```

## Uso del Dashboard
1. Abrir: `http://127.0.0.1:8000/dashboard/`
2. Iniciar sesión con `username/password`.
3. Consultar KPIs y módulos conectados a la API.

## Endpoints de API (Swagger)
- OpenAPI JSON: `GET /api/schema/`
- Swagger UI: `GET /api/docs/`

## Endpoints principales (resumen)
### Auth
- `POST /api/auth/auth/login/`  
  Retorna `access` y `refresh`.

### Dashboard
- `GET /api/dashboard/dashboard/kpis/`

### ETL
- `POST /api/etl/etl/run/`

### Pacientes
- `GET /api/etl/pacientes/`

### Analítica / Reportes
- `GET /api/analytics/analytics-stats/`
- `GET /api/reports/reportes/`

### Machine Learning
- `POST /api/ml/predicciones/`

## Documentación adicional (FASE 4)
Ver archivos:
- `Manual_instalacion.md`
- `Manual_usuario.md`
- `API_DOCUMENTATION.md`
- `FLUJO_ETL.md`
- `ARQUITECTURA.md`
- `ERD.md`
- `EVIDENCIAS_ETL.md`
- `EVIDENCIAS_ML.md`

