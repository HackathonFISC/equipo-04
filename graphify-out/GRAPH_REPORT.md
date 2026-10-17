# Graph Report - water_coordinator  (2026-10-17)

## Corpus Check
- 39 files · ~12,212 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 428 nodes · 923 edges · 21 communities (11 shown, 10 thin omitted)
- Extraction: 74% EXTRACTED · 26% INFERRED · 0% AMBIGUOUS · INFERRED: 239 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e6556cd7`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- water_coordinator_schemas_models
- models.py
- Settings
- api/rutas.py
- app.py
- registrar
- main.py
- geocoding.py
- messaging.py
- pipeline.py
- Observabilidad
- transcription.py

## God Nodes (most connected - your core abstractions)
1. `Settings` - 31 edges
2. `Repositorio` - 25 edges
3. `_ejecutar()` - 23 edges
4. `Estado` - 15 edges
5. `RegistroAfectacion` - 15 edges
6. `listar_incidentes()` - 14 edges
7. `Observabilidad` - 14 edges
8. `procesar()` - 13 edges
9. `procesar_configurado()` - 13 edges
10. `registrar()` - 12 edges

## Surprising Connections (you probably didn't know these)
- `mensaje_cobertura_parcial()` --uses--> `PlanPropuesto`  [INFERRED]
  src/water_coordinator/agents/comunicacion.py → src/water_coordinator/schemas/models.py
- `mensaje_estado()` --uses--> `PlanPropuesto`  [INFERRED]
  src/water_coordinator/agents/comunicacion.py → src/water_coordinator/schemas/models.py
- `redactar()` --uses--> `MensajeSaliente`  [INFERRED]
  src/water_coordinator/agents/comunicacion.py → src/water_coordinator/schemas/models.py
- `redactar()` --uses--> `SolicitudComunicacion`  [INFERRED]
  src/water_coordinator/agents/comunicacion.py → src/water_coordinator/schemas/models.py
- `zona_por_distrito()` --calls--> `normalizar()`  [INFERRED]
  src/water_coordinator/agents/geolocalizacion.py → src/water_coordinator/services/clasificacion.py

## Import Cycles
- None detected.

## Communities (21 total, 10 thin omitted)

### Community 0 - "water_coordinator_schemas_models"
Cohesion: 0.05
Nodes (26): mensaje_cobertura_parcial(), mensaje_estado(), redactar(), AgenteIngesta, planificar(), _solicitudes(), incidentes(), Categoria (+18 more)

### Community 1 - "models.py"
Cohesion: 0.07
Nodes (34): AgenteComunicacion, AgentePlanificacion, AgentePriorizacion, _ejecutar(), ResultadoFlujo, CalculoDemanda, Cisterna, Coordenadas (+26 more)

### Community 2 - "Settings"
Cohesion: 0.06
Nodes (19): get_settings(), Settings, estado(), EstadoIntegracion, informe(), InformeIntegracion, estado(), crear_cliente() (+11 more)

### Community 3 - "api/rutas.py"
Cohesion: 0.07
Nodes (20): DecisionPanel, eventos(), Faq, get_obs(), get_repo(), health(), Lista, mensajes() (+12 more)

### Community 4 - "app.py"
Cohesion: 0.09
Nodes (8): create_app(), ciclo(), configurar_logs(), FiltroSecretos, FormatoJSON, secretos_de(), crear_observabilidad(), faltantes_langfuse()

### Community 5 - "registrar"
Cohesion: 0.14
Nodes (12): registrar(), vincular_duplicados(), clasificar(), _contar(), extraer_datos(), extraer_ubicacion(), normalizar(), _numero() (+4 more)

### Community 6 - "main.py"
Cohesion: 0.12
Nodes (7): decidir(), demo(), main(), ErrorAprobacion, huella(), registrar_decision(), cargar_horarios()

### Community 7 - "geocoding.py"
Cohesion: 0.12
Nodes (7): AgenteGeolocalizacion, ubicar(), zona_por_distrito(), crear_geocodificador(), Geocodificador, NominatimGeocoder, ResultadoGeocodificacion

### Community 8 - "messaging.py"
Cohesion: 0.14
Nodes (9): MensajeSaliente, crear_mensajeria(), ErrorMensajeria, estado(), faltantes_whatsapp(), MessagingProvider, MockMessagingProvider, verificar_firma_webhook() (+1 more)

### Community 9 - "pipeline.py"
Cohesion: 0.12
Nodes (4): _conteo(), procesar(), procesar_configurado(), nuevo_id()

### Community 11 - "transcription.py"
Cohesion: 0.18
Nodes (6): crear_transcriptor(), GoogleSpeech, _instalado(), Transcripcion, Transcriptor, WhisperLocal

## Knowledge Gaps
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `Settings` to `api/rutas.py`, `app.py`, `main.py`, `geocoding.py`, `messaging.py`, `pipeline.py`, `transcription.py`?**
  _High betweenness centrality (0.108) - this node is a cross-community bridge._
- **Are the 26 inferred relationships involving `Settings` (e.g. with `create_app()` and `get_repo()`) actually correct?**
  _`Settings` has 26 INFERRED edges - model-reasoned connections that need verification._
- **Should `water_coordinator_schemas_models` be split into smaller, more focused modules?**
  _Cohesion score 0.0506558118498417 - nodes in this community are weakly interconnected._
- **Why does `_ejecutar()` connect `models.py` to `water_coordinator_schemas_models`, `geocoding.py`, `messaging.py`, `pipeline.py`, `Observabilidad`?**
  _High betweenness centrality (0.082) - this node is a cross-community bridge._
- **Are the 17 inferred relationships involving `Repositorio` (e.g. with `decidir()` and `eventos()`) actually correct?**
  _`Repositorio` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Should `models.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06830601092896176 - nodes in this community are weakly interconnected._
- **Why does `Repositorio` connect `api/rutas.py` to `water_coordinator_schemas_models`, `pipeline.py`, `main.py`, `models.py`?**
  _High betweenness centrality (0.060) - this node is a cross-community bridge._