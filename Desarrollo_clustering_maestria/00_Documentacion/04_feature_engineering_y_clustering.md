# 4. Feature Engineering y Diseño del Modelo de Clustering

Este documento registra las decisiones metodológicas tomadas para la construcción de las variables del modelo de segmentación, la estrategia de capas adoptada y la teoría base del clustering. Sirve como guía de referencia para la redacción del capítulo de metodología y resultados de la tesis.

---

## 4.1 Inventario completo de features posibles

A partir del análisis de cobertura de las fuentes disponibles, se identificaron dos grupos de variables provenientes de fuentes distintas con coberturas distintas.

### Fuente A — Datos SRI (acceso vía RUC)

Estas columnas provienen de los 26 archivos CSV provinciales del SRI, separados por `|`, codificación `utf-8-sig`. Se obtienen haciendo un JOIN entre `match_final_empresas.csv` (RUC limpio) y el catálogo SRI consolidado.

| # | Feature en modelo | Columna SRI origen | Transformación aplicada | Cobertura |
|---|---|---|---|---|
| 1 | `tipo_sociedad` | `TIPO_CONTRIBUYENTE` | SOCIEDAD=1, PERSONA NATURAL=0 | 163/177 (92%) |
| 2 | `obligado_contabilidad` | `OBLIGADO` | S=1, N=0 | 163/177 (92%) |
| 3 | `es_agente_retencion` | `AGENTE_RETENCION` | S=1, N=0 | ~162/177 (99% de los 163) |
| 4 | `es_contribuyente_especial` | `ESPECIAL` | S=1, N=0 | ~162/177 |
| 5 | `estado_activo` | `ESTADO_CONTRIBUYENTE` | ACTIVO=1, otro=0 | 163/177 (92%) |
| 6 | `antiguedad_anos` | `FECHA_INICIO_ACTIVIDADES` | 2026 − año(fecha) | 163/177 (92%) |
| 7 | `sector_ciiu_*` | `CODIGO_CIIU` (primera letra) | dummies G/C/M/K/S/Otro | 163/177 (92%) |
| 8 | `region_*` | `DESCRIPCION_PROVINCIA_EST` | dummies Pichincha/Guayas/Resto | 163/177 (92%) |

> **N disponible para el modelo: 163 empresas**  
> Las 14 empresas restantes no se encontraron en los archivos SRI provinciales (corresponden a empresas con domicilio fuera del catálogo o con RUC no coincidente).

---

### Fuente B — Ranking financiero SCVS (acceso vía expediente SCVS)

Estas columnas provienen del archivo `bi_ranking.csv` de la Superintendencia de Compañías, Valores y Seguros (SCVS). El acceso requiere dos pasos: primero obtener el `EXPEDIENTE` de cada empresa desde `directorio_companias.xlsx` usando el RUC, luego hacer JOIN con el ranking tomando el último año fiscal disponible por empresa.

| # | Feature en modelo | Columna ranking origen | Transformación aplicada | Cobertura |
|---|---|---|---|---|
| 9 | `log_empleados` | `n_empleados` | log₁₀(x+1) | 93/177 (53%) |
| 10 | `log_ingresos` | `ingresos_ventas` | log₁₀(x+1) | 93/177 (53%) |
| 11 | `log_activos` | `activos` | log₁₀(x+1) | 93/177 (53%) |
| 12 | `segmento` | `cod_segmento` | ordinal 1–4 (micro→grande) | 92/93 (~99%) |
| 13 | `liquidez_corriente` | `liquidez_corriente` | valor crudo (clip p99) | 88/93 (95%) |
| 14 | `margen_operacional` | `margen_operacional` | valor crudo (clip p99) | 88/93 (95%) |

> **N disponible para este enriquecimiento: 93 empresas**

---

### Variable de validación externa (nunca entra al modelo)

| Nombre | Origen | Valores | Conteo |
|---|---|---|---|
| `es_cliente_fpa` | `proyectos_empresa.xlsx` columna `EMPRESA` | 1 = ya tiene proyectos con FPA, 0 = prospecto | 50 clientes / 177 total (28%) |

Esta variable se usa **exclusivamente después** de ejecutar el clustering, para medir qué proporción de clientes reales cae en cada segmento. Incorporarla al modelo sería un error metodológico grave: el algoritmo vería la respuesta antes de segmentar, rompiendo la naturaleza no supervisada del ejercicio.

---

