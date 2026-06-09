# User Manual

## Login
- Ejecutar `POST /api/auth/auth/login/` con `username` y `password`.
- Usar el `access` token para endpoints protegidos.

## ETL
- Ejecutar `POST /api/etl/etl/run/` enviando un archivo en `file` (opcional).
- Si no envías archivo, usa el dataset del repo.

## Visualización
- KPIs: `GET /api/dashboard/dashboard/kpis/`
- Reportes: `GET /api/reports/reportes/`

## Historial ETL
- `GET /api/etl/etl/history/` (filtra por usuario autenticado).

## Exportación
- CSV/Excel/PDF desde `GET /api/reports/reportes/export/*/`

