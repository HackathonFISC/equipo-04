# Roles, autonomía y reglas de decisión de los agentes

## Centro de coordinación agéntico para la crisis del agua en Panamá Oeste

| Campo | Valor |
| --- | --- |
| **Documento** | `AGENT_CRITERIA_AND_DECISION_RULES.md` |
| **Estado** | Borrador para revisión del equipo |
| **Versión** | 1.0-rev.4 (consolida aprobaciones de prioridad, demanda, supuesto de agua limpia para planificación y adaptador futuro de WhatsApp) |
| **Alcance** | Seis agentes especializados y función de supervisión humana |
| **Naturaleza** | Especificación funcional. No contiene código ni describe componentes ya implementados. |

---

## 0. Fuentes, convenciones y advertencias

### 0.1. Fuentes utilizadas

| Fuente | Uso en este documento | Observación |
| --- | --- | --- |
| **REQ** — *Criterios y reglas de decisión del sistema*, v1.0 (documento de requisitos adjunto) | Fuente principal. Las referencias del tipo **REQ §n** remiten a sus secciones. | Es en sí mismo un borrador de requisitos operativos. |
| Conversación de trabajo de ChatGPT | Incorporada parcialmente en §0.4 y en las reglas afectadas. | Se registran solo las decisiones explícitamente confirmadas por la usuaria; no se consideran confirmados los puntos que siguen marcados [PEND] o [PROV]. |

### 0.2. Convención de estado

Cada regla, criterio o elemento relevante se etiqueta con uno de los siguientes estados:

| Etiqueta | Significado |
| --- | --- |
| **[CONF]** | **Confirmado.** Criterio expresamente definido en REQ (normalmente listado en REQ §15 o formulado como obligación en REQ §1–§14). |
| **[PROV]** | **Provisional.** Regla de REQ marcada como provisional (REQ §16) o que REQ indica que requiere validación antes de su uso en operaciones reales. |
| **[PEND]** | **Pendiente.** Información insuficiente para fijar una regla (REQ §17 o vacío identificado en este documento). |
| **[PROP]** | **Propuesta de este documento.** Elemento de diseño sugerido para completar la especificación (por ejemplo, niveles de autonomía, estados de flujo o esquema de datos). No es un requisito aprobado y debe validarse. |

**Regla de precedencia [PROP]:** si una propuesta de este documento entra en conflicto con un requisito confirmado de REQ, prevalece el requisito confirmado.

### 0.4. Decisiones confirmadas durante la revisión

| ID | Fecha | Decisión | Estado y efecto |
| --- | --- | --- | --- |
| DEC-01 | 2026-10-16 | El tiempo transcurrido desde que una afectación quedó sin agua debe influir **solo en la prioridad**, no en el cálculo de demanda ni en los días de planificación. | **[CONF]** Se elimina como regla operativa el ajuste de demanda `duración estimada + (0,5 × días transcurridos)`. El tiempo transcurrido sigue siendo una entrada del Agente 3; DEC-02 fija el máximo de 100 a los 5 días y aprueba la escala lineal para el prototipo; el redondeo y los datos temporales incompletos quedan pendientes. |
| DEC-02 | 2026-10-16 | El factor temporal `T` aumentará progresivamente con el tiempo transcurrido sin agua hasta alcanzar un máximo de 100 puntos, llegando a ese máximo a los 5 días. | **[CONF]** Se confirma una escala temporal progresiva de 0 a 100 en 5 días. Se aprueba para el prototipo la escala lineal `T = min(100, días_sin_agua / 5 × 100)` **[CONF]**; la regla de redondeo y el tratamiento de horas/fechas ausentes o inciertas siguen **[PEND]**. No aplicar esta escala a la demanda. |
| DEC-03 | 2026-10-16 | Adoptar reglas de trabajo para faltantes, desempates, excepciones, demanda, cobertura, horarios, flota, entrada de reportes, comunicaciones y trazabilidad, según las respuestas de revisión. | Las decisiones explícitas se marcan **[CONF]**; las duraciones de cálculo 1/2/2 días están **[CONF] para el modelo de planificación**, sin afirmar que la emergencia real vaya a durar ese tiempo; otros parámetros que requieren validación operativa se mantienen **[PROV]**; las fuentes o mecanismos no definidos siguen **[PEND]**; las recomendaciones no aprobadas se mantienen **[PROP]**. El detalle consolidado aparece en las secciones de cada agente y en §11. |

**Validación de coherencia:** la fórmula `duración de planificación = duración estimada + 50 % del tiempo ya transcurrido` modifica los días utilizados para calcular la demanda; por tanto, es incompatible con la decisión de que la compensación afecte solo a la prioridad. Se conserva en este documento únicamente como regla descartada para demanda, no como fórmula vigente. No se inferirá una fórmula de prioridad a partir de ella.

### 0.3. Correspondencia de denominaciones

REQ denomina a los agentes de forma ligeramente distinta a la solicitada para este documento. Se conserva la denominación de REQ y se establece la siguiente correspondencia uno a uno, sin duplicar roles:

| N.º | Denominación en este documento | Denominación en REQ §2 |
| --- | --- | --- |
| 1 | Agente de Ingesta y Validación | Agente 1: recepción y clasificación de afectaciones |
| 2 | Agente de Geolocalización | Agente 2: geolocalización y validación territorial |
| 3 | Agente de Priorización | Agente 3: priorización de afectaciones |
| 4 | Agente de Planificación de Recursos | Agente 4: planificación de recursos y demanda de agua |
| 5 | Agente de Optimización de Rutas | Agente 5: optimización de rutas |
| 6 | Chat Agent de Comunicación y Seguimiento | Chat Agent: comunicación |

El **supervisor humano** (REQ §2.7) es una **función de control**, no un agente. Este documento define exactamente **seis agentes**.

### 0.4. Advertencias generales

1. Este documento no presupone que el prototipo ya tenga acceso a APIs, mapas, servicios de geocodificación, inventarios en tiempo real, canales de mensajería ni mecanismos de despacho. OpenStreetMap/cartografía gratuita es la preferencia de fuente territorial **[CONF]**, pero el proveedor concreto, integración y condiciones de uso siguen **[PEND]**.
2. Ningún agente ejecuta acciones en el mundo real (despacho de cisternas, solicitud de vehículos a subcontratistas, envío de comunicaciones públicas extraordinarias). Los agentes **producen registros, cálculos, propuestas y mensajes**; la ejecución operativa no está documentada como capacidad del sistema.
3. Este documento define criterios de planificación y control. **No sustituye** las verificaciones de seguridad vial, la validación sanitaria ni las autorizaciones operativas correspondientes (REQ §18).

---

## 1. Introducción

### 1.1. Propósito del documento

Este documento establece, para cada uno de los seis agentes del centro de coordinación:

- su rol y alcance exclusivos;
- sus entradas, salidas y reglas de decisión;
- sus límites de autonomía y condiciones de escalamiento;
- su forma de interactuar con los demás agentes y con el supervisor humano;
- los criterios con los que se verificará que cumple su función.

Su finalidad es que el equipo pueda revisar y aprobar una asignación de responsabilidades **sin ambigüedades ni solapamientos** antes de iniciar la implementación (REQ §18).

### 1.2. Contexto operativo

El centro de coordinación atiende afectaciones relacionadas con la crisis del agua en Panamá Oeste **[CONF]**. Los tipos iniciales de afectación son **falta de agua, tubería rota y agua contaminada** **[CONF]**. La respuesta principal analizada en REQ es la distribución de agua mediante una flota de referencia de **71 cisternas** (15 propias y 56 subcontratadas) **[CONF]**, sujeta a disponibilidad horaria **[PROV]**, a la capacidad de agua de cada tipo de cisterna **[CONF]** y a un límite operativo de recorrido de 1.000 km **[PROV]**.

### 1.3. Importancia de responsabilidades específicas

En un contexto de crisis, una responsabilidad mal asignada produce errores con consecuencias reales: una ubicación estimada tratada como confirmada desvía una cisterna; una puntuación con datos faltantes convertidos en cero relega a una comunidad; un mensaje que confirma una entrega aún no aprobada genera expectativas falsas. Por ello cada agente tiene:

- **un único propietario por cada resultado** (por ejemplo, solo el Agente 4 calcula la demanda; solo el Agente 3 asigna prioridad);
- **límites explícitos** sobre lo que no le corresponde;
- **condiciones claras de transferencia y de detención**.

### 1.4. Autonomía, coordinación, trazabilidad y supervisión humana

Estos cuatro elementos se relacionan del siguiente modo:

- **Autonomía:** los agentes pueden generar recomendaciones automáticamente, pero **no deben ejecutar decisiones operativas que requieran autorización humana** (REQ §1) **[CONF]**.
- **Coordinación:** cada agente consume los resultados validados del anterior y transmite explícitamente sus incertidumbres; ninguno corrige en silencio los datos de otro.
- **Trazabilidad:** toda decisión relevante debe poder reconstruirse (REQ §13) **[CONF]**, distinguiendo propuestas automáticas, decisiones aprobadas y acciones ejecutadas.
- **Supervisión humana:** el supervisor aprueba las excepciones y decisiones operativas que superan los límites establecidos (REQ §2.7, §12) **[CONF]**.

A mayor impacto operativo y menor certeza de los datos, menor es la autonomía del agente y mayor la exigencia de trazabilidad y aprobación.

---

## 2. Objetivos del sistema de agentes

### 2.1. Objetivo general

Apoyar la coordinación de la atención de afectaciones por la crisis del agua en Panamá Oeste mediante agentes especializados que reciban, estructuren, localicen, prioricen y planifiquen la atención de dichas afectaciones, y que comuniquen sus resultados, **manteniendo la decisión operativa bajo control humano** y la trazabilidad completa del proceso (REQ §1) **[CONF]**.

### 2.2. Objetivos específicos y relación con los requisitos

| N.º | Objetivo específico | Requisito de origen | Agente responsable |
| --- | --- | --- | --- |
| OE-1 | Recibir y clasificar reportes de afectaciones en registros estructurados. | REQ §1.1, §2.1 | Agente 1 |
| OE-2 | Identificar el momento del incidente y el tiempo transcurrido desde él. | REQ §1.2, §2.1 | Agente 1 |
| OE-3 | Identificar y validar la ubicación aproximada de cada afectación. | REQ §1.2, §2.2 | Agente 2 |
| OE-4 | Establecer prioridades según tipo de instalación, vulnerabilidad y magnitud. | REQ §1.3, §2.3, §7 | Agente 3 |
| OE-5 | Calcular la demanda estimada de agua. | REQ §1.4, §2.4, §3, §8 | Agente 4 |
| OE-6 | Evaluar la disponibilidad y capacidad de las cisternas. | REQ §1.5, §5, §6, §11 | Agente 4 |
| OE-7 | Proponer planes de distribución y rutas factibles. | REQ §1.6, §2.4, §2.5, §10 | Agentes 4 y 5 |
| OE-8 | Comunicar limitaciones y resultados de cada plan. | REQ §1.7, §2.6, §9 | Agente 6 |
| OE-9 | Solicitar intervención humana cuando una decisión supere los límites. | REQ §1.8, §12 | Todos los agentes |
| OE-10 | Mantener trazabilidad de datos, cálculos, propuestas, aprobaciones y cambios. | REQ §1.9, §13 | Todos los agentes |

No se incluyen objetivos que REQ no justifique (por ejemplo, reparación de tuberías, gestión de cuadrillas o análisis de calidad del agua).

---

## 3. Arquitectura funcional y coordinación

> **Nota de estado:** REQ define los agentes y sus funciones, pero **no define** un orquestador, un bus de mensajes, un modelo de ejecución (secuencial o paralelo) ni un repositorio compartido. Todo lo que en esta sección describe *cómo* se transfieren los datos es **[PROP]**. Lo que describe *qué* información necesita cada agente se deriva de REQ.

### 3.1. Flujo general de información

El flujo lógico propuesto **[PROP]** es una cadena de responsabilidades con retroalimentación entre planificación y rutas:

1. **Agente 1** recibe un reporte y crea un registro estructurado de afectación.
2. **Agente 2** normaliza y valida la ubicación del registro.
3. **Agente 3** determina la categoría de instalación y la prioridad.
4. **Agente 4** calcula la demanda, evalúa la flota y elabora una propuesta de asignación.
5. **Agente 5** calcula rutas de recorrido completo para la propuesta y devuelve su factibilidad.
6. **Agente 4** consolida demanda, cobertura, cisternas y ruta en un **paquete de plan** y determina si requiere aprobación.
7. **Supervisor humano** aprueba, rechaza o solicita cambios cuando corresponde.
8. **Agente 6** comunica en todo momento el estado real de cada afectación y plan, a partir de los registros.

```mermaid
flowchart TD
    R[Reporte recibido] --> A1[Agente 1<br/>Ingesta y Validación]
    A1 -->|Registro estructurado<br/>estado de validación| A2[Agente 2<br/>Geolocalización]
    A2 -->|Ubicación normalizada<br/>nivel de certeza| A3[Agente 3<br/>Priorización]
    A3 -->|Categoría, prioridad<br/>factores e incertidumbre| A4[Agente 4<br/>Planificación de Recursos]
    A4 -->|Asignación propuesta<br/>cisternas y volúmenes| A5[Agente 5<br/>Optimización de Rutas]
    A5 -->|Ruta: factible / provisional /<br/>requiere excepción / pendiente de verificación| A4
    A4 -->|Paquete de plan| D{¿Requiere<br/>aprobación?}
    D -->|Sí| S[[Supervisor humano<br/>función de control]]
    D -->|No definido - ver §11| S
    S -->|Aprobado / Rechazado /<br/>Cambios solicitados| A4
    A1 -. revisión humana .-> S
    A2 -. revisión humana .-> S
    A3 -. revisión humana .-> S
    A5 -. excepción > 1.000 km .-> S
    A1 & A2 & A3 & A4 & A5 & S --> T[(Registro de trazabilidad<br/>PROP)]
    T --> A6[Chat Agent<br/>Comunicación y Seguimiento]
    A6 -. comunicación pública<br/>extraordinaria .-> S
```

**Observaciones sobre el diagrama:**

- La rama "No definido" refleja que REQ no establece si un plan con cobertura del 100 % y ruta dentro del límite puede ejecutarse sin aprobación. Mientras no se defina, **todo plan pasa por el supervisor antes de ejecutarse** (ver §7.3 y §11).
- El "Registro de trazabilidad" es una abstracción lógica **[PROP]**; REQ exige la trazabilidad (§13), no un componente concreto.
- El diagrama no implica que los agentes se ejecuten simultáneamente. Un registro puede avanzar por la cadena mientras otro está detenido en revisión humana.

### 3.2. Dependencias entre agentes

