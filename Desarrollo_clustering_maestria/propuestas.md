# [cite_start]1. Análisis de posibles soluciones [cite: 1]

## 1.1. [cite_start]Identificación y selección de la mejor solución [cite: 2]

[cite_start]Con el fin de abordar la priorización subjetiva y la falta de segmentación analitica en el pipeline de ventas de FPA Financial Planning & Analytics, se han planteado dos alternativas técnicas basadas en inteligencia artificial y análisis de datos: [cite: 3]

* [cite_start]**Propuesta A: Segmentación de oportunidades mediante clustering (Aprendizaje No Supervisado).** Esta alternativa busca identificar patrones latentes en los datos históricos (industria, cargo, pais, revenue, etc.) para agrupar los leads en segmentos homogéneos de forma automática. [cite: 4] [cite_start]Utiliza algoritmos como K-Means o clustering jerárquico para descubrir estructuras no evidentes, permitiendo asignar perfiles de prioridad (alto, medio o bajo foco) basados en la similitud de datos. [cite: 5] [cite_start]Es una solución innovadora que maximiza el descubrimiento de conocimiento en datasets que carecen de etiquetas históricas consistentes. [cite: 6]
* [cite_start]**Propuesta B: Priorización de oportunidades mediante scoring heurístico.** Consiste en el desarrollo de un motor analítico que aplica reglas de negocio ponderadas y estadística descriptiva sobre el mismo conjunto de datos. [cite: 7] [cite_start]Aunque permite un ranking claro y es altamente interpretable, su capacidad de descubrimiento se limita a criterios ya conocidos por el equipo experto, sin explotar el potencial de patrones ocultos en la información. [cite: 8]

### [cite_start]Sustentación de la selección (ISO/IEC 25010) [cite: 9]

[cite_start]Para determinar la alternativa tecnológica más adecuada para la problemática de priorización de leads de FPA Latam Ecuador, se aplicó el estándar internacional ISO/IEC 25010:2023, que define el modelo de calidad del producto de software y sus características evaluables. [cite: 10] [cite_start]Dicho eståndar establece que la calidad de un sistema de software debe analizarse desde múltiples dimensiones que contemplen tanto la adecuación funcional como los atributos de calidad no funcionales que determinan su viabilidad de implementación y sostenibilidad en el tiempo (ISO/IEC, 2023). [cite: 11] [cite_start]Se evaluaron dos propuestas alternativas de solución analítica: [cite: 12]

1.  [cite_start]**Propuesta A- Módulo Analitico de Clustering (Aprendizaje No Supervisado):** Sistema basado en algoritmos de segmentación automática (K-Means y clustering jerárquico) que agrupa los leads en perfiles de prioridad según sus características multivariadas, sin requerir etiquetas históricas supervisadas. [cite: 13] [cite_start]Genera perfiles interpretables de 'alta prioridad', 'prioridad media' y 'seguimiento mínimo' con métricas de validación interna (Silhouette Score, Davies-Bouldin Index), integrando los resultados en Oracle Autonomous Database y Oracle APEX. [cite: 14] [cite_start]**Objetivo:** Identificar patrones latentes en oportunidades comerciales históricas mediante técnicas de aprendizaje no supervisado, con el fin de segmentar las oportunidades en grupos homogéneos que sirvan como guía objetiva para la priorización comercial. [cite: 15, 17]
    > [cite_start]Comentado [DLVG1]: oscar [cite: 16]
    * [cite_start]**Alcance funcional:** Esta propuesta contempla la consolidación y limpieza de datos históricos, la aplicación de algoritmos de clustering, la interpretación de los grupos obtenidos y la asignación de nuevas oportunidades al cluster más cercano. [cite: 18] [cite_start]Los clusters resultantes se interpretan y se asocian a perfiles de prioridad (alto, medio o bajo foco), definidos con apoyo del criterio del equipo comercial. [cite: 19]
    * [cite_start]**Arquitectura y tecnologias:** La propuesta utiliza Oracle Autonomous Database para el almacenamiento estructurado de datos y resultados del modelo, scripts de Python para el procesamiento y modelado analítico, y Oracle APEX como interfaz web de visualización interactiva. [cite: 20]
    
    [cite_start]![Figura 1 Modelo de Contexto C4 - Nivel 1 (Propuesta A: Clustering)](ruta-de-la-imagen-1.png) [cite: 33]

