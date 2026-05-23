# Guía de Despliegue: Oracle Autonomous Database (MVP)

Esta guía detalla el proceso exacto para llevar los datos procesados localmente hacia un entorno preproductivo en Oracle Cloud (Always Free).

> [!IMPORTANT]
> **Reglas de Oro del Proyecto**
> - El campo `RUC` es estrictamente `VARCHAR2(13)`. Nunca debe cargarse como numérico.
> - El campo `ANIO` es numérico entero.
> - La tabla `ML_EMPRESAS_MASTER` usa `VARCHAR2(4000)` para el campo `FUENTES`.

---

## Paso 1: Creación de la Autonomous Database (Always Free)

Oracle Cloud ofrece instancias gratuitas de por vida que son perfectas para este MVP. Sigue estos pasos para aprovisionar la base de datos:

1. **Inicia sesión en Oracle Cloud (OCI):**
   - Ve a [cloud.oracle.com](https://cloud.oracle.com/) e inicia sesión con tu cuenta.
   - Si no tienes cuenta, deberás registrarte y proveer una tarjeta de crédito (no se te cobrará si usas los recursos Always Free).

2. **Navega al servicio de Autonomous Database:**
   - En el menú principal (hamburguesa arriba a la izquierda), Oracle ha actualizado recientemente los nombres. Ve a **Oracle AI Database** -> **Autonomous AI Database**.
   - Asegúrate de estar en el compartimento correcto (usualmente el compartimento raíz que tiene tu nombre o `root`).

3. **Crear la base de datos:**
   - Haz clic en el botón azul **"Create Autonomous Database"**.
   - **Compartment**: Deja el que está por defecto.
   - **Display Name**: `B2B_Segmentation_MVP` (o el nombre de tu preferencia).
   - **Database Name**: `b2bmvp` (solo letras minúsculas y números).
   - **Workload Type**: Selecciona **Transaction Processing** (ATP). Es excelente para APEX.
   - **Always Free**: **¡CRÍTICO!** Activa el interruptor que dice **"Always Free"**. Esto limitará automáticamente los recursos a 1 OCPU y 20 GB de almacenamiento, lo cual es más que suficiente para nuestros 6 millones de registros del SRI.

4. **Configurar Credenciales de Administrador:**
   - El usuario por defecto será `ADMIN`.
   - Escribe una contraseña fuerte (anótala en un lugar seguro, la vas a necesitar para todo). 
   - *Requisito de contraseña: Entre 12 y 30 caracteres, con al menos una mayúscula, una minúscula y un número.*

5. **Acceso a la Red:**
   - Selecciona **"Secure access from everywhere"** (Acceso seguro desde cualquier lugar). Esto te permitirá conectarte fácilmente sin configurar redes privadas virtuales (VCNs) complejas, ideal para un MVP.
   - Marca la casilla *"Require mutual TLS (mTLS) authentication"* si está disponible, o déjalo por defecto.

6. **Crear:**
   - Haz clic en el botón azul **"Create Autonomous Database"** al final de la página.
   - El icono se pondrá en color naranja ("Provisioning"). Espera unos 1 a 3 minutos hasta que cambie a verde ("Available").

---

## Paso 2: Ingresar a Database Actions (SQL Developer Web)

Una vez que la base de datos esté en verde ("Available"):

1. Haz clic en el botón **"Database Actions"** en la parte superior de la pantalla de detalles de tu base de datos.
2. En el menú desplegable, selecciona **"SQL"**.
3. Se abrirá una nueva pestaña con **Oracle SQL Developer Web**. Si te pide credenciales, usa el usuario `ADMIN` y la contraseña que creaste en el paso anterior.
4. Si ves un tutorial de bienvenida, puedes cerrarlo. 

### Paso 2.5: Crear un Usuario Dedicado (B2B_USER)
Es una excelente práctica no trabajar directamente con el usuario `ADMIN`. Sigue estos pasos en la ventana "Crear usuario":

**Pestaña 1: Usuario**
1. **Nombre de usuario**: Escribe `B2B_USER`.
2. **Contraseña**: Ingresa una contraseña fuerte y confírmala.
3. **Cuota en tablespace DATA**: Haz clic en el menú desplegable que dice "Utilizar cuota por defecto" y cámbialo a **"Ilimitado"** (o escribe 20G).
4. **REST, API de GraphQL... y acceso web**: **¡CRÍTICO!** Activa este interruptor (debe quedar en color azul/encendido). Si no lo activas, no podrás usar APEX.
5. Ignora las "Funciones avanzadas de acceso web".

**Pestaña 2: Roles Otorgados**
- ¡No necesitas tocar nada aquí! Al activar el interruptor de "acceso web", Oracle automáticamente le otorga a este usuario los roles básicos necesarios (`CONNECT`, `RESOURCE`, etc.) para crear tablas y vistas. Deja todas las casillas desmarcadas tal cual están.

6. Haz clic en el botón negro **"Crear usuario"** en la esquina inferior derecha.
7. Cierra sesión arriba a la derecha (donde dice ADMIN) e inicia sesión nuevamente usando el usuario `B2B_USER` y su contraseña.

---

## Paso 3: Ejecutar el DDL (Creación del Esquema)

1. Asegúrate de estar conectado como `B2B_USER` (lo verás en la esquina superior derecha).
2. Abre el archivo local **`00_Oracle_DDL_MVP.sql`** que generamos previamente.
2. Copia TODO el contenido del archivo.
3. Pégalo en la hoja de trabajo en blanco de SQL Developer Web.
4. Haz clic en el botón **"Run Script"** (el ícono de la página con un pequeño rayo verde, o presiona `F5`). 
   - *Nota: Asegúrate de usar "Run Script" y no "Run Statement" para que ejecute todas las tablas y vistas de una sola vez.*
5. En la ventana de salida inferior (Script Output), verifica que no haya errores.
6. En el panel izquierdo, actualiza (botón de refrescar) y expande la carpeta **"Tables"**. Deberías ver tus tablas creadas.

---

## Paso 4: Carga de Datos (Data Load)

Vamos a subir tus 14 archivos CSV. Oracle tiene una herramienta maravillosa de "arrastrar y soltar" llamada Data Load.

1. **Abrir la herramienta:**
   - En la misma ventana de SQL Developer Web, busca en la esquina superior derecha un botón que dice **"Carga de datos"** (Data Load), o ve al menú principal de hamburguesa arriba a la izquierda y selecciona **Carga de Datos** (Data Load).
   - En la pantalla que se abre, selecciona la opción **"Cargar Datos"** (Load Data) y luego **"Archivo Local"** (Local File).

2. **Arrastrar los archivos:**
   - Abre la carpeta `outputs/` en tu computadora.
   - Selecciona los 14 archivos CSV y arrástralos hacia la zona punteada en Oracle.

   - Ve a la derecha de cada fila y haz clic en el menú de **tres puntos verticales (`⋮`)**.
   - Selecciona **"Configuración"** (o Editar). Se abrirá una ventana de Detalles.
   - En esa ventana, abajo a la derecha, dale clic a **"Siguiente"** para ir a la pestaña **2 Destino**.
   - Aquí está la magia: cambia la opción "Crear tabla" a **"Tabla existente"**.
   - Haz clic en el ícono de la lupa (o menú desplegable) y selecciona el nombre de la tabla correspondiente en mayúsculas (ej: para `ml_empresas_master.csv`, selecciona `ML_EMPRESAS_MASTER`).
   - Revisa la tabla de Asignación (Mapping) abajo para asegurar que las columnas hagan "match" 1 a 1.
   - Dale a **"Guardar Valores"** abajo a la derecha. Repite esto para los demás archivos.

4. **Ejecutar la carga:**
   - Cuando todos los archivos digan "Tabla Existente" (Target: Existing Table), presiona el botón verde de **"Ejecutar"** (Run / Start) abajo a la derecha.
   - Verás barras de progreso.
   - Repite este proceso para todos los "chunks" (pedazos) de los archivos grandes que dividimos con Python.

---

## Paso 5: Limpieza y Validación de Integridad

Durante la carga, Oracle crea automáticamente unas tablas de registro de errores llamadas `SDW$ERR$_...` para guardar las filas que no pudo insertar (en nuestro caso, las cabeceras de los CSV).

1. **Borrar las tablas de error (Limpieza):**
   - Vuelve a tu hoja de trabajo de SQL (Worksheet).
   - Ejecuta este bloque de código para borrar toda esa basura y dejar tu esquema limpio:
     ```sql
     BEGIN
       FOR t IN (SELECT table_name FROM user_tables WHERE table_name LIKE 'SDW$ERR$_%') LOOP
         EXECUTE IMMEDIATE 'DROP TABLE "' || t.table_name || '"';
       END LOOP;
     END;
     ```

2. **Validar la carga:**
   - Ejecuta esta consulta para asegurarnos de que el número de filas en la base de datos coincida exactamente con lo que exportó Python:
     ```sql
     SELECT 'SRI_RUC_EMPRESAS_RESUMEN' as TABLA, COUNT(*) as FILAS FROM SRI_RUC_EMPRESAS_RESUMEN UNION ALL
     SELECT 'SCVS_RANKING_RESUMEN', COUNT(*) FROM SCVS_RANKING_RESUMEN UNION ALL
     SELECT 'ML_EMPRESAS_MASTER', COUNT(*) FROM ML_EMPRESAS_MASTER UNION ALL
     SELECT 'ML_EMPRESAS_ALIAS_GOLDEN_RECORD', COUNT(*) FROM ML_EMPRESAS_ALIAS_GOLDEN_RECORD UNION ALL
     SELECT 'ML_CLUSTERS_CAPA1', COUNT(*) FROM ML_CLUSTERS_CAPA1;
     ```
   - *El conteo de SRI debe ser cercano a 6.7 millones, SCVS a 1.6 millones, y Master a 181.*

¡Con esto tu base de datos Oracle está 100% lista para conectarse a APEX!

---

# Fase 4: Desarrollo en Oracle APEX

Ahora que nuestros datos están estructurados e indexados, vamos a crear la capa visual. Oracle APEX es una plataforma "Low-Code" que vive dentro de tu base de datos.

## Paso 1: Crear el Espacio de Trabajo (Workspace)

Un "Workspace" es tu entorno de desarrollo en APEX. Debemos crear uno y vincularlo obligatoriamente a nuestro esquema `B2B_USER` para que APEX pueda ver nuestras tablas.

1. **Abrir APEX como Administrador:**
   - Vuelve a la pestaña principal de **Oracle Cloud (OCI)** donde ves los detalles de tu base de datos "b2bmvp".
   - En el menú que está debajo del título verde, haz clic en la pestaña **"Tool configuration"** (Configuración de herramientas).
   - En el primer bloque llamado **Oracle APEX**, busca la fila que dice **"Public access URL"** y dale al botón de **"Copy"**.
   - Pega ese enlace en una nueva pestaña de tu navegador.
   - Se abrirá la página de inicio de sesión de APEX Administration Services.
   - En **Contraseña** (Password), ingresa la contraseña maestra que le pusiste al usuario `ADMIN` cuando creaste la base de datos hoy. Dale a "Sign In to Administration".

2. **Crear el Workspace:**
   - Una vez dentro, verás un botón verde arriba a la derecha (o en el centro) que dice **"Create Workspace"**. Haz clic ahí.
   - Te preguntará: *"How would you like to create your workspace?"*. Debes elegir **"Existing Schema"** (Esquema Existente), ya que nosotros ya creamos y llenamos nuestro esquema con datos.
   - **Database User:** Selecciona de la lista o escribe `B2B_USER`. *(¡Esto es crítico para que APEX lea tus tablas!)*
   - **Workspace Name:** Ponle `B2B_WORKSPACE`.
   - **Workspace Username:** Ponle `ADMIN_B2B` (o tu nombre, este será el usuario para loguearte a programar).
   - **Workspace Password:** Pon una contraseña segura que recuerdes.
   - Haz clic en **"Create Workspace"**.

3. **Entrar al Workspace:**
   - Te saldrá un mensaje verde de éxito diciendo que el workspace fue creado.
   - Arriba a la derecha, dale a tu nombre de admin y selecciona **Sign Out** (Cerrar sesión).
   - Haz clic en "Return to Sign In Page".
   - Ahora inicia sesión con tus nuevas credenciales:
     - **Workspace:** `B2B_WORKSPACE`
     - **Username:** `ADMIN_B2B`
     - **Password:** La contraseña que acabas de crear.

> [!IMPORTANT]
> Una vez que veas la pantalla principal de APEX (que dice App Builder, SQL Workshop, Team Development, etc.), avísame para empezar a construir la aplicación.

## Paso 2: Crear la Aplicación Base

Vamos a inicializar el "cascarón" de tu dashboard.

1. En la pantalla principal de tu Workspace, haz clic en el ícono grande que dice **"App Builder"** (el que tiene un lápiz cruzado).
2. Verás una pantalla vacía. Haz clic en el botón gigante **"Create"** (Crear) en el medio de la pantalla (o arriba a la derecha).
3. Selecciona la opción **"New Application"** (Nueva Aplicación).
4. En el campo **Name** (Nombre), escribe: `B2B Segmentación MVP`.
5. Deja todo lo demás como está por defecto (Theme Redwood, etc.) y ve hasta abajo de la página.
6. Haz clic en el botón azul **"Create Application"**.

APEX tomará unos segundos y te creará automáticamente la estructura base con una página de inicio (Page 1: Home) y navegación.

## Paso 3: Construir el Dashboard (Página 1)

Vamos a editar la página de inicio para mostrar métricas clave de nuestro modelo usando un componente llamado "Cards" (Tarjetas).

1. **Abrir el Page Designer:**
   - En la pantalla de tu aplicación, haz clic en el ícono **"1 - Home"**. 
   - Se abrirá el **Page Designer** (Diseñador de Páginas). Verás tres paneles: a la izquierda el árbol de componentes (Rendering), al medio el diseño visual (Layout), y a la derecha las propiedades (Property Editor).

2. **Crear una Región de KPIs:**
   - En el panel de la izquierda (Rendering), haz clic derecho sobre la carpeta que dice **"Body"** y selecciona **"Create Region"** (Crear Región).
   - En el panel de la **derecha** (Propiedades), configura lo siguiente:
     - **Title:** `Métricas del Modelo`
     - **Type:** Cambia "Static Content" por **"Cards"** (Tarjetas).

3. **Conectar a la Base de Datos:**
   - Un poco más abajo, en la sección **Source** (Origen):
   - **Type:** Cambia "Table / View" por **"SQL Query"** (Consulta SQL).
   - En el gran cuadro de texto que aparece, pega el siguiente código para calcular los KPIs en tiempo real:
     ```sql
     SELECT 
         'Empresas Golden Record' as TITULO, 
         TO_CHAR(COUNT(*)) as VALOR, 
         'fa-building' as ICONO 
     FROM ML_EMPRESAS_MASTER 
     UNION ALL 
     SELECT 
         'Clústeres Generados', 
         TO_CHAR(COUNT(DISTINCT SEGMENTO)), 
         'fa-pie-chart' 
     FROM ML_CLUSTERS_CAPA1;
     ```

4. **Mapear los Datos a la Tarjeta:**
   - En el panel de la derecha, baja hasta la sección **Attributes** (Atributos) (o haz clic en la pestaña "Attributes" que está al lado de "Region" en la parte superior derecha).
   - En **Title** -> Selecciona la columna `TITULO`.
   - En **Body** -> Selecciona la columna `VALOR`.
   - En **Icon and Badge** -> Icon Source: `Icon Class`, y en **Icon Class** selecciona la columna `ICONO`.

5. **Guardar y Ejecutar:**
   - Arriba a la derecha hay un botón azul que dice **"Save and Run Page"** (Guardar y Ejecutar Página) con un ícono de "Play". Haz clic en él.
   - Se abrirá tu aplicación terminada en una nueva pestaña. Inicia sesión con tus mismas credenciales de APEX para ver el resultado.

## Paso 4: Agregar Gráfico de Distribución (Pie Chart)

Ahora vamos a ponerle color al dashboard mostrando cómo se distribuyen las 181 empresas en los 4 clústeres.

1. **Vuelve al Page Designer:**
   - Vuelve a la pestaña de tu navegador donde estabas diseñando (Page Designer).
2. **Crea el Gráfico:**
   - Haz clic derecho sobre **"Body"** y dale a **"Create Region"**.
   - En la derecha, ponle de **Title:** `Distribución por Clúster`.
   - En **Type**, busca y selecciona **"Chart"** (Gráfico).
3. **Configurar la Consulta:**
   - Baja un poco y verás una sub-pestaña roja a la izquierda que dice **"Series 1"**. Dale clic.
   - A la derecha, en **Source**, cambia a **"SQL Query"** y pega esto:
     ```sql
     SELECT 
         SEGMENTO AS CLUSTER_NOMBRE, 
         COUNT(*) AS CANTIDAD
     FROM ML_CLUSTERS_CAPA1
     GROUP BY SEGMENTO;
     ```
   - Baja a la sección **Column Mapping**:
     - **Label:** `CLUSTER_NOMBRE`
     - **Value:** `CANTIDAD`
4. **Hacerlo estilo Pie (Pastel):**
   - Vuelve a hacer clic en la región "Distribución por Clúster" en el árbol de la izquierda (el nivel principal, arriba de Series 1).
   - En la derecha, en la pestaña **Attributes** (Atributos), busca el **Type** y cámbialo a **"Pie"** o **"Donut"**.
5. **¡Guarda y Ejecuta (Save and Run)!**

## Paso 5: Gráfico de Dispersión (Ingresos vs Empleados)

Para terminar la página principal, agregaremos un gráfico interactivo de burbujas/dispersión para ver dónde están paradas financieramente las empresas de cada clúster.

1. **Vuelve al Page Designer.**
2. **Crea el Gráfico:**
   - Haz clic derecho sobre **"Body"** a la izquierda y dale a **"Create Region"**.
   - A la derecha, ponle de **Title:** `Dispersión Financiera (Ingresos vs Empleados)`.
   - En **Type**, selecciona **"Chart"**.
3. **Configurar los Datos (Series):**
   - En la izquierda, abre la nueva región y haz clic en la serie (que se llamará "Series 1" o "New").
   - A la derecha, cambia el Source a **"SQL Query"** y pega esto:
     ```sql
     SELECT 
         RAZON_SOCIAL_GOLDEN,
         INGRESOS,
         EMPLEADOS,
         SEGMENTO_CAPA1
     FROM VW_CONSULTA_RUC_SRI
     WHERE INGRESOS IS NOT NULL AND EMPLEADOS IS NOT NULL;
     ```
   - Baja a la sección **Column Mapping**:
     - **Series Name** (Nombre de la serie, esto dará el color): `SEGMENTO_CAPA1`
     - **Label:** `RAZON_SOCIAL_GOLDEN`
     - **Value (o X):** `INGRESOS`
     - **Y:** `EMPLEADOS`
     *(Si no ves X y Y, asegúrate primero de cambiar el tipo de gráfico a Scatter en el siguiente paso).*
4. **Hacerlo estilo Scatter:**
   - Haz clic en la región "Dispersión Financiera" en el árbol de la izquierda.
   - En la derecha, en **Attributes**, cambia el **Type** a **"Scatter"** (Dispersión).
   - Vuelve a la Serie y asegúrate de que en "Column Mapping" tengas mapeado X a `INGRESOS` e Y a `EMPLEADOS`.
5. **¡Guarda y Ejecuta (Save and Run)!**

## Paso 6: Buscador Interactivo (Página 2)

El dashboard general ya está listo. Ahora necesitamos una página donde un usuario pueda buscar un RUC o Nombre específico y ver todo su perfil financiero y de clúster.

1. **Volver a la vista de Aplicación:**
   - En el Page Designer, haz clic en el ícono de "flecha arriba" (o haz clic en "Application XXX" en el menú superior) para volver a la lista de páginas de tu app.
2. **Crear nueva Página:**
   - Haz clic en el botón grande **"Create Page"**.
   - Selecciona **"Interactive Report"** (Reporte Interactivo).
3. **Configurar el Reporte:**
   - **Page Name:** `Buscador de Empresas`.
   - Expande la sección **Navigation** (Navegación) abajo. Asegúrate de que el interruptor **"Use Navigation"** esté encendido en verde (esto hará que la página aparezca en el menú lateral).
4. **Origen de Datos:**
   - En Data Source, selecciona **"SQL Query"** y pega esta consulta (que trae las columnas más importantes ordenadas por ingresos):
     ```sql
     SELECT 
         RUC, 
         RAZON_SOCIAL_GOLDEN, 
         ESTADO_CONTRIBUYENTE,
         SEGMENTO_CAPA1, 
         SEGMENTO_CAPA2,
         INGRESOS, 
         EMPLEADOS 
     FROM VW_CONSULTA_RUC_SRI
     ORDER BY INGRESOS DESC NULLS LAST;
     ```
5. **Crear y Ejecutar:**
   - Haz clic en **"Create Page"**.
   - Te llevará al Page Designer de esta nueva página. Simplemente dale al botón de "Play" (Save and Run Page) arriba a la derecha.

## Paso 7: Evaluación del Modelo (ARI) - Página 3

Para el rigor académico de tu tesis, el dashboard incluye la evaluación de estabilidad matemática del modelo (Adjusted Rand Index).

1. **Crear la Página Final:**
   - Vuelve al listado de páginas (Application 101) y dale a **Create Page**.
   - Selecciona **Classic Report**.
   - **Page Name:** `Evaluación del Modelo (ARI)`. (Asegúrate de marcar "Include Navigation Menu Entry").
   - En **Source**, elige **Table** y en **Table/View Name** selecciona `ML_CONCORDANCIA_ARI`.
   - Dale a **Create Page** y **Run**.

**¿Qué significa esta tabla?**
El Adjusted Rand Index (ARI) es una métrica científica (que va de -1 a 1) que tu pipeline de Python calculó para medir qué tan estables fueron los clústeres cuando el modelo de Machine Learning analizó los datos del año 1 vs el año 2. 
Mostrar esta tabla en tu App "cierra el círculo" de tu tesis, demostrando que no solo presentas datos, sino que evalúas automáticamente la calidad del modelo algorítmico detrás de ellos.
