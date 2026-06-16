# **Guía de Contexto y Prompt de Optimización Quirúrgica: HealthAnalytics IPS**

Este documento sirve como un mapa de contexto y conjunto de reglas estrictas para ti, **Blackbox AI**. Tu propósito es guiar la implementación de mejoras y correcciones en la rama mejoras-finales del proyecto **HealthAnalytics IPS** sin alterar ni romper la estructura funcional que ya existe y que ha sido probada.1

## **1\. Declaración de Arquitectura y Guardrails de Código Estable**

### **Regla de Oro de Desarrollo No Destructivo:**

**PROHIBIDO MODIFICAR O REESCRIBIR** los archivos de lógica core del framework Django y la persistencia relacional que ya funcionan correctamente.1 Cualquier nueva funcionalidad de saneamiento, corrección lingüística, parsing numérico o auditoría transaccional debe ser implementada de manera **aditiva y modular** (usando clases helper, middlewares o utilidades independientes).1 No elimines campos de modelos existentes ni reescribas vistas completas.1

### **Estructura Exacta del Repositorio a Respetar:**

healthcare-etl-platform/ │ ├── backend/ │ ├── config/ \# Configuraciones globales de Django │ ├── apps/ │ │ ├── authentication/ \# Autenticación, perfiles y control de roles (JWT)1 │ │ ├── etl/ \# Pipeline de extracción, limpieza y carga1 │ │ ├── analytics/ \# Cálculos estadísticos e indicadores clínicos1 │ │ ├── ml/ \# Entrenamiento, evaluación y predicción del modelo1 │ │ ├── dashboard/ \# Controladores y endpoints para el dashboard visual1 │ │ └── reports/ \# Lógica de generación de PDF, Excel y CSV1 │ │ │ ├── requirements.txt \# Dependencias del proyecto │ └── manage.py \# Script de administración de Django │ ├── frontend/ │ ├── templates/ \# Vistas HTML5 (Bootstrap 5\)1 │ ├── static/ \# CSS, JS (Chart.js / Plotly)1 │ └── dashboard/ \# Lógica del cliente e interacción asíncrona │ ├── datasets/ \# Archivos de datos simulados y cargados1 ├── docs/ \# Diagramas de arquitectura, flujo y ERD1 └── README.md \# Guía de instalación y uso

## **2\. Auditoría de Cumplimiento de Requisitos (Surgically Verified)**

Utiliza la siguiente matriz para saber qué elementos ya están consolidados en la arquitectura y cuáles requieren que implementes mejoras aditivas de forma segura \[1, 1\]:

| Componente | Requerimiento Técnico de Origen | Estado de Cumplimiento Actual | Acción Requerida de Tu Parte (Surgir con Precisión) |
| :---- | :---- | :---- | :---- |
| **Código Fuente** | Código modular alojado en GitHub sin credenciales expuestas.\[1, 1\] | **Completado.** El backend sigue el patrón de aplicaciones de Django.1 | Mantener la modularidad sin mezclar lógicas de distintas apps.1 |
| **Base de Datos** | Modelado relacional en MySQL o PostgreSQL.\[1, 1\] | **Completado.** Estructura de tablas para pacientes y analíticas lista.1 | Añadir la tabla de auditoría ETL mediante migraciones aditivas de Django.1 |
| **Logs del ETL** | Historial y logs detallados con tiempos de ejecución.\[1, 1\] | **Parcialmente Completado.** El script ejecuta los procesos y muestra logs en consola.1 | Crear el modelo de persistencia relacional para guardar el histórico de ejecuciones.1 |
| **Machine Learning** | Dataset entrenado, evaluación de métricas y predicciones.\[1, 1\] | **Completado.** Lógica predictiva integrada en el backend.1 | No alterar el modelo serializado ni los hiperparámetros actuales del clasificador.1 |
| **APIs REST** | Endpoints para autenticación, ETL, reportes y KPIs.\[1, 1\] | **Completado.** Enrutamiento REST funcional con Django REST Framework.1 | Segurizar los endpoints basándote en roles y permisos de JWT.1 |