2.  [cite_start]**Propuesta B Módulo de Scoring Heuristico:** Sistema basado en reglas de negocio ponderadas definidas por el equipo experto de FPA. [cite: 34] [cite_start]Calcula un puntaje compuesto por lead en función de variables como industria, tamaño de empresa, ERP instalado y urgencia declarada, generando un ranking de priorización directamente interpretable sin requerir procesamiento estadístico avanzado. [cite: 35] [cite_start]**Objetivo:** Asignar una prioridad a las oportunidades comerciales mediante un sistema de puntuación basado en reglas de negocio y estadística descriptiva, utilizando el mismo conjunto de datos históricos estructurados. [cite: 36]
    * [cite_start]**Alcance funcional:** Esta propuesta incluye la definición de reglas ponderadas, el cálculo de un puntaje total por oportunidad y la clasificación en niveles de prioridad. [cite: 37] [cite_start]El resultado es un ranking de oportunidades que apoya la toma de decisiones, basado en criterios explícitos y fácilmente interpretables. [cite: 38]
    * [cite_start]**Arquitectura y tecnologias:** La arquitectura es equivalente a la Propuesta A, diferenciándose únicamente en el motor analitico, que aplica reglas y cálculos estadísticos en base de datos en lugar de técnicas de aprendizaje automático. [cite: 39]

    [cite_start]![Figura 2 Modelo de Contexto C4 - Nivel 1 (Propuesta B: Scoring)](ruta-de-la-imagen-2.png) [cite: 45]

[cite_start]A continuación, se presenta el análisis cualitativo comparativo basado en los criterios del estándar ISO/IEC 25010:2023: [cite: 46]

| CRITERIO | PROPUESTA A CLUSTERING | PROPUESTA B SCORING HEURÍSTICO | JUSTIFICACIÓN |
| :--- | :--- | :--- | :--- |
| **Funcionalidad Analítica** | Identifica patrones no evidentes en datos históricos de leads sin necesidad de etiquetas. Genera segmentos con coherencia estadistica validada. [cite_start]Detecta perfiles de oportunidad estratégica invisibles al análisis humano subjetivo. [cite: 47] | Aplica reglas de negocio explícitas definidas por el equipo experto. Genera un score directo e interpretable. [cite_start]Su alcance analítico está limitado por el conocimiento previo del equipo, no por los datos. [cite: 47] | [cite_start]El clustering supera al scoring en capacidad de descubrimiento no guiado de patrones, particularmente relevante cuando no existe etiquetación histórica consistente (Sarikaya & Yilmaz, 2024). [cite: 47] |
| **Usabilidad** | Los resultados requieren interpretación técnica de los centroides de cada cluster. La traducción a perfiles comerciales comprensibles exige documentación adicional. [cite_start]La interfaz interactiva de Oracle APEX mitiga esta complejidad al presentar los resultados de forma visual. [cite: 47, 48] | Los resultados son directamente comprensibles: un número de score y un ranking. Curva de aprendizaje mínima. [cite_start]Adoptable por cualquier consultor comercial sin entrenamiento técnico específico. [cite: 47, 48] | El scoring es superior en usabilidad inmediata. [cite_start]El clustering requiere un esfuerzo de interpretación inicial que se facilita con herramientas visuales como Oracle APEX (Molnar, 2022). [cite: 47, 48] |
| **Fiabilidad** | Los resultados son matemáticamente consistentes dado el mismo conjunto de datos. [cite_start]La fiabilidad depende críticamente de la calidad del preprocesamiento y de la estabilidad de los parámetros del modelo (k, métrica de distancia). [cite: 48] | Alta fiabilidad en la aplicación de las reglas. Sin embargo, la calidad del output depende de la validez de las reglas definidas. [cite_start]Riesgo de capturar sesgos del equipo experto en el modelo. [cite: 48] | [cite_start]Ambas propuestas presentan niveles equiparables de fiabilidad, condicionados por factores diferentes: calidad del dato vs. calidad de las reglas. [cite: 48] |
| **Mantenibilidad** | Requiere reentrenamiento periódico del modelo ante cambios en el perfil del pipeline. Demanda competencias en ciencia de datos para ajustar parámetros y actualizar los datos en la base de datos Oracle. [cite: 48, 49] | Reglas actualizables directamente por el equipo de negocio sin intervención técnica especializada. Menor dependencia tecnológica. [cite_start]Adaptación ágil ante cambios en la estrategia comercial. [cite: 48, 49] | El scoring presenta ventaja clara en mantenibilidad. [cite_start]Los cambios en el modelo de negocio se traducen en ajustes de reglas, no en reentrenamiento estadístico ni procesamiento de datos (Sommerville, 2021). [cite: 48, 49] |
| **Costo y Tiempo de Implementación** | Mayor tiempo de desarrollo por la fase de experimentación algoritmica, validación de métricas y proceso de integración entre Python y Oracle Cloud. [cite_start]Mayor inversión inicial de esfuerzo técnico. [cite: 49] | Menor tiempo de implementación. [cite_start]El diseño del modelo de pesos y la codificación del scoring son tareas realizables directamente en la base de datos con participación del equipo comercial. [cite: 49] | El scoring tiene ventaja en eficiencia de implementación. [cite_start]El clustering requiere mayor inversión técnica inicial, pero su retorno analítico es superior a largo plazo al escalar. [cite: 49] |

