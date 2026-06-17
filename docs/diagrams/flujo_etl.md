```mermaid
flowchart TD
    A[Extract: Excel/CSV] --> B[Transform: Limpieza, IMC, Normalización, Validaciones]
    B --> C[Load: Insertar en BD + Log ETL]
    C --> D[Histórico ETL + Reportes]
```
