# Instrucciones para Claude Code

Proyecto: Centro de coordinación agéntico para la crisis del agua en Panamá Oeste (Hackathon FISC, equipo 04, Reto 1).

## Rol

Desarrollador principal y responsable del mantenimiento del repositorio: construir, mantener, documentar y probar siguiendo las instrucciones que el equipo apruebe progresivamente.

## Fase actual: construcción (etapa 1 completada el 2026-10-17)

**Fuente de verdad funcional:** `docs/AGENT_CRITERIA_AND_DECISION_RULES.md` (rev.4). Respetar sus etiquetas: `[CONF]` se codifica; `[PROV]` es un parámetro configurable; `[PROP]` es un supuesto de prototipo marcado; `[PEND]` nunca se inventa. Las decisiones posteriores de la usuaria están en `docs/DECISIONS.md` (DEC-C*). Los conflictos abiertos (C-*) no se resuelven sin preguntar.

Aprobado: AutoGen (`autogen-core`), SQLite/SQLAlchemy, Leaflet/OSM, Nominatim, OSRM, IA configurable, WhatsApp Cloud API (adaptador y simulación), Whisper local (faster-whisper), Google STT opcional, **FastAPI + Uvicorn** (API local del panel del supervisor) y **Langfuse** (observabilidad, desactivada por defecto).

## Límites obligatorios

- No conectar servicios reales con credenciales ni enviar mensajes externos sin aprobación explícita (`WHATSAPP_SEND_ENABLED=false`).
- No activar servicios de pago ni generar gastos automáticamente.
- No decidir frameworks no aprobados (Streamlit, OR-Tools…); solo registrarlos como candidatos.
- La API no tiene autenticación: las decisiones del supervisor por HTTP se registran siempre como simuladas. No exponerla fuera de `127.0.0.1`.
- La IA solo interpreta texto; prioridad, demanda, cobertura y rutas son funciones deterministas.
- Los agentes no escriben en la base de datos ni modifican la salida de otro agente: el orquestador persiste y traza.
- **Frontend (`frontend/`, del equipo):** es el panel del supervisor. Conservar su diseño (paleta, tipografías, distribución, imágenes); solo conectar datos y estados mínimos. Sin formularios de reporte ciudadano ni autenticación inventada.
- No inventar requisitos ni convertir propuestas en decisiones aprobadas.
- No usar datos reales de ciudadanos ni información personal.
- Sin despliegues, envíos, pagos ni cambios remotos en GitHub.
- No crear commits ni hacer push sin autorización explícita.
- No instalar paquetes globalmente ni modificar configuración global de Windows.
- No crear código solo para rellenar carpetas.
- **No editar `README.md`**: lo mantiene el equipo manualmente.

## Convenciones

- Python con estructura `src/` y paquete `water_coordinator`. Entorno y dependencias con `uv` (`system-certs = true` por la intercepción TLS).
- Pruebas: `uv run pytest -q` (sin red). Demo: `uv run water-coordinator demo`. Integraciones: `uv run water-coordinator estado`.
- API: `uv run uvicorn water_coordinator.api.app:app --reload --host 127.0.0.1 --port 8000` (`/docs`). Frontend: `uv run python -m http.server 5500 --bind 127.0.0.1 -d frontend`.
- Palabras clave: el código (`services/clasificacion.py`) y `docs/KEYWORDS.md` deben coincidir (hay una prueba que lo verifica).
- Tras cambiar código, regenerar el grafo con `/graphify src/water_coordinator --update`.
- Ejecutar siempre con `uv run ...` (en esta máquina `python` no está en PATH y `py` apunta a 3.4).
- Configuración solo vía variables de entorno en `config.py`; plantilla en `.env.example`, sin secretos.
- Documentación en español, en `docs/`.

## Trazabilidad (actualizar en cada cambio)

- `docs/PROJECT_STATUS.md`: fase, trabajo hecho, decisiones, dependencias instaladas, comprobaciones y resultados, bloqueos, próximos pasos.
- `docs/DECISIONS.md`: separar Aprobadas / Propuestas / Pendientes.
- `docs/TOOLING.md`: herramientas aprobadas y candidatas.
- `docs/INTEGRATIONS.md` y `docs/API_SETUP.md`: estado y conexión de cada proveedor.
- `tests/testsresults.md`: resultados de pruebas y evals.

No declarar verificaciones que no se hayan ejecutado. Al terminar una tarea, detenerse y esperar instrucciones.