| Agente | Depende de | Para obtener |
| --- | --- | --- |
| Agente 1 | Fuentes de reporte **[PEND]** | Reportes originales. |
| Agente 2 | Agente 1 | Ubicación reportada, descripción original, identificador. |
| Agente 3 | Agentes 1 y 2 | Tipo de afectación, tiempo transcurrido, datos de población y vulnerabilidad reportados, zona e instalaciones críticas cercanas. |
| Agente 4 | Agentes 1, 2 y 3; Agente 5 | Tipo y duración de afectación, tiempo transcurrido, ubicación, prioridad, factibilidad de rutas. |
| Agente 5 | Agentes 2 y 4 | Ubicaciones validadas, asignación propuesta de cisternas, ubicaciones de la organización y del punto de recogida **[PEND]**. |
| Agente 6 | Registros de todos los agentes y decisiones del supervisor | Estado real de afectaciones y planes. |

### 3.3. Condiciones de transferencia entre agentes

Una tarea solo se transfiere al siguiente agente cuando se cumplen las condiciones mínimas de la tabla. Si no se cumplen, el registro queda en el estado indicado y no avanza en silencio.

| Transferencia | Condición mínima para transferir | Si no se cumple |
| --- | --- | --- |
| Agente 1 → Agente 2 | Registro con identificador único, tipo de afectación (aunque sea con confianza baja), descripción original y fuente conservadas. | El registro queda **Pendiente de información** o **Pendiente de revisión**. |
| Agente 2 → Agente 3 | Ubicación con estado de certeza explícito (confirmada, aproximada, ambigua o no verificada) y zona asociada cuando sea posible. | Si no hay ningún dato territorial utilizable, **Pendiente de información** y revisión humana. |
| Agente 3 → Agente 4 | Categoría de instalación determinada o marcada como incierta; prioridad calculada con factores, incertidumbres y nivel de confianza. | Si la incertidumbre puede alterar significativamente la prioridad, revisión humana (REQ §7.3) antes o en paralelo a la planificación **[PROP]**. |
| Agente 4 → Agente 5 | Propuesta de asignación con cisternas candidatas (tipo, capacidad, estado de disponibilidad), volúmenes y afectaciones a atender. | No se solicita ruta; se documenta el déficit. |
| Agente 5 → Agente 4 | Ruta de recorrido completo calculada y clasificada, o justificación de inviabilidad. | Ruta marcada **pendiente de verificación** o **inviable**, con alternativas cuando existan. |
| Agente 4 → Supervisor | Paquete de plan completo según REQ §2.7 y §9. | No se presenta un paquete incompleto como listo para aprobación; se señalan los campos faltantes. |
| Cualquier agente → Agente 6 | Cambio de estado registrado. | El Chat Agent comunica el último estado registrado y su antigüedad, nunca un estado supuesto. |

### 3.4. Comunicación de resultados, errores, incertidumbres y solicitudes de revisión

Todo resultado transferido entre agentes debe incluir, como mínimo **[PROP]**, derivado de REQ §13 y §14:

1. **Resultado** (el dato o propuesta producido).
2. **Estado** (ver §8.2).
3. **Nivel de confianza o certeza** y su justificación.
4. **Datos faltantes** y parte del resultado afectada por ellos.
5. **Supuestos utilizados**, solo si están documentados y permitidos (REQ §14.3).
6. **Agente responsable** y momento de emisión.
7. **Versión de criterios y reglas aplicados** (REQ §13).
8. **Solicitud de revisión humana**, si procede, con el motivo.

Un agente que reciba un resultado incompatible con otro dato **no lo sobrescribe**: registra el conflicto, conserva ambas versiones y lo eleva según §7.

### 3.5. Papel de la supervisión humana

El supervisor humano **[CONF]**:

- aprueba las excepciones y decisiones operativas que requieren intervención humana (REQ §2.7);
- resuelve las situaciones de la tabla de REQ §12;
- recibe información suficiente para decidir: motivo de la propuesta, datos utilizados, demanda, recursos, cobertura prevista, ruta, riesgos e incertidumbres (REQ §2.7).

El supervisor **no es un agente**: no forma parte de la cadena automática, no es sustituible por un agente y sus decisiones se registran como decisiones humanas. Quién ejerce la función, cómo se le notifica y cómo se autentican sus aprobaciones está **[PEND]** (§11).

### 3.6. Trazabilidad de las decisiones

Cada agente registra sus entradas, salidas y justificaciones conforme a §9. Los registros distinguen entre **propuesta automática**, **decisión aprobada** y **acción ejecutada** (REQ §13) **[CONF]**. El sistema no registra una entrega como realizada porque un agente la haya propuesto o una ruta haya sido calculada **[CONF]**.

---

## 4. Definición individual de los agentes

---

### 4.1. Agente 1 — Ingesta y Validación (recepción y clasificación de afectaciones)

#### A. Identificación

| Campo | Contenido |
| --- | --- |
| **Nombre** | Agente de Ingesta y Validación (REQ: Agente 1, recepción y clasificación de afectaciones). |
| **Objetivo principal** | Transformar los reportes recibidos en registros estructurados que puedan utilizar los demás agentes (REQ §2.1) **[CONF]**. |
| **Problema que resuelve** | Los reportes llegan en formatos heterogéneos, incompletos o duplicados; sin estructura no pueden localizarse, priorizarse ni planificarse. |
| **Alcance** | Desde la recepción del reporte hasta la entrega de un registro estructurado con su estado de validación. No incluye la ubicación precisa, la prioridad ni la demanda. |

#### B. Responsabilidades específicas

**Tareas que debe ejecutar:**

1. Asignar un identificador único a cada registro **[CONF]**.
2. Clasificar el tipo de afectación entre: falta de agua, tubería rota, agua contaminada **[CONF]**.
3. Registrar la fecha y hora del incidente **diferenciándola** de la fecha y hora de recepción del reporte **[CONF]**.
4. Calcular el tiempo transcurrido desde el incidente cuando la fecha y hora del incidente estén disponibles **[CONF]**.
5. Registrar la ubicación aproximada **tal como fue reportada**, sin geolocalizarla **[CONF]**.
6. Conservar la fuente y la descripción original **[CONF]**.
7. Asignar un nivel de confianza a la clasificación **[CONF]** (escala **[PEND]**).
8. Registrar datos faltantes y observaciones **[CONF]**.
9. Distinguir la causa reportada de sus consecuencias **[CONF]** (por ejemplo, "tubería rota" como causa y "falta de agua" como consecuencia).
10. Detectar posibles duplicados **sin eliminarlos** automáticamente **[CONF]**.
11. Marcar como pendientes de revisión los reportes ambiguos o contradictorios **[CONF]**.
12. Señalar los reportes de contaminación como **posible riesgo sanitario** que requiere validación por autoridades o responsables competentes **[CONF]**.

**Información que debe analizar:** contenido del reporte, fuente, momento de recepción y cualquier dato sobre fecha del incidente, lugar, tipo de instalación mencionada, número de personas o vulnerabilidad **que aparezca expresamente** en el reporte.

**Resultados que debe producir:** registro estructurado de afectación (§4.1.D).

**Decisiones que puede tomar:**

- Clasificar el tipo de afectación con un nivel de confianza.
- Marcar un registro como posible duplicado de otro.
- Asignar los estados *Recibido*, *En análisis*, *Pendiente de información*, *Pendiente de revisión* o *Validado* al registro (estados **[PROP]**, ver §8.2).

**Fuera de su alcance (responsabilidad de otros agentes):**

| Responsabilidad | Propietario |
| --- | --- |
| Asignar coordenadas o confirmar ubicaciones | Agente 2 |
| Determinar la categoría de instalación para la jerarquía y calcular prioridad | Agente 3 |
| Estimar población por promedios de ocupación o calcular demanda | Agente 4 |
| Validar sanitariamente la contaminación | Autoridades o responsables competentes (externo) |
| Comunicar al público o al informante | Agente 6 |

#### C. Entradas

| Dato | Fuente | Requisito mínimo |
| --- | --- | --- |
| Reporte de afectación (texto o datos) | Archivos de prueba que simulan reportes de WhatsApp y transcripciones de audio/video **[CONF para prototipo]**; integración directa con canales reales **[PEND]**. | Debe contener al menos una descripción interpretable. |
| Fuente del reporte | Archivo de prueba / canal simulado de WhatsApp / transcripción de audio o video | Registrar el origen simulado y la fecha; integración con canales reales **[PEND]**. |
| Fecha y hora de recepción | Sistema receptor **[PEND]** | Debe registrarse siempre que sea posible. |

**Tratamiento de información:**

- **Faltante:** se registra como faltante, nunca se completa con valores supuestos. No se inventan ubicaciones, fechas, cantidades de personas ni otros datos (REQ §2.1) **[CONF]**.
- **Contradictoria:** se conservan las versiones y el registro pasa a *Pendiente de revisión* **[CONF]**.
- **No verificada:** se registra con su fuente y con estado de validación "no verificado".

#### D. Salidas

**Registro estructurado de afectación** — campos exigidos por REQ §2.1 **[CONF]**, en formato lógico sugerido **[PROP]**:

| Campo | Contenido | Estado |
| --- | --- | --- |
| `id_afectacion` | Identificador único | [CONF] |
| `tipo_afectacion` | falta de agua / tubería rota / agua contaminada / indeterminado | [CONF] (valor "indeterminado" [PROP]) |
| `causa_reportada` / `consecuencias_reportadas` | Separación causa-consecuencia | [CONF] |
| `fecha_hora_incidente` | Si consta en la fuente; si no, nulo | [CONF] |
| `fecha_hora_recepcion` | Momento de recepción | [CONF] |
| `tiempo_transcurrido` | Calculado desde el incidente; nulo si no hay fecha del incidente | [CONF] |
| `ubicacion_reportada` | Texto tal como fue reportado | [CONF] |
| `fuente` y `descripcion_original` | Conservadas sin alteración | [CONF] |
| `confianza_clasificacion` | Escala por definir | [CONF] / escala [PEND] |
| `estado_validacion` | Ver §8.2 | [CONF] / valores [PROP] |
| `datos_faltantes`, `observaciones` | Lista explícita | [CONF] |
| `posibles_duplicados` | Referencias a otros registros | [CONF] |
| `alerta_sanitaria` | Verdadero si es agua contaminada | [PROP] derivado de REQ §2.1 |
| `datos_reportados_adicionales` | Instalación mencionada, personas, vulnerabilidad, si constan | [PROP] |

**Destinatarios:** Agente 2 (principal); Agente 6 (estado); supervisor (si requiere revisión).

**Tarea completada cuando:** el registro tiene identificador, tipo (o "indeterminado" con motivo), fuente y descripción original conservadas, faltantes listados y estado asignado.

#### E. Reglas de decisión

| ID | Condición | Acción del agente | Resultado |
| --- | --- | --- | --- |
| A1-R1 | El reporte permite identificar uno de los tres tipos de afectación. | Clasifica y asigna nivel de confianza. | Registro transferible. |
| A1-R2 | El reporte describe varios tipos (p. ej., tubería rota que causa falta de agua). | Registra causa y consecuencia por separado. La clasificación principal a efectos de duración es la causa principal: si una tubería rota causa falta de agua, usar “tubería rota” **[CONF]**. | Registro transferible con observación. |
| A1-R3 | El tipo no puede determinarse. | Clasifica "indeterminado", lista faltantes. | *Pendiente de información*; revisión humana si persiste. |
| A1-R4 | Falta la fecha/hora del incidente. | No usa la fecha de recepción como sustituto; deja `tiempo_transcurrido` nulo y lo marca faltante. | Transferible, con incertidumbre explícita para Agentes 3 y 4. |
| A1-R5 | Datos del reporte se contradicen entre sí o con otro reporte. | Conserva ambas versiones. | *Pendiente de revisión*. |
| A1-R6 | Coincidencia significativa con otro registro según texto, ubicación y tiempo, cuando existan esos datos **[PROP]**. | Vincula los reportes similares como relacionados/posibles duplicados; no elimina ni fusiona automáticamente **[CONF]**. | Revisión humana para fusionar o separar **[PROP]**. |
| A1-R7 | Tipo = agua contaminada. | Activa alerta de posible riesgo sanitario. | Transferible, con requisito de validación sanitaria para el Agente 4 (REQ §8.3). |
| A1-R8 | Tipo de afectación fuera de los tres tipos iniciales. | No fuerza la clasificación. | Revisión humana; ampliación de tipos **[PEND]**. |

**No debe decidir automáticamente:** la fusión o eliminación de duplicados, la veracidad sanitaria de una contaminación, ni completar datos ausentes.

#### F. Límites y restricciones

- **Permitido:** crear y actualizar registros estructurados; clasificar; marcar estados, faltantes y duplicados.
- **Prohibido:** inventar datos; asignar coordenadas; eliminar reportes; descartar un reporte por estar incompleto; alterar la descripción original; calcular prioridad o demanda.
- **Dependencias:** ninguna de otros agentes; depende de fuentes de reporte **[PEND]**.
- **Errores e incertidumbre:** todo dato incierto se marca como tal y viaja con el registro.

#### G. Nivel de autonomía

| Elemento | Contenido |
| --- | --- |
| **Nivel asignado [PROP]** | **Nivel 1 — Ejecución controlada.** |
| **Justificación** | Sus acciones (crear, clasificar y marcar registros) son internas, reversibles y regidas por reglas explícitas. No tienen efecto operativo directo. |
| **Sin autorización** | Crear registros, clasificar, calcular tiempo transcurrido, marcar faltantes, duplicados, alertas y estados. |
| **Requiere aprobación** | Fusionar o descartar registros duplicados **[PROP]**; reclasificar un registro ya aprobado en un plan. |
| **Detener y escalar** | Contradicciones que cambien una decisión crítica (REQ §12); tipo fuera del catálogo; alerta sanitaria sin validación cuando el registro ya entra en planificación. |

#### H. Interacción con otros agentes

| Dirección | Agente | Datos | Condición |
| --- | --- | --- | --- |
| Entrega | Agente 2 | Registro estructurado completo | Al cumplir la condición de §3.3. |
| Entrega | Agente 6 | Estado del registro | Cada cambio de estado. |
| Recibe | Agente 2 | Solicitud de aclaración de ubicación | Si la ubicación reportada es insuficiente: el Agente 1 marca el registro como *Pendiente de información*; el canal para contactar al informante es **[PEND]**. |
| Eleva | Supervisor | Contradicciones, duplicados, tipos no catalogados | Según A1-R5, A1-R6, A1-R8. |

**Conflictos:** si el Agente 2 o 3 detecta que la clasificación es incompatible con otros datos, el Agente 1 no la cambia en silencio: registra la discrepancia y reabre el registro con estado *Pendiente de revisión*.

#### I. Criterios de aceptación