## 4.2 El problema de cobertura — por qué importa la fuente

La siguiente tabla resume el problema central de cobertura que motivó la estrategia de dos capas:

| Grupo | N | % del total (177) |
|---|---|---|
| Total empresas con RUC verificado (`match_final_empresas.csv`) | 177 | 100% |
| En `features_capa1.csv` (antes de deduplicar) | 175 | 99% |
| **Empresas únicas en Capa 1 (tras deduplicar por RUC)** | **163** | **92%** |
| Con expediente SCVS en directorio | 98 | 55% |
| Con datos financieros en ranking SCVS | **92** | **52%** |
| Identificadas como clientes FPA activos (en 163 únicos) | **49** | **30,1%** |

**Interpretación:** Si se construye el modelo exclusivamente con datos financieros del ranking SCVS, se descarta el 47% del dataset. Con N=92 y un K=4 clusters, el promedio sería ~23 empresas por cluster — demasiado pequeño para generalizar o para que el modelo sea operativo en el futuro con nuevos leads.

> **Nota sobre deduplicación de Capa 1 (paso crítico de preprocesamiento):**  
> El archivo `features_capa1.csv` contiene **175 filas** porque la fuente `match_final_empresas.csv` proviene de dos fuentes de leads distintas (HORAS y LEADS), y 12 empresas aparecen en ambas fuentes con el mismo RUC. Al ejecutar el modelo de clustering, estas filas duplicadas se eliminan conservando la versión con `es_cliente_fpa = 1` cuando existe conflicto, lo que resulta en **163 empresas únicas** (163 RUCs distintos). Esta deduplicación se aplica al inicio del notebook `04_modeling/01_clustering.ipynb` y es el motivo por el que la cifra de referencia del modelo es **N = 163**, no 175 ni 177.

---

## 4.3 Estrategia de dos capas — decisión metodológica adoptada

Se decidió construir el modelo en **dos capas con roles distintos**. Esta estrategia responde a la necesidad de balancear cobertura, riqueza de información y operatividad futura del sistema.

### Capa 1 — Modelo principal (defendible, operativo, replicable)

- **N = 163 empresas**
- **Features: 8 variables SRI** (binarias + categóricas → ~12–14 columnas tras one-hot encoding)
- **Propósito:** Es el modelo que se defiende en la tesis. Tiene sentido operativo para FPA porque puede aplicarse a cualquier empresa ecuatoriana que tenga RUC — los datos SRI son públicos, actualizados y de cobertura nacional.
- **Ventaja clave:** Replicable en el futuro. Cualquier nuevo lead con RUC puede ser clasificado instantáneamente.
- **Limitación:** Las features son puramente cualitativas (tipo de empresa, sector, región, antigüedad). No capturan directamente el tamaño económico real de la empresa.

### Capa 2 — Análisis de enriquecimiento (validación de robustez)

- **N = 92 empresas** (subconjunto de las 163 únicas que tienen datos en el ranking SCVS)
- **Features: 14 variables** (las 8 de Capa 1 + 6 financieras del ranking SCVS)
- **Propósito:** No es un modelo independiente — es la misma pregunta de segmentación ejecutada sobre las 93 empresas con información financiera adicional. Sirve para responder: *"¿El clustering que encontré en Capa 1 se confirma cuando tengo datos económicos reales?"*
- **Si los clusters coinciden:** El modelo Capa 1 es robusto y las variables SRI capturan la misma estructura que los datos financieros detallados.
- **Si los clusters difieren:** Se tiene una limitación metodológica relevante y una sección de discusión muy interesante para la tesis.

### Flujo de datos de las dos capas

```
match_final_empresas.csv (177 empresas con RUC)
        │
        ├── JOIN por RUC → catálogo SRI
        │       └── 163 empresas → 8 features → matriz_capa1.csv
        │
        └── JOIN por RUC → directorio SCVS → expediente
                └── JOIN por expediente → bi_ranking.csv (último año)
                        └── 93 empresas → 14 features → matriz_capa2.csv

Ambas matrices agregan: es_cliente_fpa (label de validación, NO para clustering)

Notebook de clustering:
  → Modelo principal:     K-Means sobre matriz_capa1.csv
  → Análisis de soporte:  K-Means sobre matriz_capa2.csv
  → Comparación:          ¿Los clusters coinciden en las 93 empresas comunes?
  → Validación externa:   Tasa es_cliente_fpa por cluster (en ambos modelos)
```

