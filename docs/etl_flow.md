# ETL Flow

1. **Extract**
   - Lectura de Excel o CSV.
   - Logs/contadores de registros procesados.

2. **Transform**
   - Normalización de columnas (acentos).
   - Eliminación de duplicados por `id_paciente`.
   - Tratamiento de nulos (mediana/moda).
   - Corrección ortográfica de diagnósticos.
   - Conversión de tipos numéricos.
   - Cálculo de IMC.
   - Clasificación de riesgo.

3. **Load**
   - Inserción en `ClinicalRecord`.
   - Registro de estado en `ETLRun`.