[cite_start]*Tabla 1. Análisis Cualitativo de las Alternativas* [cite: 50]
*Nota. Análisis cualitativo elaborado en base a los criterios del estándar ISO/IEC 25010:2023.* [cite: 51] [cite_start]*Adaptado de Molnar (2022), Sarikaya y Yilmaz (2024) y Sommerville (2021).* [cite: 52]

[cite_start]A continuación, se presenta la tabla de evaluación cuantitativa ponderada, donde se asignó a cada criterio un peso relativo de acuerdo con su importancia estratégica para el contexto de FPA Ecuador, y se calificó cada propuesta en una escala del 1 al 5: [cite: 53]

| CRITERIO ISO/IEC 25010 | PESO (%) | PROP. A CLUSTERING | PROP. B SCORING | POND. A | POND. B |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Funcionalidad Analítica** | 35% | 5 | 3 | 1.75 | 1.05 |
| **Usabilidad** | 15% | 4 | 5 | 0.60 | 0.75 |
| **Fiabilidad** | 15% | 4 | 4 | 0.60 | 0.60 |
| **Mantenibilidad** | 10% | 4 | 5 | 0.40 | 0.50 |
| **Costo y Tiempo de Implementación** | 15% | 3 | 5 | 0.45 | 0.75 |
| **Integración con infraestructura existente** | 10% | 5 | 4 | 0.50 | 0.40 |
| **RESULTADO PONDERADO TOTAL** | **100%** | | | **4.30** | **4.05** |

[cite_start]*Tabla 2. Análisis Cuantitativo Ponderado* [cite: 54, 55, 56, 57, 58, 59]
*Nota. Escala de evaluación: 1 = Muy deficiente, 2 = Deficiente, 3 = Aceptable, 4 = Bueno, 5 = Excelente. [cite_start]Elaboración propia con base en ISO/IEC 25010 (2023).* [cite: 60, 61]

### Conclusión de la Selección [cite: 62]

Con base en el análisis cuantitativo ponderado, la Propuesta A (Módulo de Clustering) obtiene un resultado ponderado de 4.30, frente a 4.05 de la Propuesta B (Scoring Heurístico), constituyéndose como la alternativa técnicamente superior para los objetivos analíticos del proyecto. [cite: 63] La diferencia se explica principalmente por la ventaja significativa del clustering en el criterio de Funcionalidad Analítica (peso del 35%), que es el criterio de mayor impacto estratégico dado el objetivo de identificar patrones no obvios en el pipeline de leads históricos, además de su alineación nativa con la infraestructura de Oracle Cloud. [cite: 64] 

Sin embargo, reconociendo las limitaciones del clustering en términos de usabilidad inicial, la arquitectura propuesta mitiga estas barreras implementando Oracle APEX como capa de presentación, permitiendo al equipo comercial explorar los segmentos estratégicos de manera intuitiva y visual. [cite: 65]

**Decisión:** Se selecciona la Propuesta A (Clustering). Esta elección se fundamenta en su superioridad en funcionalidad analítica, ya que permite transformar datos desordenados en información útil mediante el descubrimiento de patrones, alineándose con los objetivos académicos de investigación en IA y aportando un mayor valor tecnológico a la organización mediante una arquitectura en la nube moderna y escalable. [cite: 66]

---

## Descripción de los Módulos Analíticos [cite: 67]

### Módulo Analítico de Priorización de Oportunidades - Clustering [cite: 68]

El módulo de clustering constituye el componente de aprendizaje no supervisado del sistema analítico. [cite: 69] Su propósito central es identificar grupos naturales (clusters) de leads con características similares en el histórico del pipeline de FPA Ecuador, sin requerir etiquetas predefinidas de resultado comercial. [cite: 70] A continuación se describe cada elemento de la arquitectura funcional de este módulo: [cite: 71]

