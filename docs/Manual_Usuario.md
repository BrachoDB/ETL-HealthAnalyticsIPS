# Manual de Usuario - HealthAnalytics IPS

## Inicio de Sesión
Acceda a la plataforma e ingrese sus credenciales (Usuario: `admin`, Contraseña: `admin123`).

## Dashboard Principal
Al ingresar, verá:
- **KPIs Médicos:** Total de pacientes, críticos, hipertensos e IMC promedio.
- **Distribución de Riesgo:** Gráfico de torta que muestra el porcentaje de pacientes en cada nivel de riesgo.
- **Histórico ETL:** Tabla con el detalle de las últimas ejecuciones del proceso de carga.

## Ejecución de ETL
Para actualizar los datos desde el archivo Excel:
1. Haga clic en el botón **"Ejecutar ETL"** en la parte superior derecha.
2. El proceso se ejecutará en segundo plano. Una vez finalizado, los KPIs y la tabla de histórico se actualizarán.

## Predicción de Riesgo (Machine Learning)
Para predecir el riesgo de un nuevo paciente:
1. Diríjase a la sección **"Predicción de Riesgo (ML)"**.
2. Complete los campos con la información clínica del paciente (Edad, IMC, Glucosa, etc.).
3. Haga clic en **"Predecir Riesgo"**.
4. El sistema mostrará el nivel de riesgo predicho por el modelo de Inteligencia Artificial.

## Documentación de API
Si es un desarrollador, puede acceder a la documentación interactiva (Swagger) haciendo clic en **"API Docs"** en la barra lateral.