---

## 4.4 Por qué se aplica transformación logarítmica a las variables financieras

Las variables financieras como `ingresos_ventas`, `n_empleados` y `activos` tienen distribuciones extremadamente sesgadas. En nuestra muestra:

```
n_empleados:     mínimo = 1,        mediana = 30,        máximo = 2.877
ingresos_ventas: mínimo = 0,        mediana = 7.682.427, máximo = 662.335.105
activos:         mínimo = 0,        mediana = 12.133.053, máximo = 502.093.690
```

Si se usan los valores crudos en el algoritmo de clustering, la distancia entre dos empresas estará dominada casi exclusivamente por sus ingresos absolutos, ignorando todas las demás variables. Por ejemplo:

- La distancia en ingresos entre empresa A (100.000 USD) y empresa B (662 millones USD) es 661.9 millones.
- La distancia en antigüedad entre una empresa de 5 años y una de 10 años es 5.

Sin transformación, el modelo ve ingresos como 132 millones de veces más importante que la antigüedad.

Con $\log_{10}$, los valores se comprimen a una escala comparable:

$$\log_{10}(100.000) = 5{,}0 \qquad \log_{10}(662.000.000) = 8{,}8$$

La diferencia pasa de 661.9 millones a 3.8 — ahora es comparable con las demás variables después del escalado estándar.

> **Regla general:** Siempre que una variable financiera o de conteo tenga una distribución donde el máximo es 100x o más que la mediana, se debe aplicar $\log_{10}(x+1)$. El `+1` evita `log(0)` en empresas con ingresos = 0.

---

## 4.5 Por qué `es_cliente_fpa` se usa como validación y no como feature

Esta es una de las decisiones más importantes del diseño metodológico.

**Si `es_cliente_fpa` entrara al modelo**, el algoritmo sabría desde el inicio cuáles empresas ya compraron a FPA. El clustering tendería a crear un cluster de "clientes" y otro de "no clientes" — que es exactamente lo que queremos *descubrir*, no lo que queremos *imponer*. El modelo dejaría de ser no supervisado.

**Al mantenerla fuera**, el clustering trabaja únicamente con características observables (tipo de empresa, sector, tamaño económico, antigüedad) y agrupa empresas por similitud real. Luego, al proyectar `es_cliente_fpa` sobre los clusters ya formados, se puede responder:

- ¿Qué cluster tiene mayor concentración de clientes actuales? → Ese es el perfil de empresa que más compra a FPA
- ¿Hay clusters con 0% de clientes? → Esos son perfiles de empresa que FPA nunca ha penetrado (oportunidad o descarte)
- ¿Los prospectos del cluster de mayor conversión son prioritarios para el equipo comercial?

Este análisis se denomina en la literatura **validación externa con etiquetas latentes** (*external validation with latent labels*). Es metodológicamente correcto porque la etiqueta no fue vista por el modelo durante el entrenamiento.

---

## 4.6 Teoría del clustering — fundamentos para la tesis

### ¿Qué es el clustering?

El clustering es un método de **aprendizaje no supervisado** que agrupa observaciones en segmentos (*clusters*) de forma que los elementos del mismo grupo sean más similares entre sí que con los elementos de otros grupos. No existe una variable respuesta que predecir — el modelo *descubre* la estructura latente de los datos.

Para este proyecto: el objetivo es descubrir si existen **perfiles de empresa** diferenciados entre los 163 leads de FPA Latam, y determinar si esos perfiles se correlacionan con la probabilidad de convertirse en clientes.

### Preprocesamiento obligatorio antes del clustering

```
Variables binarias (tipo_sociedad, obligado, etc.)   → sin transformación adicional
Variables categóricas (sector_ciiu, region)          → one-hot encoding (dummies 0/1)
Variables numéricas continuas (antiguedad, log_*)    → StandardScaler (media=0, desv=1)
```

El escalado estándar es **crítico**: sin él, `antiguedad_anos` (rango 0–90) domina sobre `liquidez_corriente` (rango 0–5) únicamente por diferencia de escala, no por importancia real para la segmentación.

### Algoritmos recomendados

