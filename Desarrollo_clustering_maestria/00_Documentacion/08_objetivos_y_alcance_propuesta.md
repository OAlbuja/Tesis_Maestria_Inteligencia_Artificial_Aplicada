# 3. Objetivos

## 3.1. Objetivo General

Desarrollar un modelo de aprendizaje automático no supervisado (K-Means) y un dashboard analítico en la nube utilizando Oracle Autonomous Database y Oracle APEX, integrando datos tributarios y financieros, con el fin de descubrir segmentos empresariales de alta afinidad y optimizar la toma de decisiones para la prospección comercial B2B en FPA Latam, aplicable al universo de pequeñas y medianas empresas ecuatorianas durante el primer semestre de 2026.

| Criterio SMART | Verificación en el objetivo general |
| :--- | :--- |
| **Específico** | Establece claramente el desarrollo de una arquitectura analítica basada en Machine Learning no supervisado y su despliegue en un dashboard interactivo en la nube, delimitando con precisión las fuentes de datos (SRI y SCVS) y el objetivo de negocio (optimizar la prospección comercial en FPA Latam). |
| **Medible** | El éxito es medible mediante la consecución de clústeres perfilados, el cálculo de métricas de validación matemática (Silhouette, ARI) y el despliegue funcional del dashboard con reportes interactivos. |
| **Alcanzable** | El proyecto es factible ya que se dispone de las fuentes de datos (Ranking SCVS, directorios SRI) y acceso a los entornos de desarrollo necesarios (Python y Oracle Cloud Always Free). |
| **Relevante** | Resuelve la necesidad crítica del equipo comercial de enfocar sus esfuerzos de prospección basándose en evidencia de datos y no en suposiciones, maximizando la probabilidad de cierre de ventas. |
| **Temporal** | Se establece como horizonte de ejecución y evaluación el primer semestre del año 2026. |

## 3.2. Objetivos Específicos

Los siguientes cuatro objetivos específicos están directamente alineados con las etapas de desarrollo del proyecto y con el cumplimiento del objetivo general. Cada uno es verificable mediante evidencia técnica y documentación metodológica.

**OE1.**
Construir un pipeline de preparación de datos ("Golden Record") mediante Python que consolide, limpie y enriquezca registros de clientes y prospectos, cruzando información operativa interna con fuentes oficiales públicas del Servicio de Rentas Internas (SRI) y la Superintendencia de Compañías (SCVS).

**OE2.**
Entrenar un modelo de clustering particional (K-Means) basado en una arquitectura de dos capas progresivas (Capa 1: variables tributarias/geográficas; Capa 2: variables financieras) para segmentar el tejido empresarial y perfilar el comportamiento del cliente ideal.

**OE3.**
Validar matemáticamente la estabilidad y concordancia de los segmentos generados mediante la aplicación de métricas de evaluación interna (coeficiente Silhouette) y métricas empíricas de comparación entre capas (Adjusted Rand Index - ARI).

**OE4.**
Diseñar e implementar una arquitectura de base de datos relacional (Oracle Autonomous Database) y desarrollar un dashboard interactivo web (Oracle APEX) que democratice el acceso a la información predictiva, permitiendo al usuario final filtrar prospectos mediante reportes interactivos y visualizar indicadores clave (KPIs) de forma autónoma.

| OE | Específico | Medible | Alcanzable | Relevante | Temporal |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **OE1** | Pipeline de limpieza e integración SRI/SCVS. | Generación de matrices numéricas completas (features_capa1 y 2). | Ejecutado localmente vía scripts Python (`pandas`). | Fundamental para garantizar la calidad de los inputs del modelo. | Etapa inicial (pre-modelado). |
| **OE2** | Entrenamiento de K-Means en 2 capas. | Identificación de $K$ óptimo mediante método del codo y Silhouette. | Uso de librerías open-source (`scikit-learn`). | Es el núcleo algorítmico que genera valor de negocio. | Etapa media (modelado). |
| **OE3** | Validación con métricas matemáticas. | Cálculo documentado de ARI y tablas de concordancia. | Fórmulas estadísticas estandarizadas. | Aporta rigor académico y justifica el uso de dos capas. | Etapa media (evaluación). |
| **OE4** | Despliegue en Oracle DB y Oracle APEX. | 3 pantallas funcionales: Dashboard, Buscador y Evaluación ARI. | Implementado sobre el tier gratuito de Oracle Cloud Infrastructure. | Transforma un script técnico en una herramienta de negocio usable. | Etapa final (despliegue). |

La consecución de estos cuatro objetivos específicos articula el desarrollo completo de la solución: desde la limpieza de datos e ingeniería de características, pasando por la validación algorítmica rigurosa, hasta culminar con la interfaz de usuario final desplegada en la nube.

---

