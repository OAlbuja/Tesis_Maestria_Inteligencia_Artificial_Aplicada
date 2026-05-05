# Pipeline completo — qué se hace, en qué orden y por qué

## Paso 0 — Punto de partida

**Archivo:** `match_final_empresas.csv`

**Contiene:** 177 empresas con nombre normalizado + RUC verificado.

**Por qué es el punto de partida:**  
Es el único archivo que conecta los nombres de leads de FPA con el mundo de datos públicos. Sin el RUC limpio no hay `JOIN` posible con ninguna fuente.

---

## Paso 1 — Agregar `es_cliente_fpa` al archivo base

**Qué hace:**  
Cruza los nombres de `match_final_empresas.csv` con los nombres únicos de `proyectos_empresa.xlsx` y agrega una columna `es_cliente_fpa` con valores `1/0`.

**Por qué aquí:**  
Necesitas tener esta etiqueta disponible desde el inicio para que acompañe a cada empresa a lo largo de todo el pipeline.

No se crea en el notebook de clustering. Se crea aquí, en el origen, para que quede registrado en el archivo base.

**Resultado:**  
`match_final_empresas.csv` actualizado con la columna `es_cliente_fpa`.

---

## Paso 2 — Feature Engineering Capa 1

**Notebook:** `01_base_sri.ipynb`

### Qué hace

1. Carga `match_final_empresas.csv` y limpia el RUC usando:

   ```python
   str.zfill(13)
   ```

2. Carga los 26 archivos `SRI_RUC_*.csv` y los consolida en un solo DataFrame.

3. Deduplica por RUC usando `keep first`.

   Esto significa que si una empresa aparece en dos provincias, se conserva la primera aparición.

4. Realiza un `JOIN` izquierdo:

   ```text
   match_final ← SRI por RUC
   ```

5. Construye las 8 features:

   ### Variables binarias directas

   - `tipo_sociedad`
   - `obligado_contabilidad`
   - `es_agente_retencion`
   - `es_contribuyente_especial`
   - `estado_activo`

   ### Variable numérica continua

   - `antiguedad_anos`

   Fórmula:

   ```text
   antiguedad_anos = 2026 − año(FECHA_INICIO_ACTIVIDADES)
   ```

   ### Variables categóricas aún sin dummies

   - `sector_ciiu_macro`

     Se obtiene usando la primera letra del CIIU.

   - `region`

     Valores posibles:

     - `Pichincha`
     - `Guayas`
     - `Resto`

6. Exporta el archivo:

   ```text
   03_feature_engineering/outputs/features_capa1.csv
   ```

### Por qué se usa `JOIN` izquierdo

Se usa para conservar las 177 empresas aunque alguna no tenga datos SRI.

Las empresas que no encuentren coincidencia quedarán con valores `NaN`, lo cual debe documentarse como una limitación.

### Por qué se deduplica por RUC

Una empresa puede estar registrada en más de una provincia si tiene establecimientos en varias ubicaciones.

Para el modelo se necesita una sola fila por empresa, normalmente la asociada a su domicilio principal.

### Resultado

```text
163 empresas × 8 features
```

Las variables todavía no están codificadas.

---

## Paso 3 — Feature Engineering Capa 2

**Notebook:** `02_enriquecimiento_ranking.ipynb`

### Qué hace

1. Carga `features_capa1.csv`.

   Solo contiene las 163 empresas con datos SRI.

2. Carga `directorio_companias.xlsx` usando:

   ```python
   skiprows=4
   ```

3. Extrae el par:

   ```text
   RUC ↔ EXPEDIENTE
   ```

4. Realiza un `JOIN`:

   ```text
   features_capa1 ← directorio por RUC
   ```

   Con esto obtiene el expediente SCVS.

5. Carga `bi_ranking.csv`.

6. Filtra el ranking por los expedientes de las empresas del proyecto.

7. Para cada empresa toma el último año fiscal disponible:

   ```text
   sort por anio desc
   drop_duplicates por expediente
   ```

8. Realiza un `JOIN`:

   ```text
   resultado anterior ← ranking por expediente
   ```

9. Construye las 6 features financieras:

   - `log_empleados`

     ```text
     log_empleados = log10(n_empleados + 1)
     ```

   - `log_ingresos`

     ```text
     log_ingresos = log10(ingresos_ventas + 1)
     ```

   - `log_activos`

     ```text
     log_activos = log10(activos + 1)
     ```

   - `segmento`

     Corresponde a `cod_segmento`, tratado como variable ordinal de 1 a 4.

   - `liquidez_corriente`

     Valor crudo, con clip en percentil 99 para controlar outliers extremos.

   - `margen_operacional`

     Valor crudo, con clip en percentil 99.

