# Sistema de Apoyo a la Toma de Decisiones Comerciales (Segmentación B2B)

## Descripción del Problema y Solución
**Problema:** La priorización de leads B2B en FPA Latam se realizaba de manera subjetiva y manual, basada en la intuición de los consultores. La información histórica estaba fragmentada en Excel, sin llaves primarias (RUC) y sin etiquetas que permitieran clasificar a los prospectos mediante aprendizaje supervisado.

**Solución:** Se desarrolló un MVP (*Minimum Viable Product*) que aplica algoritmos de aprendizaje no supervisado (*K-Means*) sobre datos internos enriquecidos con fuentes públicas ecuatorianas (SRI y SCVS). El modelo identifica segmentos de alta afinidad y despliega los resultados mediante un *Surrogate Model* en un Dashboard interactivo *Low-Code* (Oracle APEX).

---

## Organización Estructurada de Carpetas
El repositorio sigue la metodología CRISP-DM, organizado en un *pipeline* secuencial dentro del directorio `/Desarrollo_clustering_maestria/`:

* `01_data_ingestion_enrichment/`: Scripts para consolidar los archivos crudos comerciales y conectarlos con los catálogos públicos del SRI y SCVS.
* `02_data_cleaning/`: Lógica de *Entity Resolution* y creación del *Golden Record* (cruce difuso y exacto de nombres comerciales a RUCs oficiales).
* `03_feature_engineering/`: Tratamiento de nulos, estandarización y creación de matrices numéricas para la Capa 1 (Tributaria) y Capa 2 (Financiera).
* `04_modeling/`: Entrenamiento del modelo K-Means y validación interna matemática (Silhouette, Elbow Method).
* `05_evaluation/`: Evaluación de resultados, validación externa con clientes históricos y cálculo del *Adjusted Rand Index* (ARI).
* `06_reporting/`: Generación de artefactos finales y reglas de segmentación para su subida a la base de datos.
* `outputs/`: Matrices, perfiles y datasets resultantes generados en cada etapa del *pipeline*.
* `00_Oracle_DDL_MVP.sql`: Script SQL con la arquitectura de tablas y vistas para desplegar el modelo en Oracle Autonomous Database.

---

## Requisitos Técnicos y Dependencias

**Para ejecutar el pipeline analítico localmente:**
* Python 3.10+
* Entorno Jupyter Notebook
* Librerías Core:
  * `pandas` y `numpy` (Manipulación de datos)
  * `scikit-learn` (Modelo K-Means y preprocesamiento)
  * `rapidfuzz` (Matching difuso de strings para *Entity Resolution*)
  * `matplotlib` y `seaborn` (Visualizaciones y gráficos)
  * `openpyxl` (Lectura de excels de entrada)

**Para el despliegue productivo en la nube:**
* Oracle Cloud Infrastructure (OCI) - Capa *Always Free*
* Oracle Autonomous Database (Almacenamiento e Inferencia)
* Oracle APEX (Interfaz *Low-Code* de usuario)

---

## Instrucciones de Ejecución Paso a Paso

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/OAlbuja/Tesis_Maestria_Inteligencia_Artificial_Aplicada.git
   cd Tesis_Maestria_Inteligencia_Artificial_Aplicada/Desarrollo_clustering_maestria
   ```

2. **Configurar Entorno Virtual:**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # (Windows)
   pip install pandas scikit-learn rapidfuzz matplotlib seaborn openpyxl jupyter
   ```

3. **Ejecutar el Pipeline Local:**
   * Abrir Jupyter Notebook.
   * Navegar a las carpetas enumeradas (del `01` al `06`) y ejecutar los *notebooks* en orden secuencial. 
   * También se puede ejecutar directamente el notebook maestro `00_orquestador_pipeline.ipynb` para procesar todo el flujo de inicio a fin.
   * Los resultados y tablas depuradas se generarán automáticamente en la carpeta `outputs/`.

4. **Despliegue en Base de Datos y APEX:**
   * Conectarse a Oracle Autonomous Database vía SQL Developer Web.
   * Ejecutar el script maestro `00_Oracle_DDL_MVP.sql` para crear el esquema, tablas y vistas predictivas (*Surrogate Model*).
   * Subir los archivos `.csv` de la carpeta `outputs/` a sus respectivas tablas en Oracle mediante la herramienta *Data Load*.
   * Importar o vincular la base de datos al *Workspace* de Oracle APEX para visualizar el *Dashboard*.

---

## Control de Versiones y Demo
* El historial de este repositorio (`git log`) evidencia la evolución iterativa del código, desde la ingesta inicial y control de calidad, hasta la construcción del modelo final y su validación externa.
* **Demo del Prototipo:** El entorno funcional se encuentra desplegado en Oracle APEX. *(Referirse al anexo del documento principal o video demostrativo para acceder a las credenciales y visualización de la interfaz).*
