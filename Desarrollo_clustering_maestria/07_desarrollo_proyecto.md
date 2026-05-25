# 7. Desarrollo del proyecto

El desarrollo del proyecto consistió en la construcción de un prototipo analítico de segmentación empresarial B2B para FPA Latam, orientado a transformar fuentes comerciales dispersas en una herramienta de priorización de prospectos basada en datos. La solución integró un pipeline local en Python/Jupyter para limpieza, resolución de entidades, feature engineering, modelado y evaluación; posteriormente, los resultados fueron trasladados a Oracle Cloud Infrastructure mediante Oracle Autonomous Database, Oracle Machine Learning y Oracle APEX. El producto final corresponde a un MVP funcional en la nube que permite consultar empresas por RUC, visualizar segmentos generados por clustering y guardar prospectos priorizados para seguimiento comercial.

| Fase | Descripción general | Resultado obtenido |
|---|---|---|
| 1. Diagnóstico e ingesta | Revisión de fuentes internas de FPA y fuentes públicas del SRI y SCVS. | Identificación de datos disponibles, brechas de calidad y necesidad de normalización. |
| 2. Limpieza y Golden Record | Normalización de nombres, resolución de entidades y consolidación por RUC. | Base única de 181 empresas con RUC verificado. |
| 3. Feature engineering | Construcción de variables tributarias, geográficas y financieras. | Matrices analíticas para Capa 1 y Capa 2. |
| 4. Modelado y evaluación | Entrenamiento de K-Means, comparación de alternativas y cálculo de métricas. | Segmentos empresariales interpretables y evaluados. |
| 5. Despliegue en nube | Carga en Oracle Autonomous Database, pruebas en OML y desarrollo en APEX. | MVP funcional con dashboard, buscador y mini-CRM de prospectos. |

**[Insertar Figura 7.1: Arquitectura final del MVP]**

Comentario sugerido bajo la figura:  
La figura resume la arquitectura implementada en el proyecto, desde las fuentes internas y públicas hasta la aplicación final en Oracle APEX. Se observa que el procesamiento analítico principal se realizó en Python/Jupyter, mientras que Oracle Autonomous Database centraliza los datos, vistas y reglas de negocio que alimentan el prototipo web.

## 7.1. Diseño de la solución

### 7.1.1. Enfoque metodológico aplicado

La solución se diseñó bajo un enfoque metodológico inspirado en CRISP-DM, adaptado a un problema de aprendizaje no supervisado. A diferencia de un modelo supervisado, el proyecto no partió de una variable objetivo robusta de compra/no compra para entrenar un clasificador. Por ello, el objetivo fue descubrir patrones de similitud entre empresas y, posteriormente, interpretar esos segmentos con apoyo de la variable `ES_CLIENTE_FPA`, utilizada únicamente como validación externa y no como entrada del entrenamiento.

El diseño priorizó la trazabilidad del dato antes del modelado. Esto significó resolver primero la identidad legal de las empresas mediante un Golden Record, enriquecer los registros con fuentes oficiales y recién después construir matrices aptas para clustering. Esta decisión redujo el riesgo de generar segmentos matemáticamente válidos pero comercialmente poco confiables.

### 7.1.2. Fases del proyecto y actividades realizadas

| Fase del proyecto | Actividades realizadas | Evidencia o artefacto |
|---|---|---|
| Diagnóstico de datos | Revisión de archivos de leads, proyectos, SRI y SCVS. Identificación de inconsistencias en nombres comerciales y ausencia de RUC en registros internos. | Notebooks de ingesta y profiling. |
| Resolución de entidades | Normalización textual, comparación de nombres, validación manual y consolidación de alias empresariales. | Golden Record de empresas. |
| Ingeniería de variables | Integración de variables SRI y SCVS; transformación de variables categóricas y financieras. | Matrices `features_capa1`, `features_capa2`, `matriz_capa1` y `matriz_capa2`. |
| Modelado | Entrenamiento de K-Means en dos capas y análisis exploratorio con clustering jerárquico. | Notebook `04_modeling/01_clustering.ipynb`. |
| Evaluación | Uso de métricas internas y validación externa con clientes FPA. | Tablas de métricas, perfiles de cluster y ARI. |
| Despliegue | Creación de tablas, vistas y aplicación APEX en OCI. | `00_Oracle_DDL_MVP.sql`, `Notebook - OML.pdf` y capturas del sistema. |

**[Insertar Figura 7.2: Diagrama de fases del proyecto]**

