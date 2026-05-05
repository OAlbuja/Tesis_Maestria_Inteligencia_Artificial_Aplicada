# 4.8 Resultados del modelo de clustering

Esta seccion presenta los resultados obtenidos a partir del notebook `04_modeling/01_clustering.ipynb`, construido sobre las matrices finales exportadas por el pipeline en `03_feature_engineering/outputs`. Los artefactos efectivamente utilizados contienen **163 empresas unicas en Capa 1** y **92 empresas en Capa 2**; por tanto, las cifras reportadas a continuacion corresponden a dichos archivos y no a conteos preliminares de fases anteriores.

Una aclaracion metodologica importante: la Capa 1 parte de 175 filas en el CSV de origen, que tras inspeccion revelaron **12 registros duplicados** (misma empresa presente en las fuentes HORAS y LEADS simultaneamente). Dichos duplicados fueron eliminados antes del modelado conservando una unica fila por RUC; cuando una empresa aparecia en ambas fuentes, se preservo su condicion `es_cliente_fpa = 1` si cualquiera de las dos filas lo indicaba. El universo efectivo de Capa 1 es, por tanto, de **163 empresas unicas**.

El analisis se realizo en dos niveles complementarios. En primer lugar, se estimo un modelo principal sobre la matriz de Capa 1, construida exclusivamente con variables firmograficas del SRI de alta cobertura. En segundo lugar, se ejecuto un analisis de robustez sobre la matriz de Capa 2, que incorpora variables financieras provenientes del ranking de la Superintendencia de Companias para el subconjunto de empresas con informacion economica disponible. En ambos casos, la variable `es_cliente_fpa` se mantuvo fuera del entrenamiento y se utilizo unicamente como criterio de validacion externa posterior.

## 4.8.1 Base analizada

La Tabla 4.x resume el universo finalmente utilizado en la etapa de clustering.

| Capa | Fuente principal | Empresas | Variables del modelo | Clientes FPA | Tasa base de clientes |
|---|---|---:|---:|---:|---:|
| Capa 1 | SRI | 163 | 15 | 49 | 30,1% |
| Capa 2 | SRI + ranking SCVS | 92 | 21 | 36 | 39,1% |

La diferencia entre ambas capas no es trivial. Mientras la Capa 1 representa el universo operativo amplio sobre el cual FPA podria clasificar futuros leads de forma reproducible, la Capa 2 corresponde a un subconjunto mas pequeno y con mayor presencia relativa de clientes actuales. Esta diferencia anticipa la existencia de un sesgo de cobertura que debe considerarse al interpretar los resultados financieros.

## 4.8.2 Seleccion del numero de clusters

La seleccion de `K` se realizo combinando tres criterios: el metodo del codo sobre la inercia intra-cluster, el indice de Silhouette y el indice de Davies-Bouldin. Adicionalmente, se reviso el tamano minimo de los clusters resultantes, con el fin de evitar soluciones artificialmente atractivas desde el punto de vista metrico pero poco defendibles en terminos de interpretacion gerencial.

### Capa 1

| K | Silhouette | Davies-Bouldin | Min cluster | Max cluster |
|---:|---:|---:|---:|---:|
| 2 | 0,256 | 1,394 | 40 | 123 |
| 3 | 0,165 | 1,517 | 20 | 103 |
| **4** | **0,171** | **2,015** | **20** | **59** |
| 5 | 0,181 | 1,818 | 11 | 48 |
| 6 | 0,173 | 1,813 | 11 | 48 |

En la Capa 1, la mejor puntuacion de Silhouette se obtuvo con `K = 2` (`0,256`) y el menor valor de Davies-Bouldin tambien correspondio a esa solucion (`1,394`). Sin embargo, esta particion generaba un esquema excesivamente grueso e imbalanceado, con clusters de 40 y 123 empresas, lo que limitaba su utilidad para segmentacion comercial fina. A medida que `K` aumentaba, la inercia descendia de forma consistente y los tamanos se volvian mas balanceados. Bajo este criterio, **`K = 4`** se selecciono como la solucion de compromiso mas adecuada, ya que produjo cuatro segmentos de tamano comparable, entre 36 y 52 empresas, manteniendo niveles razonables de cohesion y separacion (`Silhouette = 0,171`; `Davies-Bouldin = 2,015`).

