# 3. Preparacion y enriquecimiento de datos

Este documento describe la preparacion de las fuentes internas de FPA Latam, la resolucion de entidades empresariales y la construccion del archivo maestro que habilita el enriquecimiento con fuentes publicas oficiales de Ecuador. La version actual del proyecto separa explicitamente dos carriles metodologicos:

- **Carril automatizado o baseline experimental:** normalizacion, matching exacto/difuso y auditoria automatizada. Su funcion es demostrar empiricamente la dificultad de resolver empresas a partir de nombres comerciales y dejar una base productizable para futuros leads.
- **Carril manual o Golden Record:** diccionario verificado manualmente con RUC y razon social, construido a partir de busquedas en SRI para empresas con identificador ecuatoriano disponible. Este es el insumo operativo usado para el modelo final de machine learning.

La distincion es central para la tesis: el modelo final no depende de matches probabilisticos, sino de un identificador oficial verificado por empresa.

---

## 3.1 Fuentes de datos utilizadas

El proyecto parte de dos fuentes internas de FPA Latam:

| Fuente | Archivo | Rol en el proyecto |
|---|---|---|
| Leads comerciales | `leads.xlsx` | Universo historico de prospectos B2B del CRM. Se interpreta como empresas capturadas comercialmente que no necesariamente han concretado proyecto. |
| Proyectos ejecutados o activos | `proyectos_empresa.xlsx` | Registro operativo de proyectos/horas por empresa: horas estimadas, horas ejecutadas, facturacion, avance y responsable. La presencia de una empresa aqui evidencia relacion de cliente o proyecto con FPA. |

Estas fuentes contienen nombres de empresas, datos comerciales y variables operativas, pero no incluyen de forma sistematica RUC ni razon social. Por esta razon no pueden conectarse directamente con fuentes publicas ecuatorianas.

Para efectos del modelo, `proyectos_empresa.xlsx` no se usa como fuente de variables de clustering. Sus variables de horas, facturacion y avance son consecuencia de haber trabajado con FPA y podrian introducir fuga de informacion. Su uso se limita a construir la etiqueta externa `es_cliente_fpa`, que permite validar despues del clustering que segmentos concentran mayor proporcion historica de clientes.

Las fuentes publicas utilizadas para enriquecimiento son:

| Fuente publica | Uso principal |
|---|---|
| Catastro RUC del SRI | Obtencion de atributos tributarios, ubicacion, actividad economica, estado y antiguedad. |
| Directorio de companias SCVS | Vinculacion entre RUC y expediente societario. |
| Ranking financiero SCVS | Incorporacion de variables financieras y de tamano empresarial para la Capa 2. |

---

## 3.2 Problema estructural del CRM

El obstaculo principal identificado fue que las fuentes internas registran mayoritariamente el **nombre comercial** o una variante informal de la empresa, mientras que las bases oficiales se organizan alrededor del **RUC** y la **razon social**.

Ejemplos habituales de este problema son:

- Empresas registradas en el CRM con marca comercial, pero inscritas en SRI con razon social distinta.
- Abreviaturas, tildes, sufijos legales, nombres incompletos o nombres de grupo empresarial.
- Leads internacionales o marcas globales que pueden tener sociedades registradas en Ecuador, lo cual exige verificacion manual para no depender solamente de similitud textual.
- Multiples alias comerciales asociados a un mismo RUC.

El notebook `01_data_ingestion_enrichment/01_profiling_fuentes_validacion_join.ipynb` documenta este problema de forma exploratoria. Su aporte principal es mostrar que un JOIN directo por nombre no es suficiente para conectar CRM y fuentes oficiales.

Para el modelo final, el criterio operativo es la existencia de un RUC ecuatoriano verificado manualmente. El pais comercial u origen del lead queda como trazabilidad, pero no excluye un registro si la revision manual encontro una razon social ecuatoriana valida. Esta regla mantiene el foco en empresas integrables con SRI/SCVS y evita que el pipeline dependa de inferencias automaticas por similitud de marca.

---

## 3.3 Staging y normalizacion de empresas

El notebook `02_data_cleaning/01_staging_empresas_normalizadas.ipynb` prepara el universo inicial de empresas. Su funcion no es asignar RUC, sino limpiar y estandarizar nombres para habilitar comparaciones posteriores.

El proceso aplicado a cada nombre incluye:

1. Conversion a texto y eliminacion de espacios extremos.
2. Remocion de tildes y caracteres especiales.
3. Conversion a mayusculas.
4. Eliminacion de sufijos legales y conectores frecuentes.
5. Colapso de espacios multiples.
6. Construccion de una clave normalizada `name_norm`.

Los artefactos actuales de esta etapa son:

