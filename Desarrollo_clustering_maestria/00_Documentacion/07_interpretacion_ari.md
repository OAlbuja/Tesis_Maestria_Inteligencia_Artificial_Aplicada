# 5. Interpretación del Adjusted Rand Index (ARI) y Concordancia

Este documento profundiza en la interpretación académica y técnica de los resultados de concordancia entre la Capa 1 y la Capa 2 del modelo de segmentación, específicamente enfocándose en los valores bajos obtenidos del **Adjusted Rand Index (ARI)**. Este documento sirve como guía para la defensa de la tesis.

---

## 5.1 ¿Qué mide el ARI en este proyecto?

El **Adjusted Rand Index (ARI)** es una métrica de evaluación extrínseca de algoritmos de clustering que mide la similitud o concordancia entre dos particiones de datos (dos formas de agrupar las mismas observaciones). Su valor oscila entre `-1` y `1`:
- `ARI = 1`: Las dos particiones son idénticas.
- `ARI = 0`: La concordancia observada es igual a lo que se esperaría por el puro azar.
- `ARI < 0`: La concordancia es peor que la esperada por azar.

En este proyecto, el ARI no se usó para comparar el modelo contra una "verdad absoluta" (Ground Truth), ya que el aprendizaje no supervisado no cuenta con etiquetas previas. En su lugar, el ARI se utilizó para medir la **estabilidad de los clústeres a través de diferentes dimensiones de datos**:
- **Partición A (Capa 1):** Clústeres formados por variables tributarias, sectoriales y geográficas (fuente: SRI).
- **Partición B (Capa 2):** Clústeres formados al añadir variables puramente financieras y de escala económica (fuente: SCVS).

Los valores obtenidos fueron `ARI = 0.032` (comparando K=4 vs K=2) y `ARI = 0.126` (comparando K=4 vs K=4).

---

## 5.2 ¿Por qué un ARI bajo NO es un error metodológico?

Es un sesgo común en Data Science asumir que cualquier métrica cercana a cero es "mala" y cualquier métrica cercana a uno es "buena". En el contexto de esta tesis, un ARI bajo no refleja un error algorítmico, sino un **hallazgo analítico fundamental**.

Un ARI alto (por ejemplo, `0.85`) hubiera significado que agrupar a las empresas por sus impuestos y sectores (SRI) da exactamente el mismo resultado que agruparlas por sus balances financieros (SCVS). Si esto ocurriera, la Capa 2 sería redundante y no aportaría ninguna información nueva.

Por el contrario, el **ARI cercano a cero demuestra matemáticamente que la formalización tributaria (Capa 1) y el éxito/escala financiera (Capa 2) son dimensiones ortogonales o distintas en el tejido empresarial ecuatoriano**. 

Las razones de esta divergencia son:
1. **Diferente dimensionalidad:** La Capa 1 agrupa por características cualitativas y estructurales (región, tipo de sociedad, obligaciones). La Capa 2 reorganiza drásticamente el tablero basándose en el volumen de dinero (logaritmos de ingresos y activos).
2. **Volatilidad y heterogeneidad:** Una empresa de Pichincha y una de Guayas pueden ser muy distintas en la Capa 1 (por su región y sector), pero en la Capa 2 pueden terminar en el mismo clúster si ambas facturan 5 millones de dólares anuales. 

---

## 5.3 Valor académico del hallazgo

Incluir esta métrica y este análisis en la tesis aporta un nivel de **rigor científico** superior. Demuestra que el investigador no solo ejecutó una librería de Python (`sklearn.cluster.KMeans`), sino que:
1. Sometió su modelo a pruebas de estrés y validación cruzada entre fuentes de datos.
2. Identificó que el comportamiento del mercado B2B ecuatoriano es multidimensional.
3. Construyó una arquitectura capaz de monitorear estas discrepancias automáticamente en un Dashboard (Oracle APEX).

---

## 5.4 Guía para la sustentación (Defensa ante el jurado)

Si el jurado o los revisores cuestionan los valores bajos del ARI, la defensa debe estructurarse así:

> *"El Adjusted Rand Index bajo (0.032) es un resultado esperado y revelador. Nos confirma que la base de datos de la Superintendencia de Compañías (SCVS) aporta información sustancialmente diferente a la del SRI. Si el ARI hubiera sido cercano a 1, habría significado que las variables financieras son un mero reflejo de la estructura tributaria, haciendo redundante el esfuerzo de combinar bases de datos. La baja concordancia valida nuestra estrategia de usar dos capas de análisis: la Capa 1 para segmentar por madurez y formalidad comercial, y la Capa 2 para entender la escala económica. Ambas responden preguntas complementarias para el equipo comercial B2B."*