Comentario sugerido bajo la figura:  
La figura presenta las fases metodológicas seguidas durante el desarrollo. El flujo evidencia que el modelo no fue construido directamente sobre datos crudos, sino sobre una base previamente depurada, enriquecida y transformada en variables aptas para clustering.

### 7.1.3. Herramientas utilizadas

| Categoría | Herramienta o plataforma | Uso dentro del proyecto |
|---|---|---|
| Procesamiento local | Python / Jupyter Notebook | Desarrollo del pipeline de limpieza, preparación de datos, feature engineering, modelado y evaluación. |
| Manipulación de datos | pandas | Integración de archivos, transformación de columnas, generación de matrices y exportación de artefactos. |
| Modelado | scikit-learn | Entrenamiento local de K-Means, comparación de alternativas y cálculo de métricas. |
| Resolución de entidades | Técnicas de normalización textual y matching | Consolidación de nombres comerciales y alias empresariales para construir el Golden Record. |
| Base de datos cloud | Oracle Autonomous Database | Persistencia de tablas, vistas, índices, resultados del modelo y reglas de priorización. |
| Experimentación en nube | Oracle Machine Learning | Pruebas de traslado del modelo K-Means al entorno Oracle y comparación con resultados locales. |
| Interfaz low-code | Oracle APEX | Construcción del dashboard, buscador de empresas, formulario de consulta y tabla de prospectos guardados. |
| Consulta y administración | Oracle SQL Developer Web | Ejecución del DDL, carga de datos y validación de tablas y vistas. |

### 7.1.4. Criterios de evaluación

| Métrica o criterio | Descripción | Uso en el proyecto |
|---|---|---|
| Inercia | Mide la suma de distancias de las observaciones respecto a su centroide. | Apoyó la selección del número de clusters mediante el método del codo. |
| Silhouette Score | Evalúa cohesión interna del cluster y separación frente a otros clusters. | Permitió comparar soluciones con distintos valores de K. |
| Davies-Bouldin | Evalúa la relación entre dispersión interna y separación entre grupos. | Se usó como criterio complementario; valores menores indican mejor separación. |
| Tamaño de cluster | Revisa que los grupos no sean demasiado pequeños o poco accionables. | Evitó seleccionar soluciones con clusters espurios o dominados por outliers. |
| Validación externa con `ES_CLIENTE_FPA` | Cruza los segmentos con presencia histórica de clientes FPA. | Permitió interpretar afinidad comercial posterior al entrenamiento. |
| Adjusted Rand Index (ARI) | Mide concordancia entre dos agrupaciones. | Se usó para comparar la estructura de Capa 1 y Capa 2. |
| Usabilidad del prototipo | Evalúa si el resultado puede ser interpretado por usuarios no técnicos. | Se materializó mediante etiquetas de prioridad y visualizaciones en APEX. |

### 7.1.5. Diseño funcional de la solución

El diseño funcional se estructuró lógicamente en tres módulos principales:

*   **Módulo de Resolución de Entidades:** Cuyo propósito fue convertir registros internos con nombres comerciales variables en una base unificada por RUC. Este módulo permitió que los datos públicos del SRI y SCVS pudieran integrarse de forma confiable con la información interna de FPA.
*   **Módulo de Clustering de dos capas:** La Capa 1 se diseñó con variables tributarias y firmográficas, ofreciendo mayor cobertura para segmentar empresas con información básica oficial. La Capa 2 se diseñó como enriquecimiento financiero, incorporando ingresos, empleados, activos, liquidez y margen operacional para las empresas con información disponible en la SCVS.
*   **Módulo de Presentación e Inferencia en APEX:** Para evitar recalcular el modelo estadístico en cada consulta del usuario, el prototipo utiliza vistas SQL predictivas derivadas del perfilamiento de clústeres. Esta capa funciona como un *Surrogate Model* orientado a garantizar una consulta web de baja latencia y proporcionar reglas comerciales explicables.

## 7.2. Desarrollo de la solución

### 7.2.1. Descripción de los datos