10. Exporta el archivo:

   ```text
   03_feature_engineering/outputs/features_capa2.csv
   ```

### Por qué se usa el último año fiscal

El ranking tiene hasta 17 años de historia por empresa.

Para segmentar empresas, lo relevante es el estado actual del negocio, no todo el histórico.

### Por qué se aplica clip en percentil 99

La liquidez corriente puede tener valores extremadamente altos en empresas pequeñas con deudas mínimas.

Por ejemplo, una liquidez de `5000` puede destruir la escala del modelo.

Aplicar clip al percentil 99 preserva la distribución real sin permitir que un caso extremo distorsione el clustering.

### Resultado

```text
93 empresas × 14 features
```

Incluye:

- 8 features provenientes del SRI.
- 6 features financieras.

Las variables todavía no están codificadas.

---

## Paso 4 — Construcción de matrices finales

**Notebook:** `03_matriz_final.ipynb`

En este paso se construyen dos matrices paralelas.

---

## Matriz Capa 1

**Cantidad de empresas:** `N = 163`

### Qué hace

1. Carga `features_capa1.csv`.

2. Aplica one-hot encoding a:

   - `sector_ciiu_macro`
   - `region`

3. Aplica `StandardScaler` a:

   - `antiguedad_anos`

4. Las variables binarias `0/1` no se escalan.

5. Exporta:

   ```text
   matriz_capa1.csv
   ```

### Resultado

`matriz_capa1.csv` queda lista para clustering.

---

## Matriz Capa 2

**Cantidad de empresas:** `N = 93`

### Qué hace

1. Carga `features_capa2.csv`.

2. Aplica one-hot encoding a:

   - `sector_ciiu_macro`
   - `region`

3. Aplica `StandardScaler` a:

   - `antiguedad_anos`
   - `log_empleados`
   - `log_ingresos`
   - `log_activos`

4. También escala:

   - `liquidez_corriente`
   - `margen_operacional`
   - `segmento`

5. Exporta:

   ```text
   matriz_capa2.csv
   ```

### Resultado

`matriz_capa2.csv` queda lista para clustering.

---

## Justificación técnica del preprocesamiento

### Por qué one-hot encoding y no label encoding

K-Means usa distancia euclidiana.

Si se codifican sectores como:

```text
G = 1
C = 2
M = 3
```

el modelo interpretaría que `M` está más cerca de `C` que de `G`.

Eso sería falso, porque son categorías sin orden natural.

Por eso se usa one-hot encoding, ya que elimina esa jerarquía artificial.

### Por qué escalar solo las numéricas y no las binarias

Las variables binarias ya están en rango `[0,1]`.

Escalarlas no aporta valor y puede introducir ruido.

Lo mismo ocurre con las variables dummy generadas por one-hot encoding: también son `0/1`, por lo que no se escalan.

### Por qué usar StandardScaler y no MinMaxScaler

`StandardScaler` es más robusto frente a outliers.

`MinMaxScaler` comprime todo al rango `[0,1]`, pero si existe un outlier extremo, toda la distribución queda aplastada en un rango muy pequeño.

### Resultado general del Paso 4

Se obtienen dos matrices numéricas limpias, escaladas y listas para aplicar K-Means.

---

## Paso 5 — Clustering

**Notebook:** `04_modeling/01_clustering.ipynb`

---

## Exploración inicial

Se aplica clustering jerárquico con método Ward sobre Capa 1.

```text
Clustering jerárquico → Ward linkage → dendrograma visual
```

### Objetivo

Identificar valores candidatos de `K`, observando dónde se puede cortar naturalmente el árbol del dendrograma.

---

## Selección de K

Se aplica K-Means sobre Capa 1 con los siguientes valores:

```text
K = 3, 4, 5, 6
```

Para cada valor de `K`, se calculan las siguientes métricas:

- `WCSS`

  Usado para el método del codo o elbow method.

- `Silhouette Score`

  Mide qué tan bien separadas están las empresas entre clusters.

- `Davies-Bouldin Index`

  Mide la compacidad y separación de los clusters.

### Criterio de elección

Se elige el valor de `K` donde las tres métricas confluyen en una solución razonable.

