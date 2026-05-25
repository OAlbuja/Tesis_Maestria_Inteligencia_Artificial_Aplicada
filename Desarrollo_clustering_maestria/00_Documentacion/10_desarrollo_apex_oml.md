# 7. Desarrollo del proyecto: despliegue en OCI, Oracle Machine Learning y Oracle APEX

El desarrollo del proyecto consistio en transformar el modelo local de segmentacion B2B construido en Python/Jupyter en un prototipo funcional en la nube. Para ello se creo una arquitectura sobre Oracle Cloud Infrastructure (OCI) compuesta por una base Oracle Autonomous Database, un conjunto de tablas y vistas SQL para almacenar datos, segmentos y reglas de priorizacion, experimentos en Oracle Machine Learning (OML) para llevar la logica de clustering a la nube, y una aplicacion Oracle APEX que permite al usuario consultar empresas, visualizar indicadores del modelo y guardar prospectos priorizados.

## 7.1. Diseno de la solucion

### Enfoque metodologico aplicado

El enfoque aplicado fue modular y secuencial, siguiendo la logica de un pipeline de ciencia de datos: primero se consolidaron y depuraron fuentes internas y publicas, despues se construyeron variables analiticas, luego se entrenaron y evaluaron modelos de clustering, y finalmente se desplegaron los resultados en una aplicacion web de bajo codigo. Esta estructura permite separar el trabajo tecnico en capas verificables: datos, modelado, base de datos, logica de negocio e interfaz de usuario.

La solucion no se diseno como un sistema de prediccion supervisada, sino como un modelo no supervisado de segmentacion empresarial. La variable `ES_CLIENTE_FPA` no fue usada para entrenar K-Means; se utilizo posteriormente como validacion externa para interpretar si los segmentos descubiertos tenian mayor o menor afinidad historica con FPA.

### Fases del proyecto

| Fase | Actividad principal | Evidencia tecnica |
|---|---|---|
| 1. Modelado local | Entrenamiento de K-Means en dos capas: Capa 1 con variables tributarias SRI y Capa 2 con variables financieras SCVS. | `04_modeling/01_clustering.ipynb` |
| 2. Preparacion para Oracle | Conversion de artefactos locales a CSV con nombres y tipos compatibles con Oracle. | `09_preparacion_oracle_csv.py`, carpeta `outputs/` |
| 3. Creacion de base en OCI | Definicion de tablas, indices y vistas en Oracle Autonomous Database. | `00_Oracle_DDL_MVP.sql` |
| 4. Experimentacion OML | Entrenamiento y prueba de modelos K-Means dentro de Oracle Machine Learning. | `Notebook - OML.pdf` |
| 5. Prototipo APEX | Construccion de dashboard, buscador de empresas y mini-CRM de prospectos. | Capturas de la aplicacion `B2B Segmentacion MVP` |

### Herramientas utilizadas

| Herramienta | Uso dentro del proyecto |
|---|---|
| Python / Jupyter Notebook | Limpieza, feature engineering, entrenamiento inicial y evaluacion del clustering. |
| pandas / scikit-learn | Transformacion de datos, escalamiento, K-Means, metricas Silhouette, Davies-Bouldin y ARI. |
| Oracle Autonomous Database | Almacenamiento cloud de tablas oficiales, features, clusters, validaciones y vistas operativas. |
| Oracle SQL Developer Web | Ejecucion del DDL, carga de datos y validacion SQL. |
| Oracle Machine Learning | Prueba de entrenamiento K-Means dentro de la base de datos en OCI. |
| Oracle APEX | Desarrollo low-code del dashboard, buscador y registro de prospectos guardados. |

### Criterios de evaluacion

La seleccion y validacion de la solucion se baso en criterios tecnicos y funcionales:

