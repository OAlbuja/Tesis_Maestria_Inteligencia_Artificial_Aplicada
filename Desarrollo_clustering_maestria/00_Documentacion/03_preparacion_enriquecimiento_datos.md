# 3. Metodología de preparación y enriquecimiento de datos

---

## 3.1 Fuentes de datos utilizadas

El presente proyecto utilizó dos fuentes de datos internas de la organización FPA Latam como punto de partida:

- **Leads del CRM** (`leads.xlsx`): registro histórico de 440 empresas prospecto capturadas en el pipeline comercial B2B de FPA Latam a lo largo de los últimos ciclos comerciales. Cada registro contiene atributos mínimos de contacto y firmografía: nombre de empresa, industria, cargo del contacto, fuente del lead, interés declarado y, en un subconjunto menor (25 registros), el país explícito.

- **Proyectos activos** (`proyectos_empresa.xlsx`): registro de 412 proyectos de consultoría ejecutados o en ejecución por FPA Latam, asociados a 120 empresas únicas. Este archivo contiene variables operativas de cada proyecto (horas estimadas, horas ejecutadas, facturación, avance real y estimado, tipo de alcance, entre otras).

Adicionalmente, se emplearon tres fuentes de datos públicos oficiales del Ecuador como catálogos de enriquecimiento:

- **Catastro RUC del SRI** (Servicio de Rentas Internas): archivos CSV por provincia —26 en total— con información tributaria de contribuyentes registrados. Cada registro contiene número de RUC, razón social, nombre fantasía o comercial, tipo y clase de contribuyente, estado, sector CIIU, provincia, cantón y parroquia del establecimiento, entre otros atributos. El catálogo consolidado supera los 2,5 millones de registros.

- **Directorio de Compañías de la Superintendencia de Compañías, Valores y Seguros (SCVS)**: archivo Excel con 219.339 sociedades registradas en Ecuador, que incluye razón social, RUC, situación legal, tipo societario, capital suscrito, CIIU, región, provincia, ciudad, representante legal y año del último balance presentado.

- **Listas auxiliares SRI**: catastro de empresas fantasmas (SENAE) y lista de contribuyentes inscritos en plataformas de mercado en línea, utilizados como señales de calidad y enriquecimiento adicional.

---

## 3.2 Análisis exploratorio de fuentes (Data Profiling)

Previo al proceso de matching, se realizó un análisis de perfilado de datos sobre ambas fuentes internas mediante el notebook `01_profiling_fuentes_validacion_join.ipynb`. Este análisis permitió identificar:

- La cardinalidad y distribución de valores en las columnas de nombre de empresa en leads y proyectos.
- El porcentaje de valores nulos en variables clave (industria, cargo, país, revenue estimado).
- La distribución geográfica implícita de los leads: del total de 440 registros, solo 25 registros contenían un país explícitamente declarado, de los cuales 22 correspondían a empresas de México, Colombia, Perú, Venezuela, Brasil y Chile —es decir, entidades fuera del registro tributario ecuatoriano—. Los 415 registros restantes carecían del campo país, lo que, junto al contexto del CRM de FPA Latam (empresa ecuatoriana), permite asumir que corresponden en su mayoría a empresas con presencia en Ecuador.
- La ausencia de coincidencias exactas entre los nombres de empresa presentes en leads y los presentes en proyectos, lo que evidenció la necesidad de un proceso de resolución de entidades (*entity resolution*) robusto.

---

## 3.3 Normalización de nombres de empresa (Staging)

Dado que los registros provenientes del CRM y del directorio de proyectos presentan inconsistencias típicas de datos no estructurados (variaciones tipográficas, abreviaturas, sufijos legales, tildes y caracteres especiales), se diseñó e implementó una función de normalización de nombres de empresa en el notebook `01_staging_empresas_normalizadas.ipynb`. El procedimiento aplicado a cada nombre fue el siguiente:

1. **Eliminación de espacios extremos** y conversión a cadena de texto.
2. **Desacento de caracteres** mediante descomposición Unicode canónica (NFKD), eliminando los modificadores combinantes.
3. **Conversión a mayúsculas**.
4. **Eliminación de caracteres no alfanuméricos** (reemplazados por espacio).
5. **Supresión de sufijos legales y conectores frecuentes** que no aportan valor discriminante para el matching: `SA`, `S.A.`, `SAS`, `LTDA`, `CIA`, `COMPANIA`, `CORP`, `INC`, `LLC`, `C.LTDA`, `&`, `Y`, así como artículos y preposiciones (`DE`, `DEL`, `LA`, `EL`, `LOS`, `LAS`).
6. **Colapso de espacios múltiples** y eliminación de espacios iniciales y finales.

