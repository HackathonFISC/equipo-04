# Pruebas y resultados

Ejecución: `uv run pytest -q`. No requiere credenciales ni Internet.

## Última ejecución: 2026-10-17

**105 aprobadas, 5 omitidas** (integración sin credenciales), en unos 16 s. Antes eran 77; las 28 nuevas son de la API y de Langfuse.

| Archivo | Cubre | Pruebas |
| --- | --- | --- |
| `test_ingesta.py` | Hashtags, voz, causa/consecuencia (A1-R2), combinación indeterminada, `#idaan`, fecha del incidente, datos faltantes, alerta sanitaria, original conservado, duplicados y contradicciones, desacuerdo del modelo de IA (cliente simulado), coherencia de KEYWORDS.md con el código | 14 |
| `test_prioridad.py` | T lineal con tope y redondeo a 0,5; V y A; ejemplo P = 65 del documento; faltante ≠ 0 con rango; jerarquía hospital > residencial; orden de salud y escuela; "clínica" incierta; empates | 9 |
| `test_planificacion.py` | Escuela 2.800 gal; estudiantes no verificados; rurales 2.112; duraciones 1/2/2 más el 50 % de los días sin agua (DEC-C15); sin fecha no hay compensación; valores fijos de salud; demanda sin unidades; umbrales de cobertura; flota de 71; rango de carga por tipo (DEC-C16); los 6 tramos horarios; horarios por archivo; déficit nocturno; sin doble asignación; plan pendiente e incompleto | 25 |
| `test_rutas.py` | 420 km factible con autonomía pendiente; falta el regreso; más de 1.000 km sin y con emergencia; ubicación aproximada; 6.000 gal en una Small; nunca dice "óptima" | 7 |
| `test_flujo_y_aprobacion.py` | Flujo completo con traza de todos los agentes; aprobación simulada registrada y no repetible; paquete incompleto no aprobable en real; justificación obligatoria en extraordinaria; rechazo; originales inmutables; mensaje de cobertura parcial con 5 elementos; mensaje de estado sin promesas; demo con datos simulados; validación de entradas | 10 |
| `test_integraciones.py` | Todo `NOT_CONFIGURED` sin credenciales; IA intercambiable; WhatsApp no envía sin habilitar; firma de webhook; secretos fuera de logs y repr; almacenamiento seguro; Nominatim aproximado, ambiguo y caído; OSRM por tramo; carga de `.env.example` | 12 |
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

## Evals de entrega

Pendiente: definir 15 casos o más con métrica (por ejemplo, exactitud de la clasificación sobre un conjunto etiquetado y conformidad con las reglas de prioridad y demanda).