| Criterio | Aplicacion en el proyecto |
|---|---|
| Interpretabilidad | Los clusters se perfilaron con nombres comerciales comprensibles, por ejemplo `Industriales consolidados de alta afinidad FPA`. |
| Cobertura | La Capa 1 cubre las 181 empresas del Golden Record; la Capa 2 cubre 141 empresas con informacion financiera SCVS. |
| Calidad del clustering | Se compararon valores de inercia, Silhouette, Davies-Bouldin y tamanos de cluster. |
| Validacion externa | Se cruzaron los clusters con `ES_CLIENTE_FPA` para medir tasa historica de clientes por segmento. |
| Concordancia entre capas | Se calculo ARI para analizar si la estructura tributaria y la financiera agrupaban de forma similar. |
| Usabilidad | La solucion se expuso en APEX mediante KPIs, graficos, busqueda por RUC y guardado de prospectos. |

## 7.2. Desarrollo de la solucion

### Descripcion de los datos

La base analitica parte de un Golden Record de 181 empresas con RUC ecuatoriano verificado. Este Golden Record se enriquecio con fuentes publicas oficiales:

| Fuente / tabla | Descripcion | Volumen cargado |
|---|---|---:|
| `ML_EMPRESAS_MASTER` | Empresas consolidadas del Golden Record. | 181 |
| `ML_CLUSTERS_CAPA1` | Segmentos asignados por el modelo tributario/SRI. | 181 |
| `ML_CLUSTERS_CAPA2` | Segmentos asignados por el modelo financiero/SCVS. | 141 |
| `SRI_RUC_EMPRESAS_RESUMEN` | Universo resumido de RUCs del SRI. | 6.799.544 |
| `SCVS_RANKING_RESUMEN` | Historico financiero SCVS. | 1.651.467 |
| `SCVS_DIRECTORIO` | Directorio de companias SCVS. | 214.439 |

La Capa 1 usa variables tributarias y descriptivas: tipo de contribuyente, obligado a llevar contabilidad, agente de retencion, contribuyente especial, estado activo, antiguedad, macrosector CIIU y region. La Capa 2 agrega variables financieras para empresas con datos SCVS: ingresos, empleados, activos, liquidez y margen operacional, transformadas a escala logaritmica cuando correspondia.

### Preprocesamiento resumido

El preprocesamiento incluyo la normalizacion de RUC como texto de 13 caracteres, consolidacion de nombres empresariales, seleccion de un registro unico por empresa, enriquecimiento con SRI y SCVS, transformacion de variables categoricas mediante codificacion binaria, estandarizacion de variables numericas y exportacion de artefactos a CSV para ser cargados en Oracle. Los archivos grandes de SRI y SCVS se dividieron en partes para facilitar su carga mediante las herramientas de Oracle.

La preparacion para Oracle quedo automatizada en `09_preparacion_oracle_csv.py`, que genera archivos como `ml_empresas_master.csv`, `ml_features_capa1.csv`, `ml_clusters_capa1.csv`, `ml_validacion_capa1.csv` y `ml_concordancia_ari.csv`. Para volumenes mayores, `10_split_large_csvs.py` divide archivos como `sri_ruc_empresas_resumen.csv` y `scvs_ranking_resumen.csv` en chunks de 500.000 filas.

### Alternativas tecnicas evaluadas

Se evaluaron al menos dos alternativas tecnicas durante el desarrollo:

| Alternativa | Descripcion | Resultado |
|---|---|---|
| K-Means local con scikit-learn | Entrenamiento en Jupyter usando matrices ya preprocesadas, metricas internas y validacion externa. | Se adopto como referencia metodologica principal por su control, reproducibilidad e interpretabilidad. |
| K-Means en Oracle Machine Learning | Entrenamiento dentro de OCI y consulta de asignaciones de cluster desde la base de datos. | Se uso como validacion y traslado experimental a nube; requirio ajustes por diferencias de preparacion automatica y nomenclatura de modelos. |
| Ward / clustering jerarquico | Alternativa exploratoria para comparar estructura de agrupamiento. | Se mantuvo como apoyo diagnostico, no como modelo operativo final. |
| Reglas SQL tipo surrogate model | Reglas derivadas del perfilamiento K-Means para clasificar rapidamente nuevos RUCs desde APEX. | Se selecciono para el buscador operativo por su rapidez, trazabilidad y facilidad de mantenimiento en SQL. |