| Output | Registros | Columnas | Descripcion |
|---|---:|---:|---|
| `02_data_cleaning/outputs/leads_companies_clean.csv` | 326 | 4 | Empresas unicas provenientes de leads. |
| `02_data_cleaning/outputs/horas_empresas_clean.csv` | 119 | 4 | Empresas unicas provenientes de proyectos. |
| `02_data_cleaning/outputs/empresas_universe_compilado.csv` | 445 | 9 | Universo integrado LEADS + HORAS, manteniendo trazabilidad por fuente. |

Este universo normalizado se usa en el carril automatizado y como evidencia del volumen de entidades que originalmente debian resolverse.

---

## 3.4 Carril automatizado: baseline de Entity Resolution

El carril automatizado se conserva como componente metodologico del proyecto, pero no alimenta directamente el modelo final. Su objetivo fue evaluar hasta que punto era posible resolver automaticamente el RUC a partir de nombres comerciales.

### Matching exacto contra SCVS

El notebook `02_data_cleaning/02_matching_exacto_scvs.ipynb` compara los nombres normalizados del CRM contra el Directorio de Companias de la SCVS.

| Output | Registros evaluados | RUC no nulos | RUC unicos |
|---|---:|---:|---:|
| `leads_ruc_exact.csv` | 326 | 12 | 12 |
| `horas_ruc_exact.csv` | 119 | 22 | 22 |

La cobertura exacta es baja, especialmente en leads. Este resultado confirma que la similitud textual exacta no resuelve el problema estructural del CRM.

### Matching difuso como generador de candidatos

El pipeline tambien genera sugerencias difusas con RapidFuzz/SCVS:

| Output | Candidatos sugeridos | RUC unicos |
|---|---:|---:|
| `leads_ruc_sugerido_scvs.csv` | 205 | 192 |
| `horas_ruc_sugerido_scvs.csv` | 71 | 70 |

Estas sugerencias son utiles como aproximacion y como posible herramienta de productividad futura. Sin embargo, en la version final de la tesis no se tratan como verdad operacional, porque una alta similitud lexica no garantiza identidad legal cuando se trabaja con nombres comerciales.

### Interpretacion metodologica

El carril automatizado no se descarta como trabajo inutil. Su valor para la tesis es triple:

1. Evidencia empiricamente que el CRM carece de una llave oficial para integrarse con datos publicos.
2. Justifica la construccion de un Golden Record manual para proteger la validez interna del modelo.
3. Queda como propuesta de productizacion: para nuevos leads, puede sugerir candidatos y reducir el esfuerzo humano de verificacion.

Por esta razon, archivos historicos como `match_final_empresas.csv` deben entenderse como salidas del experimento automatizado, no como fuente final del modelo de clustering.

---

## 3.5 Golden Record manual

Ante la insuficiencia del matching automatico para garantizar 100% de precision, se construyo un diccionario manual de alias empresariales. Este diccionario conecta el nombre observado en el CRM con su razon social y RUC verificados.

El notebook operativo de esta etapa es:

```text
02_data_cleaning/08_consolidacion_ground_truth_manual.ipynb
```

El notebook lee todos los archivos ubicados en:

```text
02_data_cleaning/data_ruc_universo_empresas/new/
```

Los insumos manuales activos son exclusivamente `leads_ruc_new.xlsx` y `proyectos_empresa_ruc_new.xlsx`, ubicados en esa carpeta. Los archivos antiguos ubicados fuera de `new/`, como `leads_ruc.xlsx` y `proyectos_empresa_ruc.xlsx`, se consideran historicos y no deben usarse para reconstruir el Golden Record.

Adicionalmente, antes de consolidar se aplica una regla de calidad: se aceptan registros con nombre original, razon social y RUC ecuatoriano de 13 digitos verificados manualmente. El pais comercial u origen no funciona como filtro de exclusion; se conserva como dato de auditoria.

El notebook consolida la revision manual en:

```text
02_data_cleaning/data_ruc_universo_empresas/match_final_empresas_verificado.csv
```

La estructura clave del archivo final es:

| Columna | Descripcion |
|---|---|
| `nombre_original` | Alias o nombre comercial observado en la fuente interna. |
| `nombre_original_norm` | Version normalizada del alias. |
| `razon_social` | Razon social verificada manualmente. |
| `razon_social_norm` | Version normalizada de la razon social. |
| `ruc` | Identificador oficial de 13 digitos. |
| `pais_empresa` | Pais asociado cuando la revision manual lo incluyo; se conserva para trazabilidad, no como variable de clustering. |
| `sede_ecuador` | Indicador auxiliar de presencia/localizacion en Ecuador; complementa la auditoria manual pero no reemplaza al RUC verificado. |
| `n_apariciones` | Numero de apariciones consolidadas del alias. |
| `fuentes` | Archivo y fila de origen usados para trazabilidad. |