En otras palabras, la decision final para Capa 1 no se baso en maximizar una sola metrica, sino en privilegiar la interpretabilidad y la utilidad operativa del modelo. Esta eleccion es consistente con la naturaleza aplicada de la tesis: el objetivo no era obtener la mejor particion matematica posible en sentido abstracto, sino una segmentacion suficientemente estable, interpretable y accionable para el contexto comercial de FPA Latam.

### Capa 2

| K | Silhouette | Davies-Bouldin | Min cluster | Max cluster |
|---:|---:|---:|---:|---:|
| **2** | **0,390** | **1,080** | **35** | **57** |
| 3 | 0,403 | 0,838 | 2 | 57 |
| 4 | 0,414 | 0,662 | 1 | 56 |
| 5 | 0,251 | 0,960 | 1 | 48 |
| 6 | 0,241 | 1,032 | 1 | 48 |

En la Capa 2, la lectura de las metricas fue distinta. Los indicadores internos mejoraban al aumentar `K`: la Silhouette subia de `0,390` en `K = 2` a `0,414` en `K = 4`, mientras Davies-Bouldin bajaba de `1,080` a `0,662`. No obstante, esta mejora se explicaba por la aparicion de clusters diminutos de uno o dos casos, generados por empresas atipicas en sus razones financieras. En `K = 3`, el cluster minimo ya tenia apenas 2 observaciones, y en `K = 4` aparecia un cluster unitario.

Por esta razon, para el analisis principal de robustez se opto por **`K = 2`**, que produce dos grupos sustantivos de 38 y 54 empresas sin aislar outliers como segmentos independientes. De forma complementaria, se corrio una sensibilidad con `K = 4` para evidenciar explicitamente el efecto de estos casos extremos sobre la particion.

## 4.8.3 Resultados del modelo principal en Capa 1

La solucion final de Capa 1 identifico **cuatro segmentos empresariales** con perfiles claramente diferenciados en formalizacion, antiguedad, localizacion y afinidad historica con FPA.

| Cluster | Nombre interpretativo | n | Clientes FPA | Tasa de clientes |
|---|---|---:|---:|---:|
| 0 | Sociedades jovenes de alta afinidad FPA | 38 | 18 | 47,4% |
| 1 | Grandes corporativos maduros establecidos | 52 | 19 | 36,5% |
| 2 | Empresas comerciales de Guayas | 37 | 8 | 21,6% |
| 3 | Personas naturales del resto del pais | 36 | 4 | 11,1% |

La tasa base global de Capa 1 es de **30,1%** (49 clientes sobre 163 empresas).

El **Cluster 0**, denominado *Sociedades jovenes de alta afinidad FPA*, agrupa empresas con una mediana de **8,5 anos de antiguedad**, con constitucion 100% societaria, todas obligadas a llevar contabilidad, y localizacion modal en Pichincha. Su moda sectorial corresponde al macrosector `OTRO` (actividades profesionales, servicios especializados). La tasa de clientes FPA de este grupo alcanza **47,4%**, la mas alta de toda la solucion y muy por encima de la tasa base global, lo que confirma que FPA ha logrado una penetracion especialmente alta entre empresas relativamente recientes y de perfil profesional o tecnico.

El **Cluster 1**, identificado como *Grandes corporativos maduros establecidos*, reune empresas con una mediana de **48 anos de antiguedad**, con 100% de sociedades constituidas, obligadas a llevar contabilidad, con una alta proporcion de agentes de retencion (82,7%) y de contribuyentes especiales (86,5%). Su moda sectorial corresponde al macrosector `C` (industria manufacturera) y su localizacion modal es Pichincha. Su tasa de clientes se ubica en **36,5%**, por encima del promedio global, lo que sugiere que FPA tambien mantiene una presencia significativa en el segmento corporativo mas consolidado y formalizado del pais.

