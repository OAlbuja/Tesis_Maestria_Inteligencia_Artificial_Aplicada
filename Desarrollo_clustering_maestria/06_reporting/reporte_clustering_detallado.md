# Reporte detallado — Clustering de empresas (Capa 1 y Capa 2)

**Fecha:** 2026-05-09  
**Proyecto:** Desarrollo_clustering_maestria

> Nota de consistencia: las cifras de este reporte se calculan/leen desde los CSV en `04_modeling/outputs/` y `05_evaluation/outputs/`. Algunas figuras exportadas pueden mostrar N o líneas de “tasa base” de una corrida previa; usa las tablas como referencia numérica.

---

## 1) Resumen ejecutivo

Este reporte documenta los resultados del clustering en dos niveles:

- **Capa 1 (N=157):** segmentación basada en variables tipo “registro/estructura/operación” (por ejemplo, tipo de sociedad, obligaciones, sector macro, región, estado activo, fuente).
- **Capa 2 (N=87):** segmentación basada en variables con mayor contenido financiero/tamaño (por ejemplo, ingresos/activos/empleados en escala log, antigüedad, liquidez, margen, segmento).

Hallazgos principales:

- **Capa 1 (K=4) separa fuertemente la tasa FPA:**
  - Clústeres con tasas altas (~48% y ~50%) y clústeres con tasas bajas (~10.5% y ~17.1%).
- **Capa 2 (K=2) no separa tanto la tasa FPA:** ambos segmentos quedan cerca de la tasa base (~42.5%).
- **Cobertura SCVS por clúster (Capa 1):** un clúster (C2) tiene **cobertura financiera 0%**, lo que limita análisis financieros/externos para ese segmento.
- **Consistencia entre capas (ARI):** concordancia **moderada** (ARI ~0.38 para C1 K=4 vs C2 K=2 en el subconjunto común).

---

## 2) Artefactos revisados (fuentes del reporte)

### Modelado (Capa 1 y Capa 2)

- Asignaciones:
  - [`clusters_capa1.csv`](../04_modeling/outputs/clusters_capa1.csv)
  - [`clusters_capa2.csv`](../04_modeling/outputs/clusters_capa2.csv)
- Perfiles por clúster:
  - [`perfil_clusters_capa1.csv`](../04_modeling/outputs/perfil_clusters_capa1.csv)
  - [`perfil_clusters_capa2.csv`](../04_modeling/outputs/perfil_clusters_capa2.csv)
- Comparación entre capas:
  - [`comparacion_capas_best_k.csv`](../04_modeling/outputs/comparacion_capas_best_k.csv)
  - [`comparacion_capas_same_k.csv`](../04_modeling/outputs/comparacion_capas_same_k.csv)
- Sensibilidad (Capa 2 con K=4):
  - [`clusters_capa2_k4_sensibilidad.csv`](../04_modeling/outputs/clusters_capa2_k4_sensibilidad.csv)
  - [`perfil_clusters_capa2_k4.csv`](../04_modeling/outputs/perfil_clusters_capa2_k4.csv)

### Evaluación

- Métricas internas:
  - [`metricas_evaluacion_capa1.csv`](../05_evaluation/outputs/metricas_evaluacion_capa1.csv)
  - [`metricas_evaluacion_capa1_ward.csv`](../05_evaluation/outputs/metricas_evaluacion_capa1_ward.csv)
  - [`metricas_evaluacion_capa2.csv`](../05_evaluation/outputs/metricas_evaluacion_capa2.csv)
- Validación externa / consistencia:
  - [`cobertura_financiera_por_cluster.csv`](../05_evaluation/outputs/cobertura_financiera_por_cluster.csv)
  - [`tabla_concordancia_ari.csv`](../05_evaluation/outputs/tabla_concordancia_ari.csv)
- Figuras exportadas:
  - [`fig_seleccion_k_kmeans.png`](../05_evaluation/outputs/fig_seleccion_k_kmeans.png)
  - [`fig_silhouette_muestras_c1.png`](../05_evaluation/outputs/fig_silhouette_muestras_c1.png)
  - [`fig_pca_capa1.png`](../05_evaluation/outputs/fig_pca_capa1.png)
  - [`fig_tsne_capa1.png`](../05_evaluation/outputs/fig_tsne_capa1.png)
  - [`fig_pca_capa2.png`](../05_evaluation/outputs/fig_pca_capa2.png)
  - [`fig_tasa_fpa_por_cluster.png`](../05_evaluation/outputs/fig_tasa_fpa_por_cluster.png)
  - [`fig_cobertura_vs_fpa.png`](../05_evaluation/outputs/fig_cobertura_vs_fpa.png)

---

## 3) Universo y tasas base (calculadas desde asignaciones)