| Caso | Entrada de prueba | Resultado esperado |
| --- | --- | --- |
| Normal | Reporte con tipo, fecha del incidente, lugar y fuente. | Registro con todos los campos, tipo correcto, tiempo transcurrido calculado desde el incidente (no desde la recepción). |
| Incompleto | Reporte sin fecha del incidente. | `tiempo_transcurrido` nulo, faltante listado; no se usa la fecha de recepción. |
| Incompleto | Reporte sin número de personas. | Campo vacío y marcado faltante; no se inventa ninguna cifra. |
| Contradictorio | Dos reportes del mismo lugar con fechas de incidente distintas. | Ambos conservados, vinculados como posible duplicado, *Pendiente de revisión*. |
| Sanitario | Reporte de agua contaminada. | `alerta_sanitaria` activa y requisito de validación visible para el Agente 4. |
| Intervención humana | Reporte que no encaja en ningún tipo. | Clasificación "indeterminado" y elevación al supervisor. |
| Integridad | Cualquier reporte. | La descripción original y la fuente son recuperables sin alteración. |

---

### 4.2. Agente 2 — Geolocalización (geolocalización y validación territorial)

#### A. Identificación

| Campo | Contenido |
| --- | --- |
| **Nombre** | Agente de Geolocalización (REQ: Agente 2, geolocalización y validación territorial). |
| **Objetivo principal** | Determinar dónde ocurre cada afectación y preparar la información geográfica necesaria para la planificación (REQ §2.2) **[CONF]**. |
| **Problema que resuelve** | Las ubicaciones reportadas suelen ser descripciones informales; sin normalización ni grado de certeza, la priorización por zona y el cálculo de rutas no son fiables. |
| **Alcance** | Normalización, georreferenciación cuando haya datos suficientes, asociación a zona/comunidad, identificación de instalaciones críticas cercanas y declaración del grado de certeza. No calcula rutas ni prioridades. |

#### B. Responsabilidades específicas

**Tareas (REQ §2.2) [CONF]:**

1. Estandarizar las ubicaciones recibidas.
2. Identificar coordenadas cuando existan datos suficientes.
3. Asociar cada afectación con su zona o comunidad.
4. Identificar instalaciones críticas cercanas cuando corresponda.
5. Señalar ubicaciones aproximadas, ambiguas o no verificadas.
6. Proporcionar información geográfica para el cálculo de rutas.

**Información que debe analizar:** `ubicacion_reportada`, descripción original y referencias geográficas de los registros del Agente 1; OpenStreetMap u otra fuente cartográfica gratuita compatible **[CONF como preferencia de fuente]**; servicio de geocodificación concreto, cobertura y licencia/condiciones de uso **[PEND]**.

**Resultados:** ubicación normalizada con estado de certeza, zona asociada, coordenadas si procede, instalaciones críticas cercanas y observaciones.

**Decisiones que puede tomar:** asignar un estado de certeza territorial; asociar zona cuando la referencia sea inequívoca; vincular registros de una misma zona para que el Agente 3 pueda estimar el factor A.

**Fuera de su alcance:**

| Responsabilidad | Propietario |
| --- | --- |
| Clasificar el tipo de afectación | Agente 1 |
| Decidir si una instalación cercana cambia la prioridad | Agente 3 |
| Calcular distancias de recorrido y rutas | Agente 5 |
| Determinar ubicaciones de la organización y del punto de recogida de agua | Fuente operativa **[PEND]**; el Agente 2 solo las normaliza si se le proporcionan **[PROP]** |

#### C. Entradas

| Dato | Fuente | Requisito mínimo |
| --- | --- | --- |
| Registro estructurado | Agente 1 | Identificador y ubicación reportada (aunque sea vaga). |
| Referencias territoriales (zonas, comunidades, instalaciones críticas) | **[PEND]** | Fuente identificable y versionada **[PROP]**. |

**Tratamiento:**

- **Faltante:** sin ningún dato territorial → *Pendiente de información*, solicitud de aclaración y revisión humana.
- **Contradictoria** (p. ej., nombre de comunidad incompatible con el corregimiento indicado): conserva las versiones, estado "ambigua", revisión humana si afecta a instalaciones críticas o a la asignación de rutas.
- **No verificada:** se marca "no verificada"; nunca se presenta como confirmada.

#### D. Salidas

| Campo lógico [PROP] | Contenido |
| --- | --- |
| `id_afectacion` | Heredado del Agente 1 |
| `ubicacion_normalizada` | Forma estandarizada |
| `coordenadas` | Solo si hay datos suficientes; con indicación de si son **confirmadas** o **estimadas** |
| `estado_certeza` | confirmada / aproximada / ambigua / no verificada **[CONF]** (categorías tomadas de REQ §2.2; denominación exacta [PROP]) |
| `zona_comunidad` | Zona asociada o nulo |
| `instalaciones_criticas_cercanas` | Lista con tipo y fuente |
| `observaciones_geograficas` | Motivo de la certeza asignada |
| `fuente_referencia` | Fuente territorial usada |

**Destinatarios:** Agente 3 (prioridad), Agente 4 (planificación), Agente 5 (rutas), Agente 6 (estado).

**Tarea completada cuando:** cada registro tiene un estado de certeza explícito y justificado, y zona asociada o motivo de su ausencia.

#### E. Reglas de decisión

| ID | Condición | Acción | Resultado |
| --- | --- | --- | --- |
| A2-R1 | La referencia identifica un lugar de forma inequívoca y verificable con la fuente de referencia. | Normaliza, asigna coordenadas y zona. | Estado "confirmada". |
| A2-R2 | La referencia permite una zona pero no un punto. | Asigna zona; si estima un punto, lo marca "estimada". | Estado "aproximada"; transferible. |
| A2-R3 | La referencia admite varias interpretaciones. | Lista las alternativas, no elige en silencio. | Estado "ambigua"; revisión humana si la elección afecta prioridad o ruta. |
| A2-R4 | No hay información territorial utilizable. | Solicita aclaración. | *Pendiente de información*. |
| A2-R5 | La afectación coincide con o está próxima a una instalación crítica (hospital, policlínica, centro de salud, escuela). | Registra la instalación y su fuente. | Dato para el Agente 3. El umbral de "cercanía" es **[PEND]**. |
| A2-R6 | La ubicación queda fuera del ámbito de Panamá Oeste. | No descarta; señala la incoherencia territorial. | Revisión humana **[PROP]**. |

**No debe decidir automáticamente:** cuál de varias ubicaciones posibles es la correcta cuando la diferencia afecta a la prioridad o a la ruta; si una ubicación estimada es suficientemente precisa para despachar una cisterna.

#### F. Límites y restricciones

- **Permitido:** normalizar, georreferenciar con datos suficientes, asociar zonas, señalar incertidumbre.
- **Prohibido:** presentar una ubicación estimada como coordenada confirmada (REQ §2.2) **[CONF]**; modificar la ubicación reportada original; calcular rutas; asignar prioridad.
- **Dependencias:** Agente 1; OpenStreetMap/cartografía gratuita **[CONF como preferencia]**; proveedor concreto de geocodificación **[PEND]**.
- **Errores:** si la fuente territorial no está disponible, el agente no inventa coordenadas: deja el registro con estado "no verificada".

#### G. Nivel de autonomía

| Elemento | Contenido |
| --- | --- |
| **Nivel asignado [PROP]** | **Nivel 1 — Ejecución controlada.** |
| **Justificación** | Produce datos derivados reversibles y declara su certeza; no ejecuta acciones operativas. |
| **Sin autorización** | Normalizar, asignar zona, asignar coordenadas con estado de certeza, listar instalaciones cercanas. |
| **Requiere aprobación** | Elegir entre ubicaciones alternativas cuando afecte prioridad o ruta; tratar una ubicación aproximada como suficiente para una ruta ordinaria **[PROP]**. |
| **Detener y escalar** | Ubicación ambigua que afecta a una instalación crítica; contradicción territorial; ausencia total de datos. |

#### H. Interacción con otros agentes

| Dirección | Agente | Datos | Condición |
| --- | --- | --- | --- |
| Recibe | Agente 1 | Registro estructurado | Registro transferible. |
| Entrega | Agente 3 | Zona, instalaciones críticas cercanas, certeza | Ubicación con estado asignado. |
| Entrega | Agentes 4 y 5 | Ubicación normalizada y coordenadas con certeza | Ubicación con estado asignado. |
| Solicita | Agente 1 / supervisor | Aclaración de ubicación | A2-R3, A2-R4. |
| Entrega | Agente 6 | Estado territorial | Cada cambio de estado. |

**Conflictos:** si el Agente 5 detecta que una coordenada es inaccesible o incoherente con la red vial, el Agente 2 revisa el registro y, si no puede resolverlo, lo marca "ambigua" y lo eleva.

#### I. Criterios de aceptación

| Caso | Resultado esperado |
| --- | --- |
| Normal | Dirección inequívoca → ubicación "confirmada", zona y coordenadas con fuente. |
| Incompleto | Solo nombre de barrio → zona asignada, estado "aproximada", sin coordenada presentada como confirmada. |
| Contradictorio | Comunidad y corregimiento incompatibles → alternativas listadas, estado "ambigua", revisión humana si afecta prioridad o ruta. |
| Sin datos | Ubicación vacía → *Pendiente de información*. |
| Instalación crítica | Reporte junto a una policlínica → instalación listada con fuente para el Agente 3. |
| Verificación de no falsificación | Ninguna salida con estado "confirmada" procede de una estimación. |

---

### 4.3. Agente 3 — Priorización de afectaciones

#### A. Identificación

| Campo | Contenido |
| --- | --- |
| **Nombre** | Agente de Priorización (REQ: Agente 3, priorización de afectaciones). |
| **Objetivo principal** | Determinar qué afectaciones deben recibir atención primero (REQ §2.3) **[CONF]**. |
| **Problema que resuelve** | Con recursos limitados, el orden de atención debe basarse en criterios explícitos, uniformes y auditables. |
| **Alcance** | Determinación de la categoría de instalación, aplicación de la jerarquía de instalaciones críticas y cálculo de la puntuación ponderada para las demás afectaciones, con explicación e incertidumbres. |

#### B. Responsabilidades específicas

**Tareas:**

1. Identificar el tipo de instalación **antes** de aplicar la puntuación general (REQ §7.1) **[CONF]**.
2. Aplicar la jerarquía: 1) hospitales, 2) policlínicas, 3) centros de salud, 4) escuelas, 5) otras afectaciones **[CONF]**.
3. Para las "otras afectaciones", calcular `P = 0.50 × T + 0.25 × V + 0.25 × A` **[CONF]** (pesos confirmados en REQ §15). El tiempo transcurrido desde la interrupción influye solo en la prioridad. T aumenta progresivamente y alcanza 100 puntos a los 5 días; la escala lineal `T = min(100, días_sin_agua / 5 × 100)` está aprobada para el prototipo **[CONF]**. El redondeo y el tratamiento de datos temporales faltantes o inciertos siguen **[PEND]**.
4. Explicar los factores que influyeron en cada puntuación y señalar las incertidumbres (REQ §2.3) **[CONF]**.
5. Aplicar las reglas de datos faltantes de REQ §7.3 **[CONF]**.

**Información que debe analizar:** tipo de afectación, tiempo transcurrido (Agente 1); zona e instalaciones críticas (Agente 2); datos de vulnerabilidad y personas afectadas disponibles en los registros.

**Resultados:** categoría de instalación, posición en la jerarquía, puntuación P (si aplica), desglose de factores, nivel de confianza e incertidumbres.

**Decisiones que puede tomar:** asignar categoría cuando los datos sean claros; calcular P; ordenar las afectaciones como **recomendación** de orden de atención.

**Fuera de su alcance:**

| Responsabilidad | Propietario |
| --- | --- |
| Calcular la demanda de agua | Agente 4 |
| Decidir qué afectación recibe cisternas | Agente 4 (propuesta) y supervisor (aprobación) |
| Aprobar excepciones a la jerarquía | Supervisor (REQ §7.1, §12) |
| Modificar ponderaciones | Supervisor (REQ §12) |

> **Precisión:** la prioridad calculada es una **recomendación de orden**, no una garantía de atención inmediata ni una asignación de recursos.

#### C. Entradas

| Dato | Fuente | Requisito mínimo |
| --- | --- | --- |
| Tipo de afectación, tiempo transcurrido, datos reportados | Agente 1 | Registro transferible. |
| Zona, instalaciones críticas cercanas, certeza | Agente 2 | Estado de certeza asignado. |
| Escalas de normalización, umbrales, desempates | Reglas aprobadas **[PEND]** | Deben estar aprobadas antes de producción (REQ §7.2). |
| Definición operativa de vulnerabilidad (V) | **[PEND]** | REQ nombra el factor pero no lo define. |
| Fuente para la cantidad de personas afectadas en la zona (A) | **[PEND]** | REQ no precisa si se usan datos reportados, promedios de ocupación o ambos. |

**Tratamiento de datos faltantes (REQ §7.3) [CONF]:**

1. Identificar el dato faltante.
2. Señalar cómo afecta a la confianza de la puntuación.
3. **No asignar cero** automáticamente.
4. Evitar penalizar sistemáticamente a las zonas con menos información.
5. Solicitar revisión humana cuando la incertidumbre pueda alterar significativamente la prioridad.

Método para cumplir el punto 4 (por ejemplo, rango de puntuación con valores mínimo y máximo plausibles) **[PROP]**, pendiente de aprobación.

#### D. Salidas

| Campo lógico [PROP] | Contenido |
| --- | --- |
| `id_afectacion` | Heredado |
| `categoria_instalacion` | hospital / policlínica / centro de salud / escuela / otra / incierta |
| `nivel_jerarquia` | 1 a 5 |
| `puntuacion_P` | Solo para nivel 5; con T, V, A desglosados |
| `rango_P` | Si hay faltantes **[PROP]** |
| `factores_explicados` | Texto justificativo por factor |
| `datos_faltantes`, `confianza` | Explícitos |
| `requiere_revision_humana` | Sí/No con motivo |
| `version_reglas` | Versión de pesos, normalización y jerarquía |

**Destinatarios:** Agente 4 (planificación), Agente 6 (explicación de prioridades), supervisor (revisiones).

**Tarea completada cuando:** cada afectación tiene categoría (o "incierta" con motivo), nivel jerárquico, y si es nivel 5, P con desglose y confianza.

#### E. Reglas de decisión

