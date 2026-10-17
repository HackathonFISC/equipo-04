# Graph Report - water_coordinator  (2026-10-17)

## Corpus Check
- 39 files · ~12,336 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 432 nodes · 931 edges · 21 communities (11 shown, 10 thin omitted)
- Extraction: 74% EXTRACTED · 26% INFERRED · 0% AMBIGUOUS · INFERRED: 242 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `31937736`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- models.py
- Settings
- api/rutas.py
- water_coordinator_schemas_models
- transcription.py
- geocoding.py
- messaging.py
- pipeline.py
- clasificacion.py
- Observabilidad
- flota.py
- comunicacion.py

## God Nodes (most connected - your core abstractions)
1. `Settings` - 31 edges
2. `Repositorio` - 26 edges
3. `_ejecutar()` - 23 edges
4. `Estado` - 15 edges
5. `RegistroAfectacion` - 15 edges
6. `listar_incidentes()` - 14 edges
7. `Observabilidad` - 14 edges
8. `procesar()` - 13 edges
9. `procesar_configurado()` - 13 edges
10. `registrar()` - 12 edges

## Surprising Connections (you probably didn't know these)
- `planificar()` --calls--> `cobertura()`  [INFERRED]
  src/water_coordinator/agents/planificacion.py → src/water_coordinator/services/demanda.py
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

## Communities (21 total, 10 thin omitted)

### Community 0 - "models.py"
Cohesion: 0.06
Nodes (43): AgenteGeolocalizacion, ubicar(), AgenteIngesta, registrar(), vincular_duplicados(), AgentePlanificacion, planificar(), _solicitudes() (+35 more)

### Community 1 - "Settings"
Cohesion: 0.05
Nodes (15): create_app(), ciclo(), get_settings(), Settings, usar_certificados_del_sistema(), demo(), estado(), main() (+7 more)

### Community 2 - "api/rutas.py"
Cohesion: 0.06
Nodes (23): decidir(), DecisionPanel, eventos(), Faq, get_obs(), get_repo(), health(), Lista (+15 more)

### Community 3 - "water_coordinator_schemas_models"
Cohesion: 0.07
Nodes (11): zona_por_distrito(), cobertura(), tipo_aprobacion(), categoria(), factor_A(), factor_T(), factor_V(), personas_estimadas() (+3 more)

### Community 4 - "transcription.py"
Cohesion: 0.09
Nodes (17): EstadoIntegracion, informe(), InformeIntegracion, estado(), crear_cliente(), estado(), faltantes(), nombre_modelo() (+9 more)

### Community 5 - "geocoding.py"
Cohesion: 0.07
Nodes (9): crear_geocodificador(), Geocodificador, NominatimGeocoder, ResultadoGeocodificacion, crear_enrutador(), Enrutador, OSRMRouter, AlmacenLocal (+1 more)

### Community 6 - "messaging.py"
Cohesion: 0.14
Nodes (9): MensajeSaliente, crear_mensajeria(), ErrorMensajeria, estado(), faltantes_whatsapp(), MessagingProvider, MockMessagingProvider, verificar_firma_webhook() (+1 more)

### Community 7 - "pipeline.py"
Cohesion: 0.12
Nodes (4): _conteo(), procesar(), procesar_configurado(), nuevo_id()

### Community 8 - "clasificacion.py"
Cohesion: 0.20
Nodes (10): clasificar(), _contar(), extraer_datos(), extraer_ubicacion(), normalizar(), _numero(), dias_entre(), _fecha() (+2 more)

### Community 10 - "flota.py"
Cohesion: 0.27
Nodes (7): Cisterna, cisterna(), disponibles_por_horario(), _en_intervalo(), registro_flota(), solicitables(), tramo()

### Community 11 - "comunicacion.py"
Cohesion: 0.22
Nodes (5): AgenteComunicacion, mensaje_cobertura_parcial(), mensaje_estado(), redactar(), SolicitudComunicacion

## Knowledge Gaps
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `Settings` to `api/rutas.py`, `transcription.py`, `geocoding.py`, `messaging.py`, `pipeline.py`?**
  _High betweenness centrality (0.108) - this node is a cross-community bridge._
- **Are the 26 inferred relationships involving `Settings` (e.g. with `create_app()` and `get_repo()`) actually correct?**
  _`Settings` has 26 INFERRED edges - model-reasoned connections that need verification._
- **Should `models.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05809802012333658 - nodes in this community are weakly interconnected._
- **Why does `_ejecutar()` connect `models.py` to `messaging.py`, `pipeline.py`, `Observabilidad`, `flota.py`, `comunicacion.py`?**
  _High betweenness centrality (0.081) - this node is a cross-community bridge._
- **Are the 17 inferred relationships involving `Repositorio` (e.g. with `decidir()` and `eventos()`) actually correct?**
  _`Repositorio` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Should `Settings` be split into smaller, more focused modules?**
  _Cohesion score 0.05273937532002048 - nodes in this community are weakly interconnected._
- **Why does `Repositorio` connect `api/rutas.py` to `models.py`, `Settings`, `pipeline.py`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._