- **Capa 1:** N = 157, clientes FPA = 51 → **tasa base = 32.5%**
- **Capa 2:** N = 87, clientes FPA = 37 → **tasa base = 42.5%**
- **Comunes (intersección entre Capa 1 y Capa 2):** N = 87, clientes FPA = 37 → **tasa base = 42.5%**

Interpretación rápida:

- Capa 2 trabaja sobre un **subuniverso** con información adicional (financiera/tamaño). Por eso su tasa base puede diferir respecto al universo de Capa 1.

---

## 4) Metodología — Variables de entrada por capa

El pipeline de preparación parte de dos fuentes principales (LEADS y HORAS) enriquecidas con datos de la Superintendencia de Compañías (SCVS) y el SRI. Tras el matching, normalización y limpieza, se construyen dos matrices de features:

### 4.1 Capa 1 — Variables de estructura y registro (N=157)

Capa de **mayor cobertura**: usa únicamente información registral/tributaria disponible para casi todo el universo.

| Variable | Tipo | Descripción |
|---|---|---|
| `tipo_sociedad` | Binaria (0/1) | 1 = sociedad anónima/compañía; 0 = persona natural |
| `obligado_contabilidad` | Binaria | Obligación de llevar contabilidad (SRI) |
| `es_agente_retencion` | Binaria | Calificado como agente de retención (SRI) |
| `es_contribuyente_especial` | Binaria | Calificado como contribuyente especial (SRI) |
| `estado_activo` | Binaria | Empresa activa en el registro (SCVS/SRI) |
| `antiguedad_anos` | Continua (estandarizada) | Años desde constitución hasta fecha de análisis |
| `sector_ciiu_macro_*` | One-hot | Sector económico macro (C=manufactura, G=comercio, K=finanzas, M=profesionales, S=servicios, OTRO) |
| `region_*` | One-hot | Región geográfica (Guayas, Pichincha, Resto) |

Fuente: [`matriz_capa1.csv`](../03_feature_engineering/outputs/matriz_capa1.csv) / [`features_capa1.csv`](../03_feature_engineering/outputs/features_capa1.csv)

### 4.2 Capa 2 — Variables de tamaño y finanzas (N=87)

Capa de **mayor profundidad**: requiere que la empresa tenga estados financieros disponibles en SCVS. Incluye todo lo de Capa 1 más variables financieras/de tamaño derivadas de los estados financieros.

| Variable | Tipo | Descripción |
|---|---|---|
| `tipo_sociedad` | Binaria | Igual que Capa 1 |
| `obligado_contabilidad` | Binaria | Igual que Capa 1 |
| `es_agente_retencion` | Binaria | Igual que Capa 1 |
| `es_contribuyente_especial` | Binaria | Igual que Capa 1 |
| `estado_activo` | Binaria | Igual que Capa 1 |
| `antiguedad_anos` | Continua (estandarizada) | Igual que Capa 1 |
| `log_empleados` | Continua (log+estand.) | Logaritmo del número de empleados |
| `log_ingresos` | Continua (log+estand.) | Logaritmo de los ingresos totales (SCVS) |
| `log_activos` | Continua (log+estand.) | Logaritmo de los activos totales (SCVS) |
| `segmento` | Continua (estandarizada) | Segmento SCVS (1=micro, 2=pequeña, 3=mediana, 4=grande) |
| `liquidez_corriente` | Continua (estandarizada) | Activo corriente / pasivo corriente |
| `margen_operacional` | Continua (estandarizada) | Resultado operacional / ingresos |
| `sector_ciiu_macro_*` | One-hot | Igual que Capa 1 |
| `region_*` | One-hot | Igual que Capa 1 |

Fuente: [`matriz_capa2.csv`](../03_feature_engineering/outputs/matriz_capa2.csv) / [`features_capa2.csv`](../03_feature_engineering/outputs/features_capa2.csv)

### 4.3 Preprocesamiento aplicado

- Variables continuas: estandarizadas (media=0, std=1) antes del clustering.
- Variables binarias: se usan directamente (0/1).
- Variables categóricas (sector, región): codificadas como One-Hot.
- Variables financieras (empleados, ingresos, activos): transformadas a log antes de estandarizar, para reducir el efecto de outliers extremos.
- El año de los estados financieros (Capa 2) es el más reciente disponible por empresa.

### 4.4 Algoritmo y configuración

- **Algoritmo principal:** K-Means (inicialización k-means++, 100 inicializaciones, semilla fija).
- **Algoritmo comparativo:** Ward (clustering jerárquico), usado para validar robustez del K elegido.
- **Criterio de K:** combinación del método del codo (inercia) + silhouette promedio + restricción práctica de no generar clústeres con n < 10.

---

## 5) Selección de K y desempeño interno

### 5.1 Capa 1 — Comparación KMeans vs Ward

