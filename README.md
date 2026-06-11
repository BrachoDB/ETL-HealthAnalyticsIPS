# HealthAnalytics IPS - Plataforma Inteligente de Analítica Clínica

Este proyecto es una solución integral para el procesamiento, análisis y predicción de riesgo médico basado en datos clínicos.

## Características
- **ETL Automatizado:** Limpieza y transformación de datos desde Excel a MySQL usando Pandas.
- **Machine Learning:** Modelo Random Forest para la predicción de riesgo de enfermedades.
- **Dashboard Interactivo:** Visualización de KPIs y métricas críticas con Chart.js.
- **Seguridad:** Autenticación JWT y gestión de roles (Admin, Médico).
- **API Documentada:** Documentación interactiva con Swagger/OpenAPI.

## Estructura del Proyecto
```
backend/
├── apps/
│   ├── authentication/   # Gestión de usuarios y JWT
│   ├── etl/              # Proceso de extracción, limpieza y carga
│   ├── analytics/        # KPIs y estadísticas
│   ├── ml/               # Modelos predictivos
│   └── dashboard/        # Interfaz de usuario
├── config/               # Configuración de Django
└── manage.py
```

## Guía de Inicio Rápido
1. Clonar el repositorio.
2. Configurar el archivo `backend/.env` con su conexión MySQL.
3. Instalar dependencias: `pip install -r backend/requirements.txt`.
4. Ejecutar migraciones: `python backend/manage.py migrate`.
5. Ejecutar ETL inicial: `python backend/manage.py run_etl`.
6. Entrenar el modelo ML: `python backend/manage.py train_ml`.
7. Iniciar el servidor: `python backend/manage.py runserver`.

## Acceso
- **Dashboard:** http://localhost:8000/
- **Documentación API:** http://localhost:8000/api/docs/
- **Credenciales por defecto:** admin / admin123
