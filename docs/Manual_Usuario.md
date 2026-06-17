# Manual de Usuario - HealthAnalytics IPS

## Inicio de Sesión

Acceda a la plataforma e ingrese sus credenciales:

- Usuario: `admin`
- Contraseña: `admin123`

## Dashboard Principal

Al ingresar verá:

- **KPIs médicos:** total de pacientes, críticos, hipertensos e IMC promedio.
- **Distribución de riesgo:** gráfico por nivel de riesgo.
- **Edad vs riesgo:** gráfico de barras agrupado por rango de edad.
- **Carga manual CSV/Excel:** formulario para subir un archivo clínico CSV, XLSX o XLS.
- **Predicción ML:** formulario para predecir el riesgo de un paciente.
- **Exportaciones:** botones para descargar Excel, CSV o PDF.
- **Histórico ETL:** tabla con detalle de ejecuciones, duración, estado y observaciones.

## Ejecución de ETL desde archivo

1. Haga clic en el botón **"Ejecutar ETL"** en la parte superior del dashboard.
2. El sistema procesará el archivo configurado por defecto.
3. Cuando finalice, actualice el histórico con el botón de refrescar.

## Carga manual de CSV/Excel

1. En la tarjeta **"Carga manual de CSV o Excel clínico"**, seleccione un archivo `.csv`, `.xlsx` o `.xls`.
2. El archivo debe incluir las columnas clínicas requeridas.
3. Haga clic en **"Subir CSV/Excel y procesar ETL"**.
4. El sistema validará columnas y rangos clínicos antes de cargar los datos.

### Rangos clínicos válidos

- Temperatura: 35-42 °C.
- Presión sistólica: 70-220 mmHg.
- Presión diastólica: 40-140 mmHg.
- Glucosa: 40-400 mg/dL.
- Saturación de oxígeno: 70-100 %.

Los registros fuera de rango se omiten y se reportan en el histórico ETL.

## Analítica

La sección **Analítica** muestra indicadores y gráficos para revisar la información clínica cargada:

- Distribución de riesgo clínico.
- Edad vs riesgo clínico.
- Diagnósticos preliminares más frecuentes.
- Tendencia mensual de riesgo.
- Tendencias clínicas.
- Heatmap de edad vs riesgo.
- Segmentación de pacientes por sexo, riesgo y diagnóstico.
- Botones para exportar Excel, CSV o PDF.

El PDF de Analítica descarga un archivo con una tabla de registros clínicos que incluye ID, paciente, edad, sexo, diagnóstico, riesgo, presión sistólica, glucosa, saturación de oxígeno y fecha de consulta.

## Predicción de Riesgo (Machine Learning)

1. Diríjase a la sección **"Predicción de Riesgo (ML)"**.
2. Complete los campos clínicos del paciente.
3. Haga clic en **"Predecir Riesgo"**.
4. El sistema mostrará el nivel de riesgo predicho, probabilidades, explicación de variables relevantes y advertencia clínica.

## Exportación de Datos

Use los botones superiores del dashboard o de la sección Analítica:

- **Exportar Excel:** descarga el listado completo de pacientes en `.xlsx`.
- **Exportar CSV:** descarga el listado completo en `.csv`.
- **Exportar PDF:** descarga un PDF con tabla de registros clínicos.

En la sección **Reportes** también puede generar un PDF ejecutivo con KPIs, gráficos y tabla de pacientes según el periodo seleccionado.

## Reportes

La sección **Reportes** permite:

- Generar PDF ejecutivo con KPIs, gráficos y tabla de pacientes.
- Seleccionar periodo: última semana, último mes, último trimestre o último año.
- Elegir secciones a incluir: KPIs, gráficos y tabla de pacientes.
- Exportar datos en Excel o CSV.
- Consultar el histórico de descargas.

## Documentación de API

Si es desarrollador, puede acceder a la documentación interactiva (Swagger) haciendo clic en **"API Docs"** en la barra lateral.

## Roles

- **Administrador:** acceso completo.
- **Médico:** uso clínico del dashboard, pacientes, reportes y predicción.
- **Analista:** consulta de pacientes, logs ETL, KPIs y exportaciones.
