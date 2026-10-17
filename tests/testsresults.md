# Pruebas y resultados

Ejecución: `uv run pytest -q`. No requiere credenciales ni Internet.

## Última ejecución: 2026-10-17

**114 aprobadas, 5 omitidas**, en unos 21 s. Las 2 nuevas cubren `estado --comprobar` con la base de datos (D-016): sin `--comprobar` no se crea el archivo; con `--comprobar` se crea y responde `CONNECTED`; si falla, `ERROR` sin rutas ni detalles. La prueba «todo `NOT_CONFIGURED`» ahora espera `CONNECTED` en la base en memoria.

Ejecución anterior: **112 aprobadas, 5 omitidas** (incluye el proveedor `claude_code` con un subproceso simulado). Además de las 106 anteriores, hay pruebas nuevas del extractor de ubicación, el catálogo de comunidades, `/api/communities`, la `generation` de Langfuse con modelo y tokens, y la máscara.

| Archivo | Cubre | Pruebas |
| --- | --- | --- |
| `test_ingesta.py` | Hashtags, voz, causa/consecuencia (A1-R2), combinación indeterminada, `#idaan`, fecha del incidente, datos faltantes, alerta sanitaria, original conservado, duplicados y contradicciones, desacuerdo del modelo de IA (cliente simulado), coherencia de KEYWORDS.md con el código | 14 |
| `test_prioridad.py` | T lineal con tope y redondeo a 0,5; V y A; ejemplo P = 65 del documento; faltante ≠ 0 con rango; jerarquía hospital > residencial; orden de salud y escuela; "clínica" incierta; empates | 9 |
| `test_planificacion.py` | Escuela 2.800 gal; estudiantes no verificados; rurales 2.112; duraciones 1/2/2 más el 50 % de los días sin agua (DEC-C15); sin fecha no hay compensación; valores fijos de salud; demanda sin unidades; umbrales de cobertura; flota de 71; rango de carga por tipo (DEC-C16); los 6 tramos horarios; horarios por archivo; déficit nocturno; sin doble asignación; plan pendiente e incompleto | 25 |
| `test_rutas.py` | 420 km factible con autonomía pendiente; falta el regreso; más de 1.000 km sin y con emergencia; ubicación aproximada; 6.000 gal en una Small; nunca dice "óptima" | 7 |
| `test_flujo_y_aprobacion.py` | Flujo completo con traza de todos los agentes; aprobación simulada registrada y no repetible; paquete incompleto no aprobable en real; justificación obligatoria en extraordinaria; rechazo; originales inmutables; mensaje de cobertura parcial con 5 elementos; mensaje de estado sin promesas; demo con datos simulados; validación de entradas | 10 |
| `test_integraciones.py` | Todo `NOT_CONFIGURED` sin credenciales (base en memoria `CONNECTED`); comprobación real de la base (crea y conecta; error sin detalles); IA intercambiable; WhatsApp no envía sin habilitar; firma de webhook; secretos fuera de logs y repr; almacenamiento seguro; Nominatim aproximado, ambiguo y caído; OSRM por tramo; carga de `.env.example` | 14 |
| `test_api.py` | Arranque, `/health` (ok y degradado), `/docs`; lecturas vacías y con datos; FAQ; filtros validados (422); registro de reportes (201), entradas inválidas (422), duplicado (409); decisión siempre simulada, no repetible (409), no se puede pedir aprobación real (422), plan inexistente (404), extraordinaria sin motivo (409); BD caída → 503 sin detalles; CORS solo local; respuestas sin secretos ni contactos | 21 |
| `test_observabilidad.py` | Langfuse desactivado por defecto o sin claves; pipeline sin Langfuse; traza con etapas A1–A6 sin texto ni contacto; Langfuse caído no interrumpe; error marcado y propagado; `flush`; SDK real con servidor inaccesible sin secretos en logs | 7 |
| `integration/test_servicios_reales.py` | IA, Nominatim, OSRM, WhatsApp (solo lectura) y Whisper contra servicios reales | 5 omitidas |

## Verificación manual del frontend (2026-10-17, navegador integrado)

Con la API en `127.0.0.1:8000` y el frontend servido en `localhost:5500`, tras cargar datos simulados con `demo --sin-aprobacion`:

- **`admin.html`:**
  - Los KPI muestran 6 reportes y 0 entregas completadas.
  - Las notificaciones muestran 5 mensajes, todos con «Simulado · no enviado» y el estado de su plan.
  - El FAQ muestra 10 preguntas.
  - La tabla de entregas muestra los eventos de los agentes.
- **`gestion.html`:**
  - Las tablas Reportes y Tracking muestran los estados reales y los niveles de la jerarquía.
  - El botón «Aprobar (simulado)» cambió el estado a «Aprobado · simulado» y mostró la notificación.
- **API detenida:** las dos páginas muestran «No se pudo conectar con la API…» en sus espacios vacíos y una notificación de error, sin romperse.
- **Diseño:** en capturas antes y después se mantienen los encabezados, la paleta, las tipografías, la distribución y los componentes. `css/style.css` no se modificó.
- **Sin automatizar:** no hay herramientas de pruebas JavaScript en el repo, así que estos puntos se comprobaron a mano.

## Evaluaciones de comportamiento (2026-10-17): 15 de 15 PASA

Script temporal (fuera del repo) sobre una **copia** de `storage/water.db` con los 42 reportes del CSV, más escenarios en memoria. Sin IA, sin red, mensajería simulada. La base real no se modificó (0 decisiones tras la ejecución).

| # | Evaluación | Resultado obtenido |
| --- | --- | --- |
| 1 | Aprobación simulada de un plan del CSV | `aprobado`, autenticación `simulacion_de_prueba`, huella del plan y 1 evento con estado anterior y nuevo |
| 2 | Rechazo con motivo | `rechazado`; motivo guardado |
| 3 | Solicitud de cambios | `cambios_solicitados` |
| 4 | Decidir dos veces el mismo plan | Bloqueado; sigue `aprobado` |
| 5 | Aprobación real de plan incompleto (sin ruta del Agente 5) | Bloqueada (§3.3) |
| 6 | Aprobar un plan `pendiente_de_informacion` | Bloqueado |
| 7 | Plan inexistente | Error «No existe el plan» |
| 8 | Reingresar `REP-2026-001` con texto alterado | Rechazado; original intacto |
| 9 | Decisión por HTTP intentando `simulada: false` | 422; la decisión del panel queda simulada (200) |
| 10 | `GET /api/incidents` tras decidir | 42 incidentes con los estados nuevos; sin textos originales ni contactos |
| 11 | Hospital frente a 20 casas | Hospital primero (nivel 1) aunque llegó segundo |
| 12 | `#aguacontaminada` en Guadalupe | `agua_contaminada` con alerta sanitaria |
| 13 | 15 edificios (demanda > flota) | 77,06 % → `extraordinaria`; sin justificación bloqueada, con justificación registrada |
| 14 | Misma emergencia a las 10:00 y a las 22:00 | Día: 25 cisternas, 77,06 %. Noche: 10, todas subcontratadas, 30,83 % (DEC-C07) |
| 15 | Consulta irrelevante + reporte de escuela | La consulta queda `indeterminado` sin plan; los mensajes no prometen entrega |

## Evals de entrega

Pendiente: definir 15 casos o más con métrica (por ejemplo, exactitud de la clasificación sobre un conjunto etiquetado y conformidad con las reglas de prioridad y demanda).

## Verificación manual: estadísticas y mapa (2026-10-17)

Con los servidores de la usuaria en `127.0.0.1:8000` y `127.0.0.1:5500`, y los datos cargados con `demo --reiniciar --sin-aprobacion` y Nominatim activo:

- **Estadísticas:** se ven 6 reportes; el período 2026-10-17; la dona con 5 pendientes de aprobación y 1 pendiente de información; los distritos (La Chorrera 2, Arraiján 2, Capira 1, Sin distrito 1) y la tendencia de un solo día.
- **Mapa:** carga las teselas de OSM con su atribución y marca las afectaciones que tienen coordenadas estimadas. Las que no tienen coordenadas no se dibujan.

## Verificación manual: comunidades y mapa (2026-10-17)

- **Pestaña Comunidades:** muestra 16 comunidades. Barrio Colón aparece con 1 incidente, 700 personas estimadas y estado «Pendiente de aprobación»; las demás, «Sin reportes». El KPI de comunidades afectadas es 2.
- **Mapa:** muestra 4 marcadores con coordenadas reales de Nominatim.
- **Error detectado y corregido:** un `ReferenceError` (`comunidadesMensaje` usada antes de declararse) detenía el script de `gestion.html`.
