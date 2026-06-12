# Manual Técnico - HealthAnalytics IPS

## Arquitectura del Sistema
El sistema sigue una arquitectura desacoplada con un backend en **Django 5** y un frontend basado en plantillas de Django con **JavaScript (Axios)** para interactuar con una API REST.

### Componentes Principales:
1. **Módulo ETL:** Ubicado en `apps/etl`, gestiona la limpieza y carga de datos desde Excel a MySQL.
2. **Módulo ML:** Ubicado en `apps/ml`, contiene el entrenamiento del modelo Random Forest y el endpoint de predicción.
3. **Módulo Analytics:** Ubicado en `apps/analytics`, calcula KPIs y métricas clínicas.
4. **Módulo Authentication:** Gestiona usuarios y roles mediante JWT.

## Tecnologías Utilizadas
- **Backend:** Python 3.12, Django, DRF, Pandas, Scikit-Learn.
- **Base de Datos:** MySQL.
- **Frontend:** HTML5, CSS3, Bootstrap 5, Chart.js.

## Proceso ETL
El script `run_etl` realiza:
- Extracción desde `dataset_clinico_etl_1800_registros.xlsx`.
- Limpieza de duplicados por `id_paciente`.
- Corrección de tipos (edad, presión).
- Normalización de diagnósticos (typos).
- Imputación de nulos (mediana/moda).
- Cálculo automático de IMC.
- Carga en la tabla `Patient`.

## Modelo de Machine Learning
Se utiliza un **Random Forest Classifier** entrenado con las variables clínicas para predecir el `riesgo_enfermedad`.
Métricas evaluadas: Accuracy, Precision, Recall, F1-Score.

## Instalación
1. Instalar dependencias: `pip install -r requirements.txt`
2. Configurar `.env` con las credenciales de MySQL.
3. Ejecutar migraciones: `python manage.py migrate`
4. Ejecutar ETL: `python manage.py run_etl`
5. Entrenar ML: `python manage.py train_ml`
6. Iniciar servidor: `python manage.py runserver`

## Uso de `.env` para pruebas locales
Cuando el proyecto se ejecuta de forma **local**, es recomendable usar un archivo **`.env`** para administrar variables sensibles (por ejemplo, credenciales de base de datos o claves de seguridad) sin “hardcodearlas” dentro del código.

### ¿Qué es `.env`?
Es un archivo de texto que contiene pares `VARIABLE=valor` y que la aplicación lee al iniciar. Así, puedes cambiar la configuración para cada entorno (local, desarrollo, producción) sin modificar el código.

### ¿Cómo configurarlo para pruebas locales?
1. Crea el archivo `backend/.env` en la raíz del backend.
2. Define allí las variables requeridas por Django y la base de datos (por ejemplo, conexión MySQL y, si aplica, `SECRET_KEY`).
3. Antes de correr el proyecto, asegúrate de haber creado el archivo `.env` correctamente.

### Recomendaciones
- **No subas** el archivo `.env` al repositorio (debe mantenerse como información local).
- La configuración local debe hacerse antes de ejecutar comandos como:
  - `python manage.py migrate`
  - `python manage.py run_etl`
  - `python manage.py runserver`

