# 4.8 Resultados del modelo de clustering

Esta seccion presenta los resultados obtenidos a partir del notebook `04_modeling/01_clustering.ipynb`, construido sobre las matrices finales exportadas por el pipeline en `03_feature_engineering/outputs`. A diferencia de la descripcion metodologica inicial, los artefactos finales disponibles al momento de la ejecucion contienen **175 empresas en Capa 1** y **92 empresas en Capa 2**; por tanto, las cifras reportadas a continuacion corresponden a dichos archivos efectivos y no a los conteos preliminares descritos en fases anteriores del proyecto.

El analisis se realizo en dos niveles complementarios. En primer lugar, se estimo un modelo principal sobre la matriz de Capa 1, construida exclusivamente con variables firmograficas del SRI de alta cobertura. En segundo lugar, se ejecuto un analisis de robustez sobre la matriz de Capa 2, que incorpora variables financieras provenientes del ranking de la Superintendencia de Compañias para el subconjunto de empresas con informacion economica disponible. En ambos casos, la variable `es_cliente_fpa` se mantuvo fuera del entrenamiento y se utilizo unicamente como criterio de validacion externa posterior.

## 4.8.1 Base analizada

La Tabla 4.x resume el universo finalmente utilizado en la etapa de clustering.

| Capa | Fuente principal | Empresas | Variables del modelo | Clientes FPA | Tasa base de clientes |
|---|---|---:|---:|---:|---:|
| Capa 1 | SRI | 175 | 15 | 49 | 28,0% |
| Capa 2 | SRI + ranking SCVS | 92 | 21 | 36 | 39,1% |

La diferencia entre ambas capas no es trivial. Mientras la Capa 1 representa el universo operativo amplio sobre el cual FPA podria clasificar futuros leads de forma reproducible, la Capa 2 corresponde a un subconjunto mas pequeno y con mayor presencia relativa de clientes actuales. Esta diferencia anticipa la existencia de un sesgo de cobertura que debe considerarse al interpretar los resultados financieros.

## 4.8.2 Seleccion del numero de clusters

La seleccion de `K` se realizo combinando tres criterios: el metodo del codo sobre la inercia intra-cluster, el indice de Silhouette y el indice de Davies-Bouldin. Adicionalmente, se reviso el tamaño minimo de los clusters resultantes, con el fin de evitar soluciones artificialmente atractivas desde el punto de vista metrico pero poco defendibles en terminos de interpretacion gerencial.

### Capa 1

En la Capa 1, la mejor puntuacion de Silhouette se obtuvo con `K = 2` (`0,263`) y el menor valor de Davies-Bouldin tambien correspondio a esa solucion (`1,494`). Sin embargo, esta particion generaba un esquema excesivamente grueso e imbalanceado, con clusters de 119 y 56 empresas, lo que limitaba su utilidad para segmentacion comercial fina. A medida que `K` aumentaba, la inercia descendia de forma consistente y los tamaños se volvían mas balanceados. Bajo este criterio, **`K = 4`** se selecciono como la solucion de compromiso mas adecuada, ya que produjo cuatro segmentos de tamaño comparable, entre 37 y 52 empresas, manteniendo niveles razonables de cohesion y separacion (`Silhouette = 0,218`; `Davies-Bouldin = 1,648`).

En otras palabras, la decision final para Capa 1 no se baso en maximizar una sola metrica, sino en privilegiar la interpretabilidad y la utilidad operativa del modelo. Esta eleccion es consistente con la naturaleza aplicada de la tesis: el objetivo no era obtener la mejor particion matematica posible en sentido abstracto, sino una segmentacion suficientemente estable, interpretable y accionable para el contexto comercial de FPA Latam.

### Capa 2

En la Capa 2, la lectura de las metricas fue distinta. Los indicadores internos mejoraban al aumentar `K`: la Silhouette subia de `0,387` en `K = 2` a `0,411` en `K = 4`, mientras Davies-Bouldin bajaba de `1,085` a `0,674`. No obstante, esta mejora se explicaba por la aparicion de clusters diminutos de uno o dos casos, generados por empresas atipicas en sus razones financieras. En `K = 3`, el cluster minimo ya tenia apenas 2 observaciones, y en `K = 4` aparecia un cluster unitario.

