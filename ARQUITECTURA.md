# Arquitectura

## Vista general
- **Frontend** (FASE 4): HTML/CSS/JS + Chart.js.
- **Backend**: Django + DRF.
- **Auth**: JWT con `rest_framework_simplejwt`.
- **ETL**: `etl/etl_engine.py`.
- **ML**: `ml/utils_rf.py` + `ml/views.py` (Random Forest).
- **Persistencia**: PostgreSQL.

## Flujo
1. Login → JWT.
2. Frontend consume KPIs/Reportes/Pacientes con `Authorization: Bearer`.
3. ETL corre mediante `POST /api/etl/etl/run/`.
4. Predicciones corren mediante `POST /api/ml/predicciones/`.

## Observabilidad
- El endpoint de ETL guarda estado y métricas básicas de ejecución.