| ID | Condición | Acción | Resultado |
| --- | --- | --- | --- |
| A3-R1 | La afectación corresponde a un hospital, policlínica, centro de salud o escuela. | Aplica la jerarquía. | Nivel 1–4, ordenado antes que cualquier afectación de nivel 5 **[CONF]**. |
| A3-R2 | La afectación no corresponde a ninguna de esas instalaciones. | Calcula P con T, V y A normalizados entre 0 y 100 **[CONF]**. | Nivel 5 con P. |
| A3-R3 | La categoría de instalación es incierta (p. ej., el reporte menciona "clínica"). | No elige en silencio; registra alternativas. | Categoría "incierta" y revisión humana **[PROP]**. |
| A3-R4 | Dos instalaciones de la misma categoría compiten. | Propone orden por mayor tiempo sin agua y luego por mayor número estimado de personas afectadas. | Si persiste el empate o faltan datos, revisión humana; regla detallada **[PROP]**. |
| A3-R5 | Empate de P entre afectaciones de nivel 5. | Propone desempatar por mayor tiempo sin agua y luego por mayor número estimado de personas afectadas. | Si persiste el empate, elevar al supervisor **[PROP]**. |
| A3-R6 | Falta uno o más de T, V o A. | Aplica REQ §7.3; no asigna cero. | No asignar cero ni inventar el valor; presentar rango/resultado incompleto, explicar el dato faltante y solicitar revisión humana si puede cambiar el orden **[CONF]**. |
| A3-R7 | Un caso residencial parece una emergencia extraordinaria. | No altera la jerarquía. | Puede proponer una excepción justificada, pero solo el supervisor puede aprobarla; nunca altera por sí mismo la jerarquía **[CONF]**. |
| A3-R8 | Se recibe una solicitud de cambiar pesos o reglas. | No la aplica. | Requiere aprobación del supervisor (REQ §12). |

**Definición de variables [CONF]:**

- `T`: puntuación normalizada del tiempo sin agua. La compensación del tiempo transcurrido se aplicará **solo a la prioridad**, no a la demanda **[CONF]**. El factor T aumentará progresivamente con el tiempo sin agua hasta un máximo de 100 a los 5 días **[CONF]**. La escala lineal aprobada para el prototipo es `T = min(100, días_sin_agua / 5 × 100)` **[CONF]**; redondeo y fechas/horas faltantes o inciertas siguen **[PEND]**.
- `V`: puntuación de vulnerabilidad basada en los criterios aprobados: zona cercana/a la que pertenece una institución de salud, escuela, comunidad rural, comunidad residencial, comunidad antigua y comunidad con población infantil/joven **[CONF]**. La jerarquía cualitativa inicial indicada es: 1) institución de salud, 2) escuela, 3) área rural, 4) residencial **[CONF como orden de categorías]**. La traducción numérica exacta a 0–100, el radio de cercanía y la regla de combinación cuando coinciden varios criterios siguen **[PEND]**; no inventar puntuaciones numéricas.
- `A`: puntuación asociada a la cantidad de personas afectadas, estimada con los promedios de ocupación por tipo de ubicación del documento y limitada al máximo de personas/unidades validado para cada lugar **[CONF]**. No contar por encima del máximo validado de una ubicación. La transformación numérica de la estimación a 0–100 y los máximos de cada lugar cuando no estén disponibles en los datos siguen **[PEND]**; nunca inventarlos.
- Escala de cada factor: 0 a 100. La transformación de V y A a esa escala sigue **[PEND]**.
- Los criterios cualitativos para V y el uso de promedios/máximos validados para A están aprobados **[CONF]**; la conversión numérica exacta de V y A a 0–100 sigue **[PEND]**. Para empates, aplicar primero mayor tiempo sin agua y luego mayor número estimado de personas afectadas; si persiste el empate o faltan datos relevantes, elevar al supervisor **[CONF como procedimiento]**.

**No debe decidir automáticamente:** excepciones a la jerarquía, desempates sin regla aprobada, categorías inciertas que cambien el nivel jerárquico, cambios de ponderación.

#### F. Límites y restricciones

- **Permitido:** calcular y explicar prioridades; ordenar como recomendación.
- **Prohibido:** alterar la jerarquía sin aprobación; asignar cero a factores faltantes; presentar la prioridad como garantía de atención; modificar pesos; asignar recursos.
- **Dependencias:** Agentes 1 y 2; reglas de normalización aprobadas **[PEND]**.
- **Errores:** si la conversión numérica de V o A no está configurada con reglas aprobadas, el agente no inventa puntuaciones; devuelve cálculo incompleto y escala a revisión. La implementación inicial puede usar las reglas confirmadas y marcar cualquier campo sin datos como pendiente **[CONF]**.

#### G. Nivel de autonomía

| Elemento | Contenido |
| --- | --- |
| **Nivel asignado [PROP]** | **Nivel 1 — Ejecución controlada** para el cálculo; **Nivel 0 — Asistencia** respecto del efecto operativo del orden. |
| **Justificación** | El cálculo sigue reglas explícitas y es reproducible; el orden resultante solo es una recomendación hasta que se incorpora a un plan aprobado. |
| **Sin autorización** | Categorizar con datos claros, aplicar jerarquía, calcular P, explicar factores. |
| **Recomienda sin ejecutar** | Orden de atención; excepciones a la jerarquía. |
| **Requiere aprobación** | Excepciones a la jerarquía; desempates sin regla; cambios de ponderación o reglas. |
| **Detener y escalar** | Incertidumbre que pueda alterar significativamente la prioridad; datos contradictorios que cambien una decisión crítica. |

#### H. Interacción con otros agentes

| Dirección | Agente | Datos | Condición |
| --- | --- | --- | --- |
| Recibe | Agentes 1 y 2 | Registro y ubicación | Ambos con estado asignado. |
| Entrega | Agente 4 | Lista priorizada con explicación e incertidumbres | Prioridad calculada. |
| Entrega | Agente 6 | Explicación de prioridad | Cuando se solicite o cambie. |
| Eleva | Supervisor | Excepciones, empates, categorías inciertas | A3-R3 a A3-R8. |

**Conflictos:** si nuevos datos (p. ej., actualización del Agente 1) cambian el nivel jerárquico de una afectación ya incluida en un plan aprobado, el Agente 3 recalcula, registra el cambio y lo notifica al Agente 4 y al supervisor; no reordena planes aprobados por sí mismo.

#### I. Criterios de aceptación

| Caso | Resultado esperado |
| --- | --- |
| Jerarquía | Un hospital y una zona residencial con P = 95 → el hospital precede siempre. |
| Jerarquía interna | Policlínica y escuela → la policlínica precede. |
| Fórmula | T = 80, V = 60, A = 40 → P = 0,50×80 + 0,25×60 + 0,25×40 = 65. |
| Incompleto | V faltante → no se usa V = 0; P con confianza reducida o rango, faltante explícito. |
| Equidad | Una zona sin datos de vulnerabilidad no queda sistemáticamente al final por ese motivo. |
| Contradictorio | Categoría "hospital" según un reporte y "vivienda" según otro → categoría "incierta" y revisión humana. |
| Empate | P idénticos → empate señalado, sin desempate inventado. |
| Intervención humana | Solicitud de cambiar pesos a 40/30/30 → no se aplica sin aprobación registrada. |

---

### 4.4. Agente 4 — Planificación de Recursos (planificación de recursos y demanda de agua)

#### A. Identificación

| Campo | Contenido |
| --- | --- |
| **Nombre** | Agente de Planificación de Recursos (REQ: Agente 4, planificación de recursos y demanda de agua). |
| **Objetivo principal** | Calcular la cantidad estimada de agua necesaria y proponer distribuciones según la demanda, la prioridad y los recursos disponibles (REQ §2.4) **[CONF]**. |
| **Problema que resuelve** | Traducir afectaciones priorizadas en necesidades de agua cuantificadas y en propuestas de asignación de cisternas compatibles con la flota realmente disponible. |
| **Alcance** | Cálculo de demanda, evaluación de flota y disponibilidad horaria, propuesta de asignación, cálculo de cobertura, consolidación del paquete de plan **[PROP]** y determinación de la aprobación necesaria. No calcula rutas ni ejecuta asignaciones. |

#### B. Responsabilidades específicas

**Tareas [CONF] (REQ §2.4, §8, §9, §11):**

1. Estimar la demanda diaria por afectación con la tabla de REQ §3.
2. Usar promedios de ocupación cuando no exista información real verificada; preferir datos reales y confiables, dejando constancia de la fuente.
3. Aplicar las duraciones de cálculo aprobadas: falta de agua = 1 día; tubería rota = 2 días; contaminación = 2 días **[CONF]**. Son parámetros de planificación, no garantía de duración real de la emergencia. No modificar los días de planificación ni la demanda según el tiempo transcurrido sin agua; DEC-01 confirma que ese tiempo afecta solo a la prioridad.
4. Calcular la demanda total y el volumen que puede suministrarse.
5. Identificar faltantes de agua y recursos.
6. Proponer planes de cobertura parcial cuando cumplan los criterios (≥ 80 %).
7. Comprobar que las cantidades propuestas no superen el inventario disponible.
8. Comprobar simultáneamente los criterios de asignación de REQ §11.
9. Identificar las propuestas que requieren aprobación del supervisor.

**Información que debe analizar:** prioridades (Agente 3), tipos y tiempos (Agente 1), ubicaciones (Agente 2), flota y disponibilidad horaria (fuente real **[PEND]**; parámetros de referencia de REQ §5–§6), factibilidad de rutas (Agente 5).

**Decisiones que puede tomar:** qué alternativa de asignación **proponer**; si una propuesta cumple los criterios ordinarios o requiere elevación.

**Fuera de su alcance:**

| Responsabilidad | Propietario |
| --- | --- |
| Calcular rutas, distancias y autonomía | Agente 5 |
| Determinar prioridades | Agente 3 |
| Aprobar planes o excepciones | Supervisor |
| Solicitar físicamente cisternas adicionales o despacharlas | Acción operativa humana; mecanismo **[PEND]** |
| Validar fuentes de agua para afectaciones por contaminación | Autoridades competentes (REQ §8.3) |

#### C. Entradas

| Dato | Fuente | Estado |
| --- | --- | --- |
| Lista priorizada | Agente 3 | — |
| Tipo, tiempo transcurrido, datos reportados de población | Agente 1 | — |
| Ubicaciones con certeza | Agente 2 | — |
| Demanda de referencia (gal/día) | REQ §3 | [CONF] |
| Promedios de ocupación | REQ §3 | [CONF] |
| Duraciones de cálculo por tipo | Decisiones DEC-05/DEC-24 | [CONF] para el modelo de planificación; no garantizan duración real |
| Inventario de flota (71 cisternas) y capacidades | REQ §5 | [CONF] como referencia |
| Disponibilidad horaria y demoras | REQ §6 | [PROV] |
| Disponibilidad real confirmada de cisternas | **[PEND]** (REQ §17.10) | — |
| Ubicación de la organización y puntos de recogida | Organización **[PEND: se confirmará después]**; punto de carga definido por ruta **[CONF como enfoque]** | — |
| Factibilidad de rutas | Agente 5 | — |

**Tabla de demanda de referencia [CONF]:**

| Tipo | Demanda diaria | Promedio de ocupación |
| --- | --- | --- |
| Apartamentos | 79,3 gal/persona | 100 personas por edificio |
| Vivienda residencial | 79,3 gal/persona | 3 personas por vivienda |
| Vivienda rural | 26,4 gal/persona | 4 personas por vivienda |
| Escuela | 4 gal/estudiante | 700 estudiantes |
| Hospital | 13.208 gal/día **[CONF]** | — |
| Policlínica | 4.755 gal/día **[CONF]** | — |
| Centro de salud pequeño | 1.320 gal/día **[CONF]** | — |

Los promedios son por edificio, vivienda o escuela; **no** representan la población total de una comunidad **[CONF]**. Para estimar A, usar promedios asociados a las unidades/localizaciones conocidas; la delimitación de zona debe registrarse y sigue **[PEND]**.

**Tratamiento de información:**

- **Faltante** (p. ej., número de viviendas): no se inventa; la demanda queda incompleta y se señala la parte del cálculo afectada (REQ §14).
- **Desactualizada** (disponibilidad de flota sin confirmar): se trata como parámetro de planificación, nunca como evidencia de disponibilidad (REQ §11) **[CONF]**.
- **Contradictoria** (población reportada vs. promedio): prevalecen los datos reales **verificados**; si no están verificados, se presentan ambos valores y se eleva si cambia la decisión.

#### D. Salidas

**1. Cálculo de demanda por afectación [PROP formato]:** demanda diaria, base usada (dato real o promedio y su fuente), días de planificación, fórmula aplicada, demanda estimada, supuestos.

**2. Estado de flota [CONF categorías, REQ §5]:** para cada tipo (Small/Big) y origen (propia/subcontratada):

| Categoría | Significado |
| --- | --- |
| Total registrada | Inventario de referencia. |
| Disponible en el horario solicitado | Según parámetros horarios **[PROV]** o datos reales. |
| Confirmada para la operación | Solo con confirmación real. |
| Pendiente de solicitud o confirmación | Necesaria pero no confirmada; incluye demora estimada. |
| Fuera de servicio | Excluida. |

**3. Paquete de plan [PROP como consolidación; contenido CONF según REQ §2.7 y §9]:**

| Elemento | Origen |
| --- | --- |
| Motivo de la propuesta | Agente 4 |
| Afectaciones atendidas y su prioridad | Agente 3 |
| Demanda estimada | Agente 4 |
| Volumen que puede suministrarse | Agente 4 |
| Porcentaje de cobertura y volumen pendiente | Agente 4 |
| Cisternas requeridas y disponibles (con estado) | Agente 4 |
| Ruta y restricciones | Agente 5 |
| Motivo de cobertura no total | Agente 4 |
| Riesgos e incertidumbres | Agentes 2, 3, 4, 5 |
| Tipo de aprobación requerida | Agente 4 |

**Destinatarios:** Agente 5 (asignación para ruteo), supervisor (paquete de plan), Agente 6 (estado y mensaje de cobertura parcial).

**Tarea completada cuando:** existe un paquete de plan con todos los elementos, en estado *Pendiente de aprobación*, o un informe de déficit que explica por qué no puede proponerse un plan.

#### E. Reglas de decisión

**Cálculo de demanda:**

| ID | Regla | Estado |
| --- | --- | --- |
| A4-R1 | Demanda diaria = número de unidades × ocupación (real o promedio) × demanda por persona/estudiante; o valor fijo para instalaciones de salud. | [CONF] |
| A4-R2 | No se aplica compensación temporal a los días de planificación: el tiempo transcurrido sin agua afecta solo a la prioridad (DEC-01). | [CONF] |
| A4-R3 | Demanda estimada = demanda diaria × duración de planificación aprobada para el tipo de afectación. Duraciones de cálculo: falta de agua = 1 día, tubería rota = 2 días y contaminación = 2 días **[CONF] para el modelo**. No se suma el tiempo transcurrido sin agua a la demanda. | [CONF] para el modelo de planificación |
| A4-R4 | Si los días transcurridos no se conocen, no se suponen cero: se calcula con la duración estimada **y** se marca que la demanda puede estar subestimada. | [PROP] conforme a REQ §14 |
| A4-R5 | Para instalaciones de salud, los valores fijos se interpretan como demanda diaria **[CONF]**. | [CONF] / aplicación [PEND] |

