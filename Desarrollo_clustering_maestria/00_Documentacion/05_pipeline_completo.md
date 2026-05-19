# Pipeline completo del proyecto

Este documento resume que se ejecuta, en que orden y que artefactos deben quedar disponibles para reproducir el modelo de segmentacion. La version actual usa como entrada operacional el Golden Record manual:

```text
02_data_cleaning/data_ruc_universo_empresas/match_final_empresas_verificado.csv
```

El archivo historico `match_final_empresas.csv` pertenece al carril automatizado de Entity Resolution y se conserva como baseline experimental, no como fuente final del modelo.

El Golden Record final se construye unicamente desde los archivos manuales nuevos ubicados en `02_data_cleaning/data_ruc_universo_empresas/new/`. Los archivos antiguos `leads_ruc.xlsx` y `proyectos_empresa_ruc.xlsx`, ubicados fuera de `new/`, quedan como historicos y no forman parte del pipeline vigente.

El alcance del Golden Record se define por la disponibilidad de un RUC ecuatoriano verificado manualmente. El pais comercial u origen del lead queda como trazabilidad, pero no excluye un registro cuando existe razon social ecuatoriana validada por la revision manual.

---

## 1. Vista general

```text
Fuentes internas
leads.xlsx + proyectos_empresa.xlsx
        |
        v
02_data_cleaning/01_staging_empresas_normalizadas.ipynb
        |
        +--> Carril automatizado baseline
        |    02_matching_exacto_scvs.ipynb
        |    outputs exactos/difusos para diagnostico y productizacion futura
        |
        +--> Carril manual Golden Record
             data_ruc_universo_empresas/new/*.xlsx|*.csv
             08_consolidacion_ground_truth_manual.ipynb
             match_final_empresas_verificado.csv
                    |
                    v
03_feature_engineering/01_base_sri.ipynb
                    |
                    v
03_feature_engineering/02_enriquecimiento_ranking.ipynb
                    |
                    v
03_feature_engineering/03_matriz_final.ipynb
                    |
                    v
04_modeling/01_clustering.ipynb
                    |
                    v
05_evaluation/01_evaluacion_clustering.ipynb
                    |
                    v
06_reporting/reporte_clustering_detallado.*
```

---

## 2. Orden de ejecucion recomendado

| Orden | Notebook / artefacto | Rol | Salida esperada |
|---:|---|---|---|
| 0 | `01_data_ingestion_enrichment/01_profiling_fuentes_validacion_join.ipynb` | Diagnostico inicial del problema de JOIN por nombre. | Evidencia de la brecha entre nombres comerciales y registros oficiales. |
| 1 | `02_data_cleaning/01_staging_empresas_normalizadas.ipynb` | Normaliza nombres y arma universo interno. | `leads_companies_clean.csv`, `horas_empresas_clean.csv`, `empresas_universe_compilado.csv`. |
| 2 | `02_data_cleaning/02_matching_exacto_scvs.ipynb` | Baseline automatizado exacto/difuso contra SCVS. | Outputs de diagnostico y sugerencias, no usados como verdad final. |
| 3 | `02_data_cleaning/08_consolidacion_ground_truth_manual.ipynb` | Consolida archivos manuales nuevos de RUC desde `data_ruc_universo_empresas/new/`, aplicando validaciones de RUC, nombre y razon social. | `match_final_empresas_verificado.csv`. |
| 4 | `03_feature_engineering/01_base_sri.ipynb` | Une Golden Record con SRI y crea Capa 1. | `features_capa1.csv`. |
| 5 | `03_feature_engineering/02_enriquecimiento_ranking.ipynb` | Enriquece con SCVS y crea Capa 2. | `features_capa2.csv`. |
| 6 | `03_feature_engineering/03_matriz_final.ipynb` | Codifica, escala e imputa matrices. | `matriz_capa1.csv`, `matriz_capa2.csv`, `labels_capa1.csv`, `labels_capa2.csv`. |
| 7 | `04_modeling/01_clustering.ipynb` | Entrena K-Means y perfila segmentos. | `clusters_capa1.csv`, `clusters_capa2.csv`, metricas y perfiles. |
| 8 | `05_evaluation/01_evaluacion_clustering.ipynb` | Evalua estabilidad, cobertura y tasa FPA por cluster. | Tablas de validacion y figuras. |
| 9 | `06_reporting/reporte_clustering_detallado.md` | Reporte derivado para comunicacion. | Documento de resultados. |

Los notebooks historicos de matching difuso, torneo de catalogos o auditoria LLM pueden ejecutarse para investigacion adicional, pero no son prerrequisito del pipeline final mientras se use el Golden Record manual.

