# 4.8 Resultados del modelo de clustering

Esta seccion presenta los resultados actuales del modelo de segmentacion construido a partir del Golden Record manual de empresas con RUC ecuatoriano verificado. Los resultados provienen de los notebooks:

- `04_modeling/01_clustering.ipynb`
- `05_evaluation/01_evaluacion_clustering.ipynb`

El modelo final no usa las salidas probabilisticas del matching automatizado. La base de entrada esta compuesta por RUCs verificados manualmente y enriquecidos con fuentes oficiales del SRI y de la SCVS. El pais comercial u origen queda como trazabilidad; la inclusion operativa depende de contar con RUC ecuatoriano y razon social validados manualmente.

---

## 4.8.1 Base analizada

| Capa | Fuente principal | Empresas | Variables de matriz | Clientes FPA | Tasa base de clientes |
|---|---|---:|---:|---:|---:|
| Capa 1 | SRI | 181 | 14 | 82 | 45,3% |
| Capa 2 | SRI + ranking SCVS | 141 | 20 | 57 | 40,4% |

La Capa 1 constituye el modelo principal porque tiene mayor cobertura y puede replicarse para cualquier empresa con RUC ecuatoriano. La Capa 2 es un analisis complementario: incorpora variables financieras para el subconjunto de empresas que aparecen en el ranking SCVS.

La variable `es_cliente_fpa` no fue usada para entrenar K-Means. Se deriva de la presencia de la empresa en `proyectos_empresa.xlsx`, que registra proyectos/horas de FPA por empresa, y se usa exclusivamente despues del clustering como validacion externa para medir afinidad historica de FPA por segmento.

Por confidencialidad y por consistencia metodologica, los resultados se reportan de forma agregada por cluster. No se requiere revelar que empresas especificas son clientes y cuales no; basta con informar la tasa de clientes FPA por segmento.

---

## 4.8.2 Seleccion del numero de clusters

La seleccion de `K` combino cuatro criterios: inercia, Silhouette, Davies-Bouldin e interpretabilidad comercial del tamano de los clusters.

### Capa 1

| K | Silhouette | Davies-Bouldin | Min cluster | Max cluster |
|---:|---:|---:|---:|---:|
| 2 | 0,224 | 1,590 | 66 | 115 |
| 3 | 0,192 | 1,838 | 56 | 64 |
| **4** | **0,209** | **1,601** | **35** | **60** |
| 5 | 0,215 | 1,453 | 27 | 44 |
| 6 | 0,208 | 1,529 | 17 | 43 |
| 7 | 0,213 | 1,469 | 11 | 39 |
| 8 | 0,192 | 1,591 | 10 | 29 |

Aunque `K = 2` obtiene la mayor Silhouette, su segmentacion es demasiado agregada para fines comerciales. `K = 4` ofrece una solucion mas accionable, con tamanos entre 35 y 60 empresas y perfiles interpretables.

### Capa 2

| K | Silhouette | Davies-Bouldin | Min cluster | Max cluster |
|---:|---:|---:|---:|---:|
| **2** | **0,379** | **1,212** | **31** | **110** |
| 3 | 0,197 | 1,605 | 17 | 71 |
| 4 | 0,209 | 1,341 | 3 | 71 |
| 5 | 0,233 | 1,141 | 2 | 84 |
| 6 | 0,172 | 1,299 | 2 | 70 |
| 7 | 0,182 | 1,241 | 2 | 53 |
| 8 | 0,178 | 1,240 | 2 | 42 |

En Capa 2, `K = 2` es la solucion mas estable. Al aumentar `K`, aparecen grupos pequenos asociados a outliers financieros, especialmente razones de liquidez elevadas. Por ello se conserva `K = 2` como lectura principal y `K = 4` solo como sensibilidad.

---

## 4.8.3 Resultados Capa 1: modelo principal SRI

La solucion principal identifica cuatro segmentos empresariales:

| Cluster | Segmento | n | Clientes FPA | Tasa clientes | Diferencia vs base |
|---:|---|---:|---:|---:|---:|
| 0 | Comercio formal maduro en Pichincha | 46 | 20 | 43,5% | -1,8 pp |
| 1 | Industriales consolidados de alta afinidad FPA | 35 | 23 | 65,7% | +20,4 pp |
| 2 | Comercio formal emergente en Pichincha | 60 | 23 | 38,3% | -7,0 pp |
| 3 | Comercio formal regional en Guayas | 40 | 16 | 40,0% | -5,3 pp |

La tasa base de clientes en Capa 1 es 45,3%. El contraste chi-cuadrado entrega `p = 0,0556`, por lo que la diferencia entre clusters queda muy cerca del umbral de significancia de 5%, aunque no lo supera. En terminos de tesis, esto debe presentarse como una **tendencia comercial relevante**, no como una prueba estadistica concluyente.