### Justificacion de la alternativa seleccionada

El modelo principal seleccionado fue K-Means local en dos capas, complementado con vistas SQL y reglas de priorizacion en Oracle. Esta decision se justifica porque el notebook local permitio controlar completamente el preprocesamiento, comparar valores de `K`, revisar metricas e interpretar los centroides. Posteriormente, Oracle se utilizo como capa de despliegue para almacenar resultados, exponer consultas y construir el prototipo en APEX.

En Capa 1 se selecciono `K = 4` porque entrega segmentos mas accionables que `K = 2`, manteniendo tamanos razonables entre 35 y 60 empresas. En Capa 2 se selecciono `K = 2` porque fue la solucion mas estable segun Silhouette y Davies-Bouldin; el uso de `K = 4` generaba clusters pequenos influenciados por outliers financieros.

El buscador APEX no depende de ejecutar el entrenamiento cada vez que un usuario consulta una empresa. Para el uso operativo se creo `VW_BUSCADOR_PREDICTIVO`, una vista SQL que actua como modelo surrogate: toma atributos del SRI y SCVS, asigna segmentos predichos de Capa 1 y Capa 2, y calcula un `NIVEL_PRIORIDAD` interpretable.

### Desarrollo en Oracle Machine Learning

El archivo `Notebook - OML.pdf` evidencia el traslado experimental de la logica de clustering a Oracle Machine Learning. La primera prueba sincronizo datos desde una vista de entrenamiento y entreno un modelo K-Means:

La logica consistio en cargar desde Oracle una vista de entrenamiento de la Capa 1, excluir el identificador RUC de las variables predictoras y entrenar un modelo K-Means con cuatro grupos. Esta prueba permitio validar que la base de datos podia ejecutar un flujo de clustering sin depender del entorno local de Jupyter.

Durante la prueba inicial se intento guardar el modelo usando un metodo de persistencia que no estaba disponible para ese objeto de OML. Aunque esa accion genero un error, el modelo si aparecio registrado dentro del catalogo de modelos de Oracle con algoritmo K-Means y funcion de clustering, por lo que el proceso continuo mediante validaciones desde SQL Developer Web y el notebook de OML.

Luego se probaron asignaciones de cluster directamente sobre registros de empresas. La validacion consistio en consultar RUCs de prueba y verificar que Oracle devolviera un identificador de cluster para cada empresa, demostrando que el modelo podia utilizarse desde la base de datos.

Posteriormente se compararon los clusters generados por OML contra los clusters locales guardados en `ML_CLUSTERS_CAPA1`. Esa comparacion mostro que, si OML aplicaba preparacion automatica o si la matriz no era identica a la usada en scikit-learn, las asignaciones no se alineaban completamente con el modelo local. Por ello se hicieron iteraciones adicionales:

1. Entrenamiento con una vista de variables ya codificadas manualmente.
2. Eliminacion y recreacion del modelo durante las pruebas.
3. Renombrado del modelo mas reciente para mantener una referencia estable.
4. Entrenamiento con la matriz final, desactivando la preparacion automatica para aproximarse al comportamiento de Python.
5. Entrenamiento de un modelo adicional para Capa 2.
6. Otorgamiento de permisos para que el modelo pudiera consultarse desde el esquema de trabajo.

La conclusion tecnica de esta fase fue que OML permite ejecutar clustering dentro de Oracle y consultar asignaciones desde SQL, pero para el MVP se mantuvo como referencia principal el resultado local ya validado. La aplicacion APEX quedo conectada a tablas y vistas estables, lo cual mejora la trazabilidad y evita que el usuario final dependa de diferencias internas de preparacion entre motores.

### Desarrollo en Oracle Autonomous Database

En OCI se creo una base Oracle Autonomous Database y se ejecuto el script `00_Oracle_DDL_MVP.sql`. Este script define:

