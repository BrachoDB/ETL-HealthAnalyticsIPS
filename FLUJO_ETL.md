# Flujo ETL

## Extract
- Se lee el archivo enviado por el usuario (Excel/CSV).
- Fallback al dataset incluido en el repo si no se proporciona archivo.

## Transform
- Normalización de nombres de columnas (manejo de acentos).
- Eliminación de duplicados (por `id_paciente`, si existe).
- Imputación de nulos:
  - Numéricos: mediana
  - Categóricos: moda
- Corrección ortográfica básica en `diagnostico_preliminar`.
- Conversión de tipos numéricos.
- Cálculo de IMC si aplica.
- Clasificación de `riesgo_enfermedad` con heurísticas.

## Load
- Inserción en PostgreSQL mediante `bulk_create` en `ClinicalRecord`.
- Registro de ejecución ETL en `ETLRun` (estado, duración, records).

## Evidencia
- Guardar el `etl_run_id` devuelto por el endpoint.