#### Archivo Histórico en Excel (CSV) - Fuente de Datos Crudos [cite: 72]
El punto de entrada del sistema es el archivo histórico de leads exportado del CRM o procesado manualmente, almacenado en formato CSV, enriquecido con fuentes oficiales como el SRI y SCVS. [cite: 73] Este archivo contiene los registros de oportunidades comerciales con atributos firmográficos y financieros. [cite: 74, 75] Esta fuente de datos representa el 'data lake' primario del proyecto. [cite: 76] De acuerdo con Molnar (2022), la fase de ingesta y preprocesamiento es la más crítica en cualquier pipeline de aprendizaje automático, pues los errores en esta etapa se amplifican posteriormente. [cite: 77]

#### Usuario Analista / Consultor Comercial - Actor Principal [cite: 78]
El usuario analista es el profesional de FPA responsable de interpretar los resultados de la segmentación. [cite: 79] Este actor consume los insights a través de los perfiles de cluster para la toma de decisiones comerciales. [cite: 80] La interfaz interactiva en Oracle APEX está diseñada específicamente para reducir la curva de aprendizaje de este perfil de usuario, eliminando la necesidad de conocimientos técnicos en ciencia de datos. [cite: 81]

#### Scripts de Preparación y Modelado en Python - Motor Analítico [cite: 82, 83]
Este es el componente de procesamiento de machine learning. Integra funciones secuenciales que constituyen el pipeline analítico offline: [cite: 84]
* [cite_start]**Consolidación "Golden Record":** Limpieza y estructuración de datos para garantizar la calidad mediante imputación, normalización de variables numéricas y codificación. [cite: 85, 86]
* [cite_start]**Ejecución de clustering:** Aplicación del algoritmo K-Means con determinación del número óptimo de clusters ($K$) evaluado estadísticamente mediante métricas internas (Silhouette Score, Davies-Bouldin Index). [cite: 87]
* [cite_start]**Generación de Data Marts:** Exportación de las predicciones y perfiles de los clústeres en archivos optimizados (formato CSV segmentado) preparados para su carga a la base de datos productiva en la nube. [cite: 89, 90]

#### [cite_start]Oracle Autonomous Database - Persistencia Estructurada [cite: 101]
[cite_start]La base de datos Oracle en la nube (OCI) almacena tanto los datos históricos procesados ("Golden Record") como los resultados de la segmentación generada por el modelo de Python. [cite: 102] [cite_start]Actúa como el núcleo de persistencia integrado que alimenta directamente las vistas y paneles de control, garantizando alta disponibilidad, seguridad y consultas de alto rendimiento gracias a su motor autónomo. [cite: 103]

#### [cite_start]Oracle APEX - Interfaz Web Interactiva [cite: 91]
[cite_start]Oracle APEX actúa como la capa de presentación front-end del sistema. [cite: 92] [cite_start]Permite al usuario visualizar los resultados de la segmentación mediante dashboards de indicadores clave (KPIs), gráficos estadísticos y reportes interactivos navegables. [cite: 93] [cite_start]Su elección como interfaz está fundamentada en su naturaleza "low-code" e integración totalmente nativa con Oracle Autonomous Database, lo que permite un despliegue ágil, seguro e inmediato en la nube sin requerir el mantenimiento de servidores web independientes ni APIs intermedias (Oracle, 2023). [cite: 94, 96]
> [cite_start]Comentado [DLVG2]: Validar Oscar [cite: 95]

---

### [cite_start]Módulo Analitico de Priorización de Oportunidades - Scoring Heuristico [cite: 104]

[cite_start]El módulo de scoring heurístico constituye el componente de reglas de negocio propuesto como alternativa. [cite: 105] [cite_start]Su propósito es calcular un puntaje de prioridad para cada lead en función de variables predefinidas y ponderaciones establecidas por el equipo experto de FPA, generando un ranking operativo de oportunidades directamente accionable. [cite: 106] [cite_start]A diferencia del módulo de clustering, su lógica de decisión es determinística. [cite: 107]

#### [cite_start]Archivo Histórico en Excel (CSV) - Fuente de Datos [cite: 108]
[cite_start]Al igual que en el módulo de clustering, la fuente de datos primaria es el archivo CSV de leads. [cite: 109] [cite_start]El preprocesamiento se orienta específicamente a la normalización de las variables incluidas en el modelo de scoring. [cite: 110, 111]