| Componente | Ejemplos | Funcion |
|---|---|---|
| Tablas oficiales | `SRI_RUC_EMPRESAS_RESUMEN`, `SCVS_DIRECTORIO`, `SCVS_RANKING_RESUMEN` | Almacenar fuentes publicas depuradas. |
| Tablas del modelo | `ML_FEATURES_CAPA1`, `ML_FEATURES_CAPA2`, `ML_CLUSTERS_CAPA1`, `ML_CLUSTERS_CAPA2` | Guardar features, labels y clusters. |
| Tablas de validacion | `ML_VALIDACION_CAPA1`, `ML_VALIDACION_CAPA2`, `ML_CONCORDANCIA_ARI` | Exponer resultados de evaluacion. |
| Vistas analiticas | `VW_EMPRESAS_CLUSTER_CAPA1`, `VW_CONSULTA_RUC_SRI`, `VW_BUSCADOR_PREDICTIVO` | Alimentar dashboards y buscador. |
| Mini-CRM | `ML_PROSPECTOS_GUARDADOS` | Guardar prospectos priorizados desde APEX. |

Tambien se crearon indices para optimizar busquedas por RUC, razon social normalizada y cluster, especialmente pensando en consultas desde APEX.

### Desarrollo en Oracle APEX

La aplicacion construida en APEX se denomino `B2B Segmentacion MVP`. Su objetivo fue convertir los resultados del modelo en una herramienta usable para un usuario comercial. La aplicacion contiene una pagina principal de analitica y una pagina de busqueda/guardado de prospectos.

#### Pagina Home: dashboard del modelo

La pagina `Home` presenta el contexto del modelo y los principales indicadores. Incluye un panel explicativo donde se aclara que el modelo usa K-Means en dos capas:

- Capa 1 tributaria: formalidad, antiguedad, sector y region segun SRI.
- Capa 2 financiera: ingresos, empleados y activos para empresas con informacion SCVS.

Tambien se implementaron tarjetas de metricas alimentadas por SQL:

Las tarjetas resumen consultan en tiempo real las tablas del modelo para presentar cuatro indicadores: numero de empresas del Golden Record, cantidad de clusters tributarios, cantidad de clusters financieros y valor de ARI como indicador de concordancia/estabilidad entre capas. La seleccion de estos indicadores responde a la necesidad de mostrar, en una sola vista, cobertura de datos, complejidad del modelo y evidencia de evaluacion.

Esta pagina muestra 181 empresas en el Golden Record, 4 clusters de Capa 1, 2 clusters de Capa 2 y un ARI maximo cercano a 0,13. Adicionalmente se implementaron graficos de distribucion por cluster, distribucion financiera de Capa 2 y un grafico de dispersion financiera de ingresos versus empleados. El grafico de dispersion permite observar visualmente la separacion entre empresas de distinta escala economica.

#### Pagina Buscador de Empresas

La pagina `Buscador de Empresas` permite consultar un RUC especifico y obtener su perfil predictivo. En la interfaz se configuraron:

- Item de entrada `P5_RUC`.
- Boton `Buscar Prospecto`.
- Boton `Limpiar`.
- Boton `Guardar Prospecto`.
- Region `Buscador de Empresas`.
- Region `Mis Prospectos Guardados`.

El buscador utiliza como fuente la vista predictiva de la base de datos. Al ingresar un RUC, la aplicacion recupera la razon social, estado tributario, ingresos, numero de empleados, segmento predicho de Capa 1, segmento predicho de Capa 2 y nivel de prioridad comercial. La prioridad se presenta visualmente mediante una etiqueta de color para facilitar la lectura del usuario final.

El boton `Guardar Prospecto` registra la empresa consultada en una tabla auxiliar del prototipo. Antes de insertar, el proceso verifica que el RUC no exista previamente en la tabla de prospectos guardados, evitando duplicidad de registros dentro del mini-CRM.

El boton `Limpiar` borra el valor ingresado en el campo de RUC para permitir una nueva busqueda sin arrastrar el filtro anterior.

La region `Mis Prospectos Guardados` funciona como una bandeja de seguimiento. Alli se listan los RUCs guardados, su razon social, los segmentos asignados y el nivel de prioridad comercial, permitiendo que el usuario conserve los prospectos que considera relevantes.

