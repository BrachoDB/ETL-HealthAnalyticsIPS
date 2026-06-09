# TODO - FASE 3 (Analytics + Machine Learning + APIs)

## Analytics
- [x] Implementar endpoints reales en `analytics/views.py` para: media, mediana, moda, desviación estándar.
- [x] Implementar KPIs de analítica clínica (críticos, hipertensos, diabéticos, fumadores, riesgo promedio) en `/api/dashboard/kpis/`.
- [x] Implementar segmentaciones por edad, sexo, diagnóstico, IMC y riesgo en `/api/reportes/`.


## Dashboard KPIs
- [x] Implementar `/api/dashboard/kpis/` (consulta real a `ClinicalRecord`).

## Reports
- [x] Implementar `/api/reportes/` con stats + segmentaciones.

## Pacientes
- [x] Implementar `/api/pacientes/` (GET) en `etl/views.py` y ruta en `etl/urls.py`.

## Machine Learning (Random Forest)
- [x] Implementar persistencia y utilidades RandomForest (`ml/utils_rf.py`).
- [x] Implementar entrenamiento y predicción (`ml/views.py`).
- [x] Implementar API requerida `/api/predicciones/` (POST: entrena+evalúa+predice).
- [x] Alinear rutas de ML en `ml/urls.py` con compatibilidad de stubs previos.

## Swagger/OpenAPI
- [ ] Verificar que nuevos endpoints queden documentados en `/api/docs/`.

## Verificación
- [x] Ejecutar migraciones.
- [ ] Probar endpoints con Postman/curl.

