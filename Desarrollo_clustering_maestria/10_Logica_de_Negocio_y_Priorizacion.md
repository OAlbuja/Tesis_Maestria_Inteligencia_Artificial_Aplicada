# Lógica de Negocio y Priorización de Prospectos (Look-alike Modeling)

Este documento detalla el puente entre la fundamentación matemática del modelo de Machine Learning (K-Means) y su aplicación operativa en el negocio (Asignación de Prioridad Comercial para el equipo de ventas de FPA).

## 1. El Algoritmo (Lo que hicimos en Python)
Para este proyecto se utilizó **K-Means**, que es un algoritmo de Machine Learning de aprendizaje **No Supervisado**. Esto significa que al algoritmo nunca se le enseñó explícitamente quién era cliente de FPA y quién no (`ES_CLIENTE_FPA`). 

A K-Means únicamente se le proporcionaron datos "ciegos" de las empresas (Ingresos, Empleados, Antigüedad, Región, Sector) con el objetivo matemático de minimizar la varianza intra-clúster, es decir, agrupar a las empresas que más se parecieran entre sí según su estructura financiera y demográfica.

## 2. El Descubrimiento (Perfilamiento de Clústeres)
Una vez que K-Means creó los grupos matemáticos, se cruzaron los resultados con la bandera real de negocio (`ES_CLIENTE_FPA`). Este paso reveló un hallazgo fundamental para la tesis:
**Los clientes actuales de FPA no están distribuidos al azar.**

La gran mayoría de los clientes rentables y recurrentes se concentran en clústeres muy específicos. Por ejemplo, en los grupos que perfilamos y bautizamos como *"Industriales consolidados"* (Capa 1) o *"Grandes consolidadas"* (Capa 2).

## 3. La Lógica de Negocio (Look-alike Modeling)
Al implementar este modelo en el buscador de APEX, no estamos intentando "adivinar" al azar quién comprará. Estamos aplicando una técnica conocida en analítica como **"Look-alike Modeling"** (Búsqueda de Gemelos o Similares).

Si un prospecto completamente nuevo (que actualmente no le compra nada a FPA) ingresa al buscador y el modelo predictivo lo clasifica dentro del clúster *"Industriales consolidados"*, la estadística nos indica que ese prospecto es un **"Gemelo Analítico"** de los mejores clientes actuales. Tiene su mismo ADN corporativo, tamaño y madurez. Por lo tanto, la probabilidad de conversión es altísima.

## 4. La Arquitectura Híbrida de Dos Capas
Para lograr máxima precisión, el sistema no confía en un solo modelo, sino que utiliza una arquitectura predictiva de dos capas que se evalúan en tiempo real:

1. **Capa 1 (Datos Básicos del SRI):** Agrupa a las empresas por antigüedad, sector y ubicación geográfica. Generó perfiles como *"Industriales consolidados"*, *"Comercio maduro"*, etc. Actúa como una "red de seguridad" para clasificar al 100% del universo de empresas (incluyendo negocios pequeños que no tienen balances públicos).
2. **Capa 2 (Datos Financieros de SCVS):** Agrupa a las empresas exclusivamente por su músculo financiero (Logaritmo de Ingresos, Empleados y Activos). Generó perfiles como *"Grandes consolidadas"* y *"Medianas/recientes"*.

## 5. El Motor de Reglas en APEX (Priorización Comercial)
El motor programado en la base de datos para el usuario funcional (Vendedor) evalúa ambas capas simultáneamente, pero le otorga **mayor autoridad a la Capa 2**, ya que los estados financieros auditados son predictores mucho más fuertes que los datos demográficos básicos.

La regla de negocio (`NIVEL_PRIORIDAD`) funciona exactamente así:

1. **Capa 2 manda:** Si el modelo de la Capa 2 clasifica a la empresa como *"Grandes consolidadas"* 👉 **Foco Alto**.
2. **Capa 1 como respaldo:** Si la empresa no reporta a la SCVS (no tiene Capa 2), miramos la Capa 1. Si es un *"Industrial consolidado"* o *"Comercio maduro"* 👉 **Foco Alto**.
3. **Potencial medio:** Si la Capa 2 dice *"Mediana/reciente"* OR la Capa 1 dice *"Comercio emergente/regional"* 👉 **Foco Medio**.
4. **Descarte:** Cualquier otra combinación cae en 👉 **Foco Bajo**.
5. **Protección de Cartera:** Si la empresa ya es cliente actual, el sistema lo etiqueta como 👉 **Cliente Actual** (indicando oportunidad de Up-Selling o Cross-Selling, pero no de prospección en frío).

### Traducción para el Equipo de Ventas:
El equipo comercial no necesita saber qué es K-Means o qué es un Centroide. Solo necesitan interpretar el Semáforo de Prioridad:
* 🔴 **Foco Alto:** "Llámalo HOY". Tienen el presupuesto y el perfil corporativo exacto de nuestros clientes "Diamante".
* 🟡 **Foco Medio:** "Llámalo esta semana". Tienen potencial de crecimiento.
* ⚪ **Foco Bajo:** "Prospectar solo si no hay otros leads". Probabilidad de éxito muy baja.
* 🟢 **Cliente Actual:** "Venderle más". No prospectar en frío.

## 6. Evidencia Gráfica del Modelo (Validación No Supervisada)
Dado que K-Means es un modelo no supervisado, la validación del modelo se realiza cruzando los clústeres resultantes con la variable de control de negocio (`ES_CLIENTE_FPA`). 

Esta validación demuestra estadísticamente que el modelo logró segmentar correctamente el mercado, agrupando a los clientes rentables en nichos específicos (Alta Penetración) y separándolos de los comercios de baja probabilidad.

*(Nota para el autor de la tesis: Inserta aquí abajo las gráficas de barras o tablas cruzadas generadas en el cuaderno `01_clustering.ipynb` o capturas del Dashboard de APEX que muestran la "Tasa de Penetración de Clientes FPA por Clúster").*

![Distribución de Clientes FPA por Clúster de la Capa 1](ruta/a/tu/grafico_capa1.png)

![Distribución de Clientes FPA por Clúster de la Capa 2](ruta/a/tu/grafico_capa2.png)
