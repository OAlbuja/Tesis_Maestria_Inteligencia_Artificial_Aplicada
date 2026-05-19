# Reporte detallado - Clustering de empresas B2B

**Fecha de actualizacion:** 2026-05-18  
**Proyecto:** Desarrollo_clustering_maestria  
**Fuente operativa:** Golden Record manual `match_final_empresas_verificado.csv`

Este reporte resume la corrida vigente del pipeline despues de revertir la regla de exclusion por pais comercial/origen. El criterio operativo actual es: entra todo registro manual con nombre original, razon social y RUC ecuatoriano valido de 13 digitos. El pais de la empresa queda como trazabilidad, no como filtro de exclusion.

El archivo historico `match_final_empresas.csv` pertenece al carril automatizado de Entity Resolution y no se usa como fuente operativa del modelo final.

---

## 1. Resumen ejecutivo

El modelo se construye en dos capas:

| Capa | Fuente principal | Empresas | Variables de matriz | Clientes FPA | Tasa base |
|---|---|---:|---:|---:|---:|
| Capa 1 | SRI | 181 | 14 | 82 | 45,3% |
| Capa 2 | SRI + ranking SCVS | 141 | 20 | 57 | 40,4% |

Hallazgos principales:

- La Capa 1 se mantiene como modelo principal por cobertura: 181 empresas con RUC unico.
- La Capa 2 opera como enriquecimiento financiero complementario sobre 141 empresas con informacion SCVS.
- `es_cliente_fpa` se conserva solo para validacion externa agregada por cluster; no entra a K-Means.
- Las matrices finales no contienen `es_cliente_fpa`, `source_label` ni variables operativas de proyectos/horas.
- La separacion por clusters muestra una senal comercial relevante en Capa 1: el cluster 1 concentra 65,7% de clientes FPA frente a una tasa base de 45,3%.

---

## 2. Golden Record manual

El Golden Record operativo se genera desde:

```text
02_data_cleaning/data_ruc_universo_empresas/new/
```

Insumos activos principales:

- `leads_ruc_new.xlsx`
- `proyectos_empresa_ruc_new.xlsx`

Insumos historicos no operativos:

- `leads_ruc.xlsx`
- `proyectos_empresa_ruc.xlsx`

Resultados de consolidacion:

| Indicador | Valor |
|---|---:|
| Alias verificados aceptados | 209 |
| RUC unicos verificados | 181 |
| Alias provenientes de leads | 114 |
| Alias provenientes de proyectos/horas | 95 |
| Alias presentes en ambas fuentes manuales | 0 |
| Registros descartados | 312 |
| Conflictos alias -> multiples RUC | 0 |
| Conflictos RUC -> multiples razones sociales | 0 |

Los 312 registros descartados corresponden a registros sin RUC valido y/o sin razon social completa. No existe descarte operativo por pais comercial/origen en la regla vigente.

Interpretacion metodologica:

- `leads.xlsx` representa prospectos comerciales del CRM.
- `proyectos_empresa.xlsx` representa proyectos/horas trabajadas por FPA.
- `es_cliente_fpa = 1` se deriva unicamente de la presencia en proyectos/horas.
- Los resultados se reportan agregados por cluster, no empresa por empresa.

---

## 3. Artefactos operativos

### Feature Engineering

| Archivo | Filas | Columnas | Observacion |
|---|---:|---:|---|
| `features_capa1.csv` | 181 | 13 | SRI + trazabilidad + `es_cliente_fpa`. |
| `features_capa2.csv` | 141 | 20 | SRI + SCVS + trazabilidad + `es_cliente_fpa`. |
| `matriz_capa1.csv` | 181 | 14 | Matriz numerica sin labels ni variables operativas. |
| `matriz_capa2.csv` | 141 | 20 | Matriz numerica sin labels ni variables operativas. |
| `labels_capa1.csv` | 181 | 5 | Identificadores y metadata para evaluacion. |
| `labels_capa2.csv` | 141 | 6 | Identificadores y metadata para evaluacion. |

Validaciones realizadas:

| Validacion | Estado |
|---|---|
| `features_capa1.csv` queda a nivel RUC unico | Cumplido: 181 RUC unicos. |
| `features_capa2.csv` queda a nivel RUC unico | Cumplido: 141 RUC unicos. |
| `matriz_capa1.csv` no contiene `es_cliente_fpa` ni `source_label` | Cumplido. |
| `matriz_capa2.csv` no contiene `es_cliente_fpa` ni `source_label` | Cumplido. |
| Las matrices no contienen variables de horas, facturacion, avance u ocupacion | Cumplido. |
| `labels_capa1.csv` conserva `es_cliente_fpa` | Cumplido: 82 clientes. |
| `labels_capa2.csv` conserva `es_cliente_fpa` | Cumplido: 57 clientes. |

---

## 4. Seleccion de K

### Capa 1 - K-Means