| Componente analítico | Tipo de variable | Descripción | Cobertura |
|---|---|---|---:|
| Identificadores base | Categórica nominal | RUC, razón social y alias consolidados en el Golden Record. | 181 empresas |
| Capa 1: formalidad tributaria | Binaria | Tipo de sociedad, obligado a llevar contabilidad, agente de retención, contribuyente especial y estado activo. | 181 empresas |
| Capa 1: madurez empresarial | Continua | Antigüedad de la empresa calculada a partir de la fecha de inicio de actividades. | 181 empresas |
| Capa 1: sector y región | Categórica codificada | Macrosector CIIU y región principal de operación. | 181 empresas |
| Capa 2: escala financiera | Continua transformada | Ingresos, empleados y activos reportados en SCVS. | 141 empresas |
| Capa 2: indicadores financieros | Continua | Liquidez corriente y margen operacional. | 141 empresas |
| Validación externa | Binaria | Indicador de si la empresa aparece como cliente FPA en registros internos de proyectos. | 181 empresas |

La base analítica del proyecto se construyó a partir de fuentes internas de leads y proyectos de FPA, enriquecidas con información pública del Servicio de Rentas Internas y de la Superintendencia de Compañías, Valores y Seguros. El resultado fue un Golden Record de 181 empresas con RUC ecuatoriano verificado. Sobre esta base se generaron dos capas analíticas: la Capa 1, basada en atributos tributarios y firmográficos del SRI, y la Capa 2, basada en información financiera disponible en la SCVS para 141 empresas.

### 7.2.2. Preprocesamiento resumido

- Se normalizaron nombres comerciales, razones sociales y alias para reducir diferencias por mayúsculas, signos, abreviaturas y sufijos legales.
- Se estandarizó el RUC como identificador principal de 13 caracteres, evitando tratarlo como número.
- Se eliminaron duplicados y se consolidaron registros equivalentes dentro del Golden Record.
- Se integraron atributos oficiales del SRI para caracterizar formalidad tributaria, sector, región y antigüedad.
- Se integró información financiera de la SCVS para empresas con balances disponibles.
- Se codificaron variables categóricas no ordinales mediante representaciones binarias.
- Se aplicaron transformaciones logarítmicas a variables financieras para reducir asimetrías extremas.
- Se escalaron variables numéricas para evitar que variables de mayor magnitud dominaran la distancia euclidiana usada por K-Means.
- Se exportaron artefactos intermedios y finales para su carga en Oracle Autonomous Database.

### 7.2.3. Alternativas técnicas evaluadas

| Alternativa técnica | Ventajas | Desventajas | Decisión |
|---|---|---|---|
| K-Means | Eficiente, interpretable mediante centroides, compatible con scikit-learn y Oracle Machine Learning, adecuado para segmentación comercial. | Requiere seleccionar K previamente y es sensible a escala de variables y valores atípicos. | Seleccionado como modelo principal. |
| Clustering jerárquico Ward | Útil para exploración visual mediante dendrogramas y comparación de estructuras. | Menos conveniente para despliegue operativo y menos eficiente para inferencia rápida. | Usado como apoyo exploratorio, no como modelo final. |
| Modelo surrogate en SQL | Permite responder rápidamente desde APEX y explicar reglas de prioridad al usuario. | No reemplaza al entrenamiento original; depende de reglas derivadas del perfilamiento. | Seleccionado como capa operativa del buscador. |

### 7.2.4. Justificación de la alternativa seleccionada

La solución final adoptó K-Means en dos capas. En la Capa 1 se seleccionó K=4, ya que ofrecía una segmentación más útil para negocio que soluciones más agregadas. En la Capa 2 se seleccionó K=2, porque presentaba mayor estabilidad y evitaba generar grupos demasiado pequeños influenciados por valores financieros atípicos. Los segmentos resultantes fueron posteriormente interpretados y nombrados de forma comprensible para usuarios no técnicos.

K-Means fue seleccionado por su equilibrio entre rendimiento técnico e interpretabilidad. Para un proyecto aplicado a prospección comercial, no bastaba con generar grupos matemáticos: era necesario que estos pudieran traducirse en perfiles comprensibles por el equipo comercial. La estructura basada en centroides facilitó interpretar los segmentos y convertirlos en reglas de prioridad dentro del prototipo.

### 7.2.5. Uso de herramientas low-code/no-code

Oracle APEX se utilizó como herramienta low-code para construir la interfaz del MVP sin desarrollar una aplicación web tradicional desde cero. Esta decisión permitió crear una solución navegable con autenticación, dashboard, reportes, formularios, botones y tablas conectadas directamente a Oracle Autonomous Database.

El prototipo final se implementó bajo el nombre “B2B Segmentación MVP”. La aplicación incluye una pantalla de autenticación, un dashboard principal, gráficos de distribución, una visualización de dispersión financiera, un buscador de empresas por RUC y una tabla de prospectos guardados. El objetivo de esta interfaz es que un usuario comercial pueda consultar una empresa, conocer su segmento y visualizar su nivel de prioridad sin ejecutar notebooks ni manipular archivos técnicos.

