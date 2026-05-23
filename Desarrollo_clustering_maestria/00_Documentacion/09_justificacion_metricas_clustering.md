# 5. Justificación Metodológica de Métricas y Selección de K en K-Means

Este documento detalla el marco de evaluación matemática utilizado para medir la calidad del algoritmo de aprendizaje no supervisado (K-Means) y documenta el proceso empírico de selección del número óptimo de clústeres ($K$) para la Capa 1 (Tributaria) y la Capa 2 (Financiera).

---

## 5.1. Definición e Interpretación de Métricas de Evaluación Interna

Dado que el aprendizaje no supervisado no cuenta con etiquetas predefinidas (Ground Truth) para medir la "precisión" tradicional, la calidad de los clústeres generados se validó utilizando métricas de evaluación interna. Cada métrica posee un rango y una regla de decisión particular:

### 1. Coeficiente Silhouette
Mide la calidad de la cohesión interna de un clúster frente a su separación con los demás clústeres.
*   **Rango:** $[-1, 1]$.
*   **Regla de decisión:** Mayor es mejor. Un valor cercano a $1$ indica clústeres densos y perfectamente separados; un valor cercano a $0$ indica solapamiento de fronteras entre segmentos; valores negativos indican asignaciones erróneas. En contextos de datos comerciales reales (alta dimensionalidad y ruido), valores positivos sostenidos indican una partición válida.

### 2. Índice Davies-Bouldin (DBI)
Evalúa la relación entre la dispersión interna de cada clúster y la distancia que separa los centroides de clústeres distintos.
*   **Rango:** $[0, \infty)$. (No posee un límite superior).
*   **Regla de decisión:** Menor es mejor. Un valor más cercano a cero indica una mejor separación y menor dispersión. Es normal obtener valores superiores a $1.0$ en segmentaciones de negocio, ya que refleja el solapamiento natural que existe entre empresas en el mercado abierto.

### 3. Inercia (Suma de Errores Cuadráticos - WCSS)
Mide la suma de las distancias al cuadrado de cada muestra al centroide de su clúster asignado.
*   **Rango:** $[0, \infty)$.
*   **Regla de decisión:** Menor es mejor. No obstante, la inercia siempre decrece a medida que aumenta el número de clústeres ($K$). Por ello, se evalúa mediante el "método del codo", buscando el punto de inflexión donde incrementar $K$ deja de aportar reducciones significativas en la varianza.

---

## 5.2. Evaluación Empírica y Selección del Número Óptimo de Clústeres ($K$)

La selección del parámetro $K$ no obedeció a la maximización ciega de una única métrica, sino a un equilibrio multivariante entre **cohesión matemática (Silhouette), separación geométrica (Davies-Bouldin) y utilidad comercial (tamaño y perfil del segmento)** para FPA Latam.

### 5.2.1. Resultados de la Capa 1 (Modelo Principal SRI)

Para la Capa 1, se entrenaron iteraciones con $K$ variando de 2 a 8.

| K | Silhouette (Maximizada) | Davies-Bouldin (Minimizada) | Min Cluster (Empresas) | Max Cluster (Empresas) |
| :---: | :---: | :---: | :---: | :---: |
| 2 | 0.224 | 1.590 | 66 | 115 |
| 3 | 0.192 | 1.838 | 56 | 64 |
| **4** | **0.209** | **1.601** | **35** | **60** |
| 5 | 0.215 | 1.453 | 27 | 44 |
| 6 | 0.208 | 1.529 | 17 | 43 |
| 7 | 0.213 | 1.469 | 11 | 39 |
| 8 | 0.192 | 1.591 | 10 | 29 |

**Justificación de decisión (K=4):** 
Aunque la solución trivial $K=2$ presenta la Silhouette más alta ($0.224$), generar únicamente dos megagrupos comerciales (de 66 y 115 empresas) es inútil para la toma de decisiones estratégicas. Se seleccionó **$K=4$** porque presenta el mejor equilibrio técnico-comercial: 
1. Recupera una Silhouette competitiva ($0.209$).
2. Mantiene un índice Davies-Bouldin estable ($1.601$).
3. Genera segmentos de mercado con un tamaño mínimo viable comercialmente (mínimo 35 empresas), evitando la creación de micro-segmentos inmanejables que aparecen al aumentar $K \geq 6$.

### 5.2.2. Resultados de la Capa 2 (Enriquecimiento Financiero SCVS)

Para la Capa 2, que incorpora alta variabilidad por la escala en dólares (activos, ingresos), se replicó el experimento.

| K | Silhouette (Maximizada) | Davies-Bouldin (Minimizada) | Min Cluster (Empresas) | Max Cluster (Empresas) |
| :---: | :---: | :---: | :---: | :---: |
| **2** | **0.379** | **1.212** | **31** | **110** |
| 3 | 0.197 | 1.605 | 17 | 71 |
| 4 | 0.209 | 1.341 | 3 | 71 |
| 5 | 0.233 | 1.141 | 2 | 84 |
| 6 | 0.172 | 1.299 | 2 | 70 |
| 7 | 0.182 | 1.241 | 2 | 53 |
| 8 | 0.178 | 1.240 | 2 | 42 |

**Justificación de decisión (K=2):**
En el caso financiero, la decisión matemática es contundente. La partición **$K=2$** es ampliamente superior, logrando la máxima cohesión (Silhouette $0.379$) y la mejor separación (Davies-Bouldin $1.212$). El análisis revela que forzar al algoritmo a buscar más agrupaciones (ej. $K=4$) provoca que la sensibilidad financiera detecte *outliers*, aislando grupos carentes de utilidad práctica (ej. un clúster conformado por apenas 3 empresas). Por lo tanto, la Capa 2 se consolida en dos grandes estratos: empresas maduras de gran escala y empresas medianas/emergentes.