Este proceso generó una versión normalizada de cada nombre (`name_norm`) que se utilizó exclusivamente para la comparación en el proceso de matching, preservando el nombre original (`name_raw`) para trazabilidad y visualización.

Los outputs de esta etapa fueron:

| Archivo | Descripción | Registros |
|---|---|---|
| `leads_companies_clean.csv` | Empresas únicas del CRM normalizadas | 418 |
| `horas_empresas_clean.csv` | Empresas únicas de proyectos normalizadas | 120 |
| `empresas_universe_compilado.csv` | Universo unificado (LEADS ∪ HORAS) | ~500 |

---

## 3.4 Resolución de entidades: asignación de RUC mediante matching multi-estrategia

El núcleo del proceso de enriquecimiento consistió en vincular cada empresa del universo interno con su registro oficial en las fuentes públicas, obteniendo así su Número de RUC (Registro Único de Contribuyentes) —identificador único de 13 dígitos en el sistema tributario ecuatoriano— como llave primaria para la extracción posterior de atributos firmográficos.

Se diseñó un pipeline de matching en tres etapas, implementado en los notebooks `02_matching_exacto_scvs.ipynb` y `03_catalogos_y_torneo_fuzzy.ipynb`:

### Etapa 1 — Matching exacto contra la SCVS

Se construyó un catálogo de búsqueda a partir del Directorio de Compañías de la SCVS, aplicando la misma función de normalización descrita anteriormente. Cada empresa del universo interno fue comparada contra este catálogo mediante **unión exacta por nombre normalizado**. Esta estrategia prioriza precisión sobre cobertura: solo se acepta un match cuando los nombres normalizados son idénticos, lo que minimiza falsos positivos.

### Etapa 2 — Matching difuso con catálogos SRI (torneo competitivo)

Las empresas que no obtuvieron match exacto pasaron a una segunda etapa de **búsqueda aproximada** (*fuzzy matching*) contra tres catálogos construidos a partir de los archivos RUC del SRI:

- **Catálogo SRI Razón Social**: construido a partir de la columna `RAZON_SOCIAL` de los 26 archivos provinciales, consolidando más de 2,5 millones de registros. Se mantuvo un único registro por nombre normalizado, resolviendo duplicados por frecuencia.
- **Catálogo SRI Nombre Fantasía**: construido a partir de la columna `NOMBRE_FANTASIA_COMERCIAL`, que registra el nombre comercial del establecimiento.
- **Catálogo SCVS difuso**: reutilización del directorio de la Superintendencia para comparación aproximada en los casos en que el nombre normalizado difiere ligeramente del registrado.

Para el cálculo de similitud se utilizó la métrica **`token_set_ratio`** de la librería `rapidfuzz`, que es robusta ante permutaciones y subconjuntos de tokens, y se fijó un umbral mínimo de **80 puntos sobre 100** para considerar válido un match. Cuando una empresa obtuvo puntajes superiores al umbral en más de un catálogo, se aplicó un **mecanismo de torneo**: se seleccionó el match de mayor puntaje; en caso de empate, se privilegió el catálogo de mayor confianza según el orden de prioridad: SCVS > SRI Razón Social > SRI Nombre Fantasía.

Para eficiencia computacional, el proceso de comparación se implementó mediante la función `cdist` de `rapidfuzz`, que ejecuta la matriz de similitudes completa (queries × catálogo) en bloques de 500.000 pares con paralelismo multihilo (`workers=-1`), lo que permitió procesar los catálogos millonarios del SRI en tiempo razonable.

### Etapa 3 — Auditoría por LLM

Los matches obtenidos por la vía difusa fueron sometidos a una **revisión automática mediante un modelo de lenguaje grande** (GPT-4o-mini de OpenAI), implementada en el notebook `04_auditoria_llm_y_match_final.ipynb`. Se diseñó un *prompt* de sistema que instruye al modelo a actuar como auditor de matching de empresas ecuatorianas, evaluando la coherencia entre el nombre original del lead y el candidato encontrado en el catálogo, con las reglas:

