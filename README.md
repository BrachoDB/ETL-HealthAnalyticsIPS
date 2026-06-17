# HealthAnalytics IPS - Plataforma Inteligente de Analítica Clínica

Este proyecto es una solución integral para el procesamiento, análisis y predicción de riesgo médico basado en datos clínicos.

## Características
- **ETL Automatizado:** limpieza y transformación de datos desde Excel o CSV a MySQL usando Pandas.
- **Validaciones Clínicas:** omisión controlada de registros fuera de rango para temperatura, presión sistólica, glucosa y saturación de oxígeno.
- **Carga Manual CSV:** endpoint `POST /api/pacientes/upload-csv/` y formulario en el dashboard.
- **Machine Learning:** modelo Random Forest para predicción individual y batch de riesgo de enfermedades.
- **Métricas ML:** registro de accuracy, precision, recall, F1 y matriz de confusión en `MLModelMetrics`.
- **Dashboard Interactivo:** KPIs, distribución de riesgo, edad vs riesgo, predicción ML, histórico ETL y exportaciones.
- **Exportaciones:** Excel, CSV y PDF desde `/api/analytics/export/<formato>/`.
- **Seguridad:** autenticación JWT, roles Admin/Médico/Analista y permisos read-only para Analista.
- **API Documentada:** documentación interactiva con Swagger/OpenAPI.

## Estructura del Proyecto
```
backend/
├── apps/
│   ├── authentication/   # Gestión de usuarios, roles y JWT
│   ├── etl/              # Proceso de extracción, limpieza, validación y carga
│   ├── analytics/        # KPIs, edad vs riesgo y exportaciones
│   ├── ml/               # Entrenamiento, predicción y métricas del modelo
│   └── dashboard/        # Plantilla principal del dashboard
├── config/               # Configuración de Django
├── media/models/         # Modelos entrenados en formato joblib
└── manage.py

docs/
├── diagrams/             # Diagramas Mermaid de arquitectura, flujo ETL y ERD
└── sql_migrate.ps1       # Script para generar SQL de migraciones
```

## Guía de Inicio Rápido
1. Clonar el repositorio.
2. Configurar el archivo `backend/.env` con su conexión MySQL.
3. Instalar dependencias: `pip install -r backend/requirements.txt`.
4. Ejecutar migraciones: `python backend/manage.py migrate`.
5. Ejecutar ETL inicial: `python backend/manage.py run_etl`.
6. Ejecutar ETL con archivo manual: `python backend/manage.py run_etl --file ruta/al/archivo.csv`.
7. Entrenar el modelo ML: `python backend/manage.py train_ml`.
8. Iniciar el servidor: `python backend/manage.py runserver`.

## Endpoints principales
- `POST /api/pacientes/logs/run/`: ejecuta el ETL por defecto.
- `POST /api/pacientes/upload-csv/`: sube un CSV/Excel clínico y ejecuta el ETL.
- `GET /api/analytics/kpis/`: retorna KPIs, distribución de riesgo y datos para edad vs riesgo.
- `GET /api/analytics/export/xlsx/`, `/csv/`, `/pdf/`: exporta pacientes.
- `POST /api/ml/predict/`: predicción individual.
- `POST /api/ml/predict/batch/`: predicción batch con una lista de registros.

## Roles
- **ADMIN:** acceso completo.
- **MEDICO:** uso clínico del dashboard y predicción.
- **ANALISTA:** permisos read-only para consultar pacientes, logs ETL, KPIs y exportar datos analíticos.

## 🚀 Despliegue en Render

El proyecto está listo para desplegarse en **[Render.com](https://render.com)** manteniendo
**MySQL** como base de datos (externa en **Aiven**, con **SSL requerido**). No se utiliza PostgreSQL.

### Archivos de despliegue
| Archivo | Función |
|---------|---------|
| `build.sh` | Instala dependencias, ejecuta `collectstatic` y `migrate`. |
| `render.yaml` | Blueprint del servicio web (Gunicorn + variables de entorno). |
| `backend/.env.example` | Plantilla de variables para local y producción. |

### Tecnología de producción
- **Servidor WSGI:** Gunicorn.
- **Archivos estáticos:** WhiteNoise (`CompressedManifestStaticFilesStorage`).
- **Base de datos:** MySQL externo (Aiven) vía `dj-database-url` + `DATABASE_URL`, con SSL.

### Opción A — Despliegue automático con Blueprint (recomendado)
1. Sube el proyecto a un repositorio de GitHub.
2. En Render: **New + → Blueprint** y selecciona el repo (detecta `render.yaml`).
3. Render crea el servicio, ejecuta `build.sh` y arranca con Gunicorn.
4. Revisa/ajusta las variables de entorno (especialmente `DATABASE_URL` y `SECRET_KEY`).

### Opción B — Servicio Web manual
Crea un **Web Service** apuntando al repo y configúralo así:

- **Build Command:** `./build.sh`
- **Start Command:** `cd backend && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`

### Variables de entorno requeridas
| Variable | Ejemplo / valor |
|----------|-----------------|
| `SECRET_KEY` | (genera una clave larga aleatoria) |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `.onrender.com,localhost,127.0.0.1` |
| `DATABASE_URL` | `mysql://avnadmin:PASSWORD@mysql-xxxxx.aivencloud.com:21736/defaultdb` |
| `DB_SSL_REQUIRED` | `True` |
| `DB_SSL_MODE` | `REQUIRED` |
| `SECURE_SSL_REDIRECT` | `True` |
| `SESSION_COOKIE_SECURE` | `True` |
| `CSRF_COOKIE_SECURE` | `True` |

> El host público de Render (`RENDER_EXTERNAL_HOSTNAME`) se añade automáticamente a
> `ALLOWED_HOSTS` y a `CSRF_TRUSTED_ORIGINS` desde `settings.py`.

### Conexión MySQL en Aiven (SSL)
La cadena `DATABASE_URL` lleva host, puerto, usuario, contraseña y base de datos.
El cifrado SSL se activa con `DB_SSL_REQUIRED=True` (modo `REQUIRED`). Opcionalmente,
para **verificar** el certificado del servidor, descarga el `ca.pem` de Aiven, súbelo
como *Secret File* en Render y define `DB_SSL_CA=/etc/secrets/aiven-ca.pem`.

### Modelo de Machine Learning en producción
Los modelos `.joblib` viven en `backend/media/models/` y están **excluidos del repositorio**
(`.gitignore`). En producción, una vez desplegado, genera el modelo ejecutando en la
*Shell* de Render:

```bash
cd backend && python manage.py train_ml
```

(o sube los `.joblib` mediante un *Secret File* / almacenamiento persistente).

### Desarrollo local
```bash
cp backend/.env.example backend/.env   # ajusta tu conexión MySQL local
pip install -r backend/requirements.txt
python backend/manage.py migrate
python backend/manage.py runserver
```

## Documentación técnica
- Manual técnico: `docs/Manual_Tecnico.md`
- Manual de usuario: `docs/Manual_Usuario.md`
- Diagramas Mermaid: `docs/diagrams/`
- Script SQL de migraciones: `docs/sql_migrate.ps1`

## Acceso
- **Dashboard:** http://localhost:8000/
- **Documentación API:** http://localhost:8000/api/docs/
- **Credenciales por defecto:** admin / admin123