### Cluster 0: Comercio formal maduro en Pichincha

Este segmento agrupa 46 empresas, con mediana de antiguedad de 56,5 anos. Todas son sociedades y estan obligadas a llevar contabilidad. Presenta alta formalizacion tributaria: 89,1% son agentes de retencion, 95,7% contribuyentes especiales y 95,7% se encuentran activas.

Su moda sectorial es `G` (comercio) y su region modal es Pichincha. La tasa de clientes FPA es 43,5%, ligeramente por debajo de la tasa base.

### Cluster 1: Industriales consolidados de alta afinidad FPA

Este es el segmento con mayor afinidad historica. Contiene 35 empresas, de las cuales 23 son clientes FPA, para una tasa de 65,7%.

El perfil corresponde a sociedades formales, obligadas a llevar contabilidad, con 94,3% de agentes de retencion y 100% de contribuyentes especiales. Su mediana de antiguedad es 33 anos, la moda sectorial es `C` (industria manufacturera) y la region modal es Resto.

Este segmento debe destacarse como el principal hallazgo comercial de Capa 1: combina madurez, formalizacion tributaria y alta penetracion historica de FPA.

### Cluster 2: Comercio formal emergente en Pichincha

Es el segmento mas numeroso, con 60 empresas. Tiene mediana de antiguedad de 20,5 anos, moda sectorial `G` y region modal Pichincha.

Aunque todas las empresas son sociedades obligadas a llevar contabilidad, su nivel de formalizacion avanzada es menor que en los clusters 0 y 1: 58,3% son agentes de retencion y 46,7% contribuyentes especiales. Su tasa de clientes es 38,3%, inferior a la base general.

### Cluster 3: Comercio formal regional en Guayas

Este segmento contiene 40 empresas, con mediana de antiguedad de 26 anos. Su moda sectorial es `G` y su region modal es Guayas.

Presenta 82,5% de agentes de retencion, 75,0% de contribuyentes especiales y 85,0% de empresas activas. Su tasa de clientes FPA es 40,0%, tambien por debajo de la base de Capa 1, pero cercana a la tasa general.

---

## 4.8.4 Resultados Capa 2: enriquecimiento financiero SCVS

Al incorporar variables financieras, la solucion estable de Capa 2 identifica dos segmentos:

| Cluster | Segmento | n | Clientes FPA | Tasa clientes | Diferencia vs base |
|---:|---|---:|---:|---:|---:|
| 0 | Empresas grandes consolidadas | 110 | 43 | 39,1% | -1,3 pp |
| 1 | Empresas medianas y recientes de alta afinidad | 31 | 14 | 45,2% | +4,7 pp |

La tasa base de clientes en Capa 2 es 40,4%. El contraste chi-cuadrado entrega `p = 0,6883`, por lo que no se observa evidencia estadistica de diferencias fuertes entre los dos segmentos financieros en terminos de presencia de clientes FPA.

### Cluster 0: Empresas grandes consolidadas

Este segmento concentra 110 empresas y representa el perfil de mayor escala economica. Tiene mediana de antiguedad de 33 anos, mediana de `log_empleados = 2,208`, `log_ingresos = 7,620`, `log_activos = 7,575` y segmento SCVS modal/mediano 4.

Tambien presenta alta formalizacion: 91,8% son agentes de retencion, 96,4% contribuyentes especiales y 99,1% estan activas. Su tasa de clientes FPA es 39,1%, levemente inferior a la base de Capa 2.

### Cluster 1: Empresas medianas y recientes de alta afinidad

Este segmento contiene 31 empresas. Tiene mediana de antiguedad de 13 anos, menor escala relativa (`log_empleados = 0,699`, `log_ingresos = 5,210`, `log_activos = 5,870`) y segmento SCVS mediano 2.

Su formalizacion avanzada es menor: 58,1% son agentes de retencion y 12,9% contribuyentes especiales. Aun asi, alcanza la mayor tasa de clientes en Capa 2: 45,2%, equivalente a +4,7 puntos porcentuales sobre la base.

---

## 4.8.5 Sensibilidad de Capa 2

La sensibilidad con `K = 4` en Capa 2 confirma que aumentar la granularidad produce grupos mas pequenos y mas influidos por razones financieras atipicas.

| Cluster K=4 | n | Tasa clientes | Mediana antiguedad | Mediana log ingresos | Mediana liquidez |
|---:|---:|---:|---:|---:|---:|
| 0 | 71 | 50,7% | 46 | 7,886 | 1,52 |
| 1 | 15 | 46,7% | 8 | 3,884 | 0,67 |
| 2 | 52 | 25,0% | 22 | 6,990 | 1,46 |
| 3 | 3 | 33,3% | 25 | 4,754 | 20,99 |