- KMeans tiende a dar mejores resultados de **silhouette** que Ward para los mismos K, según:
  - [`metricas_evaluacion_capa1.csv`](../05_evaluation/outputs/metricas_evaluacion_capa1.csv)
  - [`metricas_evaluacion_capa1_ward.csv`](../05_evaluation/outputs/metricas_evaluacion_capa1_ward.csv)

**Extracto (Capa 1):**

| Método | K | Silhouette | Davies-Bouldin | Tamaño min/max |
|---|---:|---:|---:|---|
| KMeans | 2 | 0.266 | 1.487 | 55 / 102 |
| KMeans | 4 | 0.213 | 1.613 | 34 / 50 |
| Ward | 2 | 0.257 | 1.506 | 51 / 106 |
| Ward | 4 | 0.185 | 1.731 | 28 / 51 |

**Decisión práctica recomendada (Capa 1):** **K=4 (KMeans)** por:

- Granularidad útil (4 segmentos interpretables).
- Tamaños balanceados (34–50 por clúster) evitando micro-clústeres.

### 5.2 Capa 2 — Robustez vs "micro-clústeres"

En Capa 2, silhouette aumenta cuando K crece (hasta K=4), pero aparecen clústeres muy pequeños:

| K (KMeans) | Silhouette | Tamaño min/max | Comentario |
|---:|---:|---|---|
| 2 | 0.386 | 35 / 52 | Segmentación robusta y estable |
| 3 | 0.399 | 2 / 52 | Aparecen micro-clústeres |
| 4 | 0.409 | 1 / 50 | Riesgo alto de clúster “outlier” |

**Decisión práctica recomendada (Capa 2):** **K=2 (KMeans)** para mantener estabilidad y evitar que outliers definan clústeres de tamaño 1.

### Figura — Selección de K (KMeans)

![Selección de K — KMeans](../05_evaluation/outputs/fig_seleccion_k_kmeans.png)

---

## 6) Resultados — Capa 1 (K=4)

### 6.1 Resumen por clúster (Capa 1)

Tasa base Capa 1: **32.5%**

| Clúster | Segmento | n | Tasa FPA | Δ vs base (pp) | Cobertura SCVS |
|---:|---|---:|---:|---:|---:|
| C0 | Sociedades jovenes de alta afinidad FPA | 50 | 48.0% | +15.52 | 82.0% |
| C1 | Grandes corporativos maduros establecidos | 34 | 50.0% | +17.52 | 64.7% |
| C2 | Empresas comerciales de Guayas | 38 | 10.5% | -21.96 | 0.0% |
| C3 | Personas naturales del resto del pais | 35 | 17.1% | -15.34 | 68.6% |

Fuente:

- Asignaciones: [`clusters_capa1.csv`](../04_modeling/outputs/clusters_capa1.csv)
- Cobertura: [`cobertura_financiera_por_cluster.csv`](../05_evaluation/outputs/cobertura_financiera_por_cluster.csv)

### 6.2 Interpretación cualitativa (Capa 1)

Basado en [`perfil_clusters_capa1.csv`](../04_modeling/outputs/perfil_clusters_capa1.csv):

- **C0 — “Alta afinidad FPA” (48%)**
  - Moda región: **Pichincha**; sector macro: **C**; fuente modal: **LEADS**.
  - Alta proporción de obligaciones/atributos (p. ej., agente de retención ~82%, contribuyente especial ~86%, activo ~88%).
  - **Uso sugerido:** priorizar campañas/seguimiento comercial y propuestas de valor FPA.

- **C1 — “Grandes corporativos maduros” (50%)**
  - Moda región: **Pichincha**; fuente modal: **HORAS**.
  - Aunque el segmento sugiere “corporativos”, en los indicadores tributarios aparece menor proporción de “agente de retención” vs C0.
  - **Uso sugerido:** cuenta clave / estrategia enterprise, con enfoques de retención y expansión.

- **C2 — “Comerciales de Guayas” (10.5%)**
  - **Cobertura SCVS = 0%**, lo cual indica que para este segmento no se dispone de estados/financieros SCVS en el universo actual.
  - Sector macro modal: **G**; región modal: **Resto** (según perfil).
  - **Uso sugerido:** es el segmento “baja afinidad” y con baja trazabilidad financiera; requiere enriquecimiento adicional (otras fuentes) antes de decisiones basadas en finanzas.

- **C3 — “Personas naturales resto del país” (17.1%)**
  - Región modal: **Guayas**; sector macro: **G**; fuente modal: **LEADS**.
  - **Uso sugerido:** segmento de afinidad baja-media; enfoque más selectivo y con mayor filtrado previo.

### Figura — Silhouette por muestra (Capa 1)

![Silhouette por muestra — Capa 1](../05_evaluation/outputs/fig_silhouette_muestras_c1.png)