Ejemplos verificables (REQ §8):

- Escuela con 700 estudiantes: `700 × 4 = 2.800 gal/día`.
- 20 viviendas rurales: `20 × 4 × 26,4 = 2.112 gal/día`.
- Falta de agua con 2 días sin servicio: los 2 días transcurridos se entregan al Agente 3 para la prioridad; **no** se suman a la duración de planificación ni a la demanda (DEC-01).

**Cobertura y aprobación (REQ §9) [CONF]:**

`Cobertura (%) = (volumen entregable / demanda estimada) × 100`

| ID | Cobertura | Acción | Estado resultante |
| --- | --- | --- | --- |
| A4-R6 | = 100 % | Presenta el plan para revisión del supervisor. | *Pendiente de aprobación* antes de cualquier ejecución **[CONF]**. |
| A4-R7 | ≥ 80 % y < 100 % | Presenta como cobertura parcial con todos los campos de REQ §9; activa el mensaje especial del Agente 6. | *Pendiente de aprobación* — no ejecutable sin aprobación **[CONF]**. |
| A4-R8 | < 80 % | No lo presenta como plan ordinario; lo revisa o lo eleva para decisión extraordinaria. | *Pendiente de aprobación (extraordinaria)* **[CONF]**; condiciones operativas específicas de autorización **[PEND]**. |
| A4-R9 | Unidades incoherentes o demanda no identificable. | No calcula cobertura. | *Pendiente de información* **[CONF]**. |

El 80 % mínimo se mide sobre el plan de solución de cada incidente **[CONF]**. La autorización de planes por debajo del 80 % requiere una decisión extraordinaria del supervisor, con justificación, cobertura y demanda no satisfecha registradas **[CONF como procedimiento aceptado]**; criterios específicos para autorizarlo siguen **[PEND]**.

**Asignación de cisternas (REQ §11) [CONF]:**

| ID | Regla |
| --- | --- |
| A4-R10 | Comprobar simultáneamente: disponibilidad horaria, tipo, capacidad de agua, volumen necesario, ubicaciones de salida y recogida, ruta completa y retorno, tiempo de solicitud y restricciones de operación. |
| A4-R11 | Usar la disponibilidad real confirmada cuando exista; los mínimos y demoras horarias son parámetros, no evidencia de vehículos libres. |
| A4-R12 | No asignar la misma cisterna a dos operaciones incompatibles en el mismo periodo. |
| A4-R13 | No proponer cantidades superiores al inventario disponible. |
| A4-R14 | Si la flota no permite satisfacer todas las demandas: comparar alternativas, explicar necesidades pendientes y respetar la prioridad. |
| A4-R15 | Las capacidades (Small 3.000–5.500 gal; Big 9.000–13.000 gal) son de **agua**, no de combustible. Si no se conoce la capacidad concreta de una unidad, usar la **mínima** del rango para no sobrestimar el volumen entregable **[PROP]**. |
| A4-R16 | Para el cálculo del prototipo, asumir que el agua transportada por cisternas está limpia y calcular la demanda de la afectación por contaminación usando 2 días **[CONF como supuesto de planificación]**. El agente no verifica la potabilidad. Antes de cualquier operación real, la fuente y la potabilidad deben ser verificadas por responsables competentes; si no existe esa validación, no habilitar el despacho real y escalar. | [CONF para planificación; salvaguarda operativa] |

**Disponibilidad horaria [PROV] (REQ §6):**

| Horario | Parámetro |
| --- | --- |
| 06:00–08:00 | Se pueden solicitar más cisternas; demora estimada 1,5 h. |
| 08:00–16:00 | Mínimo 25 cisternas (5 propias, 20 subcontratadas); solicitar más: 40 min. |
| 16:00–19:00 | Solicitudes adicionales con demora provisional de 1,5 h **[PROV]**. |
| 19:00–06:00 | Solo 10 cisternas, todas subcontratadas. |

Los intervalos se interpretan de forma contigua: al terminar un intervalo comienza el siguiente, sin solapamiento **[CONF]**. A las 19:00 cambia la disponibilidad de cisternas; no se modifica por esa razón la demora indicada para el tramo anterior **[CONF]**. El horario y la demora 16:00–19:00 siguen **[PROV]** hasta validación operativa.

**No debe decidir automáticamente:** aprobar cualquier plan, solicitar cisternas adicionales, autorizar cobertura < 80 %, convertir el supuesto de planificación de agua limpia en una certificación sanitaria real, ni reasignar recursos de un plan aprobado.

#### F. Límites y restricciones

- **Permitido:** calcular demanda, evaluar flota, generar alternativas, consolidar paquetes de plan, determinar la aprobación requerida.
- **Prohibido:** inventar capacidades, inventarios, disponibilidades o volúmenes; presentar una propuesta como asignación autorizada; ejecutar o despachar; solicitar vehículos; registrar entregas como realizadas.
- **Dependencias:** Agentes 1, 2, 3 y 5; fuentes de disponibilidad real **[PEND]**.
- **Errores:** si falta un dato indispensable para una operación segura, solicita confirmación (REQ §14.5) y no presenta el plan como listo.

**Distinción obligatoria:**

| Término | Significado |
| --- | --- |
| Planificación recomendada | Propuesta del Agente 4; sin efecto operativo. |
| Asignación autorizada | Propuesta aprobada por el supervisor, con registro de aprobación. |
| Asignación ejecutada | Acción operativa efectivamente realizada y registrada por quien la ejecuta (mecanismo **[PEND]**). |

#### G. Nivel de autonomía

| Elemento | Contenido |
| --- | --- |
| **Nivel asignado [PROP]** | **Nivel 0 — Asistencia** (con cálculos internos de Nivel 1). |
| **Justificación** | Sus resultados son propuestas con impacto operativo directo sobre recursos escasos; REQ exige aprobación para coberturas parciales y no documenta capacidad de ejecución. |
| **Sin autorización** | Calcular demanda y cobertura; evaluar flota; generar y comparar alternativas; consolidar paquetes de plan. |
| **Recomienda sin ejecutar** | Asignación de cisternas; solicitud de cisternas adicionales; planes de cobertura parcial. |
| **Requiere aprobación** | Todo plan para ejecución; cobertura 80–<100 %; cobertura < 80 % (extraordinaria); cambios importantes en planes aprobados. |
| **Detener y escalar** | Inventario insuficiente; para operación real, falta de verificación sanitaria de la fuente/agua; datos contradictorios que cambien la asignación; doble asignación detectada; unidades o demanda no identificables. En el prototipo, el supuesto de agua limpia solo habilita el cálculo, no un despacho real. |

#### H. Interacción con otros agentes

| Dirección | Agente | Datos | Condición |
| --- | --- | --- | --- |
| Recibe | Agente 3 | Lista priorizada | Prioridad calculada. |
| Recibe | Agentes 1 y 2 | Tipo, tiempos, población reportada, ubicación | Registros transferibles. |
| Entrega | Agente 5 | Asignación propuesta: cisternas, capacidades, volúmenes, afectaciones, horario | Asignación compatible con inventario. |
| Recibe | Agente 5 | Ruta clasificada y alternativas | Cálculo de ruta finalizado. |
| Entrega | Supervisor | Paquete de plan | Paquete completo. |
| Entrega | Agente 6 | Estado del plan; datos para mensaje de cobertura parcial | Cobertura parcial o cambio de estado. |

**Conflictos:** si el Agente 5 declara inviable la ruta, el Agente 4 reformula la asignación (otra cisterna, otro tipo, otra combinación) o documenta el déficit; no fuerza la ruta. Si los recursos no alcanzan para respetar la prioridad, presenta las alternativas y la consecuencia de cada una al supervisor.

#### I. Criterios de aceptación

| Caso | Resultado esperado |
| --- | --- |
| Normal | Escuela sin datos reales → 2.800 gal/día con el promedio de 700 estudiantes y la fuente "promedio REQ §3". |
| Dato real | Escuela con 450 estudiantes verificados → 1.800 gal/día; prevalece el dato real con su fuente. |
| Separación prioridad/demanda | Falta de agua con 2 días sin servicio → `T = 40` según la escala aprobada; la duración de planificación sigue siendo 1 día para falta de agua. El tiempo transcurrido no cambia la demanda. |
| Cobertura parcial | Demanda 10.000 gal, entregable 8.500 → 85 %, pendiente 1.500 gal, *Pendiente de aprobación*, mensaje especial activado. |
| Cobertura insuficiente | 7.000 de 10.000 → 70 %; no se presenta como plan ordinario; elevación extraordinaria. |
| Inventario | Plan que requiere 30 cisternas a las 22:00 → no se propone más de lo disponible; déficit documentado. |
| Doble asignación | Misma cisterna en dos operaciones simultáneas → detectado y bloqueado. |
| Contaminación | Para el prototipo, se calcula demanda con 2 días suponiendo agua de cisterna limpia; no se afirma que el agua real sea potable. Antes de despacho real, validar fuente/potabilidad y escalar si falta validación. |
| Incompleto | Comunidad sin número de viviendas → demanda no calculada, faltante explícito, sin cifra inventada. |
| Distinción de estados | Ningún plan aparece como "aprobado" o "ejecutado" sin registro de aprobación o ejecución. |

---

### 4.5. Agente 5 — Optimización de Rutas

#### A. Identificación

| Campo | Contenido |
| --- | --- |
| **Nombre** | Agente de Optimización de Rutas (REQ: Agente 5). |
| **Objetivo principal** | Proponer rutas factibles para las cisternas asignadas a las afectaciones (REQ §2.5) **[CONF]**. |
| **Problema que resuelve** | Convertir una asignación de cisternas en un recorrido completo viable, dentro de los límites de distancia y con identificación de riesgos. |
| **Alcance** | Cálculo y clasificación de rutas de recorrido completo para asignaciones propuestas por el Agente 4. No asigna cisternas ni prioriza afectaciones. |

#### B. Responsabilidades específicas

**Tareas [CONF] (REQ §2.5, §10):**

1. Construir cada ruta con el recorrido completo, en este orden: salida desde la organización → desplazamiento al punto de recogida → recogida de agua → atención de las afectaciones asignadas → regreso a la organización.
2. Calcular la distancia de **todos** los desplazamientos, no solo la ida.
3. Considerar capacidad de agua, disponibilidad y tipo de vehículo, condiciones de las vías, tráfico y elevación, autonomía y consumo de combustible cuando existan datos validados, y tiempo de solicitud de cisternas adicionales.
4. Intentar mantener cada ruta dentro del límite de 1.000 km **[PROV]**.
5. Clasificar cada ruta (ver §4.5.D).
6. Para rutas que superan el límite, preparar la solicitud de excepción con justificación, distancia adicional, riesgos y alternativas.

**Información que debe analizar:** asignación propuesta (Agente 4), ubicaciones validadas (Agente 2), ubicación de la organización y del punto de recogida **[PEND]**, datos de vías, tráfico y elevación **[PEND]**, datos de combustible **[PEND]**.

**Decisiones que puede tomar:** qué ruta proponer entre las evaluadas; cómo clasificarla.

**Fuera de su alcance:**

| Responsabilidad | Propietario |
| --- | --- |
| Asignar o cambiar cisternas | Agente 4 |
| Validar o corregir ubicaciones | Agente 2 |
| Aprobar excepciones de distancia | Supervisor |
| Verificar la seguridad del recorrido y la viabilidad de combustible | Supervisor **[CONF]** |

> **Objetivo de optimización [PROP aceptada como criterio de diseño]:** respetar la prioridad, capacidades y restricciones; maximizar la demanda cubierta y, entre planes comparables, minimizar la distancia total. La ruta debe incluir organización → carga → afectaciones → regreso a la organización. La ruta > 1.000 km requiere aprobación de excepción. No declarar seguridad o autonomía confirmadas sin verificación del supervisor.

#### C. Entradas

| Dato | Fuente | Requisito mínimo |
| --- | --- | --- |
| Asignación propuesta | Agente 4 | Cisternas con tipo y capacidad, afectaciones y volúmenes, horario. |
| Ubicaciones de afectaciones | Agente 2 | Estado de certeza explícito. |
| Ubicación de la organización | **[PEND]** | Indispensable para el recorrido completo. |
| Punto(s) de recogida de agua | **[PEND]** | Indispensable para el recorrido completo. |
| Vías, tráfico, elevación | **[PEND]** | Si faltan, la ruta no puede ser "factible" sin observación. |
| Combustible, rendimiento, autonomía | **[PEND]** — Capacidad de tanque: 400 L (Small) y 600 L (Big) **[CONF]**; consumo/autonomía **[PEND]** | No inferir consumo ni autonomía a partir de la capacidad del tanque. |

**Tratamiento:**

- Ubicación de afectación "aproximada" o "no verificada" → la ruta solo puede ser **provisional**.
- Falta de organización o punto de recogida → no se calcula ruta; *Pendiente de información*.
- Falta de datos de autonomía validados → ruta **pendiente de verificación** de autonomía (REQ §10.4) **[CONF]**.

#### D. Salidas

**Clasificación de rutas** (REQ §2.5, §10.4) **[CONF]**:

| Clasificación | Condición |
| --- | --- |
| **Factible** | Recorrido completo ≤ 1.000 km, ubicaciones con certeza suficiente, capacidad compatible con el volumen y sin restricciones conocidas incumplidas. |
| **Provisional** | Calculada con datos aproximados, no verificados o con parámetros provisionales. |
| **Requiere autorización por excepción** | Recorrido completo > 1.000 km justificado por emergencia. |
| **Pendiente de verificación** | No existe información suficiente para validar la autonomía (REQ §10.4). |
| **Inviable** [PROP] | No existe ruta que cumpla las restricciones con los datos disponibles. |

Una ruta puede acumular condiciones (p. ej., provisional y pendiente de verificación); todas deben mostrarse **[PROP]**.

**Contenido por ruta [PROP formato]:** cisterna, secuencia de paradas (las cinco etapas), distancia por tramo y total, volumen por parada, restricciones consideradas, datos faltantes, riesgos, clasificación y alternativas evaluadas.

**Distinción obligatoria:**

| Término | Significado |
| --- | --- |
| Ruta propuesta | Calculada por el Agente 5. |
| Ruta validada | Cuyas restricciones de seguridad y autonomía han sido verificadas por separado. |
| Ruta autorizada para ejecución | Aprobada por el supervisor como parte de un plan. |

**Destinatarios:** Agente 4 (consolidación del plan), supervisor (vía paquete de plan o solicitud de excepción), Agente 6 (estado).

**Tarea completada cuando:** cada cisterna de la asignación tiene una ruta clasificada con recorrido completo, o una declaración justificada de inviabilidad.

#### E. Reglas de decisión