El cluster de 3 empresas con liquidez mediana de 20,99 ilustra por que `K = 4` no se adopta como solucion principal: detecta casos financieramente especiales, pero no necesariamente segmentos comerciales robustos.

---

## 4.8.6 Cobertura financiera por cluster de Capa 1

La cobertura SCVS no es uniforme entre clusters, pero todos los segmentos de Capa 1 cuentan con representacion financiera:

| Cluster Capa 1 | Segmento | n total | n con financieras | Cobertura SCVS | Tasa FPA |
|---:|---|---:|---:|---:|---:|
| 0 | Comercio formal maduro en Pichincha | 46 | 39 | 84,8% | 43,5% |
| 1 | Industriales consolidados de alta afinidad FPA | 35 | 22 | 62,9% | 65,7% |
| 2 | Comercio formal emergente en Pichincha | 60 | 45 | 75,0% | 38,3% |
| 3 | Comercio formal regional en Guayas | 40 | 35 | 87,5% | 40,0% |

Este resultado corrige una lectura anterior del proyecto: ya no existe un cluster con cobertura financiera nula. La cobertura minima observada es 62,9%.

---

## 4.8.7 Concordancia entre capas

La concordancia entre Capa 1 y Capa 2 se midio con Adjusted Rand Index (ARI) sobre las 141 empresas presentes en ambas capas.

| Comparacion | Empresas comunes | ARI |
|---|---:|---:|
| C1 K=4 vs C2 K=2 | 141 | 0,032 |
| C1 K=4 vs C2 K=4 | 141 | 0,126 |

La concordancia es baja. Esto no debe interpretarse como un error del modelo, sino como evidencia de que las variables financieras introducen una estructura distinta a la capturada por las variables tributarias del SRI.

La tabla de cruce para la solucion principal es:

| Cluster Capa 1 | Capa 2: grandes consolidadas | Capa 2: medianas y recientes |
|---:|---:|---:|
| 0 | 37 | 2 |
| 1 | 22 | 0 |
| 2 | 24 | 21 |
| 3 | 27 | 8 |

La lectura principal es que Capa 1 separa mejor perfiles formales, sectoriales y territoriales, mientras que Capa 2 reorganiza a las empresas por escala economica y madurez financiera. Ambas capas responden preguntas complementarias.

---

## 4.8.8 Implicaciones para FPA Latam

Los resultados sugieren tres implicaciones practicas:

1. **El segmento industrial consolidado es el mas atractivo historicamente.**  
   El Cluster 1 de Capa 1 alcanza 65,7% de clientes FPA, 20,4 puntos porcentuales por encima de la base. Este segmento deberia ser prioritario para estrategias de prospeccion y retencion.

2. **El comercio formal no es homogeneo.**  
   Los clusters comerciales se dividen por madurez, region y nivel de formalizacion. Pichincha y Guayas aparecen como geografias relevantes, pero con tasas de clientes inferiores al segmento industrial consolidado.

3. **La informacion financiera agrega una lectura distinta, no una simple confirmacion.**  
   El ARI bajo muestra que agregar SCVS no replica la segmentacion SRI. La Capa 2 distingue tamano y escala economica; por tanto, es util como analisis complementario, no como reemplazo del modelo principal.

---

## 4.8.9 Sintesis para redaccion final

El modelo principal de Capa 1, basado en variables SRI y construido sobre 181 empresas con RUC verificado manualmente, identifica cuatro segmentos empresariales interpretables. El hallazgo mas relevante es el segmento de **Industriales consolidados de alta afinidad FPA**, que presenta la mayor concentracion historica de clientes.

La Capa 2, construida sobre 141 empresas con informacion financiera SCVS, muestra que las variables economicas reorganizan la estructura de clusters. La baja concordancia entre capas (`ARI = 0,032`) indica que la formalizacion tributaria y la escala financiera capturan dimensiones distintas del universo empresarial.

En consecuencia, la tesis debe defender la Capa 1 como modelo operativo principal y presentar la Capa 2 como enriquecimiento analitico. El valor metodologico del proyecto reside en haber transformado un CRM sin identificadores oficiales en una matriz de segmentacion trazable, basada en RUCs verificados y fuentes publicas oficiales.

---

## Nota de uso

Para tablas finales del capitulo 4, usar como fuente:

- `04_modeling/outputs/perfil_clusters_capa1.csv`
- `04_modeling/outputs/perfil_clusters_capa2.csv`
- `05_evaluation/outputs/validacion_externa_capa1.csv`
- `05_evaluation/outputs/validacion_externa_capa2.csv`
- `05_evaluation/outputs/cobertura_financiera_por_cluster.csv`
- `05_evaluation/outputs/tabla_concordancia_ari.csv`