Como evidencia funcional, en la captura del buscador se observa la consulta del RUC `1790084604001`, correspondiente a `CONFITECA C.A.`, clasificada como `Industriales consolidados de alta afinidad FPA`, `Empresas grandes consolidadas` y prioridad `Foco Alto`. Tambien se evidencia el guardado de un prospecto en la tabla inferior, por ejemplo `PITEX SA`, con prioridad `Foco Alto`.

### Evidencia visual del prototipo

Esta subseccion debe ubicarse inmediatamente despues de la descripcion de Oracle APEX, porque las capturas funcionan como evidencia visual de las funcionalidades descritas. En el documento final se recomienda insertar las imagenes en el mismo orden en que un usuario interactua con el sistema: ingreso, revision del dashboard, exploracion grafica, busqueda de empresa y evidencia de configuracion en APEX.

**Figura 7.1. Pantalla de inicio de sesion del MVP en Oracle APEX.**

[Insertar aqui la captura de la pantalla de login]

La figura muestra el mecanismo de autenticacion de la aplicacion `B2B Segmentacion MVP` desplegada en Oracle APEX. Esta pantalla evidencia que el prototipo no se presenta como un archivo local, sino como una aplicacion web alojada en Oracle Cloud, con acceso mediante usuario y contrasena. Para la documentacion, se recomienda ocultar o no mostrar credenciales reales; basta con evidenciar la existencia del control de acceso.

**Figura 7.2. Dashboard principal del modelo de segmentacion B2B.**

[Insertar aqui la captura del Home con el panel de contexto, tarjetas de metricas y graficos circulares]

La figura presenta la pagina principal del prototipo, donde se resumen los componentes del modelo analitico. En esta vista se observan los indicadores de cobertura del Golden Record, la cantidad de clusters por capa y el indicador ARI. Tambien se muestran graficos de distribucion que permiten interpretar rapidamente la composicion de los segmentos generados.

**Figura 7.3. Visualizacion de dispersion financiera.**

[Insertar aqui la captura del grafico Ingresos vs Empleados]

La figura muestra la dispersion de empresas segun ingresos y numero de empleados. Esta visualizacion permite observar diferencias de escala entre empresas y complementa la interpretacion de la Capa 2 financiera. Su valor dentro del documento es mostrar que el prototipo no solo lista resultados, sino que tambien permite explorar patrones visuales del universo empresarial.

**Figura 7.4. Buscador predictivo de empresas por RUC.**

[Insertar aqui la captura del buscador con CONFITECA C.A. o una empresa consultada]

La figura evidencia la funcionalidad operativa del sistema. Al ingresar un RUC, el prototipo devuelve la razon social, estado del contribuyente, ingresos, empleados, segmento tributario, segmento financiero y nivel de prioridad. En el ejemplo mostrado, la empresa consultada se clasifica como prioridad `Foco Alto`, lo que traduce el resultado del modelo en una recomendacion comercial accionable.

**Figura 7.5. Prospectos guardados en el mini-CRM del prototipo.**

[Insertar aqui la captura donde se observe la tabla Mis Prospectos Guardados]

La figura muestra la capacidad del sistema para almacenar prospectos priorizados. Esta funcionalidad convierte el dashboard en una herramienta de seguimiento comercial, ya que permite conservar empresas consultadas y revisar posteriormente su segmento y prioridad asignada.

**Figura 7.6. Configuracion low-code en Oracle APEX Page Designer.**

[Insertar aqui la captura del Page Designer con regiones, item P5_RUC y botones]

La figura documenta que la interfaz fue construida en Oracle APEX mediante componentes low-code. En el panel de diseno se observan regiones, items de entrada, botones y fuentes de datos asociados al buscador. Esta evidencia es importante porque demuestra que el MVP fue implementado como una aplicacion funcional y no solamente como una visualizacion estatica.

**Figura 7.7. Notebook de Oracle Machine Learning.**

[Insertar aqui una captura representativa del Notebook - OML.pdf]

La figura permite evidenciar la fase de experimentacion en Oracle Machine Learning. En esta etapa se traslado la logica de clustering a OCI, se probaron modelos K-Means dentro de la base y se compararon sus asignaciones contra los resultados locales. Esta captura respalda el proceso de ensayo y error propio del desarrollo del MVP.