| K | Silhouette | Davies-Bouldin | Min cluster | Max cluster |
|---:|---:|---:|---:|---:|
| 2 | 0,224 | 1,590 | 66 | 115 |
| 3 | 0,192 | 1,838 | 56 | 64 |
| **4** | **0,209** | **1,601** | **35** | **60** |
| 5 | 0,215 | 1,453 | 27 | 44 |
| 6 | 0,208 | 1,529 | 17 | 43 |
| 7 | 0,213 | 1,469 | 11 | 39 |
| 8 | 0,192 | 1,591 | 10 | 29 |

Aunque K=2 obtiene la mayor Silhouette, K=4 se conserva como solucion principal por interpretabilidad y granularidad comercial. Sus clusters tienen tamanos entre 35 y 60 empresas.

### Capa 2 - K-Means

| K | Silhouette | Davies-Bouldin | Min cluster | Max cluster |
|---:|---:|---:|---:|---:|
| **2** | **0,379** | **1,212** | **31** | **110** |
| 3 | 0,197 | 1,605 | 17 | 71 |
| 4 | 0,209 | 1,341 | 3 | 71 |
| 5 | 0,233 | 1,141 | 2 | 84 |
| 6 | 0,172 | 1,299 | 2 | 70 |
| 7 | 0,182 | 1,241 | 2 | 53 |
| 8 | 0,178 | 1,240 | 2 | 42 |

K=2 se mantiene como configuracion de Capa 2 porque evita micro-clusters y ofrece una lectura financiera estable.

---

## 5. Resultados Capa 1

Tasa base Capa 1: **45,3%**  
Contraste chi-cuadrado vs `es_cliente_fpa`: `chi2 = 7,58`, `p = 0,0556`.

| Cluster | Segmento | n | Clientes FPA | Tasa FPA | Diferencia vs base | Cobertura SCVS |
|---:|---|---:|---:|---:|---:|---:|
| 0 | Comercio formal maduro en Pichincha | 46 | 20 | 43,5% | -1,8 pp | 84,8% |
| 1 | Industriales consolidados de alta afinidad FPA | 35 | 23 | 65,7% | +20,4 pp | 62,9% |
| 2 | Comercio formal emergente en Pichincha | 60 | 23 | 38,3% | -7,0 pp | 75,0% |
| 3 | Comercio formal regional en Guayas | 40 | 16 | 40,0% | -5,3 pp | 87,5% |

Lectura:

- El cluster 1 concentra la mayor afinidad historica con FPA.
- La diferencia estadistica queda muy cerca del umbral de 5%, por lo que debe reportarse como tendencia comercial relevante, no como prueba concluyente.
- La cobertura SCVS es suficiente en todos los clusters; la minima observada es 62,9%.

---

## 6. Resultados Capa 2

Tasa base Capa 2: **40,4%**  
Contraste chi-cuadrado vs `es_cliente_fpa`: `chi2 = 0,16`, `p = 0,6883`.

| Cluster | Segmento | n | Clientes FPA | Tasa FPA | Diferencia vs base |
|---:|---|---:|---:|---:|---:|
| 0 | Empresas grandes consolidadas | 110 | 43 | 39,1% | -1,3 pp |
| 1 | Empresas medianas y recientes de alta afinidad | 31 | 14 | 45,2% | +4,7 pp |

Lectura:

- La Capa 2 agrega profundidad financiera, pero separa menos la afinidad historica con FPA que la Capa 1.
- Su valor principal es complementar la interpretacion con tamano, empleados, ingresos, activos, liquidez y margen operacional.

---

## 7. Concordancia entre capas

| Comparacion | Empresas comunes | ARI |
|---|---:|---:|
| C1 K=4 vs C2 K=2 | 141 | 0,0315 |
| C1 K=4 vs C2 K=4 | 141 | 0,1258 |

La concordancia es baja. Esto es esperable porque la Capa 2 incorpora variables financieras que no existen en Capa 1 y trabaja sobre un subconjunto de empresas. La tesis debe presentar la Capa 2 como enriquecimiento complementario, no como reemplazo del modelo principal.

---

## 8. Figuras exportadas

Las figuras actuales se encuentran en:

```text
05_evaluation/outputs/
```

Archivos principales:

- `fig_seleccion_k_kmeans.png`
- `fig_silhouette_muestras_c1.png`
- `fig_pca_capa1.png`
- `fig_tsne_capa1.png`
- `fig_pca_capa2.png`
- `fig_tasa_fpa_por_cluster.png`
- `fig_cobertura_vs_fpa.png`

---

## 9. Conclusion para tesis

El resultado final valida la separacion metodologica entre:

1. un carril automatizado de Entity Resolution, usado como diagnostico y propuesta futura, y
2. un Golden Record manual, usado como fuente operativa para construir las matrices del modelo.

La Capa 1 es el modelo principal porque maximiza cobertura y mantiene variables publicas replicables. La Capa 2 aporta interpretacion financiera adicional, pero no sustituye a la Capa 1. En ambos casos, la etiqueta `es_cliente_fpa` queda fuera del entrenamiento y se utiliza solo para validar, de forma agregada, si los clusters tienen sentido comercial para FPA.
