# Graph Report - water_coordinator  (2026-10-17)

## Corpus Check
- Corpus is ~9,420 words - fits in a single context window. You may not need a graph.

## Summary
- 347 nodes · 699 edges · 19 communities (11 shown, 8 thin omitted)
- Extraction: 76% EXTRACTED · 24% INFERRED · 0% AMBIGUOUS · INFERRED: 168 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Integraciones y configuración
- Agente 6 Comunicación
- CLI y configuración
- Agentes 1-4 núcleo
- Agentes AutoGen (handlers)
- Geocodificación Nominatim
- Clasificación por palabras clave
- Reglas de prioridad T V A P
- Transcripción Whisper/Google
- Flota y horarios
- Logs y redacción de secretos

## God Nodes (most connected - your core abstractions)
1. `procesar()` - 27 edges
2. `Settings` - 25 edges
3. `RegistroAfectacion` - 14 edges
4. `registrar()` - 12 edges
5. `AgenteIngesta` - 12 edges
6. `Repositorio` - 12 edges
7. `planificar()` - 11 edges
8. `main()` - 11 edges
9. `ubicar()` - 10 edges
10. `demo()` - 10 edges

## Surprising Connections (you probably didn't know these)
- `mensaje_cobertura_parcial()` --uses--> `PlanPropuesto`  [INFERRED]
  agents/comunicacion.py → schemas/models.py
- `mensaje_estado()` --uses--> `PlanPropuesto`  [INFERRED]
  agents/comunicacion.py → schemas/models.py
- `redactar()` --uses--> `MensajeSaliente`  [INFERRED]
  agents/comunicacion.py → schemas/models.py
- `procesar()` --uses--> `AgenteComunicacion`  [INFERRED]
  orchestration/pipeline.py → agents/comunicacion.py
- `zona_por_distrito()` --calls--> `normalizar()`  [INFERRED]
  agents/geolocalizacion.py → services/clasificacion.py

## Import Cycles
- None detected.

## Communities (19 total, 8 thin omitted)

### Community 0 - "Integraciones y configuración"
Cohesion: 0.06
Nodes (25): Settings, estado(), MensajeSaliente, EstadoIntegracion, informe(), InformeIntegracion, estado(), crear_cliente() (+17 more)

### Community 1 - "Agente 6 Comunicación"
Cohesion: 0.07
Nodes (27): AgenteComunicacion, mensaje_cobertura_parcial(), mensaje_estado(), redactar(), AgenteGeolocalizacion, ubicar(), AgenteIngesta, vincular_duplicados() (+19 more)

### Community 2 - "CLI y configuración"
Cohesion: 0.06
Nodes (11): get_settings(), demo(), main(), ErrorPersistencia, Repositorio, ahora(), PlanPropuesto, ErrorAprobacion (+3 more)

### Community 3 - "Agentes 1-4 núcleo"
Cohesion: 0.08
Nodes (6): zona_por_distrito(), planificar(), _solicitudes(), cobertura(), tipo_aprobacion(), clasificar_ruta()

### Community 4 - "Agentes AutoGen (handlers)"
Cohesion: 0.09
Nodes (8): AgentePlanificacion, AgentePriorizacion, procesar(), ResultadoFlujo, ListaPriorizada, LotePlanes, SolicitudPlanificacion, SolicitudPriorizacion

### Community 5 - "Geocodificación Nominatim"
Cohesion: 0.09
Nodes (6): crear_geocodificador(), Geocodificador, NominatimGeocoder, ResultadoGeocodificacion, AlmacenLocal, ErrorAlmacenamiento

### Community 6 - "Clasificación por palabras clave"
Cohesion: 0.21
Nodes (11): registrar(), clasificar(), _contar(), extraer_datos(), extraer_ubicacion(), normalizar(), _numero(), dias_entre() (+3 more)

### Community 7 - "Reglas de prioridad T V A P"
Cohesion: 0.17
Nodes (9): Categoria, categoria(), factor_A(), factor_T(), factor_V(), ordenar(), personas_estimadas(), priorizar() (+1 more)

### Community 8 - "Transcripción Whisper/Google"
Cohesion: 0.18
Nodes (6): crear_transcriptor(), GoogleSpeech, _instalado(), Transcripcion, Transcriptor, WhisperLocal

### Community 9 - "Flota y horarios"
Cohesion: 0.31
Nodes (7): Cisterna, cisterna(), disponibles_por_horario(), _en_intervalo(), registro_flota(), solicitables(), tramo()

### Community 10 - "Logs y redacción de secretos"
Cohesion: 0.24
Nodes (4): configurar_logs(), FiltroSecretos, FormatoJSON, secretos_de()

## Knowledge Gaps
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `procesar()` connect `Agentes AutoGen (handlers)` to `Integraciones y configuración`, `Agente 6 Comunicación`, `CLI y configuración`, `Geocodificación Nominatim`, `Flota y horarios`?**
  _High betweenness centrality (0.124) - this node is a cross-community bridge._
- **Are the 23 inferred relationships involving `procesar()` (e.g. with `AgenteComunicacion` and `AgenteGeolocalizacion`) actually correct?**
  _`procesar()` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Should `Integraciones y configuración` be split into smaller, more focused modules?**
  _Cohesion score 0.06487434248977206 - nodes in this community are weakly interconnected._
- **Why does `Settings` connect `Integraciones y configuración` to `Transcripción Whisper/Google`, `CLI y configuración`, `Logs y redacción de secretos`, `Geocodificación Nominatim`?**
  _High betweenness centrality (0.098) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `Settings` (e.g. with `demo()` and `estado()`) actually correct?**
  _`Settings` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Should `Agente 6 Comunicación` be split into smaller, more focused modules?**
  _Cohesion score 0.06936026936026936 - nodes in this community are weakly interconnected._
- **Why does `Repositorio` connect `CLI y configuración` to `Agentes AutoGen (handlers)`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._