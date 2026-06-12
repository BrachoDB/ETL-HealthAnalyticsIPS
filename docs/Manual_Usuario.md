# Manual de Usuario - HealthAnalytics IPS

## Inicio de Sesión
Acceda a la plataforma e ingrese sus credenciales:

- Usuario: `admin`
- Contraseña: `admin123`

## Dashboard Principal
Al ingresar verá:

- **KPIs médicos:** total de pacientes, críticos, hipertensos e IMC promedio.
- **Distribución de riesgo:** gráfico de torta por nivel de riesgo.
- **Edad vs riesgo:** gráfico de barras agrupado por rango de edad.
- **Carga manual CSV:** formulario para subir un archivo clínico CSV.
- **Predicción ML:** formulario para predecir el riesgo de un paciente.
- **Exportaciones:** botones para descargar Excel, CSV o PDF.
- **Histórico ETL:** tabla con detalle de ejecuciones, duración, estado y observaciones.

## Ejecución de ETL desde Excel
1. Haga clic en el botón **"Ejecutar ETL"** en la parte superior derecha.
2. El proceso se ejecutará en segundo plano.
3. Cuando finalice, actualice el histórico con el botón de refrescar.

## Carga manual de CSV
1. En la tarjeta **"Carga manual de CSV clínico"**, seleccione un archivo `.csv`.
2. El CSV debe incluir las columnas clínicas requeridas.
3. Haga clic en **"Subir CSV y procesar ETL"**.
4. El sistema validará columnas y rangos clínicos antes de cargar los datos.

### Rangos clínicos válidos
- Temperatura: 35-42 °C.
- Presión sistólica: 70-220 mmHg.
- Glucosa: 40-400 mg/dL.
- Saturación de oxígeno: 70-100 %.

Los registros fuera de rango se omiten y se reportan en el histórico ETL.

## Predicción de Riesgo (Machine Learning)
1. Diríjase a la sección **"Predicción de Riesgo (ML)"**.
2. Complete los campos clínicos del paciente.
3. Haga clic en **"Predecir Riesgo"**.
4. El sistema mostrará el nivel de riesgo predicho y las probabilidades por categoría.

## Exportación de Datos
Use los botones superiores:

- **Exportar Excel:** descarga el listado completo de pacientes en `.xlsx`.
- **Exportar CSV:** descarga el listado completo en `.csv`.
- **Exportar PDF:** descarga un resumen PDF con fecha, total de pacientes y columnas exportadas.

## Documentación de API
Si es desarrollador, puede acceder a la documentación interactiva (Swagger) haciendo clic en **"API Docs"** en la barra lateral.

## Roles
- **Administrador:** acceso completo.
- **Médico:** uso clínico del dashboard y predicción.
- **Analista:** consulta de pacientes, logs ETL, KPIs y exportaciones.
