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