---

## Modelo principal

Se entrena K-Means con el `K` elegido sobre:

```text
matriz_capa1.csv
```

Luego se guardan las etiquetas de cluster:

```text
cluster_capa1
```

para cada empresa.

---

## Análisis de soporte

Se repite el mismo proceso sobre:

```text
matriz_capa2.csv
```

Luego se guardan las etiquetas:

```text
cluster_capa2
```

---

## Comparación de robustez

Para las 93 empresas que están presentes en ambas capas, se compara si los clusters coinciden.

Se calcula el índice:

```text
Adjusted Rand Index — ARI
```

### Criterio

```text
Si ARI > 0.6 → modelo robusto
```

---

## Validación externa

Para cada cluster se calcula:

```text
es_cliente_fpa.mean()
```

Esto representa la tasa de conversión del segmento.

Luego se visualiza mediante un gráfico de barras por cluster.

### Resultado del Paso 5

Se obtiene:

- Etiquetas de segmento para 163 empresas.
- Perfiles interpretados por cluster.
- Tasa de conversión FPA por segmento.

---

# Resumen visual del pipeline completo

```text
match_final_empresas.csv (177 empresas)
        |
        v
    PASO 1
[Agregar es_cliente_fpa] + proyectos_empresa.xlsx
        |
        +------------------------------------------------+
        |                                                |
        v                                                v
    PASO 2                                           PASO 3
[JOIN x SRI]                              [JOIN x directorio SCVS x ranking]
features_capa1.csv (163 x 8)             features_capa2.csv (93 x 14)
        |                                                |
        v                                                v
    PASO 4a                                          PASO 4b
[Encoding + Scaling]                     [Encoding + Scaling]
matriz_capa1.csv (163 x ~14)             matriz_capa2.csv (93 x ~20)
        |                                                |
        +-----------------------+------------------------+
                                |
                                v
                            PASO 5
                [Hierarchical + dendrograma]
                [K-Means K=3..6 + métricas]
                [Elegir K óptimo]
                [Asignar clusters]
                [Validar con es_cliente_fpa]
                [Interpretar y nombrar segmentos]
```

---

# Aclaración sobre `es_cliente_fpa`

## Pregunta

¿No habíamos dicho que no íbamos a agregar la columna para validar si es o no es cliente FPA porque sería hacer trampa?

## Respuesta

Sí, la preocupación es correcta, pero no hay contradicción.

La clave está en diferenciar **en qué archivo se agrega** y **para qué se usa**.

---

## Distinción clave

| Archivo | ¿Se agrega `es_cliente_fpa`? | ¿Para qué? |
|---|---:|---|
| `match_final_empresas.csv` | Sí | Es metadata del negocio. Es un atributo de cada empresa que debe quedar registrado en el archivo base. |
| `features_capa1.csv` | Sí | Viaja como columna, pero marcada como “no usar en modelo”. |
| `matriz_capa1.csv` | No | Este es el input real del K-Means. Aquí la columna no existe. |
| K-Means | Nunca la ve | El algoritmo solo recibe la matriz sin `es_cliente_fpa`. |
| Después del clustering | Sí se usa | Se usa para validar qué clusters coinciden con clientes reales. |

---

## En términos simples

Agregar `es_cliente_fpa` al CSV base no es trampa, porque ese archivo es solo un registro de la realidad.

Lo que sí sería trampa es meter esa columna dentro de `matriz_capa1.csv`, que es lo que K-Means consume.

---

## Analogía

Tienes una lista de estudiantes con su nota final ya publicada.

Guardar esa nota en el archivo de estudiantes no es trampa.

Lo que sería trampa es darle esa nota al modelo cuando le pides que prediga quién va a aprobar.

---

## Flujo correcto

```text
match_final_empresas.csv
        |
        | incluye es_cliente_fpa como metadata
        v
features_capa1.csv
        |
        | es_cliente_fpa se conserva solo como referencia
        v
matriz_capa1.csv
        |
        | es_cliente_fpa se excluye
        v
K-Means
        |
        | el modelo no ve es_cliente_fpa
        v
clusters
        |
        | después se compara contra es_cliente_fpa
        v
validación externa
```

---

## Conclusión

No hay fuga de información mientras `es_cliente_fpa` no entre en la matriz usada por K-Means.

La regla de oro es:

```text
es_cliente_fpa puede existir en archivos de trazabilidad,
pero jamás debe entrar como feature del modelo.
```