| ID | Condición | Acción | Resultado |
| --- | --- | --- | --- |
| A5-R1 | Falta alguna de las cinco etapas del recorrido. | No presenta la ruta. | Error de construcción; recalcular. |
| A5-R2 | Recorrido completo ≤ 1.000 km y datos suficientes. | Propone la ruta. | "Factible" (aún sujeta a aprobación del plan). |
| A5-R3 | Recorrido completo ≤ 1.000 km con datos aproximados. | Propone con observaciones. | "Provisional". |
| A5-R4 | Recorrido completo > 1.000 km sin emergencia justificada. | Busca alternativas; si no hay, la declara no apta como ruta ordinaria. | Devuelta al Agente 4 para reformular. |
| A5-R5 | Recorrido completo > 1.000 km con emergencia. | Aplica los seis pasos de REQ §10.3: justificar, calcular el recorrido con retorno, comprobar autonomía y disponibilidad, presentar distancia adicional, riesgos y alternativas, solicitar aprobación, no autorizar la salida. | "Requiere autorización por excepción". |
| A5-R6 | Sin datos de autonomía validados. | Puede usar 400 L (Small) y 600 L (Big) como capacidad nominal de tanque **[CONF]**, pero no infiere autonomía ni consumo sin datos validados. | "Pendiente de verificación". |
| A5-R7 | El volumen asignado excede la capacidad de agua de la cisterna. | No la presenta. | Devuelta al Agente 4. |
| A5-R8 | Cambio importante en una ruta aprobada. | No lo aplica. | Requiere aprobación del supervisor (REQ §12). Cambios de ruta después de la aprobación y cualquier recorrido que supere 1.000 km requieren nueva revisión del supervisor **[CONF]**; umbral cuantitativo para variaciones menores sigue **[PEND]**. |
| A5-R9 | Coordenada inaccesible o incoherente. | No la corrige. | Devuelta al Agente 2. |

**No debe decidir automáticamente:** autorizar rutas > 1.000 km; autorizar la salida de un vehículo; modificar rutas aprobadas; dar por válida la autonomía; declarar óptima una ruta.

#### F. Límites y restricciones

- **Permitido:** calcular, comparar y clasificar rutas; preparar solicitudes de excepción.
- **Prohibido:** presentar como ordinaria una ruta > 1.000 km; omitir el regreso; inferir autonomía o consumo únicamente a partir de la capacidad del tanque; autorizar salidas; afirmar optimalidad sin función objetivo.
- **Dependencias:** Agentes 2 y 4; datos operativos **[PEND]**.
- **Advertencia [CONF]:** la aprobación de una excepción **no garantiza** que el vehículo tenga autonomía suficiente; la seguridad y el combustible se verifican por separado (REQ §10.3).

#### G. Nivel de autonomía

| Elemento | Contenido |
| --- | --- |
| **Nivel asignado [PROP]** | **Nivel 0 — Asistencia.** |
| **Justificación** | Una ruta implica desplazamiento real de vehículos y riesgos de seguridad; la autonomía no está validada y el límite de 1.000 km es provisional. |
| **Sin autorización** | Calcular, comparar y clasificar rutas; preparar solicitudes de excepción. |
| **Recomienda sin ejecutar** | Ruta propuesta y alternativas. |
| **Requiere aprobación** | Rutas > 1.000 km; cambios importantes en rutas aprobadas; ejecución de cualquier ruta. |
| **Detener y escalar** | Excepción de emergencia; ruta inviable que deja afectaciones prioritarias sin atención; incoherencia territorial. |

#### H. Interacción con otros agentes

| Dirección | Agente | Datos | Condición |
| --- | --- | --- | --- |
| Recibe | Agente 4 | Asignación propuesta | Asignación compatible con inventario. |
| Recibe | Agente 2 | Ubicaciones con certeza | Estado asignado. |
| Entrega | Agente 4 | Rutas clasificadas, alternativas, riesgos | Cálculo finalizado. |
| Devuelve | Agente 2 | Coordenadas problemáticas | A5-R9. |
| Eleva | Supervisor | Solicitud de excepción | A5-R5. |
| Entrega | Agente 6 | Estado de ruta | Cambio de estado. |

**Conflictos:** si la ruta más corta no atiende primero a la afectación de mayor prioridad, el agente presenta ambas alternativas y la consecuencia de cada una; el orden de prioridad no se sacrifica sin decisión humana **[PROP]**, conforme a REQ §11.

#### I. Criterios de aceptación

| Caso | Resultado esperado |
| --- | --- |
| Recorrido completo | Toda ruta incluye las cinco etapas y la distancia incluye el regreso. |
| Normal | Ruta de 420 km con datos completos → "factible". |
| Límite | Ruta de 1.050 km sin emergencia → no presentada como ordinaria. |
| Excepción | Ruta de 1.050 km con emergencia → solicitud con justificación, distancia adicional, riesgos, alternativas; salida no autorizada. |
| Combustible | Capacidad de tanque Small 400 L y Big 600 L confirmada; consumo y autonomía sin datos validados → "pendiente de verificación". |
| Ubicación aproximada | Ruta con ubicación "aproximada" → "provisional". |
| Capacidad | 6.000 gal asignados a una Small cuya capacidad es desconocida → rechazado (6.000 supera incluso el máximo de 5.500). |
| Terminología | Ninguna salida usa "óptima" mientras no exista función objetivo aprobada. |

---

### 4.6. Agente 6 — Chat Agent de Comunicación y Seguimiento

#### A. Identificación

| Campo | Contenido |
| --- | --- |
| **Nombre** | Chat Agent de Comunicación y Seguimiento (REQ: Chat Agent, comunicación). |
| **Objetivo principal** | Generar comunicaciones comprensibles y coherentes con el estado real de la planificación (REQ §2.6) **[CONF]**. |
| **Problema que resuelve** | Los resultados técnicos de los agentes deben explicarse sin crear expectativas falsas ni comprometer entregas no aprobadas. |
| **Alcance** | Responder consultas e informar estados, prioridades, coberturas y limitaciones a partir de los registros del sistema. El componente de "seguimiento" consiste en reflejar la evolución de estados registrados; no incluye verificar entregas en campo. |

#### B. Responsabilidades específicas

**Tareas [CONF] (REQ §2.6, §9):**

1. Informar sobre el estado de las afectaciones.
2. Explicar las decisiones de priorización cuando sea necesario.
3. Comunicar la cobertura prevista y las limitaciones de los planes.
4. Generar el **mensaje especial de cobertura parcial**, que debe:
   1. explicar que el suministro propuesto es parcial;
   2. indicar la cantidad estimada que se podrá entregar;
   3. explicar qué proporción de la necesidad se cubrirá;
   4. identificar la necesidad que seguirá pendiente;
   5. evitar prometer una entrega antes de la aprobación del supervisor.
5. No afirmar que una entrega está confirmada si solo existe una propuesta.
6. Usar exclusivamente información de los registros y resultados del sistema.

**Consultas que puede atender [PROP, derivado de REQ §2.6]:** estado de una afectación; motivo de su prioridad; existencia y estado de un plan; cobertura prevista y necesidad pendiente; datos pendientes o incertidumbres registradas.

**Fuera de su alcance:**

| Responsabilidad | Propietario |
| --- | --- |
| Generar o modificar datos, prioridades, planes o rutas | Agentes 1–5 |
| Aprobar planes o comunicaciones extraordinarias | Supervisor |
| Recibir reportes de afectaciones como canal oficial | Canales simulados de WhatsApp y contacto privado cuando el reporte se haya recibido por chat o llamada **[CONF como flujo objetivo]**; integración real y permisos de envío **[PEND]** |

#### C. Entradas

| Dato | Fuente |
| --- | --- |
| Estados y resultados | Registros de los Agentes 1–5 |
| Decisiones del supervisor | Registro de aprobaciones |
| Consultas de usuarios | WhatsApp/contacto privado como canales objetivo **[CONF como intención]**; integración real **[PEND]** |

**Canales y privacidad:** el objetivo es responder a usuarios por WhatsApp y por contacto privado cuando el reporte haya llegado por chat o llamada **[CONF como requisito de diseño]**. El prototipo usa mensajes simulados; envío real por WhatsApp, permisos y mecanismo de consentimiento **[PEND]**. El único dato personal de contacto previsto para guardar es el número celular **[CONF]**; no guardar otros datos personales innecesarios. Retención, acceso, cifrado y manejo de medios originales/transcripciones siguen **[PEND]**.

**Tratamiento:** si el dato no existe en los registros, el agente lo dice; si el registro está desactualizado, indica la fecha de su último estado; si hay contradicción entre registros, no elige: informa que el caso está en revisión.