### Figuras — Embeddings (PCA / t-SNE) para visualización

> PCA/t-SNE se usan aquí como **visualización** (no como modelo).

![PCA 2D — Capa 1](../05_evaluation/outputs/fig_pca_capa1.png)

![t-SNE 2D — Capa 1](../05_evaluation/outputs/fig_tsne_capa1.png)

---

## 7) Resultados — Capa 2 (K=2)

### 7.1 Resumen por clúster (Capa 2)

Tasa base Capa 2: **42.5%**

| Clúster | Segmento | n | Tasa FPA | Δ vs base (pp) |
|---:|---|---:|---:|---:|
| C0 | Empresas pequenas y recientes | 35 | 42.9% | +0.33 |
| C1 | Empresas medianas-grandes consolidadas | 52 | 42.3% | -0.22 |

Fuente:

- Asignaciones: [`clusters_capa2.csv`](../04_modeling/outputs/clusters_capa2.csv)
- Perfiles: [`perfil_clusters_capa2.csv`](../04_modeling/outputs/perfil_clusters_capa2.csv)

### 7.2 Interpretación cualitativa (Capa 2)

Basado en [`perfil_clusters_capa2.csv`](../04_modeling/outputs/perfil_clusters_capa2.csv):

- **C0 — Pequeñas y recientes**
  - Mediana antigüedad ~8 años.
  - Métricas en escala log (empleados/activos/ingresos) sugieren menor tamaño relativo.

- **C1 — Medianas-grandes consolidadas**
  - Mediana antigüedad ~36.5 años.
  - Escalas log más altas (empleados/ingresos/activos), consistente con mayor tamaño.

Conclusión operativa:

- Esta capa separa bien por **tamaño/madurez**, pero **no separa de forma marcada** por tasa FPA (ambos segmentos quedan cerca de la tasa base).

### Figura — PCA 2D (Capa 2)

![PCA 2D — Capa 2](../05_evaluation/outputs/fig_pca_capa2.png)

### Sensibilidad K=4 (Capa 2)

El análisis K=4 crea clústeres muy pequeños (n=1–2), típicamente outliers (por ejemplo, liquidez extremadamente alta).

- Perfil K=4: [`perfil_clusters_capa2_k4.csv`](../04_modeling/outputs/perfil_clusters_capa2_k4.csv)

---

## 8) Validación externa: Cobertura financiera (SCVS) vs afinidad FPA

La cobertura financiera por clúster (Capa 1) muestra un patrón relevante:

- C0 (82%), C1 (64.7%) y C3 (68.6%) tienen cobertura SCVS moderada/alta.
- **C2 tiene cobertura 0%**, lo que limita contrastes financieros y puede sesgar análisis “financieros” si se mezclan universos.

Figura:

![Cobertura SCVS vs Tasa FPA — Capa 1](../05_evaluation/outputs/fig_cobertura_vs_fpa.png)

---

## 9) Consistencia entre capas (ARI)

En el subconjunto común (N=87), la concordancia entre particiones es **moderada**:

| Comparación | N comunes | ARI |
|---|---:|---:|
| C1 K=4 vs C2 K=2 | 87 | 0.376 |
| C1 K=4 vs C2 K=4 | 87 | 0.324 |

Fuente: [`tabla_concordancia_ari.csv`](../05_evaluation/outputs/tabla_concordancia_ari.csv)

Interpretación:

- Las capas capturan criterios distintos (Capa 1: “estructura/operación”; Capa 2: “tamaño/finanzas”), por lo que no se espera ARI alto.

---

## 10) Recomendaciones de uso (operativas)

1) **Priorización comercial (FPA):**
- En Capa 1, priorizar C0 y C1 por tasas FPA muy superiores a la base.
- Tratar C2 como segmento de baja afinidad; evitar esfuerzos intensivos salvo que haya señales adicionales.

2) **Estrategia de datos:**
- Para C2 (cobertura SCVS 0%), considerar enriquecer con otras fuentes o validar si su naturaleza (tipo de contribuyente/actividad) explica la ausencia en SCVS.

3) **Uso combinado de capas:**
- Capa 1 sirve mejor para “afinidad FPA” (separación clara).
- Capa 2 sirve mejor para “tamaño/madurez” (segmentación empresarial) y puede complementar el perfilado, aunque no discrimine FPA por sí sola.

---

## 11) Cómo regenerar el reporte (reproducibilidad)

- Re-generar outputs y figuras ejecutando:
  - `04_modeling/01_clustering.ipynb`
  - `05_evaluation/01_evaluacion_clustering.ipynb`

- Luego actualizar este reporte si cambian los CSV/figuras.

---

## Anexo A — Figura: Tasa de clientes FPA por clúster

![Tasa de clientes FPA por clúster](../05_evaluation/outputs/fig_tasa_fpa_por_cluster.png)