## **3\. Formulación Clínica y Matemática Obligatoria (Inalterable)**

Para evitar alucinaciones en los cálculos analíticos y predictivos, debes ceñirte estrictamente a las siguientes expresiones y umbrales definidos para el negocio 1:

### **3.1. Ecuación Matemática del Índice de Masa Corporal (IMC)**

El cálculo automático de IMC en la fase de transformación del ETL debe emplear de manera inalterable la siguiente fórmula:  
![][image1]  
*Donde la variable peso está en kilogramos y la variable altura en metros.*  
Rangos de clasificación diagnóstica del IMC (No alucinar umbrales):

* **Bajo peso:** IMC inferior a 18.5  
* **Normal:** IMC entre 18.5 y 24.9  
* **Sobrepeso:** IMC entre 25 y 29.9  
* **Obesidad:** IMC igual o superior a 30

### **3.2. Métricas del Modelo de Clasificación Predictiva (Machine Learning)**

Para el panel de evaluación del modelo en el dashboard, debes calcular y renderizar las siguientes métricas exactas basadas en la matriz de confusión:  
![][image2]  
![][image3]

### **3.3. Umbrales de Seguridad de Alertas Críticas**

El sistema clínico debe disparar alertas visuales inmediatas basándose en los siguientes valores límite:

* **Presión Sistólica Crítica:** Superior a 180 mmHg  
* **Glucosa Crítica:** Superior a 300 mg/dL  
* **Saturación de Oxígeno Crítica:** Inferior a 85%

## **4\. Plan de Mejoras Técnicas Aditivas (Especificación de Código)**

A continuación, se detalla la estructura lógica exacta que debes implementar para corregir inconsistencias del dataset clínico simulado.1 Debes proporcionar el código de estas clases utilitarias de forma aislada para que puedan ser integradas sin afectar el core del proyecto:

### **4.1. Corrección Ortográfica de Diagnósticos (Similitud Léxica)**

El dataset simulado incluye errores tipográficos como "hipertencion", "hiper\_tension" e "hipertension" en la variable diagnóstico\_preliminar.1 Debes implementar una utilidad que limpie el texto y use similitud de caracteres en español para mapear al diagnóstico oficial :

Python  
import unicodedata  
from difflib import get\_close\_matches

class CorrectorLinguisticoClinico:  
    """Sanea de forma no destructiva las inconsistencias en los diagnosticos clinicos."""

    def \_\_init\_\_(self, catalogo\_oficial=None):  
        self.catalogo\_oficial \= catalogo\_oficial or \[  
            "hipertensión arterial",  
            "diabetes mellitus tipo 2",  
            "asma bronquial",  
            "obesidad mórbida",  
            "insuficiencia renal crónica",  
            "sano"  
        \]

    @staticmethod  
    def normalizar\_texto(texto: str) \-\> str:  
        """Remueve tildes, convierte a minusculas y elimina espacios en blanco extras."""  
        if not isinstance(texto, str):  
            return ""  
        texto\_descompuesto \= unicodedata.normalize('NFKD', texto)  
        texto\_limpio \= "".join(\[c for c in texto\_descompuesto if not unicodedata.combining(c)\])  
        return texto\_limpio.strip().lower()

    def corregir\_diagnostico(self, diagnostico: str, cutoff: float \= 0.80) \-\> str:  
        """Mapea un diagnostico mal escrito al termino oficial mas cercano en español."""  
        if not diagnostico or str(diagnostico).strip().lower() in \['nan', 'null', 'none'\]:  
            return "sin diagnóstico preliminar"  
          
        limpio \= self.normalizar\_texto(diagnostico)  
        mapeo\_catalogo \= {self.normalizar\_texto(diag): diag for diag in self.catalogo\_oficial}  
          
        if limpio in mapeo\_catalogo:  
            return mapeo\_catalogo\[limpio\]  
              
        coincidencias \= get\_close\_matches(limpio, mapeo\_catalogo.keys(), n=1, cutoff=cutoff)  
        if coincidencias:  
            return mapeo\_catalogo\[coincidencias\]  
              
        return diagnostico.strip().capitalize()

