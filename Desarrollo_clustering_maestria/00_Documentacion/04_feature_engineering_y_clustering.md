# 4. Feature Engineering y diseño del clustering

Este documento registra la construccion de variables, la estrategia de dos capas y las decisiones de modelado usadas para segmentar empresas B2B de FPA Latam. La version actual parte del archivo verificado manualmente `match_final_empresas_verificado.csv`; los outputs del matching automatizado se conservan como baseline metodologico, pero no como entrada operacional del modelo final.

---

## 4.1 Unidad de analisis

La unidad de analisis del modelo es la **empresa identificada por RUC ecuatoriano unico**. Esta decision evita duplicar empresas que aparecen con mas de un alias comercial en leads o en proyectos, y permite conectar cada observacion con SRI/SCVS mediante una llave oficial verificada manualmente.

El flujo base es:

```text
Golden Record manual
match_final_empresas_verificado.csv
        |
        v
deduplicacion por RUC
        |
        v
features_capa1.csv
```

El archivo verificado contiene 209 alias aceptados y 181 RUC unicos en la ultima ejecucion documentada. Despues de consolidar por RUC, la Capa 1 trabaja con empresas unicas integrables con SRI. Estos conteos deben recalcularse despues de cada actualizacion de los archivos manuales nuevos.

---

## 4.2 Variable de validacion externa

La variable `es_cliente_fpa` identifica si la empresa aparece en `proyectos_empresa.xlsx`, que es el registro operativo de proyectos/horas de FPA por empresa. Por tanto, esta variable no describe una caracteristica firmografica externa de la empresa; describe una relacion historica con FPA.

| Uso | Decision |
|---|---|
| Se conserva en `features_capa1.csv` y `features_capa2.csv` | Si, para trazabilidad y evaluacion posterior. |
| Entra a `matriz_capa1.csv` o `matriz_capa2.csv` | No. |
| Es vista por K-Means | Nunca. |
| Se usa despues del clustering | Si, para comparar tasas de clientes por segmento. |

Esta separacion evita fuga de informacion. El clustering sigue siendo no supervisado porque el algoritmo agrupa empresas usando atributos tributarios y financieros, no la etiqueta historica de cliente.

Las variables operativas de `proyectos_empresa.xlsx` (horas estimadas, horas ejecutadas, facturacion, avance, ocupacion, responsable, etc.) tampoco se incluyen en el clustering. Usarlas mezclaria atributos de mercado con resultados de la gestion comercial de FPA. Su valor metodologico esta en permitir una validacion externa agregada: una vez creados los clusters, se calcula la tasa de clientes por segmento sin revelar ni usar esa informacion durante el entrenamiento.

---

## 4.3 Capa 1: variables SRI

La Capa 1 es el modelo principal de la tesis porque usa informacion publica de alta cobertura y replicable para cualquier empresa con RUC ecuatoriano.

**Notebook:** `03_feature_engineering/01_base_sri.ipynb`  
**Output:** `03_feature_engineering/outputs/features_capa1.csv`

| Indicador | Valor |
|---|---:|
| Empresas | 181 |
| RUC unicos | 181 |
| Clientes FPA | 82 |
| Tasa base de clientes | 45,3% |

Distribucion por origen operacional:

| `source_label` | Empresas |
|---|---:|
| LEADS | 99 |
| HORAS | 77 |
| HORAS+LEADS | 5 |

### Variables construidas en Capa 1

| Variable | Tipo | Fuente |
|---|---|---|
| `tipo_sociedad` | Binaria | SRI, tipo de contribuyente. |
| `obligado_contabilidad` | Binaria | SRI, obligado a llevar contabilidad. |
| `es_agente_retencion` | Binaria | SRI, agente de retencion. |
| `es_contribuyente_especial` | Binaria | SRI, contribuyente especial. |
| `estado_activo` | Binaria | SRI, estado del contribuyente. |
| `antiguedad_anos` | Numerica | Diferencia entre 2026 y fecha de inicio de actividades. |
| `sector_ciiu_macro` | Categorica | Primera letra del codigo CIIU. |
| `region` | Categorica | Pichincha, Guayas o Resto. |

La matriz final de Capa 1 contiene 14 columnas numericas:

```text
tipo_sociedad
obligado_contabilidad
es_agente_retencion
es_contribuyente_especial
estado_activo
antiguedad_anos
sector_ciiu_macro_C
sector_ciiu_macro_G
sector_ciiu_macro_K
sector_ciiu_macro_M
sector_ciiu_macro_OTRO
region_Guayas
region_Pichincha
region_Resto
```

---

## 4.4 Capa 2: enriquecimiento financiero SCVS

La Capa 2 es un analisis complementario. Agrega variables financieras y de tamano empresarial del ranking SCVS para el subconjunto de empresas con informacion disponible.

**Notebook:** `03_feature_engineering/02_enriquecimiento_ranking.ipynb`  
**Output:** `03_feature_engineering/outputs/features_capa2.csv`

| Indicador | Valor |
|---|---:|
| Empresas | 141 |
| RUC unicos | 141 |
| Clientes FPA | 57 |
| Tasa base de clientes | 40,4% |

Distribucion por origen operacional:

| `source_label` | Empresas |
|---|---:|
| LEADS | 84 |
| HORAS | 52 |
| HORAS+LEADS | 5 |

### Variables adicionales de Capa 2