Por esta razon, para el analisis principal de robustez se opto por **`K = 2`**, que produce dos grupos sustantivos de 38 y 54 empresas sin aislar outliers como segmentos independientes. De forma complementaria, se corrio una sensibilidad con `K = 4` para evidenciar explicitamente el efecto de estos casos extremos sobre la particion.

## 4.8.3 Resultados del modelo principal en Capa 1

La solucion final de Capa 1 identifico **cuatro segmentos empresariales** con perfiles claramente diferenciados en formalizacion, antiguedad, localizacion y afinidad historica con FPA.

| Cluster | Nombre interpretativo | n | Clientes FPA | Tasa de clientes |
|---|---|---:|---:|---:|
| 0 | Corporativos maduros formalizados | 52 | 19 | 36,5% |
| 1 | Sociedades comerciales de Guayas | 37 | 8 | 21,6% |
| 2 | Empresas menos formalizadas del resto | 43 | 4 | 9,3% |
| 3 | Sociedades formales jovenes de alta afinidad | 43 | 18 | 41,9% |

El **Cluster 0**, denominado *Corporativos maduros formalizados*, agrupa empresas con una mediana de **48 años de antiguedad**, predominio absoluto de sociedades constituidas, obligadas a llevar contabilidad y con alta presencia de agentes de retencion y contribuyentes especiales. Su moda sectorial corresponde al macrosector `C` y su localizacion modal es Pichincha. La tasa de clientes FPA de este grupo alcanza **36,5%**, claramente por encima de la tasa base global de **28,0%**, lo que sugiere una fuerte afinidad de FPA con organizaciones de trayectoria, alto nivel de formalizacion y mayor madurez institucional.

El **Cluster 1**, identificado como *Sociedades comerciales de Guayas*, reune empresas mas jovenes, con mediana de **12 años**, fuertemente concentradas en el sector `G` y geograficamente en Guayas. Aunque la formalizacion juridica sigue siendo alta, la presencia de agentes de retencion y contribuyentes especiales es bastante menor que en el Cluster 0. Su tasa de clientes se ubica en **21,6%**, es decir, por debajo del promedio global. Esto sugiere que, aun dentro de empresas formalmente constituidas, no todo perfil comercial urbano presenta la misma propension historica de compra hacia FPA.

El **Cluster 2**, nombrado *Empresas menos formalizadas del resto*, constituye el hallazgo mas distintivo del modelo principal. Se trata de organizaciones ubicadas principalmente fuera de Guayas y Pichincha, con muy baja proporcion de sociedades mercantiles, practicamente sin obligacion contable, sin condicion de agente de retencion y sin estatus de contribuyente especial. Su tasa de clientes es de apenas **9,3%**, la mas baja de toda la segmentacion y aproximadamente un tercio de la tasa base general. En terminos practicos, este segmento representa el perfil con menor penetracion historica para FPA.

El **Cluster 3**, rotulado como *Sociedades formales jovenes de alta afinidad*, agrupa empresas relativamente recientes, con mediana de **9 años**, formalmente constituidas y contablemente estructuradas, pero sin los niveles de madurez tributaria del Cluster 0. Su localizacion modal es Pichincha y su tasa de clientes alcanza **41,9%**, la mas alta de toda la solucion. Este resultado es especialmente relevante porque indica que FPA no solo ha logrado penetrar empresas corporativas consolidadas, sino tambien sociedades formales mas jovenes que parecen estar en una etapa de crecimiento y profesionalizacion compatible con los servicios de consultoria ofrecidos.

En conjunto, los clusters 0 y 3 concentran **37 de los 49 clientes FPA identificados en Capa 1**, es decir, **75,5%** del total de clientes observados, a pesar de representar el **54,3%** de las empresas segmentadas. Este hallazgo sugiere que la mayor parte de la traccion comercial historica de FPA se concentra en dos perfiles concretos: empresas corporativas maduras y sociedades formales jovenes con señales de profesionalizacion.

## 4.8.4 Resultados del analisis de robustez en Capa 2