#### [cite_start]Motor de Reglas en Base de Datos - Scoring Heuristico Núcleo Funcional [cite: 112]
[cite_start]El núcleo de este módulo integra funciones que constituyen el pipeline de scoring directamente sobre los datos estructurados: [cite: 112]
> [cite_start]Comentado [DLVG3]: Borrar? [cite: 114]
* [cite_start]**Cálculo de reglas ponderadas:** Cálculo del score compuesto para cada lead mediante la función: Score = (Peso_variable_i x Valor_normalizado_i). [cite: 116] 
* [cite_start]**Generación de ranking:** Normalización del score compuesto a una escala de 0 a 100, clasificación de leads en categorías de prioridad y generación del ranking final evaluado mediante sentencias y vistas SQL. [cite: 118]

#### [cite_start]Oracle APEX - Interfaz de Scoring [cite: 119, 120]
[cite_start]La visualización de este ranking se implementaría directamente como un reporte tabular en Oracle APEX, permitiendo a los usuarios ordenar las oportunidades por su puntaje heurístico, garantizando un mantenimiento ágil y nula dependencia de infraestructuras analíticas externas. [cite: 122, 123]

### [cite_start]Comparación Funcional entre Módulos [cite: 124]
> [cite_start]Comentado [DLVG4]: Validar si se bora [cite: 125]

| DIMENSIÓN | CLUSTERING | SCORING HEURÍSTICO |
| :--- | :--- | :--- |
| **Tipo de análisis** | [cite_start]Aprendizaje no supervisado [cite: 129, 130] | [cite_start]Reglas de negocio ponderadas [cite: 131, 132] |
| **Requiere etiquetas** | [cite_start]No [cite: 133, 134] | [cite_start]No [cite: 135] |
| **Interpretabilidad** | [cite_start]Media (requiere perfilamiento de clusters) [cite: 136, 137] | [cite_start]Alta (score directo) [cite: 138] |
| **Frecuencia de uso** | [cite_start]Periódico (análisis estratégico) [cite: 139] | [cite_start]Diario (priorización operativa) [cite: 140, 141] |
| **Capacidad de descubrimiento** | [cite_start]Alta (detecta patrones no conocidos) [cite: 142, 145] | [cite_start]Limitada al conocimiento previo [cite: 147] |
| **Mantenimiento requerido** | [cite_start]Reentrenamiento periódico de scripts Python [cite: 143, 144, 146] | [cite_start]Actualización de reglas en BD [cite: 148] |

[cite_start]*Tabla 3. Comparación funcional entre módulos* [cite: 149]
*Nota. [cite_start]Elaboración propia con base en Molnar (2022) y Sarikaya & Yilmaz (2024).* [cite: 150]

---

## 1.2. Impacto del proyecto en la sociedad [cite: 151]

El desarrollo e implementación de este sistema de apoyo a la toma de decisiones genera beneficios significativos bajo un análisis de impacto multidimensional: [cite: 152]

* [cite_start]**Económico:** Mejora la eficiencia operativa de la consultora al reducir significativamente el tiempo de análisis manual de leads (estimado entre 73 y 110 horas acumuladas). [cite: 153] [cite_start]Esto optimiza el uso de recursos y permite una mayor escalabilidad del proceso comercial B2B. [cite: 154]
* [cite_start]**Tecnológico:** Representa un avance en la integración de modelos de Machine Learning en Python con plataformas empresariales robustas "cloud-native" como Oracle Autonomous Database y Oracle APEX. [cite: 155] [cite_start]Sienta las bases para una cultura de decisiones basadas en datos dentro de la organización, fomentando la adopción de arquitecturas analíticas modernas y sin requerir infraestructura física local. [cite: 156]
* [cite_start]**Social y Profesional:** Mitiga la dependencia del conocimiento tácito individual, reduciendo el estrés laboral derivado de la incertidumbre en la toma de decisiones y facilitando la transferencia de conocimiento entre consultores. [cite: 157] [cite_start]A nivel académico, contribuye con metodologias para el tratamiento de datos limitados y heterogéneos en contextos reales de PyMEs. [cite: 158]
* [cite_start]**Ético:** El proyecto se adhiere a principios de IA responsable al garantizar la privacidad de los datos, excluyendo información personal identificable (PII) y manteniendo siempre al ser humano como el decisor final (sistema de apoyo, no de automatización total). [cite: 159]