Interpretacion de las fuentes internas:

| Fuente | Interpretacion en el pipeline |
|---|---|
| `leads.xlsx` | Prospectos registrados en CRM. Se tratan como no clientes salvo que el mismo RUC tambien aparezca en proyectos. |
| `proyectos_empresa.xlsx` | Registro de horas/proyectos por empresa. Se usa para identificar clientes historicos de FPA mediante `es_cliente_fpa = 1`. |

Las columnas operativas de `proyectos_empresa.xlsx` no entran a `matriz_capa1.csv` ni `matriz_capa2.csv`. Solo alimentan la etiqueta externa de validacion.

---

## 3. Comandos de ejecucion

Desde la raiz del repositorio:

```powershell
jupyter nbconvert --to notebook --execute --inplace "02_data_cleaning/01_staging_empresas_normalizadas.ipynb" --ExecutePreprocessor.timeout=1200
jupyter nbconvert --to notebook --execute --inplace "02_data_cleaning/02_matching_exacto_scvs.ipynb" --ExecutePreprocessor.timeout=1200
jupyter nbconvert --to notebook --execute --inplace "02_data_cleaning/08_consolidacion_ground_truth_manual.ipynb" --ExecutePreprocessor.timeout=1200
jupyter nbconvert --to notebook --execute --inplace "03_feature_engineering/01_base_sri.ipynb" --ExecutePreprocessor.timeout=1200
jupyter nbconvert --to notebook --execute --inplace "03_feature_engineering/02_enriquecimiento_ranking.ipynb" --ExecutePreprocessor.timeout=1200
jupyter nbconvert --to notebook --execute --inplace "03_feature_engineering/03_matriz_final.ipynb" --ExecutePreprocessor.timeout=1200
jupyter nbconvert --to notebook --execute --inplace "04_modeling/01_clustering.ipynb" --ExecutePreprocessor.timeout=1200
jupyter nbconvert --to notebook --execute --inplace "05_evaluation/01_evaluacion_clustering.ipynb" --ExecutePreprocessor.timeout=1200
```

Nota operativa: en este ambiente aparece un mensaje de perfil de PowerShell/conda al iniciar comandos. No impidio la ejecucion de los notebooks; se valida por el codigo de salida y por la actualizacion de los artefactos.

---

## 4. Contrato de artefactos actual

### Staging

| Archivo | Filas | Columnas |
|---|---:|---:|
| `02_data_cleaning/outputs/leads_companies_clean.csv` | 326 | 4 |
| `02_data_cleaning/outputs/horas_empresas_clean.csv` | 119 | 4 |
| `02_data_cleaning/outputs/empresas_universe_compilado.csv` | 445 | 9 |

### Baseline automatizado

| Archivo | Filas | RUC no nulos | RUC unicos |
|---|---:|---:|---:|
| `leads_ruc_exact.csv` | 326 | 12 | 12 |
| `horas_ruc_exact.csv` | 119 | 22 | 22 |
| `leads_ruc_sugerido_scvs.csv` | 205 | 205 | 192 |
| `horas_ruc_sugerido_scvs.csv` | 71 | 71 | 70 |

Estos outputs se documentan como evidencia del problema de resolucion de entidades. No deben reemplazar al Golden Record sin validacion humana.

### Golden Record manual

Insumos activos:

```text
02_data_cleaning/data_ruc_universo_empresas/new/leads_ruc_new.xlsx
02_data_cleaning/data_ruc_universo_empresas/new/proyectos_empresa_ruc_new.xlsx
```

Insumos historicos que no deben usarse en el pipeline vigente:

```text
02_data_cleaning/data_ruc_universo_empresas/leads_ruc.xlsx
02_data_cleaning/data_ruc_universo_empresas/proyectos_empresa_ruc.xlsx
```

| Archivo | Filas | RUC unicos | Observacion |
|---|---:|---:|---|
| `match_final_empresas_verificado.csv` | 209 | 181 | Alias verificados manualmente. |
| `match_final_empresas_verificado_descartados.csv` | 312 | - | Registros descartados o incompletos. |
| `match_final_empresas_verificado_conflictos_alias.csv` | 0 | - | Sin alias conflictivos. |
| `match_final_empresas_verificado_conflictos_ruc.csv` | 0 | - | Sin RUC conflictivos. |

### Feature Engineering

