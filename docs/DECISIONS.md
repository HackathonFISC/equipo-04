# Registro de decisiones

Cada decisión avanza así: **Pendiente → Propuesta → Aprobada** (o Descartada). Solo el equipo puede aprobar.

**Fuente de verdad funcional:** [AGENT_CRITERIA_AND_DECISION_RULES.md](AGENT_CRITERIA_AND_DECISION_RULES.md), versión 1.0-rev.4, copiada sin cambios. Sus etiquetas `[CONF]`, `[PROV]`, `[PEND]` y `[PROP]` se respetan. Las decisiones de abajo con prefijo **DEC-C** las tomó la usuaria el 2026-10-17 y **todavía no están incorporadas al documento de criterios**.

## Aprobadas

| ID | Decisión | Fecha | Fuente |
| --- | --- | --- | --- |
| D-001 | Python con estructura `src/` y paquete `water_coordinator`. | 2026-10-16 | Guía del repositorio |
| D-002 | `uv` para el entorno y las dependencias. | 2026-10-16 | Guía del repositorio |
| D-003 | `README.md` lo mantiene el equipo a mano. | 2026-10-16 | Instrucciones del equipo |
| D-004 | Sin datos personales reales ni credenciales en el repositorio. | 2026-10-16 | Instrucciones del equipo |
| D-005 | Fase de **construcción**. Primera etapa: reporte → A1 → A2 → A3 → A4 → plan → aprobación simulada → traza. | 2026-10-17 | Usuaria |
| D-006 | **AutoGen** (`autogen-core` 0.7.5) para coordinar a los agentes. | 2026-10-17 | Usuaria |
| D-007 | Integraciones preparadas sin credenciales: Leaflet, OSM, Nominatim, OSRM, modelo de IA configurable, WhatsApp Cloud API (adaptador + simulación), Whisper local, Google STT opcional, SQLite→PostgreSQL, almacenamiento local y logs estructurados. | 2026-10-17 | Usuaria |
| D-008 | El documento de criterios rev.4 queda en `docs/` como fuente de verdad. | 2026-10-17 | Usuaria |
| D-009 | ~~No se modifica la carpeta `frontend/`~~. **Obsoleta (2026-10-17):** el frontend ya se subió (PR #1) y se conectó a la API conservando su diseño (D-010). | 2026-10-17 | Usuaria |
| DEC-C01 | Redondeo **al 0,5 más cercano** (mitades hacia arriba) para T, V y A. | 2026-10-17 | Usuaria |
| DEC-C02 | El Agente 1 identifica la fecha del incidente en el texto al filtrar ("hace 2 días", "desde ayer", "desde el lunes", "15/10"…). Si no la encuentra, queda nula: nunca se usa la fecha de recepción. | 2026-10-17 | Usuaria |
| DEC-C03 | Escala de confianza de la clasificación: `alta` / `media` / `baja` / `ninguna` (criterios en [KEYWORDS.md](KEYWORDS.md)). Definida por Claude a discreción, con autorización de la usuaria. | 2026-10-17 | Usuaria → Claude |
| DEC-C04 | **Conversión de V a 0–100**, a discreción de Claude con autorización de la usuaria. Base = el criterio presente de mayor valor: salud cercana 100, escuela 80, área rural 60, área residencial 40. Se suman +10 por comunidad antigua y +10 por población infantil/juvenil, con tope de 100. Si no hay evidencia de ningún criterio base, V queda **faltante** (nunca 0). | 2026-10-17 | Usuaria → Claude |
| DEC-C05 | **Conversión de A a 0–100**, a discreción de Claude: `A = min(100, personas_estimadas / 1000 × 100)`. Las personas se estiman con promedios de ocupación por unidad. El número de personas reportado (no verificado) solo se usa si no hay unidades. La referencia 1000 es configurable (`A_PERSONAS_REFERENCIA`). Los máximos validados por lugar siguen [PEND]. | 2026-10-17 | Usuaria → Claude |
| DEC-C06 | Flota de 71 cisternas. Organización: 10 Small y 5 Big. Subcontratadas: 40 Small y 16 Big. | 2026-10-17 | Usuaria |
| DEC-C07 | **Horarios configurables**, aplicados en todo flujo mientras no se ordene un cambio. 06:00–19:00: al menos 25 disponibles (5 de la organización y 20 subcontratadas). 19:00–06:00: solo 10, todas subcontratadas. Pedir más: 40 min de demora entre 08:00 y 16:00; 1,5 h entre 06:00–08:00 y entre 16:00–20:00. | 2026-10-17 | Usuaria |
| DEC-C08 | 400 L (Small) y 600 L (Big) **son capacidades del tanque de combustible**. 1.000 km es el límite provisional. En una emergencia, aprobada manualmente, la ruta puede extenderse al máximo siempre que el camión pueda regresar a la organización. Orden de la ruta: salida → recoger el agua → afectaciones → regreso a la organización. | 2026-10-17 | Usuaria |
| DEC-C09 | Los valores de ocupación son **promedios por edificio o vivienda**, no la población de una comunidad. Una escuela tiene en promedio 700 estudiantes. | 2026-10-17 | Usuaria |
| DEC-C10 | Prioridad en salud: hospitales → policlínicas → centros de salud. | 2026-10-17 | Usuaria |
| DEC-C11 | El planificador propone planes aunque no cubran toda la necesidad, si cubren al menos el 80 %. El supervisor debe aprobarlos y el Agente 6 genera un mensaje especial para esa afectación. | 2026-10-17 | Usuaria |
| DEC-C12 | Los galones son por día. Duración de restauración: falta de agua 1 día, tubería rota 2 días, agua contaminada 2 días. | 2026-10-17 | Usuaria |
| DEC-C13 | Palabras clave `#idaan #sinagua #faltadeagua #tuberiarota`, con sus equivalentes en voz y las ampliaciones recomendadas ([KEYWORDS.md](KEYWORDS.md)). | 2026-10-17 | Usuaria |
| DEC-C14 | Whisper local mediante **faster-whisper**, como extra opcional (`transcripcion-local`). | 2026-10-17 | Usuaria |
| DEC-C15 | **Compensación temporal en la demanda** (resuelve C-01; **reemplaza a DEC-01 del documento en lo que respecta a la demanda**). `días_planificación = duración(tipo) + 0,5 × días_sin_agua`. Los días sin agua se cuentan desde el incidente hasta la recepción del reporte, no hasta la hora de planificación. El tiempo sin agua sigue subiendo la prioridad (T). Si no hay fecha del incidente, no se compensa y se avisa que la demanda puede estar subestimada. | 2026-10-17 | Usuaria |
| D-010 | **FastAPI + Uvicorn** como API HTTP local del panel del supervisor (`api/`). El frontend (panel del supervisor, no ciudadano) consume la API sin cambiar su diseño. No hay formularios de reporte ni autenticación inventada. | 2026-10-17 | Usuaria |
| D-011 | Las decisiones del supervisor por HTTP (`POST /api/plans/{id}/decision`) se registran **siempre como simuladas**. Las reales solo por CLI hasta que exista autenticación. | 2026-10-17 | Usuaria |
| D-012 | `POST /api/incidents` registra y procesa reportes con el pipeline existente (sin formulario en el frontend). | 2026-10-17 | Usuaria |
| D-013 | Los filtros y etiquetas del frontend usan los estados reales del backend (`Estado`); las reglas de negocio no cambian. | 2026-10-17 | Usuaria |
| D-014 | FAQ del panel en `admin.html`, debajo de «Notificaciones recientes», con las clases existentes. | 2026-10-17 | Usuaria |
| D-015 | **Langfuse** (SDK oficial 5.x) para observar las ejecuciones del pipeline: desactivado por defecto, una traza por ejecución y una observación por agente, sin datos sensibles. | 2026-10-17 | Usuaria |
| DEC-C16 | **Capacidad por tipo** (resuelve C-03). Todas las Small cargan entre 3.000 y 5.500 gal; todas las Big, entre 9.000 y 13.000 gal. El máximo es la capacidad que se usa para la cobertura y el mínimo es la carga mínima. Cuando el tipo no se conoce (la disponibilidad por horario no lo indica), se usa el menor máximo, 5.500 gal, para no sobrestimar. | 2026-10-17 | Usuaria |
| D-016 | `estado --comprobar` comprueba la base de datos de verdad: abre la conexión, ejecuta `SELECT 1` y responde `CONNECTED` o `ERROR`. En SQLite crea el archivo y las tablas si no existen. | 2026-10-17 | Usuaria |

## Conflictos que necesitan confirmación

| ID | Conflicto | Qué se implementó |
| --- | --- | --- |
| C-01 | Compensación temporal en la demanda. | **Resuelto (2026-10-17) → DEC-C15.** |
| C-02 | Entre 19:00 y 20:00 la disponibilidad es de 10 subcontratadas, pero la ventana de pedir más con 1,5 h llega hasta las 20:00. | La usuaria reiteró los mismos horarios el 2026-10-17. Se mantienen ambas reglas: entre 19:00 y 20:00 hay 10 disponibles y se pueden pedir más con 1,5 h; de 20:00 a 06:00 no se puede pedir más. Si se quiere otra lectura, hay que indicarlo. |
| C-03 | Capacidad concreta de las cisternas. | **Resuelto (2026-10-17) → DEC-C16.** |

## Propuestas (implementadas como supuestos de prototipo, no aprobadas)

| ID | Propuesta | Motivo |
| --- | --- | --- |
| P-001 | `requires-python >= 3.12`; el entorno usa CPython 3.14.8. | Versión mínima por confirmar. |
| P-002 | Backend de build `uv_build`. | Necesario para la estructura `src/`. |
| P-003 | La disponibilidad por horario no indica el tipo de cada unidad. Esas unidades se tratan como "desconocido" con 5.500 gal (el menor máximo, DEC-C16). | No sobrestimar el volumen entregable. |
| P-004 | Si P está incompleto, el orden usa el **punto medio** de su rango. | Ni premia ni penaliza la falta de datos (REQ §7.3). |
| P-005 | Un viaje por cisterna en cada planificación. | Las vueltas múltiples no están documentadas. |
| P-006 | Mientras falte la ruta, el paquete de plan queda **incompleto**: solo admite aprobación **simulada** de prueba (§3.3, DEC-19). | Un paquete incompleto no puede presentarse como listo. |
| P-007 | Los estudiantes reportados y no verificados no reemplazan el promedio de 700; se registran como dato alternativo. | DOC §4.4.C. |
| P-008 | "Clínica" se clasifica como categoría **incierta** y va a revisión humana. | A3-R3. |
| P-009 | Referencia territorial: los 5 distritos de Panamá Oeste (Arraiján, Capira, Chame, La Chorrera, San Carlos). Coincidir con un distrito da certeza "aproximada". | Fuente territorial [PEND]. |
| P-010 | La aprobación extraordinaria (<80 %) exige una justificación escrita. | DEC-07. |
| P-011 | Los reportes `indeterminado` no pasan del Agente 1; el Agente 6 les pide más información. | §3.3. |
| P-013 | Urgencia en el Tracking = nivel de la jerarquía del Agente 3 (1–5). El KPI «Urgencia crítica» queda sin calcular ("-") porque no hay definición aprobada. | Evita inventar una regla de urgencia. |
| P-014 | El panel registra las decisiones con el supervisor `panel-web (sin autenticación)`. | No hay identidad verificada (DEC-19). |
| P-015 | Estadísticas calculadas en el navegador a partir de `/api/incidents`. Los KPI sin definición aprobada (incidencias confirmadas, comunidades afectadas, tiempo promedio de atención) quedan en «-». «Analizados por IA» solo cuenta las clasificaciones contrastadas con el modelo. | No inventar indicadores. |
| P-016 | TLS verificado con el almacén de certificados de Windows (`truststore`), porque un antivirus o proxy intercepta TLS y `certifi` rechaza su certificado. | Sin esto fallaban Nominatim, Claude y Langfuse. |
| P-017 | `demo --reiniciar` vacía la base SQLite de desarrollo (no funciona con PostgreSQL). | Permite repetir el demo con IDs fijos. |
| P-018 | Catálogo de comunidades (`services/territorio.py`) con corregimientos de La Chorrera (9) y Arraiján (7). Se excluyen los corregimientos cabecera homónimos del distrito. **Pendiente de validación por el equipo.** Si la comunidad y el distrito del texto no coinciden, la ubicación es «ambigua». | Petición de la usuaria (≥3 comunidades por distrito). |
| P-019 | Instrumentación según la skill oficial de Langfuse: nombres verbo-objeto (`procesar-reportes`, `clasificar-reportes`…); la llamada a Claude se registra como `generation` con modelo y tokens reales; sin `session_id` (no hay continuidad entre ejecuciones; `id_ejecucion` va en metadata); etiquetas `prototipo` y origen (`cli-demo`/`api`); máscara de contactos y teléfonos. El texto del reporte no se envía. | https://langfuse.com/docs/observability/best-practices |
| P-020 | Proveedor `claude_code` (`tools/claude_code.py`): Claude se usa a través del `claude.exe` de la app de escritorio, con la sesión de la usuaria y sin API key ni créditos (decisión de la usuaria, 2026-10-17). Una llamada por subproceso, sin herramientas y con el prompt de sistema propio. | La API de Anthropic exige créditos y la usuaria no los usará. Solo para desarrollo local. |
| P-012 | El modelo de IA solo contrasta la clasificación. Si discrepa, la confianza baja a `baja` y el registro va a revisión; nunca sobrescribe. | Separar la IA de las reglas. |

## Pendientes

- Tipo (Small o Big) de las unidades disponibles en cada horario.
- Consumo y autonomía reales de Small y Big. Sin estos datos, toda ruta queda "pendiente de verificación" y no puede calcularse el máximo de una extensión de emergencia.
- Ubicación de la organización y puntos de carga por ruta (necesarios para el Agente 5).
- Umbral de cercanía a instalaciones críticas y fuente de datos de esas instalaciones.
- Máximos validados de personas por lugar (tope de A).
- Proveedor y modelo de IA concretos (hoy `none`).
- Criterios de autorización extraordinaria <80 %.
- Autenticación del supervisor, retención de datos y control de acceso.
- Integración del frontend (Leaflet) cuando se suba la carpeta `frontend/`.
- Fuente y potabilidad del agua antes de cualquier operación real (crítico).

## Hallazgos abiertos (2026-10-17, tarea de API)

- ~~Claude no funciona con la versión instalada~~. **Resuelto en el código:** se fijó `anthropic>=0.48,<1` (0.125.0). Con esa versión la petición llega a Anthropic, pero la API exige la cabecera `anthropic-workspace-id`, porque la clave no está asociada a un workspace. **Superado:** con un workspace correcto la API responde «credit balance is too low». La usuaria decidió no usar créditos y Claude se usa por Claude Code (P-020). Antes, el `MODEL_WORKSPACE_ID` devolvía 404 («Workspace … not found»). Hay que usar el ID de un workspace de la misma organización que la clave, o una clave asociada a un workspace. Mientras tanto, el Agente 1 clasifica con reglas y la `generation` de Claude en Langfuse sigue sin verificar.
- ~~Ubicación reportada con una palabra de más~~. **Corregido:** un punto termina la ubicación. Con Nominatim, ahora 4 de las 5 ubicaciones del demo tienen coordenadas (antes 2).
- **Planificación entre lotes:** cada `POST /api/incidents` se planifica en su propio lote, así que el Agente 4 no conoce las cisternas asignadas en lotes anteriores. Puede haber doble asignación entre lotes. Está documentado y no está resuelto.
