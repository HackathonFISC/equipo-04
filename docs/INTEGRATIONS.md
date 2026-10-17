# Estado de las integraciones

El estado se calcula en vivo con:

```bash
uv run water-coordinator estado
```

Con `--comprobar` hace una llamada real a cada servicio configurado. Es la única forma de obtener `CONNECTED`.

| Estado | Significado |
| --- | --- |
| `NOT_CONFIGURED` | Faltan variables o el extra opcional. El sistema funciona sin ese servicio y no inventa sus resultados. |
| `CONFIGURED` | Las variables están presentes, pero la conexión no se ha comprobado. |
| `CONNECTED` | Una comprobación real (`--comprobar`) tuvo éxito. |
| `ERROR` | La comprobación falló. Se informa el tipo de error, nunca las credenciales. |
| `DISABLED` | El servicio está configurado pero desactivado a propósito (p. ej. envío de WhatsApp sin aprobación). |

## Estado registrado (2026-10-17, `estado --comprobar`, sin archivo `.env`)

| Integración | Proveedor | Estado | Qué falta |
| --- | --- | --- | --- |
| Modelo de IA | AutoGen: OpenAI / compatible con OpenAI (Ollama) / Anthropic | `NOT_CONFIGURED` | `MODEL_PROVIDER`, `MODEL_NAME` y, según el proveedor, `MODEL_API_KEY` o `MODEL_BASE_URL`. Sin modelo se clasifica con reglas. |
| Geocodificación | Nominatim (OSM) | `NOT_CONFIGURED` | `GEOCODER_PROVIDER=nominatim` y `NOMINATIM_USER_AGENT` con un contacto. Sin geocodificador: certeza "aproximada" por distrito o "no verificada", sin coordenadas. |
| Rutas | OSRM | `NOT_CONFIGURED` | `OSRM_BASE_URL` y la ubicación de la organización (`ORGANIZACION_LAT/LON`, [PEND]). El Agente 5 no forma parte de la etapa 1. |
| Mapas | Leaflet + teselas OSM | `NOT_CONFIGURED` | `MAP_TILE_URL` y la integración de Leaflet en `frontend/` (fuera del alcance de la tarea de API; el mapa sigue como placeholder). |
| Mensajería | Simulada (`mock`) | `CONFIGURED` | Funciona sin red. WhatsApp Cloud API: `NOT_CONFIGURED` (token, phone number id, app secret, verify token). Con credenciales queda `DISABLED` hasta poner `WHATSAPP_SEND_ENABLED=true`. |
| Transcripción | Whisper local (faster-whisper) / Google STT | `NOT_CONFIGURED` | Whisper: `uv sync --extra transcripcion-local` y `TRANSCRIPTION_PROVIDER=whisper_local`. Google: el extra, credenciales y facturación. |
| Base de datos | SQLite (SQLAlchemy) | `CONFIGURED` | Nada. Para PostgreSQL basta cambiar `DATABASE_URL` e instalar el driver. |
| Archivos | Almacenamiento local | `CONFIGURED` | La política de retención está [PEND]: no se borra nada automáticamente. |
| Observabilidad | Langfuse (SDK 5.0.2) | `DISABLED` | `LANGFUSE_TRACING_ENABLED=true` y las tres variables `LANGFUSE_*`. Implementada y probada en local con un cliente simulado y con el SDK real contra un puerto cerrado; **ninguna traza verificada aún en un proyecto real de Langfuse**. |
| API HTTP | FastAPI + Uvicorn (local) | Implementada | Solo `127.0.0.1`; CORS solo para `CORS_ORIGINS`. Sin autenticación: las decisiones por HTTP son simuladas. |
| Monitoreo externo | Sentry (opcional) | `DISABLED` | No implementado; los logs JSON locales con redacción de secretos están siempre activos. |

**Probado con servicios reales:** ninguno. No hay credenciales y no se activaron servicios externos.
**Probado sin red:** todos los adaptadores, con transportes HTTP simulados (`tests/test_integraciones.py`).

## Pruebas de integración

Están en `tests/integration/test_servicios_reales.py` y se activan una a una. Cada una requiere su variable `RUN_INTEGRATION_*` y la configuración del servicio en `.env`.

| Variable | Qué prueba | ¿Coste? |
| --- | --- | --- |
| `RUN_INTEGRATION_LLM=1` | Una petición mínima al modelo. | Sí, unos pocos tokens (excepto con Ollama local). |
| `RUN_INTEGRATION_NOMINATIM=1` | Una búsqueda ("La Chorrera, Panamá Oeste"). | No. |
| `RUN_INTEGRATION_OSRM=1` | Un tramo de prueba. | No (si el servidor está disponible). |
| `RUN_INTEGRATION_WHATSAPP=1` | **Solo lectura** del número; no envía mensajes. | No. |
| `RUN_INTEGRATION_WHISPER=1` y `WHISPER_AUDIO_PRUEBA=ruta` | Transcribe un audio de prueba sin datos personales. | No (local). |

Ejemplo:

```bash
RUN_INTEGRATION_NOMINATIM=1 uv run pytest tests/integration -q
```