### **4.2. Parser de Números Escritos en Palabras (Saneamiento de Edad)**

Para subsanar errores en la entrada de la columna edad (donde algunos registros vienen como "Treinta" o "Veintidós"), implementa el siguiente transformador léxico para el pipeline :

Python  
import re

class ParserNumericoEspanol:  
    """Transforma representaciones textuales de numeros en español a sus digitos enteros."""

    UNIDADES \= {  
        'cero': 0, 'un': 1, 'uno': 1, 'dos': 2, 'tres': 3, 'cuatro': 4, 'cinco': 5,  
        'seis': 6, 'siete': 7, 'ocho': 8, 'nueve': 9, 'diez': 10,  
        'once': 11, 'doce': 12, 'trece': 13, 'catorce': 14, 'quince': 15,  
        'dieciseis': 16, 'diecisiete': 17, 'dieciocho': 18, 'diecinueve': 19,  
        'veinte': 20, 'veintiuno': 21, 'veintidos': 22, 'veintitres': 23,  
        'veinticuatro': 24, 'veinticinco': 25, 'veintiseis': 26, 'veintisiete': 27,  
        'veintiocho': 28, 'veintinueve': 29  
    }  
      
    DECENAS \= {  
        'treinta': 30, 'cuarenta': 40, 'cincuenta': 50, 'sesenta': 60,  
        'setenta': 70, 'ochenta': 80, 'noventa': 90  
    }

    @classmethod  
    def limpiar\_palabra(cls, palabra: str) \-\> str:  
        palabra \= palabra.lower().replace('í', 'i').replace('é', 'e').replace('á', 'a')  
        return re.sub(r'\[^a-z\]', '', palabra)

    @classmethod  
    def palabra\_a\_entero(cls, texto: str) \-\> int:  
        """Parsea cadenas como 'treinta y dos' o '45' a un entero valido."""  
        if not texto:  
            return None  
        texto\_limpio \= texto.strip().lower()  
        if texto\_limpio.isdigit():  
            return int(texto\_limpio)  
              
        tokens \= \[cls.limpiar\_palabra(p) for p in texto\_limpio.split() if p not in \['y', 'con'\]\]  
          
        acumulado \= 0  
        for token in tokens:  
            if token in cls.UNIDADES:  
                acumulado \+= cls.UNIDADES\[token\]  
            elif token in cls.DECENAS:  
                acumulado \+= cls.DECENAS\[token\]  
                  
        return acumulado if acumulado \> 0 else None

### **4.3. Persistencia de Auditoría Histórica de Procesos ETL**

Para asegurar la trazabilidad y la auditabilidad exigidas por las normativas de salud , debes estructurar el siguiente modelo relacional en Django (apps/etl/models.py) sin modificar las tablas de pacientes existentes 1:

Python  
from django.db import models  
from django.contrib.auth import get\_user\_model

User \= get\_user\_model()