**Figura 7.8. Arquitectura final del MVP.**

[Insertar aqui un diagrama de arquitectura de la solucion]

La figura debe sintetizar el flujo completo de la solucion: fuentes internas y publicas, procesamiento local en Python/Jupyter, carga a Oracle Autonomous Database, experimentacion con Oracle Machine Learning y consumo final mediante Oracle APEX. Este diagrama puede generarse con una herramienta de diseno o con apoyo de inteligencia artificial, siempre que represente fielmente los componentes implementados. Es recomendable incluirlo porque ayuda al lector a comprender la integracion entre datos, modelo, base de datos e interfaz sin depender de explicaciones tecnicas extensas.

### Arquitectura del prototipo

La arquitectura final del MVP integra cinco bloques. El primer bloque corresponde a las fuentes internas y publicas: archivos de leads, proyectos, SRI y SCVS. El segundo bloque corresponde al procesamiento local en Python/Jupyter, donde se realizo limpieza, Golden Record, feature engineering, entrenamiento K-Means y evaluacion. El tercer bloque corresponde a Oracle Autonomous Database, donde se almacenaron tablas, indices, vistas, validaciones y reglas de prioridad. El cuarto bloque corresponde a Oracle Machine Learning, usado para probar el entrenamiento de K-Means dentro de la nube. El quinto bloque corresponde a Oracle APEX, donde el usuario final consulta el dashboard, busca empresas y guarda prospectos.

Esta arquitectura separa el componente academico/modelado del componente operativo/prototipo. El modelo local documenta el metodo y los resultados, mientras que Oracle y APEX permiten exponer esos resultados en una herramienta accesible para usuarios no tecnicos.

## 7.3. Resultados y discusion

### Que se logro

El proyecto logro desplegar un MVP funcional en OCI que permite consultar y visualizar la segmentacion B2B de empresas ecuatorianas. El prototipo integra una base de datos Oracle con tablas oficiales, resultados del modelo y vistas de negocio; una capa experimental de Oracle Machine Learning; y una aplicacion APEX con dashboard, graficos y buscador por RUC.

Los resultados cuantitativos principales fueron:

| Indicador | Resultado |
|---|---:|
| Empresas Golden Record | 181 |
| Empresas con Capa 1 | 181 |
| Empresas con Capa 2 | 141 |
| Clusters Capa 1 | 4 |
| Clusters Capa 2 | 2 |
| ARI C1 K=4 vs C2 K=2 | 0,032 |
| ARI C1 K=4 vs C2 K=4 | 0,126 |

En Capa 1, el segmento mas relevante fue `Industriales consolidados de alta afinidad FPA`, con 35 empresas, 23 clientes FPA y una tasa historica de clientes de 65,7%, equivalente a +20,4 puntos porcentuales frente a la tasa base. Este hallazgo respalda la utilidad del modelo como herramienta de priorizacion comercial.

En Capa 2, el segmento `Empresas medianas y recientes de alta afinidad` alcanzo una tasa de clientes de 45,2%, superior a la base de Capa 2 en +4,7 puntos porcentuales. Sin embargo, la diferencia financiera fue menos marcada que en Capa 1, por lo que la Capa 2 se interpreta como enriquecimiento complementario y no como reemplazo del modelo tributario principal.

### Principales hallazgos

El primer hallazgo es que los clientes historicos de FPA no se distribuyen aleatoriamente. El cruce posterior de clusters con `ES_CLIENTE_FPA` permitio identificar segmentos con mayor afinidad comercial, especialmente empresas industriales consolidadas.

El segundo hallazgo es que la dimension tributaria y la dimension financiera capturan estructuras distintas. El ARI bajo entre capas no representa un fallo del modelo, sino una senal de que cada capa agrupa a las empresas con criterios diferentes: la Capa 1 explica formalidad, sector y region, mientras que la Capa 2 explica escala economica y estructura financiera.

