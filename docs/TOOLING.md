# Herramientas

## Entorno local

| Herramienta | Versión | Uso |
| --- | --- | --- |
| Git | 2.55.0.windows.5 | Control de versiones |
| uv | 0.12.23 | Entorno y dependencias (`system-certs = true` en el proyecto) |
| CPython (gestionado por uv) | 3.14.8 | Intérprete del proyecto |
| Node | 24.21.0 | Disponible para el frontend (no usado por el backend) |
| graphify (`graphifyy`) | 0.9.82 | Grafo del código; instalado con `uv tool`, fuera del proyecto |

Nota: `python` no está en el PATH (es un alias de Microsoft Store) y `py` usa Python 3.4.3. Usa siempre `uv run`.

## Aprobadas e integradas

| Herramienta | Categoría | Estado |
| --- | --- | --- |
| AutoGen (`autogen-core`, `autogen-ext`) 0.7.5 | Orquestación multiagente | En uso. Riesgo: AutoGen está en modo mantenimiento (Microsoft lo sustituye por Agent Framework). |
| pydantic / pydantic-settings | Contratos y configuración | En uso |
| SQLAlchemy 2.1 + SQLite | Persistencia (migrable a PostgreSQL) | En uso |
| httpx | Cliente HTTP de los adaptadores | En uso |
| pytest + pytest-asyncio | Pruebas | En uso |
| Leaflet + teselas OSM | Mapas en el frontend | Preparado (variables); frontend congelado |
| Nominatim | Geocodificación | Adaptador listo; `NOT_CONFIGURED` |
| OSRM | Rutas | Adaptador listo; `NOT_CONFIGURED` |
| OpenAI / compatible (Ollama) / Anthropic | Modelo de IA | Cliente intercambiable; `NOT_CONFIGURED` |
| WhatsApp Business Cloud API | Mensajería | Adaptador listo con envío bloqueado; se usa la simulación |
| faster-whisper | Transcripción local | Extra opcional, no instalado |
| Google Cloud Speech-to-Text | Transcripción remota | Extra opcional, no instalado |

## Candidatas (sin aprobar)

| Herramienta | Categoría | Nota |
| --- | --- | --- |
| FastAPI u otro | API / webhook de WhatsApp | Necesario para el webhook y la interfaz del supervisor |
| Streamlit u otro | Interfaz | Alternativa si no se usa el frontend actual |
| OR-Tools | Optimización de rutas | Útil en la etapa 2 (Agente 5) |
| Ruff | Lint y formato | Por evaluar |
| Sentry | Monitoreo externo | Opcional; `SENTRY_DSN` reservado |
| psycopg | Driver de PostgreSQL | Instalar solo si se migra |