| Archivo | Filas | Columnas | Observacion |
|---|---:|---:|---|
| `features_capa1.csv` | 181 | 13 | SRI + trazabilidad + `es_cliente_fpa`. |
| `features_capa2.csv` | 141 | 20 | SRI + SCVS + trazabilidad + `es_cliente_fpa`. |
| `matriz_capa1.csv` | 181 | 14 | Matriz numerica sin `es_cliente_fpa`. |
| `matriz_capa2.csv` | 141 | 20 | Matriz numerica sin `es_cliente_fpa`. |
| `labels_capa1.csv` | 181 | 5 | Identificadores y metadata para unir etiquetas. |
| `labels_capa2.csv` | 141 | 6 | Identificadores y metadata para unir etiquetas. |

### Modelado y evaluacion

| Archivo | Filas | Descripcion |
|---|---:|---|
| `04_modeling/outputs/clusters_capa1.csv` | 181 | Segmentos principales K-Means, K=4. |
| `04_modeling/outputs/clusters_capa2.csv` | 141 | Segmentos financieros K-Means, K=2. |
| `05_evaluation/outputs/validacion_externa_capa1.csv` | 4 | Tasa de clientes por cluster Capa 1. |
| `05_evaluation/outputs/validacion_externa_capa2.csv` | 2 | Tasa de clientes por cluster Capa 2. |
| `05_evaluation/outputs/tabla_concordancia_ari.csv` | 2 | Concordancia entre capas. |

---

## 5. Validaciones obligatorias

Antes de usar los resultados en la tesis, se deben cumplir estas condiciones:

| Validacion | Estado actual |
|---|---|
| El modelo usa `match_final_empresas_verificado.csv`, no `match_final_empresas.csv`. | Cumplido. |
| `features_capa1.csv` tiene una sola fila por RUC. | Cumplido: 181 RUC unicos. |
| `features_capa2.csv` tiene una sola fila por RUC. | Cumplido: 141 RUC unicos. |
| Las matrices no contienen `es_cliente_fpa`. | Cumplido. |
| Las matrices no contienen nulos. | Cumplido. |
| `source_winner` identifica el origen manual del RUC. | Cumplido: `GROUND_TRUTH_MANUAL`. |
| La evaluacion no asume cobertura financiera nula en ningun cluster. | Cumplido: la cobertura minima observada es 62,9%. |

---

## 6. Decision sobre el archivo antiguo `match_final_empresas.csv`

El archivo antiguo no se elimina conceptualmente. Se reclasifica como salida del carril automatizado de investigacion.

En la tesis debe explicarse asi:

> Durante la investigacion se implemento un pipeline automatizado de resolucion de entidades para vincular nombres comerciales del CRM con registros oficiales. Este pipeline permitio estimar la dificultad del problema y generar candidatos plausibles, pero no alcanzo el nivel de certeza requerido para usar sus salidas como base del modelo no supervisado. Por ello, para la etapa final se construyo un Golden Record manual de RUCs verificados, mientras que el pipeline automatizado queda como propuesta de productizacion futura asistida por revision humana.

Esto evita presentar el trabajo automatizado como un intento fallido. Su rol correcto es de baseline, diagnostico y propuesta futura.

---

## 7. Flujo correcto de `es_cliente_fpa`

```text
proyectos_empresa.xlsx
        |
        | presencia del RUC en proyectos/horas => es_cliente_fpa = 1
        v
features_capa1.csv / features_capa2.csv
        |
        | conservan es_cliente_fpa como metadata
        v
matriz_capa1.csv / matriz_capa2.csv
        |
        | excluyen es_cliente_fpa
        v
K-Means
        |
        | genera clusters sin conocer quienes son clientes
        v
validacion externa
        |
        | compara tasa de clientes por segmento
        v
interpretacion comercial
```

La regla de oro es:

```text
es_cliente_fpa puede viajar como metadata,
pero nunca puede entrar como feature del clustering.
```

---

## 8. Salidas finales para redaccion de tesis

Los archivos mas importantes para redactar resultados son:

| Proposito | Archivo |
|---|---|
| Perfil de segmentos Capa 1 | `04_modeling/outputs/perfil_clusters_capa1.csv` |
| Perfil de segmentos Capa 2 | `04_modeling/outputs/perfil_clusters_capa2.csv` |
| Validacion externa Capa 1 | `05_evaluation/outputs/validacion_externa_capa1.csv` |
| Validacion externa Capa 2 | `05_evaluation/outputs/validacion_externa_capa2.csv` |
| Cobertura financiera por cluster | `05_evaluation/outputs/cobertura_financiera_por_cluster.csv` |
| Concordancia entre capas | `05_evaluation/outputs/tabla_concordancia_ari.csv` |

Estos archivos deben ser la fuente principal para tablas del capitulo de resultados.