El **Cluster 2**, nombrado *Empresas comerciales de Guayas*, reune empresas con mediana de **12 anos**, formalmente constituidas como sociedades (100%) y en su gran mayoria obligadas a llevar contabilidad (97,3%). Sin embargo, la presencia de agentes de retencion y contribuyentes especiales es considerablemente menor que en los clusters anteriores. Su moda sectorial es `G` (comercio al por mayor y menor) y su localizacion modal es Guayas. La tasa de clientes se ubica en **21,6%**, por debajo del promedio global, lo que indica que este perfil comercial urbano tiene menor afinidad historica con FPA que los segmentos anteriores.

El **Cluster 3**, rotulado como *Personas naturales del resto del pais*, constituye el hallazgo mas distintivo y estructuralmente diferente del modelo. A diferencia de los otros tres grupos, en este cluster **el 91,7% de los registros corresponde a personas naturales** (no a sociedades mercantiles), con una proporcion de obligados a contabilidad de apenas 5,6%, sin agentes de retencion y sin contribuyentes especiales. Solo el 41,7% de las empresas del grupo figura como activa en el SRI. Su localizacion modal es el resto del pais (fuera de Pichincha y Guayas) y su moda sectorial es `G`. La tasa de clientes es de **11,1%**, la mas baja de la solucion y aproximadamente un tercio de la tasa base general. Este segmento representa el perfil con menor penetracion historica para FPA, y su naturaleza --mayoritariamente personas naturales con baja formalizacion-- explica tanto su baja afinidad comercial como su nula cobertura en la capa financiera, segun se desarrolla en la seccion 4.8.6.

En conjunto, los clusters 0 y 1 concentran **37 de los 49 clientes FPA identificados en Capa 1**, es decir, **75,5%** del total de clientes observados, a pesar de representar el **55,2%** de las empresas segmentadas. Este hallazgo sugiere que la mayor parte de la traccion comercial historica de FPA se concentra en dos perfiles concretos: empresas jovenes de perfil profesional con alta afinidad, y grandes corporativos maduros con alta formalizacion tributaria.

## 4.8.4 Resultados del analisis de robustez en Capa 2

Al incorporar variables financieras y de tamano empresarial, la solucion estable de Capa 2 converge en **dos grandes segmentos**.

| Cluster | Nombre interpretativo | n | Clientes FPA | Tasa de clientes |
|---|---|---:|---:|---:|
| 0 | Empresas pequenas y recientes | 38 | 17 | 44,7% |
| 1 | Empresas medianas-grandes consolidadas | 54 | 19 | 35,2% |

El **Cluster 0** reune empresas con mediana de **7 anos de antiguedad**, segmento 1 en la clasificacion empresarial, menor tamano relativo en empleados, ingresos y activos (log_ingresos mediana aprox. 0, log_activos mediana aprox. 4,1), y una mediana de liquidez corriente de **0,84**. A pesar de representar el perfil economico aparentemente mas pequeno, este grupo alcanza la mayor tasa de clientes FPA, con **44,7%**. Este resultado sugiere que una parte importante de la demanda historica de FPA proviene de empresas jovenes o medianamente estructuradas que se encuentran en fases de consolidacion y requieren apoyo para formalizar procesos, tecnologia o gestion.

El **Cluster 1**, por su parte, agrupa firmas con mediana de **40 anos**, mayores niveles de empleo, ingresos y activos (log_ingresos mediana aprox. 7,5, log_activos aprox. 7,5), y una posicion empresarial correspondiente al **segmento 4** (grande). Estas empresas exhiben tambien mayor presencia de agentes de retencion (85,2%) y contribuyentes especiales (90,7%). Su tasa de clientes, aunque ligeramente menor (**35,2%**), sigue estando por encima de la tasa base de Capa 1 y evidencia que FPA tambien participa en el segmento empresarial consolidado.

La lectura mas importante de esta capa no es solamente que existen dos perfiles economicos diferenciados, sino que **ambos concentran una proporcion alta de clientes FPA**. En la muestra financiera, los clientes se distribuyen de forma casi equilibrada entre ambos grupos: **47,2%** en el cluster de empresas pequenas y recientes, y **52,8%** en el cluster de empresas medianas-grandes consolidadas. Esto indica que, cuando se observan las variables economicas, el patron comercial de FPA no se restringe a un unico estrato de tamano, sino que cubre tanto organizaciones en consolidacion como firmas ya maduras.

