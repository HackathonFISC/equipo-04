# Graph Report - water_coordinator  (2026-10-17)

## Corpus Check
- 41 files · ~13,779 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 463 nodes · 1007 edges · 27 communities (17 shown, 10 thin omitted)
- Extraction: 74% EXTRACTED · 26% INFERRED · 0% AMBIGUOUS · INFERRED: 264 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `fb34ccdc`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- api/rutas.py
- models.py
- main.py
- water_coordinator_schemas_models
- registrar
- RegistroAfectacion
- Observabilidad
- messaging.py
- flota.py
- transcription.py
- EstadoIntegracion
- geocoding.py
- config.py
- monitoreo.py
- routing.py
- storage.py
- water_coordinator_config
- Settings

## God Nodes (most connected - your core abstractions)
1. `Settings` - 32 edges
2. `Repositorio` - 29 edges
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

## Communities (27 total, 10 thin omitted)

### Community 0 - "api/rutas.py"
Cohesion: 0.07
Nodes (33): comunidades(), DecisionPanel, eventos(), Faq, get_repo(), health(), incidentes(), Lista (+25 more)

### Community 1 - "models.py"
Cohesion: 0.06
Nodes (24): AgenteComunicacion, AgenteGeolocalizacion, AgentePriorizacion, _conteo(), _ejecutar(), procesar(), procesar_configurado(), ResultadoFlujo (+16 more)

### Community 2 - "main.py"
Cohesion: 0.05
Nodes (10): decidir(), demo(), main(), DecisionSupervisor, ErrorAprobacion, huella(), registrar_decision(), cargar_horarios() (+2 more)

### Community 3 - "water_coordinator_schemas_models"
Cohesion: 0.08
Nodes (10): mensaje_cobertura_parcial(), mensaje_estado(), redactar(), AgentePlanificacion, planificar(), _solicitudes(), SolicitudPlanificacion, calcular_demanda() (+2 more)

### Community 4 - "registrar"
Cohesion: 0.11
Nodes (16): ubicar(), registrar(), clasificar(), _contar(), extraer_datos(), extraer_ubicacion(), normalizar(), _numero() (+8 more)

### Community 5 - "RegistroAfectacion"
Cohesion: 0.10
Nodes (12): AgenteIngesta, vincular_duplicados(), Categoria, RegistroAfectacion, categoria(), factor_A(), factor_T(), factor_V() (+4 more)

### Community 6 - "Observabilidad"
Cohesion: 0.12
Nodes (4): get_obs(), enmascarar(), Etapa, Observabilidad

### Community 7 - "messaging.py"
Cohesion: 0.15
Nodes (7): MensajeSaliente, crear_mensajeria(), ErrorMensajeria, MessagingProvider, MockMessagingProvider, verificar_firma_webhook(), WhatsAppCloudApiProvider

### Community 8 - "flota.py"
Cohesion: 0.19
Nodes (8): Cisterna, cisterna(), disponibles_por_horario(), _en_intervalo(), registro_flota(), solicitables(), tramo(), clasificar_ruta()

### Community 9 - "transcription.py"
Cohesion: 0.18
Nodes (6): crear_transcriptor(), GoogleSpeech, _instalado(), Transcripcion, Transcriptor, WhisperLocal

### Community 10 - "EstadoIntegracion"
Cohesion: 0.25
Nodes (8): estado(), estado_base_de_datos(), EstadoIntegracion, informe(), InformeIntegracion, estado(), estado(), estado()

### Community 11 - "geocoding.py"
Cohesion: 0.21
Nodes (4): crear_geocodificador(), Geocodificador, NominatimGeocoder, ResultadoGeocodificacion

### Community 12 - "config.py"
Cohesion: 0.18
Nodes (4): create_app(), ciclo(), get_settings(), usar_certificados_del_sistema()

### Community 13 - "monitoreo.py"
Cohesion: 0.24
Nodes (4): configurar_logs(), FiltroSecretos, FormatoJSON, secretos_de()

### Community 14 - "routing.py"
Cohesion: 0.21
Nodes (4): crear_enrutador(), Enrutador, estado(), OSRMRouter

### Community 16 - "water_coordinator_config"
Cohesion: 0.29
Nodes (4): crear_cliente(), estado(), faltantes(), nombre_modelo()

### Community 17 - "Settings"
Cohesion: 0.31
Nodes (6): Settings, crear_observabilidad(), faltantes_langfuse(), estado(), faltantes_whatsapp(), AlmacenLocal

## Knowledge Gaps
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `Settings` to `api/rutas.py`, `models.py`, `main.py`, `messaging.py`, `transcription.py`, `EstadoIntegracion`, `geocoding.py`, `config.py`, `monitoreo.py`, `routing.py`, `water_coordinator_config`?**
  _High betweenness centrality (0.114) - this node is a cross-community bridge._
- **Are the 27 inferred relationships involving `Settings` (e.g. with `create_app()` and `get_repo()`) actually correct?**
  _`Settings` has 27 INFERRED edges - model-reasoned connections that need verification._
- **Should `api/rutas.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06682692307692308 - nodes in this community are weakly interconnected._
- **Why does `Repositorio` connect `api/rutas.py` to `models.py`, `main.py`, `EstadoIntegracion`?**
  _High betweenness centrality (0.076) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `Repositorio` (e.g. with `comunidades()` and `decidir()`) actually correct?**
  _`Repositorio` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Should `models.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06412583182093164 - nodes in this community are weakly interconnected._
- **Why does `Observabilidad` connect `Observabilidad` to `api/rutas.py`, `models.py`, `RegistroAfectacion`, `Settings`?**
  _High betweenness centrality (0.071) - this node is a cross-community bridge._