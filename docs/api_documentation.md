# API Documentation

La documentación formal se encuentra en Swagger generado con drf-spectacular:
- **OpenAPI JSON**: `GET /api/schema/`
- **Swagger UI**: `GET /api/docs/`

Endoints por módulo (alto nivel):
- Auth: `POST /api/auth/auth/login/`
- ETL: `POST /api/etl/etl/run/`, `GET /api/etl/etl/history/` (Historial)
- Pacientes: `GET /api/etl/pacientes/`
- Dashboard KPIs: `GET /api/dashboard/dashboard/kpis/`
- Analítica/Reports: `GET /api/analytics/analytics-stats/`, `GET /api/reports/reportes/`
- ML: `POST /api/ml/predicciones/`
- Exportaciones: 
  - `GET /api/reports/reportes/export/csv/`
  - `GET /api/reports/reportes/export/excel/`
  - `GET /api/reports/reportes/export/pdf/`