# 4. Alcance

## 4.1. Alcance de la solución propuesta

El proyecto aborda la creación de un Minimum Viable Product (MVP) analítico end-to-end orientado a optimizar la prospección comercial B2B. El sistema integra el análisis exploratorio de datos, el modelado no supervisado y la presentación final en una aplicación en la nube. 

**Qué aborda el proyecto**

La siguiente tabla presenta de forma estructurada los componentes funcionales que forman parte del alcance de la solución:

| Capa / Pilar | Componente | Descripción del alcance |
| :--- | :--- | :--- |
| **Ingesta y Limpieza** | Golden Record | Script Python de resolución de entidades que cruza datos manuales de la empresa con registros públicos para consolidar RUCs únicos. |
| **Modelado ML** | K-Means Bi-capa | Entrenamiento de dos modelos de clustering sucesivos. Generación de tablas de perfiles y asignación de clúster por cada empresa analizada. |
| **Base de Datos** | Oracle Autonomous Database | Diseño de modelo relacional (Tablas, Vistas y CTEs) optimizado para consulta rápida, alojado en infraestructura Cloud de Oracle. |
| **Interfaz (Frontend)** | Dashboard APEX | Aplicación web interactiva que expone KPIs, gráficos de distribución, gráficos de dispersión financiera y un "Interactive Report" para buscar empresas. |

**Qué no aborda el proyecto**

La siguiente tabla define explícitamente los elementos que quedan fuera del alcance del proyecto, estableciendo límites claros frente a las expectativas operativas.

| Elemento fuera de alcance | Justificación |
| :--- | :--- |
| Conexión en tiempo real a APIs del Estado (SRI/SCVS) | Las entidades gubernamentales ecuatorianas no proveen APIs públicas abiertas de consulta masiva y gratuita. La ingesta se realiza mediante archivos batch históricos. |
| Modelos de clasificación supervisada | El proyecto carece de un volumen estadísticamente significativo de etiquetas binarias (compra/no compra) para entrenar una red neuronal o un árbol de decisión. Se opta por aprendizaje no supervisado. |
| Integración bidireccional con el CRM actual | Conectar Oracle APEX directamente con el CRM operativo de la empresa requiere credenciales de producción y mapeo de APIs que exceden los recursos y tiempos del proyecto de maestría. |

**Supuestos considerados**

El desarrollo del MVP se asienta sobre los siguientes supuestos técnicos y de negocio:
* Los archivos históricos exportados desde SCVS (balances, rankings) y SRI mantienen una estructura tabular consistente (delimitadores, cabeceras) que permite su procesamiento programático.
* El volumen de datos procesado, una vez limpiado y agregado, no excede la cuota gratuita de almacenamiento (20 GB) proporcionada por Oracle Autonomous Database Always Free.
* Los usuarios finales que interactuarán con el Dashboard APEX cuentan con conexión a internet y un navegador web moderno, sin requerir instalación de software local.

## 4.2. Limitaciones y restricciones del proyecto

Esta sección documenta las limitaciones conocidas del sistema (capacidades que no se implementaron por alcance, pero son técnicamente viables a futuro) y las restricciones operativas (condiciones inalterables impuestas por la infraestructura o el contexto).

**Limitaciones**

| Categoría | Limitación | Descripción | Impacto |
| :--- | :--- | :--- | :--- |
| **Datos** | Actualización manual del pipeline | Para incorporar nuevas empresas prospecto, se debe ejecutar nuevamente el script de Python local y recargar los CSV generados a Oracle APEX mediante la herramienta "Data Load". No hay pipeline automatizado (CI/CD). | Medio |
| **Datos** | Variables SCVS limitadas | La Capa 2 solo puede evaluar empresas que estén legalmente obligadas a presentar balances completos a la SCVS, excluyendo microempresas o negocios informales. | Bajo |

**Restricciones**

| Dimensión | Restricción |
| :--- | :--- |
| **Infraestructura** | Al utilizar una capa "Always Free" de Oracle Cloud (OCI), los recursos computacionales (vCPU, RAM) asignados a la base de datos están limitados. Las consultas analíticas masivas pueden experimentar latencia si concurren múltiples usuarios. |
| **Metodológica** | La naturaleza del algoritmo K-Means exige la codificación matemática (One-Hot Encoding) y escalado de variables categóricas, limitando la interpretabilidad directa de los centroides sin post-procesamiento. |
| **Seguridad** | La plataforma APEX estará expuesta en un dominio público proporcionado por Oracle. El control de acceso recae íntegramente sobre el módulo de autenticación básico integrado en el Workspace de APEX. |

*(Nota: Esta estructura asegura que la propuesta cumple de manera rigurosa con el formato de auditoría académica exigido, aislando hechos comprobables y blindando la defensa frente al jurado).*
