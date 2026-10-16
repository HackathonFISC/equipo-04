# Arquitectura (propuesta, NO definitiva)

> Estado: borrador. El diseño se sigue trabajando fuera del repositorio. Nada de este documento es una decisión aprobada salvo que figure como tal en `DECISIONS.md`.

## Estructura del repositorio

| Ruta | Propósito previsto | Estado |
|------|--------------------|--------|
| `src/water_coordinator/main.py` | Punto de entrada | Esqueleto sin lógica |
| `src/water_coordinator/config.py` | Configuración centralizada desde variables de entorno | Mínimo (`APP_ENV`, `LOG_LEVEL`) |
| `src/water_coordinator/schemas/` | Modelos y contratos de datos | Vacío |
| `src/water_coordinator/agents/` | Agentes futuros | Vacío |
| `src/water_coordinator/tools/` | Integraciones futuras | Vacío |
| `src/water_coordinator/services/` | Reglas de negocio futuras | Vacío |
| `src/water_coordinator/orchestration/` | Coordinación entre agentes | Vacío |
| `src/water_coordinator/api/` | API, solo si se aprueba | Vacío |
| `tests/` | Pruebas y evals | Estrategia pendiente |
| `data/` | Datos de ejemplo sintéticos | Vacío |

## Elementos conocidos

- El sistema será multiagente y debe tener un **punto de intervención humana** explícito (exigido por la plantilla de entrega).

## Pendiente de diseño

- Qué agentes existen, sus responsabilidades y entradas/salidas.
- Flujo de orquestación y dónde interviene el humano.
- Persistencia, interfaz de usuario, API y fuentes de datos.
- Diagrama de arquitectura.

Ver `DECISIONS.md` y `TOOLING.md`.