**Integración futura de WhatsApp [CONF como arquitectura prevista]:** definir una interfaz `MessagingProvider` con implementación `MockMessagingProvider` para pruebas y un adaptador futuro `WhatsAppCloudApiProvider`. El adaptador real se implementará después de configurar un portafolio comercial de Meta, una cuenta de WhatsApp Business (WABA), un número empresarial registrado, un token seguro y permisos de mensajería/gestión, además de una aplicación backend accesible mediante HTTPS con webhook entrante y validación de solicitudes. Los tokens se guardan en variables de entorno/gestor de secretos y nunca en el repositorio. Los mensajes salientes permanecen simulados hasta aprobación explícita. **Coste:** se puede desarrollar y probar la interfaz simulada sin pagar a Meta ni enviar mensajes reales. La Cloud API no debe considerarse completamente gratuita: Meta cobra según su tarifa vigente para los tipos/categorías de mensajes aplicables, y el alojamiento del backend o del webhook también puede tener coste. Revisar la tarifa oficial antes de activar el canal real. Referencias: documentación de Cloud API de Meta (https://developers.facebook.com/docs/whatsapp/cloud-api/overview) y términos de WhatsApp Business (https://www.whatsapp.com/legal/meta-terms-whatsapp-business).

#### D. Salidas

- Respuestas a consultas con el **estado registrado** y su **fecha**.
- Explicaciones de prioridad basadas en los factores del Agente 3.
- Mensajes de cobertura parcial (plantilla lógica **[PROP]**):

  > Para la afectación [id/zona], el plan **propuesto** prevé un suministro **parcial** de aproximadamente [volumen] galones, equivalente al [x] % de la necesidad estimada de [demanda] galones. Quedarían pendientes unos [pendiente] galones. Este plan **está pendiente de aprobación** y no constituye una confirmación de entrega.

- Borradores de comunicación pública extraordinaria, siempre en estado *Pendiente de aprobación*.

**Destinatarios:** usuarios de la interfaz **[PEND]**; supervisor (borradores y remisiones).

**Tarea completada cuando:** la respuesta coincide con el último estado registrado, distingue propuesta/aprobado/ejecutado/verificado y declara las incertidumbres relevantes.

#### E. Reglas de decisión

| ID | Condición | Acción |
| --- | --- | --- |
| A6-R1 | Estado registrado = Propuesto o Pendiente de aprobación. | Comunicar como propuesta; nunca como entrega confirmada. |
| A6-R2 | Estado = Aprobado. | Comunicar como aprobado, no como entregado. |
| A6-R3 | Estado = Ejecutado / Verificado (registrados por quien corresponda). | Comunicar con la fecha del registro. |
| A6-R4 | Cobertura parcial propuesta. | Generar el mensaje especial con los cinco elementos de REQ §9. |
| A6-R5 | Consulta sobre hora de llegada sin dato registrado. | Indicar que no existe hora confirmada; no estimarla por cuenta propia. |
| A6-R6 | Consulta sobre ubicación aproximada o datos inciertos. | Comunicar la incertidumbre tal como está registrada. |
| A6-R7 | Comunicación pública extraordinaria. | Preparar borrador y obtener autorización (REQ §12). Definición de "extraordinaria" **[PEND]**. |
| A6-R8 | Solicitud fuera de competencia (p. ej., "cambien mi prioridad", "envíen una cisterna"). | No comprometer; remitir a la persona responsable. |
| A6-R9 | Registros contradictorios. | Informar que el caso está en revisión. |
| A6-R10 | Información sobre agua contaminada. | No afirmar seguridad ni inseguridad sanitaria sin validación de autoridades; reflejar el estado registrado. |

**No debe decidir automáticamente:** promesas de suministro, horarios de llegada, confirmaciones de atención, comunicaciones públicas extraordinarias, ni información sanitaria no validada.

#### F. Límites y restricciones

- **Permitido:** responder con datos registrados, explicar, redactar borradores.
- **Prohibido:** inventar estados, compromisos, horarios o confirmaciones; modificar registros; publicar comunicaciones extraordinarias sin autorización; revelar datos personales sin política definida **[PEND]**.
- **Dependencias:** registros de todos los agentes y del supervisor.

#### G. Nivel de autonomía

| Elemento | Contenido |
| --- | --- |
| **Nivel asignado [PROP]** | **Nivel 1 — Ejecución controlada** para respuestas informativas; **Nivel 0** para comunicaciones públicas extraordinarias. |
| **Justificación** | Informar estados registrados es acotado y verificable; una comunicación pública tiene efectos externos difíciles de revertir. |
| **Sin autorización** | Responder consultas con datos registrados; generar el mensaje de cobertura parcial como información de un plan pendiente **[PROP]** — su difusión fuera del sistema depende de canales y permisos **[PEND]**. |
| **Requiere aprobación** | Comunicaciones públicas extraordinarias. |
| **Detener y escalar** | Solicitudes de compromisos, consultas con riesgo sanitario, contradicciones, peticiones fuera de competencia. |

#### H. Interacción con otros agentes

| Dirección | Agente | Datos | Condición |
| --- | --- | --- | --- |
| Recibe | Agentes 1–5 | Estados, prioridades, planes, rutas, incertidumbres | Cada cambio registrado. |
| Recibe | Agente 4 | Datos del mensaje de cobertura parcial | A4-R7. |
| Recibe | Supervisor | Aprobaciones y autorizaciones de comunicación | Decisión registrada. |
| Remite | Supervisor / persona responsable | Casos fuera de competencia | A6-R7, A6-R8. |

El Agente 6 **no envía instrucciones** a los demás agentes; solo consume sus resultados. **[PROP]**

#### I. Criterios de aceptación

| Caso | Resultado esperado |
| --- | --- |
| Normal | Consulta sobre afectación con plan aprobado → "aprobado", con fecha, sin decir "entregado". |
| Cobertura parcial | Plan al 85 % → mensaje con los cinco elementos y aviso de aprobación pendiente. |
| Incompleto | Consulta sin dato de hora → "no hay hora confirmada". |
| Contradictorio | Dos estados incompatibles → "caso en revisión". |
| Fuera de competencia | "Prioricen mi calle" → sin compromiso; remisión. |
| Sanitario | Consulta sobre si el agua ya es potable sin validación → no se afirma. |
| Integridad | Ninguna respuesta contiene datos ausentes de los registros. |

---

## 5. Matriz de autonomía

### 5.1. Escala utilizada [PROP]

REQ no establece una escala oficial. Se utiliza provisionalmente la siguiente, que **no representa permisos técnicos existentes**:

| Nivel | Nombre | Descripción |
| --- | --- | --- |
| 0 | Asistencia | Analiza y recomienda; no ejecuta decisiones operativas. |
| 1 | Ejecución controlada | Realiza tareas acotadas y reversibles dentro de reglas explícitas. |
| 2 | Autonomía condicionada | Ejecuta decisiones previamente autorizadas dentro de límites definidos. |
| 3 | Autonomía ampliada | Ejecuta acciones expresamente autorizadas con controles y supervisión. |

**Ningún agente recibe nivel 2 o 3**, porque REQ no documenta capacidades de ejecución operativa ni autorizaciones previas que lo justifiquen. La posibilidad técnica de automatizar una acción no basta para conceder autonomía.

### 5.2. Matriz

| Agente | Nivel | Puede hacer autónomamente | Recomienda, no ejecuta | Requiere aprobación humana | Escala cuando | Registros obligatorios |
| --- | --- | --- | --- | --- | --- | --- |
| 1. Ingesta y Validación | 1 | Crear, clasificar y marcar registros; calcular tiempo transcurrido; marcar duplicados y alertas sanitarias | Fusión de duplicados | Fusionar/descartar registros; reclasificar registros incluidos en planes aprobados | Contradicciones críticas; tipos no catalogados; contaminación | Original, fuente, clasificación, confianza, faltantes, estados |
| 2. Geolocalización | 1 | Normalizar, asociar zona, asignar coordenadas con certeza, listar instalaciones cercanas | Elección entre ubicaciones alternativas | Elección que afecte prioridad o ruta | Ambigüedad en instalaciones críticas; ausencia de datos; fuera de ámbito | Ubicación original y normalizada, certeza, fuente territorial |
| 3. Priorización | 1 (cálculo) / 0 (efecto) | Categorizar con datos claros, aplicar jerarquía, calcular P, explicar | Orden de atención; excepciones | Excepciones a la jerarquía; desempates sin regla; cambio de pesos | Incertidumbre significativa; categoría incierta; empates relevantes | Factores, pesos, versión de reglas, faltantes, confianza |
| 4. Planificación de Recursos | 0 | Calcular demanda y cobertura; evaluar flota; comparar alternativas; consolidar plan | Asignación de cisternas; solicitud de cisternas adicionales | Todo plan a ejecutar; cobertura parcial; cobertura < 80 %; cambios a planes aprobados | Déficit; contaminación sin validación; doble asignación; datos contradictorios | Fórmulas, bases de cálculo, inventario usado, alternativas, motivos |
| 5. Optimización de Rutas | 0 | Calcular, comparar y clasificar rutas; preparar excepciones | Ruta y alternativas | Rutas > 1.000 km; cambios importantes; ejecución | Emergencia; inviabilidad; autonomía no verificable | Tramos, distancias, restricciones, datos faltantes, clasificación |
| 6. Chat Agent | 1 / 0 | Responder con datos registrados | Borradores de comunicación pública | Comunicación pública extraordinaria | Compromisos solicitados; temas sanitarios; contradicciones | Consulta, respuesta, registros fuente usados |

---

## 6. Reglas de aprobación humana y escalamiento

### 6.1. Situaciones de aprobación obligatoria [CONF] (REQ §12)

| Situación | Acción requerida | Agente que eleva |
| --- | --- | --- |
| Ruta superior a 1.000 km | Aprobar manualmente la excepción de emergencia. | Agente 5 (vía Agente 4) |
| Cobertura entre 80 % y < 100 % | Aprobar el plan antes de ejecutarlo. | Agente 4 |
| Cobertura < 80 % | Revisar y decidir si procede una excepción extraordinaria. | Agente 4 |
| Cambio importante de una ruta aprobada | Evaluar y aprobar antes de ejecutar. | Agente 5 |
| Excepción a la jerarquía de prioridades | Justificar y aprobar. | Agente 3 |
| Datos contradictorios que cambien una decisión crítica | Revisión humana. | Cualquier agente |
| Comunicación pública extraordinaria | Autorización correspondiente. | Agente 6 |
| Cambio de ponderaciones o reglas operativas | Aprobar antes de aplicar. | Cualquier agente que reciba la solicitud |

### 6.2. Condiciones adicionales de escalamiento

| Condición | Regla | Estado |
| --- | --- | --- |
| Información crítica ausente | Solicitar confirmación cuando el dato sea indispensable para una operación segura (REQ §14.5). | [CONF] |
| Incertidumbre que altera significativamente la prioridad | Revisión humana (REQ §7.3). | [CONF] |
| Contaminación | Para planificación, asumir agua de cisterna limpia y usar duración de cálculo de 2 días. Para operación real, validar fuente/potabilidad antes del despacho. | [CONF como supuesto de planificación; validación real pendiente] |
| Ubicaciones sin validar usadas para rutas | Ruta provisional; revisión si la elección de ubicación cambia la ruta. | [PROP] |
| Empates relevantes o categorías inciertas | Revisión humana. | [PROP] (desempate [PEND]) |
| Recursos insuficientes para la demanda priorizada | Presentar alternativas y necesidades pendientes. | [CONF] (REQ §11) |
| Rutas inviables | Devolver al Agente 4; si no hay alternativa, elevar con el déficit. | [PROP] |
| Conflicto entre recomendaciones de agentes | Ningún agente impone su resultado; se conservan ambos y se eleva. | [PROP] |
| Solicitudes fuera de competencia | Remitir a la persona responsable. | [PROP] |
| Compromisos operativos no autorizados | Prohibido asumirlos; elevar. | [CONF] (REQ §1, §2.6) |
| Plan con cobertura 100 % y ruta ≤ 1.000 km | Requiere aprobación hasta que el equipo defina lo contrario. | [PROP] / [PEND] |

### 6.3. Distinción de fases

| Fase | Quién la produce | Qué significa | Qué NO significa |
| --- | --- | --- | --- |
| 1. **Recomendación** | Agente | Propuesta calculada con datos y reglas registradas. | Que se vaya a ejecutar. |
| 2. **Decisión aprobada** | Supervisor humano | Autorización registrada (quién, qué, cuándo, versión de datos y reglas — REQ §12). | Que se haya ejecutado. |
| 3. **Acción ejecutada** | Responsable operativo (mecanismo **[PEND]**) | La acción ocurrió y quedó registrada por quien la ejecutó. | Que el resultado sea el previsto. |
| 4. **Resultado verificado** | Responsable de verificación **[PEND]** | Se comprobó el efecto (p. ej., volumen entregado). | — |

**Reglas [CONF]:** no existe aprobación automática; los agentes no registran ejecuciones ni verificaciones por inferencia; una entrega no se registra como realizada porque se haya propuesto o calculado su ruta (REQ §13).

---

## 7. Contratos de intercambio de información

### 7.1. Tabla de intercambios [PROP salvo indicación]

| Emisor | Receptor | Información | Activador | Validaciones requeridas | Resultado esperado | Error / información insuficiente |
| --- | --- | --- | --- | --- | --- | --- |
| Agente 1 | Agente 2 | Registro estructurado | Registro transferible | Identificador, tipo o "indeterminado", fuente, descripción original, faltantes | Ubicación normalizada | Registro queda *Pendiente de información* / *Pendiente de revisión* |
| Agente 1 | Agente 6 | Estado del registro | Cambio de estado | Estado válido | Información consultable | Se muestra último estado con fecha |
| Agente 2 | Agente 3 | Zona, instalaciones críticas, certeza | Ubicación con estado | Estado de certeza justificado | Prioridad | Sin datos territoriales: *Pendiente de información* |
| Agente 2 | Agentes 4 y 5 | Ubicación y coordenadas con certeza | Ubicación con estado | No presentar estimación como confirmada | Planificación y ruta | Ruta provisional o no calculada |
| Agente 3 | Agente 4 | Lista priorizada con factores e incertidumbre | Prioridad calculada | Jerarquía aplicada; sin ceros por faltantes; versión de reglas | Demanda y asignación | Revisión humana si la incertidumbre es significativa |
| Agente 4 | Agente 5 | Asignación propuesta | Asignación compatible con inventario | Sin doble asignación; volumen ≤ capacidad; horario | Ruta clasificada | No se solicita ruta; déficit documentado |
| Agente 5 | Agente 4 | Rutas clasificadas y alternativas | Cálculo finalizado | Recorrido completo; distancia total; clasificación | Paquete de plan | Ruta inviable → reformulación |
| Agente 5 | Agente 2 | Coordenadas problemáticas | Incoherencia detectada | — | Revisión de ubicación | Estado "ambigua" y escalamiento |
| Agente 4 | Supervisor | Paquete de plan | Paquete completo | Elementos de REQ §2.7 y §9 | Decisión registrada | Paquete incompleto no se presenta como listo |
| Agente 5 | Supervisor (vía Agente 4) | Solicitud de excepción > 1.000 km | A5-R5 | Seis pasos de REQ §10.3 | Decisión registrada | Sin justificación no se eleva como excepción |
| Agente 4 | Agente 6 | Datos de cobertura parcial | A4-R7 | Unidades coherentes; demanda identificable | Mensaje especial | Sin datos, no se genera mensaje |
| Supervisor | Agente 4 / Agente 6 | Aprobación, rechazo o cambios | Decisión | Identidad, fecha, alcance, versión (REQ §12) | Actualización de estado | Decisión sin registro completo no cambia el estado **[PROP]** |
| Agente 6 | Supervisor | Borrador de comunicación extraordinaria / remisión | A6-R7, A6-R8 | — | Autorización o respuesta | Sin autorización no se difunde |

### 7.2. Estados del flujo

| Estado | Descripción | Estado de la definición |
| --- | --- | --- |
| Recibido | Reporte registrado por el Agente 1. | [PROP] |
| En análisis | Un agente está procesando el registro. | [PROP] |
| Pendiente de información | Falta un dato necesario para continuar. | [PROP] (derivado de REQ §14) |
| Pendiente de revisión | Ambigüedad o contradicción que requiere revisión humana. | [CONF] (REQ §2.1) |
| Validado | Registro o dato con validación suficiente para el siguiente agente. | [CONF] como "estado de validación" (REQ §2.1); valor [PROP] |
| Propuesto | Plan o ruta generado por agentes. | [CONF] (REQ §13: "propuestas generadas automáticamente") |
| Pendiente de aprobación | Propuesta presentada al supervisor. | [CONF] implícito en REQ §9, §12 |
| Aprobado | Decisión registrada del supervisor. | [CONF] (REQ §13) |
| Ejecutado | Acción efectivamente realizada. | [CONF] (REQ §13) |
| Verificado | Resultado comprobado. | [PROP] |
| Pendiente de verificación (ruta) | Autonomía no validable. | [CONF] (REQ §10.4) |
| Rechazado | Decisión negativa del supervisor. | [PROP] |
| Bloqueado | No puede avanzar por una restricción (p. ej., validación sanitaria). | [PROP] |

**Reglas de transición [PROP]:** solo el supervisor puede llevar un elemento a *Aprobado* o *Rechazado*; solo el responsable operativo puede llevarlo a *Ejecutado*; ningún agente salta estados; todo cambio se registra con autor, fecha y motivo.

### 7.3. Campos comunes del mensaje entre agentes — esquema recomendado [PROP]

| Campo | Descripción |
| --- | --- |
| `id_mensaje` | Identificador del intercambio. |
| `id_afectacion` / `id_plan` | Objeto al que se refiere. |
| `agente_emisor` / `destinatario` | Responsables. |
| `fecha_hora_emision` | Momento. |
| `estado` | Según §7.2. |
| `resultado` | Contenido específico del agente. |
| `confianza` | Nivel y justificación. |
| `datos_faltantes` | Lista y efecto. |
| `supuestos` | Documentados y permitidos. |
| `requiere_revision_humana` | Sí/No y motivo. |
| `version_reglas` | Versión de criterios aplicada. |
| `referencias_origen` | Registros de los que deriva. |

---

## 8. Reglas transversales de error e incertidumbre [CONF] (REQ §14)

Cuando un agente no tenga información suficiente para una decisión confiable:

1. Identifica qué dato falta.
2. Determina qué parte del cálculo o de la propuesta queda afectada.
3. Usa supuestos solo si están documentados y permitidos.
4. Muestra la incertidumbre al supervisor.
5. Solicita confirmación si el dato es indispensable para una operación segura.
6. No presenta estimaciones como hechos confirmados.

**La falta de datos no provoca automáticamente que una afectación pierda prioridad** **[CONF]**.

---

## 9. Trazabilidad, seguridad y calidad

### 9.1. Registro mínimo [CONF] (REQ §13)

| Elemento registrado | Agente responsable principal |
| --- | --- |
| Identificador de la afectación | Agente 1 |
| Fuente y fecha de recepción | Agente 1 |
| Archivo de prueba/transcripción de audio o video y referencia al original disponible | Agente 1; conservación de medios originales sujeta a política **[PEND]** |
| Datos originales y normalizados | Agentes 1 y 2 |
| Clasificación y nivel de confianza | Agente 1 |
| Datos faltantes y supuestos | Todos |
| Demanda calculada y fórmula aplicada | Agente 4 |
| Puntuación de prioridad y factores | Agente 3 |
| Inventario y disponibilidad considerados | Agente 4 |
| Planes y rutas propuestos | Agentes 4 y 5 |
| Cobertura y necesidad pendiente | Agente 4 |
| Motivos de rechazo o selección de alternativas | Agentes 4 y 5 |
| Solicitudes de aprobación, respuestas y responsable | Agente que eleva / supervisor |
| Cambios posteriores y motivos | Agente que realiza el cambio |
| Versión de criterios y reglas | Todos |
| Modelo/proveedor y agente que produjo cada resultado, entradas estructuradas, validaciones y errores | Orquestador / agente emisor **[PROP]** |
| Plan confirmado por humano, registro de despacho y volumen entregado confirmado | Supervisor/operador humano; sistema registra el resultado reportado **[CONF]** |

### 9.2. Criterios de calidad

| Criterio | Regla | Estado |
| --- | --- | --- |
| Justificación de decisiones | Cada resultado incluye los factores y reglas que lo produjeron. | [CONF] |
| Identificación de faltantes | Explícita en cada salida. | [CONF] |
| Historial de cambios | Todo cambio de estado conserva el estado anterior, autor, fecha y motivo. | [CONF] (REQ §13) / formato [PROP] |
| Responsable de cada resultado | Cada salida identifica al agente emisor. | [PROP] |
| Aprobaciones humanas | Quién, qué, cuándo y versión de datos y reglas. | [CONF] (REQ §12) |
| Inmutabilidad del original | Los datos originales no se sobrescriben. | [CONF] (REQ §2.1) / mecanismo [PEND] |
| Reproducibilidad | Con los mismos datos y versión de reglas se obtiene el mismo resultado. | [PROP] |

### 9.3. Seguridad y protección de datos

REQ **no documenta** políticas de protección de datos personales, control de acceso, autenticación del supervisor, retención de registros ni herramientas de auditoría. Este documento **no las inventa**. Se establecen solo los siguientes principios mínimos **[PROP]**, sujetos a aprobación:

- El dato personal de contacto previsto para conservar es el número celular **[CONF]**. El prototipo debe minimizar otros datos personales; la política de acceso y retención sigue **[PEND]**.
- El Chat Agent no debe revelar datos personales ni de terceros hasta que existan reglas de acceso.
- Las aprobaciones deben poder atribuirse inequívocamente a una persona autorizada; el mecanismo es **[PEND]**.

---

## 10. Verificación de coherencia del documento

Revisión realizada antes de la entrega:

| Verificación | Resultado |
| --- | --- |
| Número de agentes | Seis. El supervisor es una función de control, no un agente. |
| Solapamiento de roles | Cada resultado tiene un único propietario: clasificación (A1), ubicación (A2), categoría de instalación y prioridad (A3), demanda, flota, cobertura y paquete de plan (A4), rutas (A5), comunicación (A6). Puntos de contacto aclarados: A1 registra la instalación *mencionada*; A2 identifica instalaciones *cercanas*; A3 *determina* la categoría. A4 asigna cisternas; A5 solo calcula rutas para esa asignación. |
| Autonomía vs. REQ §1 | Ningún agente ejecuta decisiones operativas; ningún agente supera el nivel 1. |
| Aprobaciones vs. REQ §12 | Las ocho situaciones obligatorias están asignadas a un agente que eleva (§6.1). |
| Cobertura parcial | Regla de 80 %, aprobación y mensaje especial coherentes entre A4, A6 y §6. |
| Recorrido y límite | Cinco etapas, 1.000 km provisional, excepción con seis pasos y verificación separada de autonomía. |
| Capacidades atribuidas | No se atribuye acceso a mapas, APIs, inventarios en tiempo real ni canales; se marcan como [PEND]. |
| Estados | Diferenciados entre [CONF] y [PROP] (§7.2). |

---

## 11. Estado de decisiones y pendientes

### 11.1. Decisiones consolidadas durante la revisión

| ID | Tema | Decisión registrada | Estado |
| --- | --- | --- | --- |
| DEC-01 | Tiempo sin agua | El tiempo transcurrido afecta solo a la prioridad; no se suma a la demanda ni a los días de planificación. | [CONF] |
| DEC-02 | Factor T | T crece linealmente de 0 a 100 durante los primeros 5 días sin agua y queda limitado a 100 después. Fórmula: `T = min(100, días_sin_agua / 5 × 100)`. | [CONF] para el prototipo; redondeo/fechas inciertas [PEND] |
| DEC-03 | Datos faltantes y empates | No asignar cero a factores faltantes; presentar resultado incompleto y revisar si puede cambiar la prioridad. Desempatar por mayor tiempo sin agua y luego por mayor número estimado de personas afectadas; si persiste, revisión humana. | [CONF] |
| DEC-04 | Excepciones de prioridad | Una emergencia residencial puede proponerse como excepción, pero requiere aprobación del supervisor y justificación registrada. | [CONF] |
| DEC-05 | Duraciones de cálculo y causa principal | Falta de agua = 1 día; tubería rota = 2 días; agua contaminada = 2 días. Si una tubería rota causa falta de agua, se usa la duración de tubería rota. Para contaminación, el modelo asume que el agua entregada por cisternas está limpia y calcula demanda para 2 días; esto es un supuesto de planificación, no una certificación sanitaria. | [CONF] para el modelo de planificación; validación sanitaria real [PEND] |
| DEC-06 | Demanda sanitaria | Hospital 13.208 gal/día, policlínica 4.755 gal/día, centro de salud pequeño 1.320 gal/día. | [CONF] según decisión de la usuaria; validar la fuente en operación real [PEND] |
| DEC-07 | Cobertura | El 80 % se mide sobre el plan de solución de cada incidente. Menos de 80 % requiere decisión extraordinaria del supervisor y registro de la demanda no satisfecha. | [CONF]; criterios operativos específicos <80 % [PEND] |
| DEC-08 | Horarios | Los intervalos son contiguos sin solapamiento. A las 19:00 cambia la disponibilidad, no la demora del intervalo previo. | [CONF]; parámetros horarios siguen [PROV] |
| DEC-09 | Flota y combustible | La disponibilidad para el prototipo se ingresa manualmente. Capacidad de tanque confirmada: Small 400 L, Big 600 L. No se infiere consumo ni autonomía a partir de esos valores. | Disponibilidad manual y capacidades [CONF]; consumo/autonomía [PEND] |
| DEC-10 | Ubicaciones de ruta | La ubicación de la organización se confirmará después; el punto de carga se define para cada ruta. | Organización [PEND]; enfoque por ruta [CONF] |
| DEC-11 | Optimización | Priorizar reglas de prioridad y capacidad, maximizar demanda cubierta y luego minimizar distancia entre planes comparables. | [PROP] aceptada como criterio de diseño; función exacta y datos de tráfico [PEND] |
| DEC-12 | Rutas y seguridad | Cualquier cambio de ruta aprobada requiere revisión del supervisor; superar 1.000 km exige excepción. El supervisor valida seguridad y combustible. | [CONF] |
| DEC-13 | Entrada de reportes | En el prototipo, usar archivos de prueba que simulen WhatsApp y transcripciones de audio/video; preparar instrucciones para transcribirlos. | [CONF para prototipo]; herramienta de transcripción concreta [PEND] |
| DEC-14 | Duplicados y confianza | Vincular reportes similares sin eliminarlos ni fusionarlos automáticamente. | Vinculación [CONF]; umbrales de similitud y escala de confianza [PEND] |
| DEC-15 | Geografía y vulnerabilidad | Preferir OpenStreetMap/cartografía gratuita. Vulnerabilidad considera zonas con instituciones de salud, escuelas, áreas rurales/residenciales, comunidades antiguas y comunidades con población infantil/joven. | Fuente preferida y factores candidatos [CONF]; proveedor, distancia y pesos [PEND] |
| DEC-16 | Personas afectadas | Estimar con promedios de ocupación por tipo de ubicación/unidad. | [CONF]; delimitación de zona afectada [PEND] |
| DEC-17 | Agua contaminada | Para el cálculo de planificación, asumir que el agua enviada en cisternas está limpia y calcular demanda para 2 días. | [CONF] como supuesto del modelo; en operación real la potabilidad y la fuente deben estar verificadas por responsables competentes [PEND] |
| DEC-18 | Aprobación de planes | Todo plan requiere aprobación humana antes de ejecución, incluidos planes al 100 % con rutas ≤1.000 km. | [CONF] |
| DEC-19 | Supervisor y ejecución | En la interfaz frontend, una persona actúa como supervisor; en pruebas, la aprobación puede simularse con Claude. El humano confirma el plan y el sistema registra el resultado comunicado. | [CONF] para flujo de prueba; identidad/autenticación real [PEND] |
| DEC-20 | Comunicación | Objetivo: usuarios por WhatsApp y contacto privado si reportaron por chat o llamada. El prototipo debe dejar un adaptador/interfaz para una integración futura con WhatsApp Business Platform Cloud API; por ahora usa modo simulado y no envía mensajes reales. Comunicaciones extraordinarias requieren aprobación. | Canales objetivo y arquitectura desacoplada [CONF]; credenciales, webhook, permisos, costes y categorías de mensajes [PEND] |
| DEC-21 | Privacidad y auditoría | Guardar solo el número celular como dato personal de contacto previsto. Registrar originales/normalizados, cálculos, versiones de reglas, propuestas, aprobaciones, cambios y resultados confirmados. | Número y trazabilidad [CONF]; retención/acceso y campos técnicos adicionales [PEND]/[PROP] |
| DEC-22 | Autonomía del prototipo | Los agentes analizan, calculan y proponen; no asignan ni despachan cisternas ni envían comunicaciones externas sin aprobación. | [CONF] como decisión de prototipo |
| DEC-23 | Vulnerabilidad y población afectada | V considera la presencia/cercanía de instituciones de salud, escuelas, áreas rurales/residenciales, comunidades antiguas y comunidades con población infantil/joven; orden cualitativo indicado: salud, escuela, rural, residencial. A se estima con promedios de ocupación del documento y no supera el máximo validado para cada lugar. | Criterios cualitativos y método de estimación [CONF]; convertir V/A a puntuaciones numéricas 0–100, definir radios y aportar máximos validados cuando falten [PEND] |
| DEC-24 | Duración para calcular demanda | Duración de cálculo aprobada: falta de agua 1 día, tubería rota 2 días, agua contaminada 2 días; si la tubería rota causa falta de agua, aplicar la duración de tubería rota. | [CONF] para el modelo de planificación |
| DEC-25 | Integración futura con WhatsApp | Crear una interfaz desacoplada para recibir/enviar mensajes, con implementación simulada en esta fase y un adaptador futuro para WhatsApp Business Platform Cloud API. No almacenar tokens en el código ni enviar mensajes reales durante el prototipo. | [CONF] arquitectura prevista; credenciales, endpoint, permisos y costes [PEND] |
| DEC-26 | Aprobación de criterios de prioridad | Se confirma la escala lineal de T hasta 100 a los 5 días y se aprueban los criterios cualitativos de vulnerabilidad V y el uso de promedios/máximos validados para estimar A. La conversión numérica de V/A a 0–100 no queda definida por los valores dados y no debe inventarse. | T y criterios cualitativos V/A [CONF]; conversión numérica V/A [PEND] |
| DEC-27 | Estado de duraciones | Duraciones de cálculo para el prototipo confirmadas: falta de agua 1 día, tubería rota 2 días, agua contaminada 2 días; si la tubería rota causa la falta de agua, aplicar la duración de tubería rota. | [CONF] para el modelo de planificación |

### 11.2. Pendientes que siguen abiertos

| N.º | Pendiente | Agente(s) | Impacto |
| --- | --- | --- | --- |
| 1 | Definir redondeo y tratamiento de horas parciales, fechas/horas ausentes o inciertas para T. La escala lineal está aprobada para el prototipo. | A1, A3 | Medio |
| 2 | Aunque se aprobaron los criterios cualitativos de V y el método de estimación de A, definir su conversión numérica reproducible a 0–100, el radio de cercanía y cómo combinar criterios de vulnerabilidad solapados. No inventar puntuaciones: hasta aprobar la conversión, P queda incompleto cuando dependa de V/A. | A2, A3 | Alto |
| 3 | Definir umbral de cercanía a instalaciones críticas y delimitación de la zona afectada. | A2, A3, A4 | Alto |
| 4 | Definir escala de confianza de clasificación y criterios de vinculación de reportes similares. | A1 | Medio |
| 5 | Validar fuentes de las demandas diarias de instalaciones de salud antes de uso real; las duraciones de cálculo 1/2/2 días ya están aprobadas. | A4, supervisor | Alto |
| 6 | Definir criterios específicos de autorización extraordinaria de cobertura <80 %. | A4, supervisor | Alto |
| 7 | Confirmar parámetros horarios de disponibilidad y demora en operación real, manteniendo intervalos contiguos. | A4 | Alto |
| 8 | Obtener consumo por km/autonomía real de Small y Big; confirmar condiciones operativas de los tanques de 400/600 L. | A5 | Alto |
| 9 | Confirmar ubicación de la organización, puntos concretos de carga por ruta y fuente/actualización de tráfico, vías y elevación. | A2, A5 | Alto |
| 10 | Precisar qué magnitud de variación de recorrido, aparte de superar 1.000 km, cuenta como cambio importante; mientras tanto, cualquier cambio post-aprobación se eleva. | A5, supervisor | Medio |
| 11 | Elegir herramienta/proceso de transcripción de audio/video y definir cómo se conservan o eliminan los archivos originales. | A1 | Medio |
| 12 | Implementar la futura integración de WhatsApp Business Platform Cloud API: cuenta empresarial, número, token seguro, endpoint HTTPS/webhook, permisos, consentimiento, plantillas y revisión de la tarifa vigente por mensaje; evaluar también el coste de alojamiento del backend. En esta fase solo dejar interfaz/adaptador y modo simulado. | A6, supervisor | Alto |
| 13 | Definir reglas finales de comunicación pública extraordinaria y audiencia/permisos por tipo de mensaje. | A6, supervisor | Alto |
| 14 | Definir retención, control de acceso y seguridad de registros y números de contacto. | Todos | Alto |
| 15 | Antes de operar en la realidad, definir cómo se verifica la potabilidad del agua y quién autoriza la fuente de carga. El prototipo asume agua de cisterna limpia solo para el cálculo. | A4, supervisor | Crítico |
| 16 | Confirmar reglas para afectaciones que no encajen en falta de agua, tubería rota o contaminación. | A1 | Medio |
| 17 | Aprobar el formato técnico final de trazabilidad, identificadores de versión, logs de modelo/proveedor y auditoría de acciones. | Todos | Medio |
| 18 | Confirmar la estrategia técnica de coordinación/orquestación y proveedores de modelos para el entorno de prototipo. | Orquestador | Medio |

### 11.3. Reglas de implementación derivadas

- Los elementos **[CONF]** pueden codificarse como reglas, con pruebas unitarias.
- Los elementos **[PROV]** deben configurarse como parámetros modificables y mostrarse como provisionales.
- Los elementos **[PROP]** no deben tratarse como política definitiva sin aprobación explícita; si se usan para experimentar, deben identificarse como supuestos de prototipo.
- Los elementos **[PEND]** no pueden suplirse con valores inventados. Si afectan una decisión crítica, el flujo se detiene o solicita revisión humana.
- La simulación de aprobación por Claude se limita a pruebas; no sustituye una aprobación humana en operación real.

---

## 12. Condición para pasar a implementación

La implementación del prototipo puede comenzar con datos simulados y parámetros marcados **[PROV]**/**[PROP]**. La escala lineal de T, los criterios cualitativos de V, el uso de promedios/máximos validados para A y las duraciones de planificación 1/2/2 días están aprobados para el prototipo. La conversión numérica de V/A a 0–100 sigue pendiente; no se debe inventar, y P debe marcarse incompleto hasta disponer de esa regla. No debe habilitar operaciones reales hasta resolver los pendientes críticos de §11.2, en particular validación sanitaria, seguridad/autonomía de rutas, conversión numérica completa de V/A, aprobación humana y protección de datos.

La implementación deberá incluir pruebas para las reglas de prioridad, los cálculos de demanda, la cobertura parcial, los límites de ruta, la disponibilidad horaria y los mecanismos de aprobación humana. Los criterios de aceptación de la sección 4 (apartado I de cada agente) sirven como base para esas pruebas.

**Este documento define roles, criterios de planificación y control. No sustituye las verificaciones de seguridad, la validación sanitaria ni las autorizaciones operativas correspondientes.**