Al incorporar variables financieras y de tamaño empresarial, la solucion estable de Capa 2 converge en **dos grandes segmentos**.

| Cluster | Nombre interpretativo | n | Clientes FPA | Tasa de clientes |
|---|---|---:|---:|---:|
| 0 | Empresas pequeñas y recientes | 38 | 17 | 44,7% |
| 1 | Empresas medianas-grandes consolidadas | 54 | 19 | 35,2% |

El **Cluster 0** reune empresas con mediana de **7 años de antiguedad**, **segmento 1** en la clasificacion empresarial, menor tamaño relativo en empleados, ingresos y activos, y una mediana de liquidez corriente de **0,84**. A pesar de representar el perfil economico aparentemente mas pequeño, este grupo alcanza la mayor tasa de clientes FPA, con **44,7%**. Este resultado sugiere que una parte importante de la demanda historica de FPA proviene de empresas jovenes o medianamente estructuradas que se encuentran en fases de consolidacion y requieren apoyo para formalizar procesos, tecnologia o gestion.

El **Cluster 1**, por su parte, agrupa firmas con mediana de **40 años**, mayores niveles de empleo, ingresos y activos, y una posicion empresarial media correspondiente al **segmento 4**. Estas empresas exhiben tambien mayor presencia de agentes de retencion y contribuyentes especiales. Su tasa de clientes, aunque ligeramente menor (**35,2%**), sigue estando por encima de la tasa base de Capa 1 y evidencia que FPA tambien participa en el segmento empresarial consolidado.

La lectura mas importante de esta capa no es solamente que existen dos perfiles economicos diferenciados, sino que **ambos concentran una proporcion alta de clientes FPA**. En la muestra financiera, los clientes se distribuyen casi de forma equilibrada entre ambos grupos: **47,2%** en el cluster de empresas pequeñas y recientes, y **52,8%** en el cluster de empresas medianas-grandes consolidadas. Esto indica que, cuando se observan las variables economicas, el patron comercial de FPA no se restringe a un unico estrato de tamaño, sino que cubre tanto organizaciones en consolidacion como firmas ya maduras.

## 4.8.5 Sensibilidad de Capa 2 y efecto de outliers

La corrida de sensibilidad con `K = 4` en Capa 2 confirmo que las mejoras metricas observadas para valores mayores de `K` respondian principalmente al aislamiento de casos atipicos y no a la aparicion de segmentos economicamente interpretables. En esta solucion surgieron dos clusters pequeños adicionales: uno de **2 empresas** con liquidez corriente extraordinariamente alta, y otro de **1 empresa** con margen operacional extremo. En conjunto, estos micro-clusters no constituyen segmentos de mercado defendibles, sino expresiones de outliers financieros que distorsionan la particion cuando se fuerza una mayor granularidad.

Por ello, la solucion de `K = 2` debe considerarse mas robusta para fines de interpretacion gerencial y comparacion metodologica con la Capa 1.

## 4.8.6 Comparacion entre capas y sesgo de cobertura

La comparacion entre ambos modelos se realizo sobre las **92 empresas comunes** presentes en Capa 2. Cuando se contrasto la solucion principal de Capa 1 (`K = 4`) con la solucion estable de Capa 2 (`K = 2`), el **Adjusted Rand Index (ARI)** fue de **0,392**. Al repetir el ejercicio con la misma granularidad nominal (`K = 4` en ambas capas), el ARI descendio a **0,340**. En ambos casos, la concordancia puede considerarse **parcial**, pero no alta.

Este resultado indica que la informacion financiera no simplemente refina la segmentacion firmografica del SRI, sino que introduce una estructura adicional que redistribuye varias empresas entre grupos. En particular, dentro de las 92 observaciones comunes se observan tres patrones:

1. El segmento de **corporativos maduros formalizados** de Capa 1 se alinea mayoritariamente con el cluster de **empresas medianas-grandes consolidadas** de Capa 2: **41 de 43 empresas** con cobertura financiera caen en ese grupo.
2. El segmento de **sociedades comerciales de Guayas** se reparte entre ambos clusters financieros, aunque con predominio del grupo de **empresas pequeñas y recientes**: **17 de 25 empresas**.
3. El segmento de **sociedades formales jovenes de alta afinidad** tambien se concentra mayoritariamente en el cluster de **empresas pequeñas y recientes**: **19 de 24 empresas**.