| Variable | Transformacion | Interpretacion |
|---|---|---|
| `log_empleados` | `log10(n_empleados + 1)` | Tamano laboral. |
| `log_ingresos` | `log10(ingresos_ventas + 1)` | Escala comercial. |
| `log_activos` | `log10(activos + 1)` | Escala patrimonial. |
| `segmento` | Ordinal | Segmento empresarial SCVS. |
| `liquidez_corriente` | Clip de outliers, luego escalado | Solvencia de corto plazo. |
| `margen_operacional` | Clip de outliers, luego escalado | Rentabilidad operativa. |

La matriz final de Capa 2 contiene 20 columnas numericas: las 14 de Capa 1 mas 6 variables financieras.

Existe una empresa con faltantes crudos en liquidez y margen operacional. La etapa `03_matriz_final.ipynb` imputa estos valores antes de exportar `matriz_capa2.csv`, por lo que la matriz entregada al modelo no contiene nulos.

---

## 4.5 Construccion de matrices

**Notebook:** `03_feature_engineering/03_matriz_final.ipynb`

| Matriz | Empresas | Columnas numericas | Nulos |
|---|---:|---:|---:|
| `matriz_capa1.csv` | 181 | 14 | 0 |
| `matriz_capa2.csv` | 141 | 20 | 0 |

Las reglas de preprocesamiento son:

1. Las variables binarias permanecen como 0/1.
2. `sector_ciiu_macro` y `region` se transforman con one-hot encoding.
3. Las variables numericas continuas se escalan con `StandardScaler`.
4. `es_cliente_fpa` no se incluye en las matrices de entrenamiento.

La eleccion de one-hot encoding es necesaria porque K-Means usa distancia euclidiana. Codificar sectores como numeros enteros impondria una jerarquia artificial entre categorias que no tienen orden natural.

---

## 4.6 Transformaciones financieras

Las variables financieras suelen tener distribuciones altamente asimetricas. Por esa razon se usa `log10(x + 1)` en empleados, ingresos y activos.

La transformacion reduce la dominancia de empresas extremadamente grandes y permite que el modelo compare empresas en una escala mas estable. El termino `+1` evita problemas con valores iguales a cero.

Adicionalmente, `liquidez_corriente` y `margen_operacional` se acotan para reducir el impacto de outliers financieros. Esta decision es importante porque razones financieras extremas pueden provocar clusters de uno, dos o tres casos, poco utiles para una interpretacion comercial.

---

## 4.7 Algoritmo de clustering

El algoritmo principal es **K-Means**, por tres razones:

1. Es interpretable para explicar segmentos a usuarios de negocio.
2. Funciona adecuadamente con matrices numericas escaladas.
3. Permite comparar soluciones de distintos valores de `K` mediante metricas internas.

Tambien se calculan metricas con clustering jerarquico Ward como apoyo exploratorio, pero la segmentacion final reportada se basa en K-Means.

Las metricas usadas para seleccionar `K` son:

| Metrica | Criterio |
|---|---|
| Inercia | Menor es mejor; se revisa el metodo del codo. |
| Silhouette | Mayor es mejor. |
| Davies-Bouldin | Menor es mejor. |
| Tamano minimo de cluster | Evita soluciones con micro-segmentos no accionables. |

---

## 4.8 Seleccion de K

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

Aunque `K = 2` tiene la mejor Silhouette, genera una particion demasiado gruesa para segmentacion comercial. `K = 4` ofrece un equilibrio razonable entre interpretabilidad, tamanos de segmento y separacion.

La decision final para Capa 1 es:

```text
K-Means Capa 1: K = 4
```

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

En Capa 2, `K = 2` es la solucion mas estable: maximiza Silhouette y evita micro-clusters derivados de outliers financieros. Se conserva una corrida `K = 4` solo como sensibilidad.

La decision final para Capa 2 es:

```text
K-Means Capa 2: K = 2
```

---

## 4.9 Segmentos finales definidos

La salida de modelado genera dos archivos principales:

| Output | Empresas | Descripcion |
|---|---:|---|
| `04_modeling/outputs/clusters_capa1.csv` | 181 | Segmentos principales basados en SRI. |
| `04_modeling/outputs/clusters_capa2.csv` | 141 | Segmentos complementarios con variables financieras SCVS. |

Los segmentos finales son:

### Capa 1

| Cluster | Segmento |
|---:|---|
| 0 | Comercio formal maduro en Pichincha |
| 1 | Industriales consolidados de alta afinidad FPA |
| 2 | Comercio formal emergente en Pichincha |
| 3 | Comercio formal regional en Guayas |

### Capa 2

| Cluster | Segmento |
|---:|---|
| 0 | Empresas grandes consolidadas |
| 1 | Empresas medianas y recientes de alta afinidad |

---

## 4.10 Lectura metodologica

La tesis debe presentar la Capa 1 como el modelo principal porque es el mas replicable y tiene mayor cobertura. La Capa 2 no reemplaza a la Capa 1; la complementa con variables economicas para estudiar si la estructura firmografica cambia cuando se dispone de informacion financiera.

El resultado esperado no es que ambas capas produzcan clusters identicos. De hecho, si los datos financieros introducen otra estructura, eso es un hallazgo: indica que el SRI permite una segmentacion formal y territorial, mientras que SCVS agrega una lectura economica y de escala empresarial.