El tercer hallazgo es que el modelo puede convertirse en una herramienta de negocio mediante reglas interpretables. En APEX, el usuario no necesita conocer K-Means ni centroides; solo revisa el RUC, segmento y prioridad comercial: `Foco Alto`, `Foco Medio`, `Foco Bajo` o `Cliente Actual`.

### Interpretacion de fortalezas y debilidades

La principal fortaleza de la solucion es su trazabilidad: cada resultado mostrado en APEX proviene de tablas, vistas o artefactos generados por el pipeline. Ademas, el uso de APEX reduce la barrera tecnica para usuarios comerciales, ya que no requiere ejecutar notebooks ni manipular archivos.

Otra fortaleza es la interpretabilidad. Los clusters no se presentan como numeros, sino como perfiles empresariales: comercio formal maduro, comercio emergente, industria consolidada o empresas grandes consolidadas. Esto facilita la adopcion por parte de negocio.

La principal debilidad es que el MVP no esta conectado en tiempo real a fuentes externas ni al CRM productivo. La actualizacion requiere volver a ejecutar el pipeline, preparar CSV y cargarlos nuevamente a Oracle. Ademas, el buscador usa un surrogate model basado en reglas SQL; por tanto, debe entenderse como una aproximacion operativa derivada del perfilamiento, no como una prediccion probabilistica supervisada.

## 7.4. Implicaciones eticas

El proyecto trabaja con datos empresariales y fuentes oficiales, no con datos personales sensibles. Aun asi, existen implicaciones eticas relevantes porque la herramienta puede influir en la asignacion de atencion comercial hacia unas empresas sobre otras.

La primera consideracion es la privacidad y minimizacion de datos. El modelo utiliza RUC, razon social, atributos tributarios, sector, region e indicadores financieros empresariales. No se incorporan datos personales de representantes legales, contactos individuales, telefonos o correos en el entrenamiento del modelo.

La segunda consideracion es el riesgo de sesgo comercial. Si el equipo de ventas usa el semaforo de prioridad como unica fuente de decision, podria descuidar empresas nuevas o sectores poco representados historicamente. Por ello, el resultado debe entenderse como apoyo a la decision y no como mecanismo automatico de exclusion.

La tercera consideracion es la transparencia. Los segmentos y reglas de prioridad fueron documentados en SQL y en archivos de soporte, de modo que pueden auditarse. Esto evita que el sistema opere como una caja negra frente al usuario.

La cuarta consideracion es la seguridad. Al estar desplegada en APEX sobre un dominio publico de Oracle, el acceso debe mantenerse restringido mediante autenticacion del workspace, roles de usuario y buenas practicas de contrasenas. La tabla de prospectos guardados tambien debe considerarse informacion comercial sensible.

Finalmente, la solucion debe comunicar claramente sus limitaciones: K-Means no predice conversion individual con certeza; identifica similitudes estructurales entre empresas. Por tanto, la decision comercial final debe combinar el resultado del modelo con criterio humano, conocimiento del mercado y validacion directa del prospecto.

## Evidencia sugerida para anexos

| Evidencia | Descripcion |
|---|---|
| Captura APEX Home | Muestra el dashboard `B2B Segmentacion MVP`, las tarjetas de metricas, distribucion por cluster y distribucion financiera. |
| Captura grafico de dispersion | Evidencia la visualizacion `Dispersión Financiera (Ingresos vs Empleados)`. |
| Captura Buscador de Empresas | Muestra busqueda por RUC, segmentos predichos y nivel de prioridad. |
| Captura Page Designer APEX | Evidencia configuracion low-code de regiones, items, botones y consultas SQL. |
| `Notebook - OML.pdf` | Evidencia el proceso de ensayo y error en Oracle Machine Learning. |
| `00_Oracle_DDL_MVP.sql` | Evidencia la estructura de tablas, vistas e indices de la base en OCI. |
| `04_modeling/01_clustering.ipynb` | Evidencia el entrenamiento local y la seleccion del modelo. |
| `10_Logica_de_Negocio_y_Priorizacion.md` | Evidencia la traduccion del clustering a reglas de priorizacion comercial. |
