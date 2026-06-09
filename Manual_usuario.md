# Manual de usuario

## 1. Acceso
1. Abrir: `http://127.0.0.1:8000/dashboard/`
2. Iniciar sesión.

## 2. Navegación
- **Dashboard**: KPIs y gráficas.
- **Pacientes**: búsqueda y tabla.
- **ETL**: subir dataset y ejecutar carga.
- **Predicciones**: ejecutar entrenamiento/evaluación y predicción.
- **Reportes**: estadísticas y segmentaciones.

## 3. Autenticación
- El login devuelve JWT.
- El frontend adjunta el token `Authorization: Bearer <access>` a todas las llamadas.