Sin embargo, el hallazgo mas importante no esta en la concordancia parcial, sino en el **sesgo de cobertura**. El cluster de Capa 1 denominado *Empresas menos formalizadas del resto* tiene **43 empresas** en el universo principal, pero **ninguna de ellas** aparece en la Capa 2. Es decir, su cobertura financiera es exactamente **0,0%**. En contraste, los otros segmentos muestran coberturas de **82,7%**, **67,6%** y **55,8%**, respectivamente.

Esta ausencia total confirma que la capa financiera no representa de forma homogénea a todo el universo de empresas detectado por la segmentacion principal. En consecuencia, los resultados de Capa 2 deben interpretarse como un ejercicio de robustez sobre un subconjunto sesgado hacia empresas mas visibles, mas formalizadas o con mayor trazabilidad economica en los registros de la SCVS.

## 4.8.7 Implicaciones para FPA Latam

Desde una perspectiva aplicada, los resultados permiten derivar al menos tres implicaciones estratégicas.

Primero, el modelo principal de Capa 1 confirma que FPA posee una mayor afinidad historica con dos perfiles muy concretos: **corporativos maduros formalizados** y **sociedades formales jovenes de alta afinidad**. Estos segmentos deberian constituir el nucleo de una estrategia de priorizacion comercial, ya que concentran la mayor parte de clientes observados.

Segundo, el segmento de **empresas menos formalizadas del resto** presenta muy baja conversion historica y, ademas, nula cobertura financiera en la fuente SCVS. Esto sugiere que se trata de un perfil en el que FPA o bien no ha desarrollado penetracion comercial efectiva, o bien enfrenta barreras estructurales de acceso, presupuesto o formalizacion. En terminos de gestion comercial, este grupo podria tratarse como un segmento de baja prioridad o como una cartera de desarrollo de largo plazo con una propuesta de valor diferenciada.

Tercero, la evidencia de Capa 2 sugiere que, cuando existe informacion economica disponible, FPA atiende tanto a empresas de mayor tamaño y madurez como a empresas mas pequeñas pero en fases activas de consolidacion. Esto abre una linea de interpretacion relevante para la tesis: la afinidad comercial de FPA no depende exclusivamente del tamaño de la empresa, sino del momento organizacional en que esta se encuentra y de su necesidad de profesionalizacion, eficiencia o transformacion.

## 4.8.8 Sintesis de resultados

En sintesis, el ejercicio de clustering permitio identificar una estructura segmentaria clara y accionable dentro del universo de empresas enriquecidas. El modelo principal, construido con variables SRI de alta cobertura, resulto suficiente para distinguir cuatro perfiles empresariales con distinta afinidad historica hacia FPA. El analisis financiero de robustez confirmo parcialmente esta estructura, pero tambien revelo que el subconjunto con datos economicos disponibles esta sesgado hacia empresas mas formalizadas y visibles en la SCVS. Por tanto, la contribucion central del modelo no reside solo en haber producido segmentos interpretables, sino en demostrar que la segmentacion firmografica basada en fuentes publicas ya captura una parte sustantiva de la logica comercial de FPA, al tiempo que deja explicitadas sus limitaciones de cobertura y representatividad.

---

## Nota de uso para redaccion final

- Donde dice `Tabla 4.x` o donde quieras insertar graficos, puedes referenciar las salidas del notebook (`metricas_kmeans_capa1.csv`, `perfil_clusters_capa1.csv`, `cobertura_financiera_por_cluster_capa1.csv`, etc.).
- Si decides que tu capitulo 4 ya tiene otra numeracion interna, puedes renombrar esta seccion como `4.4`, `4.5` o la que corresponda sin tocar el contenido sustantivo.
- Conviene reconciliar en el texto metodologico previo la diferencia entre los conteos preliminares (`163/93`) y los artefactos finales realmente usados (`175/92`), para que no quede una inconsistencia narrativa en la tesis.
