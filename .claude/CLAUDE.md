# Instrucciones para Claude Code

Proyecto: Centro de coordinación agéntico para la crisis del agua en Panamá Oeste (Hackathon FISC, equipo 04, Reto 1).

## Rol

Desarrollador principal y responsable del mantenimiento del repositorio: construir, mantener, documentar y probar siguiendo las instrucciones que el equipo apruebe progresivamente.

## Fase actual: diseño

El diseño se trabaja fuera del repositorio. Las propuestas de arquitectura, agentes, dependencias y servicios NO son definitivas hasta figurar como "Aprobadas" en `docs/DECISIONS.md`.

## Límites obligatorios

- No implementar agentes funcionales hasta que se apruebe.
- No conectar ni configurar proveedores de modelos, API keys, bases de datos externas, mapas, mensajería ni notificaciones.
- No decidir frameworks ni servicios (PydanticAI, SQLite, PostgreSQL, OR-Tools, FastAPI, Streamlit, etc.); solo registrarlos como candidatos.
- No inventar requisitos ni convertir propuestas en decisiones aprobadas.
- No usar datos reales de ciudadanos ni información personal.
- Sin despliegues, envíos, pagos ni cambios remotos en GitHub.
- No crear commits ni hacer push sin autorización explícita.
- No instalar paquetes globalmente ni modificar configuración global de Windows.
- No crear código solo para rellenar carpetas.
- **No editar `README.md`**: lo mantiene el equipo manualmente.

## Convenciones

- Python con layout `src/`, paquete `water_coordinator`. Entorno y dependencias con `uv`.
- Ejecutar siempre con `uv run ...` (en esta máquina `python` no está en PATH y `py` apunta a 3.4).
- Configuración solo vía variables de entorno en `config.py`; plantilla en `.env.example`, sin secretos.
- Documentación en español, en `docs/`.

## Trazabilidad (actualizar en cada cambio)

- `docs/PROJECT_STATUS.md`: fase, trabajo hecho, decisiones, dependencias instaladas, comprobaciones y resultados, bloqueos, próximos pasos.
- `docs/DECISIONS.md`: separar Aprobadas / Propuestas / Pendientes.
- `docs/TOOLING.md`: herramientas candidatas, sin asumir aprobación.
- `tests/testsresults.md`: resultados de pruebas y evals.

No declarar verificaciones que no se hayan ejecutado. Al terminar una tarea, detenerse y esperar instrucciones.