### 7.2.6. Arquitectura del prototipo

| Capa de arquitectura | Componente tecnológico | Función dentro del MVP |
|---|---|---|
| Fuentes de datos | Leads, proyectos, SRI y SCVS | Proveen datos internos y públicos para construir la base analítica. |
| Procesamiento local | Python/Jupyter | Limpieza, Golden Record, feature engineering, entrenamiento y evaluación. |
| Persistencia cloud | Oracle Autonomous Database | Almacena tablas oficiales, features, clusters, métricas y vistas de consulta. |
| Experimentación cloud | Oracle Machine Learning | Permite probar el entrenamiento K-Means dentro del entorno Oracle y comparar resultados. |
| Modelo surrogate | Vistas SQL y reglas de prioridad | Traduce el perfilamiento de clusters en respuestas rápidas para el buscador. |
| Presentación | Oracle APEX | Expone dashboard, buscador por RUC y mini-CRM de prospectos guardados. |

Como parte del despliegue, se creó una base Oracle Autonomous Database en OCI. En esta base se definieron tablas para almacenar el Golden Record, variables, clusters, métricas de validación y datos oficiales del SRI y SCVS. También se construyeron vistas orientadas al consumo por APEX, incluyendo una vista predictiva que traduce los resultados del modelo en reglas de priorización comercial. Esta vista funciona como un modelo surrogate: no recalcula K-Means en cada consulta, sino que aplica reglas derivadas del perfilamiento de los clusters para responder rápidamente al usuario.

Oracle Machine Learning se utilizó como una fase de experimentación y validación en nube. En el notebook de OML se realizaron pruebas para entrenar modelos K-Means dentro del entorno Oracle y comparar sus asignaciones con los resultados locales. Durante este proceso se identificó que la preparación automática de datos de OML podía generar diferencias frente al pipeline local, por lo que el modelo local validado en Python se mantuvo como referencia principal para el MVP. Esta decisión permitió conservar trazabilidad metodológica y evitar inconsistencias entre motores de procesamiento.

### 7.2.7. Evidencia visual del sistema

**[Insertar Figura 7.3: Pantalla de login del sistema]**

Comentario sugerido bajo la figura:  
La figura muestra la pantalla de autenticación del prototipo desplegado en Oracle APEX. Esta evidencia permite demostrar que la solución fue implementada como una aplicación web en la nube con acceso controlado por usuario y contraseña, y no únicamente como un análisis local.

**[Insertar Figura 7.4: Dashboard principal en Oracle APEX]**

Comentario sugerido bajo la figura:  
La figura presenta la página principal del MVP, donde se resumen los indicadores del modelo: empresas del Golden Record, cantidad de clusters por capa y métrica ARI. Además, se muestran gráficos de distribución que permiten interpretar visualmente la composición de los segmentos.

**[Insertar Figura 7.5: Gráfico de dispersión financiera]**

Comentario sugerido bajo la figura:  
La figura muestra la relación entre ingresos y empleados para las empresas analizadas. Esta visualización permite identificar diferencias de escala económica y complementa la interpretación de la Capa 2 financiera.

**[Insertar Figura 7.6: Buscador predictivo de empresas]**

Comentario sugerido bajo la figura:  
La figura evidencia la funcionalidad principal del prototipo. Al ingresar un RUC, el sistema devuelve la razón social, estado tributario, ingresos, empleados, segmento tributario, segmento financiero y nivel de prioridad. En el ejemplo mostrado, la empresa consultada aparece como “Foco Alto”, lo que convierte el resultado analítico en una recomendación comercial accionable.

**[Insertar Figura 7.7: Prospectos guardados]**

Comentario sugerido bajo la figura:  
La figura muestra la funcionalidad de guardado de prospectos. Esta sección actúa como un mini-CRM dentro del prototipo, permitiendo conservar empresas consultadas y revisar posteriormente su segmentación y prioridad comercial.

**[Insertar Figura 7.8: Page Designer de Oracle APEX]**

Comentario sugerido bajo la figura:  
La figura documenta la construcción low-code del prototipo en Oracle APEX. Se observan regiones, botones, campos de entrada y reportes configurados desde el diseñador visual, lo que evidencia que la solución fue implementada como una aplicación funcional conectada directamente a la base de datos.