| Algoritmo | Ventajas | Desventajas | Rol en este proyecto |
|---|---|---|---|
| **K-Means** | Rápido, interpretable, funciona bien con features escaladas | Asume clusters esféricos, sensible a outliers extremos | ✅ Algoritmo principal |
| **Hierarchical (Ward)** | El dendrograma permite visualizar el número de clusters natural | No escala bien con N grande | ✅ Exploración inicial para elegir K |
| **K-Medoids (PAM)** | Más robusto a outliers que K-Means | Más lento computacionalmente | ✅ Análisis de robustez |
| **DBSCAN** | Detecta clusters de forma arbitraria, identifica ruido | Difícil calibrar en datos de alta dimensión | ⚠️ Opcional |

### Cómo elegir el número de clusters K

Ninguna métrica sola es suficiente — se usan tres en conjunto:

**a) Método del Codo (Elbow):**  
Se grafica la inercia intra-cluster (WCSS) en función de K. El punto de inflexión ("codo") indica el K a partir del cual agregar más clusters ya no reduce sustancialmente la inercia.

$$\text{WCSS}(K) = \sum_{k=1}^{K} \sum_{x_i \in C_k} \|x_i - \mu_k\|^2$$

**b) Índice de Silhouette:**  
Para cada punto mide qué tan bien está asignado a su cluster (rango: −1 a +1). Se busca **maximizar** el promedio.

$$s(i) = \frac{b(i) - a(i)}{\max\bigl(a(i),\; b(i)\bigr)}$$

Donde $a(i)$ = distancia media a los otros puntos del mismo cluster, y $b(i)$ = distancia media al cluster vecino más cercano.

**c) Índice de Davies-Bouldin:**  
Mide el ratio entre dispersión intra-cluster y separación inter-cluster. Se busca **minimizar**.

$$DB = \frac{1}{K} \sum_{i=1}^{K} \max_{j \neq i} \frac{\sigma_i + \sigma_j}{d(\mu_i, \mu_j)}$$

### Flujo metodológico completo del clustering

```
1. Cargar matriz_capa1.csv (163 empresas, 8 features)
        ↓
2. One-hot encoding de sector_ciiu y region
        ↓
3. StandardScaler en variables numéricas (antiguedad_anos, log_*)
        ↓
4. Clustering jerárquico (Ward) → dendrogram → inspeccionar K candidatos
        ↓
5. K-Means con K = 3, 4, 5, 6
   → calcular silhouette score
   → calcular Davies-Bouldin index
   → calcular WCSS (método del codo)
        ↓
6. Elegir K óptimo con base en las 3 métricas
        ↓
7. Interpretar clusters: perfil de centroides por feature
        ↓
8. Validación externa: tasa es_cliente_fpa por cluster
        ↓
9. Nombrar segmentos con criterio de negocio
   (ej: "Corporativo Activo", "PYME Técnica", "Microempresa Incipiente")
        ↓
10. Exportar etiquetas de cluster → base para scoring de nuevos leads
        ↓
[Repetir pasos 3–10 con matriz_capa2.csv para análisis de robustez]
```

### Interpretación y comunicación de resultados

Una vez definidos los K clusters, cada uno se describe con:

- **Perfil cuantitativo:** valor promedio (centroide) de cada feature por cluster
- **Nombre interpretativo:** etiqueta de negocio que resume el perfil (lo más valioso para FPA)
- **Tasa de conversión FPA:** `es_cliente_fpa.mean()` por cluster → qué segmento concentra más clientes actuales
- **Recomendación táctica:** "FPA debe priorizar el segmento X porque concentra el Y% de clientes actuales y el perfil sugiere Z"

---

## 4.7 Resumen de decisiones tomadas

| Decisión | Opción elegida | Justificación |
|---|---|---|
| Fuente principal de features | SRI (vía RUC) | Cobertura máxima, datos públicos, operativo para producción |
| Datos financieros (ranking SCVS) | Capa 2 / análisis de soporte | Solo 53% cobertura — no viable como modelo principal |
| `es_cliente_fpa` en el modelo | NO — solo validación externa | Incluirla rompería la naturaleza no supervisada |
| Transformación variables financieras | log₁₀(x+1) | Distribución extremadamente sesgada — escala dominaría el clustering |
| Variables cualitativas | one-hot encoding | Necesario para calcular distancias euclidianas en K-Means |
| Escalado | StandardScaler | Evita que variables de mayor rango dominen la distancia |
| Algoritmo principal | K-Means | Velocidad, interpretabilidad, estándar en literatura |
| Selección de K | Elbow + Silhouette + Davies-Bouldin | Ninguna métrica sola es suficiente |
