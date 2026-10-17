# Roadmap y plan de construcción

| Fase | Objetivo | Estado |
| --- | --- | --- |
| 0. Preparación | Estructura, documentación y configuración mínima. | Completada (2026-10-16) |
| 1. Diseño | Documento de criterios rev.4 y decisiones DEC-C. | Completada; los conflictos C-01 a C-03 siguen abiertos |
| **2. Construcción, etapa 1** | Reporte → A1 → A2 → A3 → A4 → plan → aprobación simulada → traza; integraciones sin credenciales. | **Completada (2026-10-17)** |
| 3. Construcción, etapa 2 | Agente 5 en el flujo (OSRM y ubicación de la organización), alternativas de ruta y excepción de 1.000 km. | Pendiente de datos [PEND] |
| 4. Interfaz | Mapa Leaflet e interfaz del supervisor en `frontend/`; backend HTTP si se aprueba. | Pendiente (frontend congelado) |
| 5. Integraciones reales | IA, Nominatim, Whisper y WhatsApp con credenciales y aprobación. | Pendiente de cuentas |
| 6. Evals | 15 casos o más, métrica y resultados (requisito de entrega). | Hay pruebas unitarias; faltan los evals formales |
| 7. Entrega | README, diagrama, bitácora de IA y tag `final-24h`. | Pendiente |

## Detalle de la etapa 1

| Paso | Archivos | Estado |
| --- | --- | --- |
| Contratos de datos | `schemas/models.py` | Hecho |
| Reglas deterministas | `services/*.py` | Hecho |
| Agentes AutoGen | `agents/*.py` | Hecho (A1, A2, A3, A4, A6) |
| Orquestador y traza | `orchestration/pipeline.py`, `persistence/repository.py` | Hecho |
| Supervisor | `services/aprobacion.py`, `water-coordinator aprobar` | Hecho |
| Adaptadores | `tools/*.py` | Hechos, sin credenciales |
| Datos simulados | `data/simulados/reportes.json` | Hecho |
| Pruebas | `tests/` | 76 aprobadas y 5 de integración omitidas |
| Documentación | `docs/*.md` | Hecha |
| Grafo del código | `graphify-out/` | Hecho |
