# Graph Report - water_coordinator  (2026-10-17)

## Corpus Check
- 41 files · ~13,692 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 461 nodes · 998 edges · 28 communities (17 shown, 11 thin omitted)
- Extraction: 74% EXTRACTED · 26% INFERRED · 0% AMBIGUOUS · INFERRED: 259 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `73467b76`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- api/rutas.py
- models.py
- water_coordinator_schemas_models
- main.py
- registrar
- Observabilidad
- messaging.py
- pipeline.py
- Settings
- flota.py
- transcription.py
- EstadoIntegracion
- geocoding.py
- monitoreo.py
- routing.py
- AgenteGeolocalizacion
- llm.py
- AlmacenLocal
- ClaudeCodeClient

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
- `mensaje_estado()` --uses--> `Estado`  [INFERRED]
  src/water_coordinator/agents/comunicacion.py → src/water_coordinator/schemas/models.py
- `mensaje_estado()` --uses--> `PlanPropuesto`  [INFERRED]
  src/water_coordinator/agents/comunicacion.py → src/water_coordinator/schemas/models.py
- `redactar()` --uses--> `Estado`  [INFERRED]
  src/water_coordinator/agents/comunicacion.py → src/water_coordinator/schemas/models.py

## Import Cycles
- None detected.

## Communities (28 total, 11 thin omitted)

### Community 0 - "api/rutas.py"
Cohesion: 0.07
Nodes (31): comunidades(), DecisionPanel, eventos(), Faq, get_repo(), health(), incidentes(), Lista (+23 more)

### Community 1 - "models.py"
Cohesion: 0.07
Nodes (23): AgenteComunicacion, AgenteIngesta, AgentePlanificacion, AgentePriorizacion, _ejecutar(), ResultadoFlujo, CalculoDemanda, Coordenadas (+15 more)

### Community 2 - "water_coordinator_schemas_models"
Cohesion: 0.06
Nodes (21): mensaje_cobertura_parcial(), mensaje_estado(), redactar(), vincular_duplicados(), planificar(), _solicitudes(), Categoria, Certeza (+13 more)

### Community 3 - "main.py"
Cohesion: 0.06
Nodes (8): decidir(), demo(), main(), ErrorAprobacion, huella(), registrar_decision(), cargar_horarios(), ruta_claude()

### Community 4 - "registrar"
Cohesion: 0.11
Nodes (16): ubicar(), registrar(), clasificar(), _contar(), extraer_datos(), extraer_ubicacion(), normalizar(), _numero() (+8 more)

### Community 5 - "Observabilidad"
Cohesion: 0.11
Nodes (4): get_obs(), enmascarar(), Etapa, Observabilidad

### Community 6 - "messaging.py"
Cohesion: 0.15
Nodes (7): MensajeSaliente, crear_mensajeria(), ErrorMensajeria, MessagingProvider, MockMessagingProvider, verificar_firma_webhook(), WhatsAppCloudApiProvider

### Community 7 - "pipeline.py"
Cohesion: 0.12
Nodes (4): _conteo(), procesar(), procesar_configurado(), nuevo_id()

### Community 8 - "Settings"
Cohesion: 0.15
Nodes (8): create_app(), ciclo(), get_settings(), Settings, usar_certificados_del_sistema(), estado(), crear_observabilidad(), faltantes_langfuse()

### Community 9 - "flota.py"
Cohesion: 0.19
Nodes (8): Cisterna, cisterna(), disponibles_por_horario(), _en_intervalo(), registro_flota(), solicitables(), tramo(), clasificar_ruta()

### Community 10 - "transcription.py"
Cohesion: 0.18
Nodes (6): crear_transcriptor(), GoogleSpeech, _instalado(), Transcripcion, Transcriptor, WhisperLocal

### Community 11 - "EstadoIntegracion"
Cohesion: 0.25
Nodes (8): EstadoIntegracion, informe(), InformeIntegracion, estado(), faltantes_whatsapp(), estado(), estado(), estado()

### Community 12 - "geocoding.py"
Cohesion: 0.21
Nodes (3): crear_geocodificador(), estado(), NominatimGeocoder

### Community 13 - "monitoreo.py"
Cohesion: 0.24
Nodes (4): configurar_logs(), FiltroSecretos, FormatoJSON, secretos_de()

### Community 14 - "routing.py"
Cohesion: 0.22
Nodes (3): crear_enrutador(), Enrutador, OSRMRouter

### Community 15 - "AgenteGeolocalizacion"
Cohesion: 0.25
Nodes (3): AgenteGeolocalizacion, Geocodificador, ResultadoGeocodificacion

### Community 16 - "llm.py"
Cohesion: 0.33
Nodes (4): crear_cliente(), estado(), faltantes(), nombre_modelo()

## Knowledge Gaps
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `Settings` to `api/rutas.py`, `main.py`, `messaging.py`, `pipeline.py`, `transcription.py`, `EstadoIntegracion`, `geocoding.py`, `monitoreo.py`, `routing.py`, `llm.py`, `AlmacenLocal`?**
  _High betweenness centrality (0.114) - this node is a cross-community bridge._
- **Are the 26 inferred relationships involving `Settings` (e.g. with `create_app()` and `get_repo()`) actually correct?**
  _`Settings` has 26 INFERRED edges - model-reasoned connections that need verification._
- **Should `api/rutas.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06927551560021153 - nodes in this community are weakly interconnected._
- **Why does `Observabilidad` connect `Observabilidad` to `api/rutas.py`, `models.py`, `Settings`, `pipeline.py`?**
  _High betweenness centrality (0.072) - this node is a cross-community bridge._
- **Are the 19 inferred relationships involving `Repositorio` (e.g. with `comunidades()` and `decidir()`) actually correct?**
  _`Repositorio` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Should `models.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07390648567119155 - nodes in this community are weakly interconnected._
- **Why does `_ejecutar()` connect `models.py` to `api/rutas.py`, `Observabilidad`, `messaging.py`, `pipeline.py`, `flota.py`, `AgenteGeolocalizacion`?**
  _High betweenness centrality (0.071) - this node is a cross-community bridge._