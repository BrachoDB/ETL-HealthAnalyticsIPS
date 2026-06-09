# Documentación de APIs

La documentación formal se encuentra en el Swagger generado por `drf-spectacular`.

- OpenAPI JSON: `GET /api/schema/`
- Swagger UI: `GET /api/docs/`

## Endpoints por módulo
### Auth
- `POST /api/auth/auth/login/`

### Dashboard
- `GET /api/dashboard/dashboard/kpis/`

### ETL
- `POST /api/etl/etl/run/`

### Pacientes
- `GET /api/etl/pacientes/`

### Analítica
- `GET /api/analytics/analytics-stats/`

### Machine Learning
- `POST /api/ml/predicciones/`

### Reportes
- `GET /api/reports/reportes/`

> Nota: todos los endpoints requieren autenticación excepto el login.