## 4.8.5 Sensibilidad de Capa 2 y efecto de outliers

La corrida de sensibilidad con `K = 4` en Capa 2 confirmo que las mejoras metricas observadas para valores mayores de `K` respondian principalmente al aislamiento de casos atipicos y no a la aparicion de segmentos economicamente interpretables. En esta solucion surgieron dos clusters pequenos adicionales: uno de **2 empresas** con liquidez corriente extraordinariamente alta (mediana 3.228), y otro de **1 empresa** --Coca-Cola Ecuador-- con margen operacional extremo (4.931). En conjunto, estos micro-clusters no constituyen segmentos de mercado defendibles, sino expresiones de outliers financieros que distorsionan la particion cuando se fuerza una mayor granularidad.

Por ello, la solucion de `K = 2` debe considerarse mas robusta para fines de interpretacion gerencial y comparacion metodologica con la Capa 1.

## 4.8.6 Comparacion entre capas y sesgo de cobertura

### Sesgo de cobertura por cluster de Capa 1

Antes de analizar la concordancia entre modelos, es fundamental examinar que clusters de Capa 1 tienen representacion en Capa 2.

| Cluster Capa 1 | Nombre | n total | n con datos financieros | Cobertura | Tasa FPA |
|---|---|---:|---:|---:|---:|
| 0 | Sociedades jovenes de alta afinidad FPA | 38 | 24 | 63,2% | 47,4% |
| 1 | Grandes corporativos maduros establecidos | 52 | 43 | 82,7% | 36,5% |
| 2 | Empresas comerciales de Guayas | 37 | 25 | 67,6% | 21,6% |
| 3 | Personas naturales del resto del pais | 36 | 0 | **0,0%** | 11,1% |

El hallazgo mas importante es que el **Cluster 3** (*Personas naturales del resto del pais*) tiene **0% de cobertura financiera** en Capa 2: ninguna de sus 36 empresas aparece en el ranking de la SCVS. Esto no es un error del modelo, sino una consecuencia estructural: las personas naturales no estan obligadas a reportar estados financieros a la Superintendencia de Companias, por lo que simplemente no existen en esa fuente. Este cluster de menor afinidad comercial con FPA es tambien el mas invisible para cualquier analisis basado en datos economicos formales.

### Concordancia entre modelos (ARI)

La comparacion entre ambos modelos se realizo sobre las **92 empresas comunes** presentes en Capa 2. Cuando se contrasto la solucion principal de Capa 1 (`K = 4`) con la solucion estable de Capa 2 (`K = 2`), el **Adjusted Rand Index (ARI)** fue de **0,391**. Al repetir el ejercicio con la misma granularidad nominal (`K = 4` en ambas capas), el ARI descendio a **0,340**. En ambos casos, la concordancia puede considerarse **parcial pero sustantiva**, no aleatoria.

### Tabla de correspondencia entre capas (K=4 vs K=2)

| Cluster Capa 1 | Capa 2 grupo 0 (pequenas) | Capa 2 grupo 1 (medianas-grandes) |
|---|---:|---:|
| 0 -- Sociedades jovenes alta afinidad (24 con datos) | 19 | 5 |
| 1 -- Grandes corporativos maduros (43 con datos) | 2 | 41 |
| 2 -- Empresas comerciales Guayas (25 con datos) | 17 | 8 |
| 3 -- Personas naturales (0 con datos) | -- | -- |

Este resultado indica que la informacion financiera no simplemente refina la segmentacion firmografica del SRI, sino que introduce una estructura adicional que redistribuye varias empresas entre grupos. En particular se observan tres patrones:

1. El segmento de **grandes corporativos maduros** de Capa 1 se alinea casi completamente con el cluster de **empresas medianas-grandes consolidadas** de Capa 2: **41 de 43 empresas** (95,3%) con cobertura financiera caen en ese grupo. La coherencia es muy alta.
2. El segmento de **sociedades jovenes de alta afinidad** de Capa 1 se concentra en el cluster de **empresas pequenas y recientes** de Capa 2: **19 de 24 empresas** (79,2%), lo que es consistente con su perfil de menor antiguedad.
3. Las **empresas comerciales de Guayas** se reparten entre ambos clusters financieros con predominio del grupo de pequenas y recientes: **17 de 25 empresas** (68,0%). Este resultado refleja la heterogeneidad interna de ese segmento desde el punto de vista economico.