class AuditoriaTransaccionalETL(models.Model):  
    """Modelo para guardar de manera persistente los logs e historicos del pipeline ETL."""  
      
    ESTADOS \=

    fecha\_ejecucion \= models.DateTimeField(auto\_now\_add=True, db\_index=True)  
    usuario\_responsable \= models.ForeignKey(User, on\_delete=models.SET\_NULL, null=True, related\_name='logs\_etl')  
    archivo\_fuente \= models.CharField(max\_length=255, blank=True, null=True)  
    registros\_saneados \= models.IntegerField(default=0)  
    tiempo\_ejecucion\_segundos \= models.FloatField(default=0.0)  
    estado\_finalizacion \= models.CharField(max\_length=15, choices=ESTADOS, default='EXITOSO')  
    informe\_errores \= models.TextField(blank=True, null=True)

    class Meta:  
        db\_table \= 'auditoria\_procesos\_etl'  
        ordering \= \['-fecha\_ejecucion'\]

    def \_\_str\_\_(self):  
        return f"ETL {self.id} \- {self.estado\_finalizacion} \- {self.fecha\_ejecucion}"

### **4.4. Control de Acceso por Roles (RBAC) con JWT**

Asegúrate de restringir las vistas del backend de Django REST Framework según los siguientes perfiles de usuario obligatorios 1:

* **Administrador:** Gestión total del sistema clínico. Acceso sin restricciones a /api/\*.1  
* **Médico:** Acceso clínico y analítica predictiva individual. Habilitado para /api/pacientes/, /api/predicciones/ y /api/reportes/.1  
* **Analista:** Operación y ejecución manual del pipeline ETL. Habilitado para /api/etl/run/, /api/dashboard/kpis/ y /api/reportes/.1

## **5\. Principios de Interoperabilidad (SQL on FHIR y FAIR)**

Para dotar al proyecto de un enfoque vanguardista y alineado con la ingeniería de datos en salud moderna 2:

1. **FAIR (Findable, Accessible, Interoperable, Reusable):** Al generar o transformar conjuntos de datos simulados, separa de forma segura el identificador real del paciente de la información clínica, utilizando un ID sintético (ej. HospitalName:counter) para preservar la privacidad.3  
2. **SQL on FHIR:** Diseña las estructuras relacionales de Django de modo que las tablas planas correspondientes a expedientes clínicos se puedan mapear conceptualmente a esquemas estandarizados como *ViewDefinitions* de recursos HL7/FHIR (ej. recursos *Patient* y *Observation*), facilitando la portabilidad y consultas de análisis clínico federado.2

## **6\. Reglas de Comportamiento Estrictas para Blackbox AI**

Cuando el desarrollador te solicite implementar o corregir una de estas mejoras, debes actuar con la precisión de un cirujano de software:

1. **Enfoque Aditivo Primero:** No alteres el código core que ya funciona. Provee soluciones modulares que el desarrollador pueda importar sin destruir la lógica existente.1  
2. **Bloques de Código Selectivos:** No imprimas archivos completos de más de 100 líneas de código. En su lugar, utiliza bloques de tipo diff o indica claramente en qué archivo y línea exacta debe colocarse el fragmento sugerido.1  
3. **Sin Alucinaciones de Framework:** No inventes librerías ni dependencias innecesarias en el requirements.txt. Utiliza estrictamente la infraestructura configurada: Django, Django REST Framework, Pandas, Scikit-Learn y MySQL/PostgreSQL.1  
4. **Respeto a las Fórmulas Matemáticas:** Asegura que los cálculos de IMC, las métricas de rendimiento de Machine Learning y las condiciones de alerta crítica sigan al pie de la letra las expresiones provistas en este documento.1

#### **Fuentes citadas**

1. Reto Técnico Analitica Datos Desarrollo FullStack.pdf  
2. Health Analytics \- InfoCentral, acceso: junio 16, 2026, [https://infocentral.infoway-inforoute.ca/en/collaboration/communities/health-analytics](https://infocentral.infoway-inforoute.ca/en/collaboration/communities/health-analytics)  
3. I-ETL: an interoperability-aware health (meta)data pipeline to enable federated analyses \- PMC, acceso: junio 16, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC12519790/](https://pmc.ncbi.nlm.nih.gov/articles/PMC12519790/)

[image1]: <data:image/png;base64,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>

[image2]: <data:image/png;base64,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>

[image3]: <data:image/png;base64,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>