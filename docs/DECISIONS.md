# Registro de decisiones

Cada decisión pasa por: **Pendiente → Propuesta → Aprobada** (o Descartada). Solo el equipo aprueba.

## Aprobadas

| ID | Decisión | Fecha | Fuente |
|----|----------|-------|--------|
| D-001 | Lenguaje Python con layout `src/` y paquete `water_coordinator` | 2026-10-16 | Guía del repositorio del equipo |
| D-002 | `uv` como gestor de entorno y dependencias (`pyproject.toml`, `uv.lock`) | 2026-10-16 | Guía del repositorio del equipo |
| D-003 | `README.md` se mantiene manualmente; no lo edita el asistente | 2026-10-16 | Instrucciones del equipo |
| D-004 | Sin datos personales reales ni credenciales en el repositorio | 2026-10-16 | Instrucciones del equipo |

## Propuestas (no aprobadas)

| ID | Propuesta | Notas |
|----|-----------|-------|
| P-001 | `requires-python = ">=3.12"` | Valor provisional en `pyproject.toml`. El entorno local usa CPython 3.14.8 gestionado por uv. Confirmar versión mínima. |
| P-002 | Backend de build `uv_build` | Necesario para instalar el paquete `src/` en el entorno local. Reemplazable. |

## Pendientes

- Framework de agentes (PydanticAI u otro).
- Proveedor y modelo de LLM.
- Persistencia (SQLite, PostgreSQL u otra).
- Optimización/asignación (OR-Tools u otra).
- API (FastAPI u otra, o ninguna).
- Interfaz (Streamlit u otra).
- Framework de pruebas y métrica de evals.
- Fuentes de datos y formato de datos sintéticos.
- Lista de agentes y punto de intervención humana.