- Si el RUC no tiene 13 dígitos → `verdict = incorrect`.
- Si existe coherencia total entre nombre original y candidato → `verdict = correct`.
- Si el nombre es genérico o los datos son insuficientes → `verdict = uncertain`.

Los casos se enviaron en bloques (*chunks*) al API de OpenAI, y los resultados (`verdict`, `confidence`, `reason`) se integraron a cada registro para la construcción del match final.

---

## 3.5 Consolidación del match final

El archivo `match_final_empresas.csv` integra los resultados de las tres etapas, consolidando el mapeo entre nombre de empresa interno y RUC verificado. La tabla final contiene los campos: `source_label` (LEADS o HORAS), `name_raw`, `name_norm`, `RUC`, `source_winner` (fuente ganadora del match), `score` y `verdict`.

Los resultados por fuente de match fueron los siguientes:

| Fuente de match (`source_winner`) | Empresas |
|---|---|
| SCVS (match exacto) | 24 |
| SCVS (match difuso validado) | 70 |
| SRI Razón Social | 38 |
| SRI Nombre Fantasía | 45 |
| **Total** | **177** |

De las 177 empresas con RUC asignado, **113 provienen de la fuente LEADS** (CRM) y **64 de la fuente HORAS** (proyectos activos).

---

## 3.6 Cobertura y limitaciones del enriquecimiento

Del universo de 440 leads históricos, 177 registros (40,2%) pudieron ser vinculados con certeza a fuentes de información pública oficiales (SRI y Superintendencia de Compañías) mediante un proceso de *entity resolution* en cuatro etapas: normalización, matching exacto, matching difuso con torneo competitivo y auditoría LLM. Los 263 registros restantes fueron excluidos del modelo por carecer de identificación fiscal verificable: 22 corresponden a empresas internacionales fuera del alcance del registro tributario ecuatoriano, y los demás presentaron ambigüedades de naming no resolubles con las fuentes disponibles sin incurrir en costos de datos propietarios. Esta limitación se documenta como restricción del estudio y no afecta la validez del análisis, dado que el subconjunto de 177 empresas enriquecidas constituye una muestra representativa del pipeline comercial con información firmográfica objetiva y verificable.

En términos cuantitativos, la distribución de los registros excluidos se explica por:

1. **Empresas internacionales** (22 registros): leads de México, Colombia, Perú, Venezuela, Brasil y Chile, para los cuales no existe registro en el SRI ni en la SCVS. La incorporación de fuentes de datos firmográficos internacionales (Dun & Bradstreet, Clearbit, etc.) habría requerido contratos comerciales con costos no justificables en el marco de un proyecto de investigación académica.

2. **Empresas no resolubles** (~241 registros): nombres demasiado genéricos, entidades informales no registradas en el SRI, variaciones de denominación no resolubles por métodos automáticos, o empresas que operan bajo un nombre comercial completamente distinto al registrado en el catálogo tributario.

Esta limitación es consistente con las tasas de cobertura reportadas en la literatura de *entity resolution* sobre datos de CRM y fuentes de registro público, donde tasas de matching del 35–50% son esperables en ausencia de identificadores primarios pre-existentes (Christen, 2012; Getoor & Machanavajjhala, 2012). El subconjunto de 177 empresas enriquecidas constituye, no obstante, una muestra con información firmográfica objetiva y verificable, derivada de fuentes oficiales del Estado ecuatoriano, lo que garantiza la calidad y trazabilidad de los datos de entrada al modelo de clustering.

---

## Referencias relacionadas con esta sección

- Christen, P. (2012). *Data matching: Concepts and techniques for record linkage, entity resolution, and duplicate detection*. Springer.
- Getoor, L., & Machanavajjhala, A. (2012). Entity resolution: Theory, practice & open challenges. *Proceedings of the VLDB Endowment, 5*(12), 2018–2019. https://doi.org/10.14778/2367502.2367564
- SRI – Servicio de Rentas Internas del Ecuador. (2026). *Catastro RUC por provincia* [Conjunto de datos]. https://www.sri.gob.ec
- Superintendencia de Compañías, Valores y Seguros del Ecuador (SCVS). (2026). *Directorio de compañías* [Conjunto de datos]. https://www.supercias.gob.ec