### Resultados de consolidacion

| Indicador | Valor |
|---|---:|
| Alias verificados aceptados | 209 |
| RUC unicos verificados | 181 |
| Alias provenientes de leads | 114 |
| Alias provenientes de proyectos/horas | 95 |
| Registros descartados por validacion o incompletitud | 312 |
| Conflictos alias -> multiples RUC | 0 |
| Conflictos RUC -> multiples razones sociales | 0 |

El resultado no es solamente un archivo auxiliar, sino el **diccionario de alias manual** del proyecto. En terminos metodologicos, funciona como el Ground Truth que permite pasar de nombres comerciales no estandarizados a identificadores oficiales verificables.

En esta etapa tambien se preserva la distincion entre prospectos y clientes historicos: los alias provenientes solo de `leads_ruc_new.xlsx` se tratan como prospectos/no clientes, mientras que los alias provenientes de archivos manuales derivados de `proyectos_empresa.xlsx` se marcan como clientes FPA. Si un mismo RUC aparece en ambas fuentes, prevalece la condicion de cliente para la validacion externa.

---

## 3.6 Conexion con Feature Engineering

El notebook `03_feature_engineering/01_base_sri.ipynb` fue actualizado para dejar de ingerir outputs del carril automatizado y usar directamente el Golden Record manual.

El flujo actual es:

```text
match_final_empresas_verificado.csv
        |
        v
deduplicacion por RUC
        |
        v
JOIN con Catastro RUC del SRI
        |
        v
features_capa1.csv
```

La unidad de observacion del modelo pasa a ser el **RUC unico**, no el alias. Esto evita que una misma empresa entre dos veces al modelo por estar escrita con nombres comerciales distintos.

La Capa 1 actual queda asi:

| Artefacto | Registros | RUC unicos | Clientes FPA |
|---|---:|---:|---:|
| `features_capa1.csv` | 181 | 181 | 82 |

Ademas, el archivo conserva columnas de trazabilidad como `source_label`, `source_winner`, `score` y `verdict`. En la version actual, `source_winner = GROUND_TRUTH_MANUAL` y `verdict = VERIFICADO_MANUAL`, dejando claro que el origen del RUC es la revision manual.

---

## 3.7 Enriquecimiento con SCVS

La Capa 2 incorpora informacion financiera y de tamano empresarial de la SCVS. El notebook `03_feature_engineering/02_enriquecimiento_ranking.ipynb` toma las empresas de Capa 1, obtiene el expediente societario desde el Directorio de Companias y luego cruza contra el ranking financiero.

La cobertura actual es:

| Artefacto | Registros | RUC unicos | Clientes FPA |
|---|---:|---:|---:|
| `features_capa2.csv` | 141 | 141 | 57 |

Existe una fila con valores financieros crudos incompletos en liquidez y margen; estos faltantes se imputan en la etapa de construccion de matrices, antes del clustering.

---

## 3.8 Decision metodologica para la tesis

La narrativa recomendada es la siguiente:

> El proyecto encontro una limitacion estructural comun en iniciativas de analitica B2B: los CRM suelen registrar nombres comerciales porque son utiles para la operacion comercial, pero las fuentes publicas oficiales organizan la informacion por razon social y RUC. Esta diferencia impide una integracion directa y vuelve necesario un proceso de resolucion de entidades.

En consecuencia:

- El matching automatizado se presenta como baseline experimental y propuesta futura.
- El Golden Record manual se presenta como solucion metodologica para garantizar precision en el modelo final.
- El modelo K-Means se entrena solo sobre empresas con RUC verificado manualmente.
- La validez del clustering se apoya en datos oficiales del SRI y SCVS, no en similitudes textuales probabilisticas.

Esta decision protege la calidad academica del experimento y, al mismo tiempo, deja abierta una linea aplicada: convertir el pipeline automatizado en una herramienta asistida para sugerir RUCs de nuevos leads, siempre con revision humana antes de incorporarlos al modelo.

---

## Referencias relacionadas

- Christen, P. (2012). *Data matching: Concepts and techniques for record linkage, entity resolution, and duplicate detection*. Springer.
- Getoor, L., & Machanavajjhala, A. (2012). Entity resolution: Theory, practice & open challenges. *Proceedings of the VLDB Endowment, 5*(12), 2018-2019.
- SRI - Servicio de Rentas Internas del Ecuador. Catastro RUC por provincia.
- Superintendencia de Companias, Valores y Seguros del Ecuador. Directorio de companias y ranking empresarial.