## 4.8.7 Implicaciones para FPA Latam

Desde una perspectiva aplicada, los resultados permiten derivar al menos tres implicaciones estrategicas.

Primero, el modelo principal de Capa 1 confirma que FPA posee una mayor afinidad historica con dos perfiles muy concretos: **sociedades jovenes de alta afinidad** (47,4% de tasa de clientes) y **grandes corporativos maduros** (36,5%). Estos segmentos deberian constituir el nucleo de una estrategia de priorizacion comercial, ya que concentran tres de cada cuatro clientes observados.

Segundo, el segmento de **personas naturales del resto del pais** presenta la tasa de conversion mas baja (11,1%), nula cobertura financiera en la SCVS y un perfil de muy baja formalizacion tributaria. Esto sugiere que se trata de un perfil en el que FPA o bien no ha desarrollado penetracion comercial efectiva, o bien enfrenta barreras estructurales de acceso, presupuesto o formalizacion. En terminos de gestion comercial, este grupo podria tratarse como un segmento de baja prioridad o como una cartera de desarrollo de largo plazo con una propuesta de valor diferenciada. Su ausencia total en los datos de la SCVS es a la vez una limitacion del analisis y un indicador del nivel de formalidad institucional del segmento.

Tercero, la evidencia de Capa 2 sugiere que, cuando existe informacion economica disponible, FPA atiende tanto a empresas de mayor tamano y madurez como a empresas mas pequenas pero en fases activas de consolidacion. Esto abre una linea de interpretacion relevante para la tesis: la afinidad comercial de FPA no depende exclusivamente del tamano de la empresa, sino del momento organizacional en que esta se encuentra y de su necesidad de profesionalizacion, eficiencia o transformacion.

## 4.8.8 Sintesis de resultados

En sintesis, el ejercicio de clustering permitio identificar una estructura segmentaria clara y accionable dentro del universo de 163 empresas unicas analizadas. El modelo principal, construido con variables SRI de alta cobertura, resulto suficiente para distinguir cuatro perfiles empresariales con distinta afinidad historica hacia FPA: desde sociedades jovenes de perfil profesional con casi la mitad de sus integrantes como clientes actuales, hasta personas naturales de baja formalizacion con una tasa de conversion de apenas uno de cada nueve prospectos. El analisis financiero de robustez confirmo parcialmente esta estructura --especialmente para el perfil corporativo maduro (ARI de concordancia 0,391)-- pero tambien revelo que el subconjunto con datos economicos disponibles esta sesgado estructuralmente: el segmento de menor afinidad y menor formalizacion (personas naturales) es al mismo tiempo el completamente invisible para la SCVS. Por tanto, la contribucion central del modelo no reside solo en haber producido segmentos interpretables, sino en demostrar que la segmentacion firmografica basada en fuentes publicas ya captura una parte sustantiva de la logica comercial de FPA, al tiempo que deja explicitadas sus limitaciones de cobertura y representatividad.

---

## Nota de uso para redaccion final

- Donde dice `Tabla 4.x` puedes insertar la referencia a la tabla del notebook o referenciar directamente los CSVs: `metricas_kmeans_capa1.csv`, `perfil_clusters_capa1.csv`, `cobertura_financiera_por_cluster_capa1.csv`, etc.
- Si el capitulo 4 tiene otra numeracion interna, puedes renombrar esta seccion (`4.4`, `4.5`, etc.) sin tocar el contenido sustantivo.
- Los 12 duplicados eliminados en Capa 1 deben mencionarse en la seccion de preprocesamiento (capitulo 3 o en la apertura del capitulo 4) para que la cifra de 163 quede justificada antes de llegar a esta seccion de resultados.
- El ARI de 0,391 es un resultado solido para justificar la validez cruzada del modelo: no indica identidad entre las dos capas (lo que seria sospechoso) sino una concordancia moderada-alta, coherente con el hecho de que ambas capas miden dimensiones distintas del mismo universo.