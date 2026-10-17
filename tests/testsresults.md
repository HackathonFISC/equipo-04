# Pruebas y resultados

Ejecución: `uv run pytest -q`. No requiere credenciales ni Internet.

## Última ejecución: 2026-10-17

**77 aprobadas, 5 omitidas** (integración sin credenciales), en unos 7 s.

| Archivo | Cubre | Pruebas |
| --- | --- | --- |
| `test_ingesta.py` | Hashtags, voz, causa/consecuencia (A1-R2), combinación indeterminada, `#idaan`, fecha del incidente, datos faltantes, alerta sanitaria, original conservado, duplicados y contradicciones, desacuerdo del modelo de IA (cliente simulado), coherencia de KEYWORDS.md con el código | 14 |
| `test_prioridad.py` | T lineal con tope y redondeo a 0,5; V y A; ejemplo P = 65 del documento; faltante ≠ 0 con rango; jerarquía hospital > residencial; orden de salud y escuela; "clínica" incierta; empates | 9 |
| `test_planificacion.py` | Escuela 2.800 gal; estudiantes no verificados; rurales 2.112; duraciones 1/2/2 más el 50 % de los días sin agua (DEC-C15); sin fecha no hay compensación; valores fijos de salud; demanda sin unidades; umbrales de cobertura; flota de 71; rango de carga por tipo (DEC-C16); los 6 tramos horarios; horarios por archivo; déficit nocturno; sin doble asignación; plan pendiente e incompleto | 25 |
| `test_rutas.py` | 420 km factible con autonomía pendiente; falta el regreso; más de 1.000 km sin y con emergencia; ubicación aproximada; 6.000 gal en una Small; nunca dice "óptima" | 7 |
| `test_flujo_y_aprobacion.py` | Flujo completo con traza de todos los agentes; aprobación simulada registrada y no repetible; paquete incompleto no aprobable en real; justificación obligatoria en extraordinaria; rechazo; originales inmutables; mensaje de cobertura parcial con 5 elementos; mensaje de estado sin promesas; demo con datos simulados; validación de entradas | 10 |
| `test_integraciones.py` | Todo `NOT_CONFIGURED` sin credenciales; IA intercambiable; WhatsApp no envía sin habilitar; firma de webhook; secretos fuera de logs y repr; almacenamiento seguro; Nominatim aproximado, ambiguo y caído; OSRM por tramo; carga de `.env.example` | 12 |
| `integration/test_servicios_reales.py` | IA, Nominatim, OSRM, WhatsApp (solo lectura) y Whisper contra servicios reales | 5 omitidas |

## Evals de entrega

Pendiente: definir 15 casos o más con métrica (por ejemplo, exactitud de la clasificación sobre un conjunto etiquetado y conformidad con las reglas de prioridad y demanda).