**[Insertar Figura 7.9: Notebook de Oracle Machine Learning]**

Comentario sugerido bajo la figura:  
La figura evidencia la fase de experimentación en Oracle Machine Learning. En esta etapa se realizaron pruebas para trasladar la lógica de clustering al entorno Oracle y comparar los resultados obtenidos con el modelo local validado en Python.

## 7.3. Resultados y discusión

El proyecto logró convertir información comercial dispersa en una solución analítica funcional para priorización de prospectos B2B. El primer resultado relevante fue la construcción de un Golden Record de 181 empresas con RUC verificado. Este paso fue fundamental, ya que permitió pasar de registros comerciales no estandarizados a una base estructurada y trazable.

| Indicador | Resultado |
|---|---:|
| Empresas en Golden Record | 181 |
| Empresas modeladas en Capa 1 | 181 |
| Empresas modeladas en Capa 2 | 141 |
| Clusters seleccionados en Capa 1 | 4 |
| Clusters seleccionados en Capa 2 | 2 |
| Segmento más relevante | Industriales consolidados de alta afinidad FPA |
| Tasa de clientes FPA en segmento principal | 65,7% |

En términos de modelado, la Capa 1 identificó cuatro segmentos empresariales basados en información tributaria, sectorial y geográfica. El segmento más relevante fue “Industriales consolidados de alta afinidad FPA”, que concentró 35 empresas, de las cuales 23 correspondían a clientes FPA. Esto representa una tasa histórica de clientes de 65,7%, superior a la tasa base de la capa. Este hallazgo sugiere que ciertas características de formalidad, madurez y sector económico están asociadas con mayor afinidad comercial.

La Capa 2, basada en información financiera, identificó dos segmentos principales. Aunque esta capa aportó una lectura complementaria sobre escala económica, la diferencia en afinidad comercial fue menos marcada que en la Capa 1. La comparación entre capas mediante ARI mostró baja concordancia, lo cual no se interpreta como un error, sino como evidencia de que las variables tributarias y financieras capturan dimensiones distintas del universo empresarial.

Desde el punto de vista funcional, el MVP permitió exponer los resultados del modelo en una aplicación web. El usuario puede ingresar un RUC, consultar el perfil de la empresa, observar su segmento y obtener una prioridad comercial. La clasificación en niveles como “Foco Alto”, “Foco Medio”, “Foco Bajo” o “Cliente Actual” facilita la adopción por parte de usuarios no técnicos, ya que traduce el resultado algorítmico en una acción comercial comprensible.

La principal fortaleza de la solución es su trazabilidad: los resultados mostrados en APEX provienen de tablas, vistas y artefactos generados por el pipeline. Además, la implementación en Oracle APEX reduce la barrera de uso, ya que el usuario final no necesita conocer Python, K-Means ni SQL para interactuar con el modelo. Como limitación, el MVP no se encuentra conectado en tiempo real al CRM ni a APIs oficiales; la actualización de datos requiere ejecutar nuevamente el pipeline y recargar la información en Oracle.

## 7.4. Implicaciones éticas

El proyecto utiliza datos empresariales y fuentes públicas oficiales, no datos personales sensibles. Sin embargo, existen implicaciones éticas relacionadas con el uso de modelos analíticos para orientar decisiones comerciales. La primera consideración es la privacidad: el sistema trabaja con RUC, razón social, atributos tributarios y financieros de empresas, evitando incorporar información personal de representantes, contactos, teléfonos o correos en el entrenamiento del modelo.

La segunda consideración es el riesgo de sesgo comercial. Si el usuario interpreta el nivel de prioridad como una verdad absoluta, podría descuidar empresas nuevas, pequeñas o pertenecientes a sectores con menor representación histórica. Por ello, el modelo debe entenderse como una herramienta de apoyo a la decisión y no como un mecanismo automático de exclusión.

La tercera consideración es la transparencia. Los segmentos generados fueron interpretados y documentados, y las reglas de priorización se implementaron en vistas de base de datos trazables. Esto permite explicar por qué una empresa recibe determinado nivel de prioridad y reduce el riesgo de operar como una “caja negra”.

Finalmente, la solución requiere controles de acceso adecuados, ya que la información de prospectos y priorización comercial puede considerarse sensible para la empresa. El uso de autenticación en Oracle APEX contribuye a limitar el acceso al prototipo, aunque en una futura versión productiva sería necesario complementar este mecanismo con roles de usuario, auditoría de consultas y políticas formales de seguridad de la información.
