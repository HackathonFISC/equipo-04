# Graph Report - water_coordinator  (2026-10-17)

## Corpus Check
- 40 files · ~13,223 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 448 nodes · 976 edges · 26 communities (13 shown, 13 thin omitted)
- Extraction: 74% EXTRACTED · 26% INFERRED · 0% AMBIGUOUS · INFERRED: 256 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3a9790e8`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Settings
- models.py
- Repositorio
- prioridad.py
- pipeline.py
- Observabilidad
- registrar
- _ejecutar
- geocoding.py
- api/rutas.py
- transcription.py
- repository.py
- flota.py
- config.py
- monitoreo.py

## God Nodes (most connected - your core abstractions)
1. `Settings` - 31 edges
2. `Repositorio` - 28 edges
3. `_ejecutar()` - 23 edges
4. `Observabilidad` - 17 edges
5. `Estado` - 16 edges
6. `RegistroAfectacion` - 15 edges
7. `listar_incidentes()` - 15 edges
8. `AgenteIngesta` - 13 edges
9. `procesar()` - 13 edges
10. `procesar_configurado()` - 13 edges

## Surprising Connections (you probably didn't know these)
- `listar_comunidades()` --calls--> `catalogo()`  [INFERRED]
  src/water_coordinator/services/consultas.py → src/water_coordinator/services/territorio.py
- `mensaje_cobertura_parcial()` --uses--> `PlanPropuesto`  [INFERRED]
  src/water_coordinator/agents/comunicacion.py → src/water_coordinator/schemas/models.py
- `mensaje_cobertura_parcial()` --uses--> `RegistroAfectacion`  [INFERRED]
  src/water_coordinator/agents/comunicacion.py → src/water_coordinator/schemas/models.py
- `mensaje_estado()` --uses--> `Estado`  [INFERRED]
  src/water_coordinator/agents/comunicacion.py → src/water_coordinator/schemas/models.py
- `mensaje_estado()` --uses--> `PlanPropuesto`  [INFERRED]
  src/water_coordinator/agents/comunicacion.py → src/water_coordinator/schemas/models.py

## Import Cycles
- None detected.

## Communities (26 total, 13 thin omitted)

### Community 0 - "Settings"
Cohesion: 0.05
Nodes (27): Settings, estado(), MensajeSaliente, EstadoIntegracion, informe(), InformeIntegracion, estado(), crear_cliente() (+19 more)

### Community 1 - "models.py"
Cohesion: 0.08
Nodes (36): ubicar(), AgenteIngesta, vincular_duplicados(), comunidades(), eventos(), incidentes(), mensajes(), CalculoDemanda (+28 more)

### Community 2 - "Repositorio"
Cohesion: 0.08
Nodes (15): decidir(), registrar_incidente(), demo(), main(), procesar(), procesar_configurado(), ResultadoFlujo, ErrorPersistencia (+7 more)

### Community 3 - "prioridad.py"
Cohesion: 0.07
Nodes (15): AgentePlanificacion, planificar(), _solicitudes(), LotePlanes, SolicitudPlanificacion, cobertura(), tipo_aprobacion(), categoria() (+7 more)

### Community 5 - "Observabilidad"
Cohesion: 0.12
Nodes (5): crear_observabilidad(), enmascarar(), Etapa, faltantes_langfuse(), Observabilidad

### Community 6 - "registrar"
Cohesion: 0.14
Nodes (15): registrar(), clasificar(), _contar(), extraer_datos(), extraer_ubicacion(), normalizar(), _numero(), dias_entre() (+7 more)

### Community 7 - "_ejecutar"
Cohesion: 0.12
Nodes (11): AgenteComunicacion, mensaje_cobertura_parcial(), mensaje_estado(), redactar(), AgentePriorizacion, _conteo(), _ejecutar(), ListaPriorizada (+3 more)

### Community 8 - "geocoding.py"
Cohesion: 0.14
Nodes (6): AgenteGeolocalizacion, LoteUbicaciones, crear_geocodificador(), Geocodificador, NominatimGeocoder, ResultadoGeocodificacion

### Community 9 - "api/rutas.py"
Cohesion: 0.16
Nodes (9): DecisionPanel, Faq, get_obs(), get_repo(), health(), Lista, _repo(), ReporteNuevo (+1 more)

### Community 10 - "transcription.py"
Cohesion: 0.18
Nodes (6): crear_transcriptor(), GoogleSpeech, _instalado(), Transcripcion, Transcriptor, WhisperLocal

### Community 12 - "flota.py"
Cohesion: 0.31
Nodes (7): Cisterna, cisterna(), disponibles_por_horario(), _en_intervalo(), registro_flota(), solicitables(), tramo()

### Community 13 - "config.py"
Cohesion: 0.18
Nodes (4): create_app(), ciclo(), get_settings(), usar_certificados_del_sistema()

### Community 14 - "monitoreo.py"
Cohesion: 0.24
Nodes (4): configurar_logs(), FiltroSecretos, FormatoJSON, secretos_de()

## Knowledge Gaps
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `Settings` to `Repositorio`, `Observabilidad`, `geocoding.py`, `api/rutas.py`, `transcription.py`, `config.py`, `monitoreo.py`?**
  _High betweenness centrality (0.107) - this node is a cross-community bridge._
- **Are the 26 inferred relationships involving `Settings` (e.g. with `create_app()` and `get_repo()`) actually correct?**
  _`Settings` has 26 INFERRED edges - model-reasoned connections that need verification._
- **Should `Settings` be split into smaller, more focused modules?**
  _Cohesion score 0.051251956181533644 - nodes in this community are weakly interconnected._
- **Why does `Observabilidad` connect `Observabilidad` to `models.py`, `Repositorio`, `api/rutas.py`, `_ejecutar`?**
  _High betweenness centrality (0.075) - this node is a cross-community bridge._
- **Are the 19 inferred relationships involving `Repositorio` (e.g. with `comunidades()` and `decidir()`) actually correct?**
  _`Repositorio` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Should `models.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08270676691729323 - nodes in this community are weakly interconnected._
- **Why does `Repositorio` connect `Repositorio` to `models.py`, `repository.py`, `api/rutas.py`?**
  _High betweenness centrality (0.072) - this node is a cross-community bridge._