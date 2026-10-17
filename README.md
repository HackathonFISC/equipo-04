# Nombre del proyecto

<!-- Cambia el 0 por el número de su reto y deja la línea tal cual ("Reto: N"):
       1 = Agua · 2 = Educación · 3 = Empleabilidad
     No cambien de reto sin autorización de los organizadores. -->
Reto: 1

## Equipo

- Anyeline Arauz (@anyelinearauz-jpg)
- Analía Rodríguez (@leaniuwnm)
- Alanis Martez (@Ali-SMgt)

## Problema

El crecimiento urbano acelerado de Panamá Oeste, concentrado en distritos como Arraiján y La Chorrera, ha sobrepasado significativamente la capacidad operativa de las plantas potabilizadoras y las redes de distribución existentes. Frente a labores de mantenimiento, fallas tubulares o periodos de baja producción, comunidades enteras sufren desabastecimiento prolongado de agua potable por días, dependiendo de la distribución a través de carros cisterna. 

 
Actualmente, los reclamos y reportes llegan de forma dispersa mediante WhatsApp, redes sociales y llamadas telefónicas, careciendo de un centro de consolidación e inteligencia de datos. Esto genera: 


Redundancia no gestionada: Un mismo incidente es reportado cientos de veces. 

Invisibilidad de sectores vulnerables: Zonas con menor penetración digital o redes sociales quedan excluidas de la atención. 

Asignación inequitativa e ineficiente: Se prioriza a quienes generan mayor presión mediática o protestas, en lugar de atender criterios de prioridad crítica (como Centros de Salud, asilos/hogares de adultos mayores o escuelas). 

Incertidumbre social: La desinformación sobre los horarios de distribución fomenta cierres de calles y desconfianza institucional. 

Los afectados son la población de las zonas que pierden suministro de agua potable.

## Arquitectura de agentes

AquaAlerta es un centro de coordinación multiagente para la crisis del agua en Panamá Oeste. Recibe reportes ciudadanos (simulados de WhatsApp o transcripciones de audio), los convierte en afectaciones estructuradas, las ubica, las prioriza y propone un plan de abastecimiento con cisternas. **Ningún plan se ejecuta sin la aprobación de un supervisor humano.**

La coordinación usa **AutoGen** (`autogen-core`): cada agente es un `RoutedAgent` con contratos de entrada y salida tipados con Pydantic. Los agentes no escriben en la base de datos; el orquestador valida cada salida, la guarda y deja traza.

### Agentes

| Agente | Qué hace | Herramientas |
| --- | --- | --- |
| **A1 · Ingesta y clasificación** | Clasifica el reporte (falta de agua, tubería rota, agua contaminada) por palabras clave (`#sinagua`, `#tuberiarota`, `#idaan`, formas habladas). Extrae la fecha del incidente, la ubicación reportada y las unidades afectadas. Detecta duplicados y activa la alerta sanitaria. | Reglas deterministas. **Claude** contrasta la clasificación; si discrepa, el caso va a revisión humana. |
| **A2 · Geolocalización** | Normaliza la ubicación y la asocia a un distrito y una comunidad del catálogo de La Chorrera y Arraiján. Declara la certeza (confirmada, aproximada, ambigua o no verificada) y nunca inventa coordenadas. | Catálogo territorial y **Nominatim (OpenStreetMap)**. |
| **A3 · Priorización** | Aplica la jerarquía hospital → policlínica → centro de salud → escuela → resto. Para el resto calcula `P = 0,50·T + 0,25·V + 0,25·A`. Si falta un factor, P queda incompleto y se pide revisión; nunca se asigna cero. | Funciones deterministas. |
| **A4 · Planificación de recursos** | Calcula la demanda en galones/día × (duración del tipo + 50 % de los días sin agua). Asigna cisternas de la flota de 71 según el horario y calcula la cobertura: 100 % es ordinaria, 80–99 % parcial y menos de 80 % extraordinaria. | Funciones deterministas. Flota y horarios configurables. |
| **A5 · Rutas** *(reglas listas, aún fuera del flujo)* | Recorrido salida → carga → afectaciones → regreso, con límite de 1.000 km y excepción de emergencia aprobada por el supervisor. | **OSRM**. |
| **A6 · Comunicación** | Redacta los mensajes para quien reportó a partir de los registros: estado, cobertura parcial y datos faltantes. Nunca promete entregas ni horas. | Mensajería **simulada**. El adaptador de WhatsApp Cloud API está listo, con el envío bloqueado. |

### Punto de intervención humana

El **supervisor** es una función de control, no un agente. Desde el panel web (`gestion.html`) aprueba, rechaza o pide cambios en cada plan:

- Todo plan necesita aprobación, incluso con cobertura del 100 %.
- Una cobertura menor al 80 % exige justificación escrita.
- Aprobar no significa ejecutar: «ejecutado» lo registra solo el responsable operativo.
- Mientras no haya autenticación, las decisiones del panel se registran como **simuladas**.

Además pasan a revisión humana: las ubicaciones ambiguas, las categorías inciertas (p. ej. «clínica»), los empates persistentes, los reportes contradictorios y los desacuerdos entre Claude y las reglas.

### Diagrama
```mermaid
flowchart TD
    R["Reporte ciudadano<br/>WhatsApp simulado / transcripción"] --> A1["A1 · Ingesta y clasificación"]
    A1 -.->|contraste opcional| LLM[("Claude")]
    A1 -->|tipo determinado| A2["A2 · Geolocalización"]
    A1 -.->|"indeterminado: pide información"| A6
    A2 -.-> NOM[("Nominatim / OSM")]
    A2 --> A3["A3 · Priorización<br/>jerarquía + P = 0,5T + 0,25V + 0,25A"]
    A3 --> A4["A4 · Planificación<br/>demanda, flota, horarios, cobertura"]
    A4 -.->|etapa 2| A5["A5 · Rutas"]
    A5 -.-> OSRM[("OSRM")]
    A4 --> PLAN[("Plan propuesto<br/>pendiente de aprobación")]
    A4 --> A6["A6 · Comunicación<br/>mensajes simulados"]
    PLAN --> SUP{{"Supervisor humano<br/>panel web"}}
    SUP -->|"aprobado / rechazado / cambios"| DB[("SQLite<br/>registros + traza")]
    A1 & A2 & A3 & A4 & A6 --> DB
    DB --> UI["Panel del supervisor<br/>admin.html · gestion.html"]
    A1 & A2 & A3 & A4 & A6 -.->|trazas| LF[("Langfuse")]
```

**Flujo**
El reporte entra por la CLI (demo) o por la API (POST /api/incidents).
A1 → A2 → A3 → A4 → A6 se ejecutan en secuencia dentro del runtime de AutoGen. Los reportes indeterminados se quedan en A1 y A6 pide más información.
Cada salida se guarda en SQLite con su traza: agente, versión de reglas y modelo usado.
El panel consulta la API y el supervisor decide cada plan.
Si está activado, cada ejecución se envía a Langfuse como una traza con una observación por agente y las llamadas a Claude como generation.

## Tecnologías y fuentes de datos
Tecnologías

Backend: Python 3.14 con uv.
Agentes: AutoGen 0.7.5 (autogen-core).
Contratos y configuración: Pydantic y pydantic-settings.
Base de datos: SQLAlchemy sobre SQLite (migrable a PostgreSQL).
API: FastAPI + Uvicorn (local).
Modelo de IA: Claude (claude-sonnet-5-5) a través de Claude Code, sin API key. El proveedor es intercambiable: Anthropic API, OpenAI o Ollama.
Mapas: Leaflet 1.9.4 con teselas de OpenStreetMap.
Geocodificación: Nominatim. Rutas: OSRM (etapa 2).
Observabilidad: Langfuse (SDK 5, OpenTelemetry).
Preparados sin activar: WhatsApp Business Cloud API, Whisper local (faster-whisper) y Google Speech-to-Text.
Pruebas: pytest (112 pruebas sin red).
Frontend: HTML, CSS y JavaScript.

Fuentes de datos

Reportes: simulados en data/simulados/reportes.json, con contactos ficticios sim:*. No se usan datos reales de ciudadanos.

Reglas operativas: docs/AGENT_CRITERIA_AND_DECISION_RULES.md (rev.4) y las decisiones de docs/DECISIONS.md. 

Incluyen la demanda de referencia (79,3 gal/persona urbana, 26,4 rural, 4 por estudiante y valores fijos para salud), los promedios de ocupación, la flota de 71 cisternas (Small 3.000–5.500 gal, Big 9.000–13.000 gal) y los horarios de disponibilidad.
Territorio: distritos de Panamá Oeste y corregimientos de La Chorrera y Arraiján (services/territorio.py).
Cartografía: OpenStreetMap, vía Nominatim y las teselas de OSM.

## Instalación y ejecución
Requisitos: Windows, macOS o Linux con uv y Git. uv instala Python por su cuenta.

Instalar dependencias:
git clone https://github.com/HackathonFISC/equipo-04.git
cd equipo-04
uv sync
Configurar. Copia .env.example a .env. Sin cambiar nada funciona en modo simulado, sin claves:
Reglas sin IA.
Mensajería simulada.
Sin geocodificación.
Para activar servicios (todos opcionales y sin claves reales en el repo):

Claude sin API key: MODEL_PROVIDER=claude_code y MODEL_NAME=claude-sonnet-5-5. Requiere la app de escritorio de Claude con la sesión iniciada.
Coordenadas reales: GEOCODER_PROVIDER=nominatim y NOMINATIM_USER_AGENT=nombre-app (correo@ejemplo).
Trazas: LANGFUSE_TRACING_ENABLED=true y las claves de tu proyecto de Langfuse.
Más detalle en docs/API_SETUP.md.

Cargar datos de demostración. --reiniciar vacía la base local de desarrollo:
uv run water-coordinator demo --reiniciar --sin-aprobacion
Iniciar la API (terminal 1):
```bash uv run uvicorn water_coordinator.api.app:app --reload --host 127.0.0.1 --port 8000 ```
Documentación interactiva: http://127.0.0.1:8000/docs

Iniciar el panel (terminal 2):
```bash uv run python -m http.server 5500 --bind 127.0.0.1 -d frontend ```
Abrir http://127.0.0.1:5500/admin.html y http://127.0.0.1:5500/gestion.html. Abrirlos como archivo (file://) no funciona.

Pruebas y estado de las integraciones:
```bash uv run pytest -q ```
```bash uv run water-coordinator estado```

La API no tiene autenticación y está pensada solo para uso local (127.0.0.1). Las aprobaciones desde el panel se registran como simuladas y ningún mensaje se envía realmente.


## Evals

Al menos 15 casos de prueba, métrica y resultados.


## Bitácora de IA

| Parte del proyecto | Herramienta de IA | Qué hizo la IA | Qué se decidió o modificó a mano |
| --- | --- | --- | --- |
| Documento de criterios y reglas de decisión (`docs/AGENT_CRITERIA_AND_DECISION_RULES.md`, rev.4) | ChatGPT | Redactó la especificación de los 6 agentes, sus reglas, estados y matriz de autonomía a partir de los requisitos del equipo. | El equipo respondió las preguntas de diseño y confirmó o descartó reglas (DEC-01 a DEC-27). Se copió al repo sin cambios. |
| Estructura del repositorio y documentación base (`docs/`, `.env.example`, `.gitignore`, `CLAUDE.md`) | Claude Code (Claude Opus) | Creó la estructura `src/`, la documentación inicial y la configuración segura sin secretos. | El README lo mantiene el equipo a mano; la IA no lo editó. |
| Decisiones de negocio posteriores (DEC-C01 a DEC-C16) | — (equipo) | La IA propuso las fórmulas de V y A y la escala de confianza cuando se le pidió «a su discreción», y señaló conflictos (C-01 a C-03). | La usuaria decidió: redondeo a 0,5, flota de 71 (10/5 propias, 40/16 subcontratadas), horarios, capacidades por tipo, la compensación del 50 % del tiempo sin agua en la demanda y la cobertura mínima del 80 %. |
| Sistema multiagente (A1–A4, A6), orquestación AutoGen, reglas deterministas, persistencia, adaptadores, CLI | Claude Code | Implementó el código, los datos simulados y las pruebas automatizadas (112 aprobadas). | Las reglas siguen el documento rev.4 y las decisiones del equipo. Los conflictos con el documento se consultaron antes de aplicarse. |
| Palabras clave (`docs/KEYWORDS.md`) | Claude Code | Amplió la lista con formas habladas y regionalismos panameños («pluma», «botando agua», «idan»). | El equipo definió los hashtags base: `#idaan`, `#sinagua`, `#faltadeagua`, `#tuberiarota`. |
| Diseño del frontend (`frontend/`: páginas, CSS, imágenes) | Herramienta no registrada en el repo (completar por el equipo) | — | Diseño visual del equipo (PR #1). |
| Conexión del frontend con la API, estadísticas, mapa Leaflet, comunidades, FAQ | Claude Code | Escribió el JavaScript (`js/api.js` y los scripts de las páginas) y la API FastAPI, conservando el diseño. Se verificó con capturas antes y después. | El equipo aprobó cada cambio visual (bloque FAQ, filtros con estados reales). El CSS no se modificó. |
| Observabilidad con Langfuse | Claude Code con la skill oficial `langfuse` (github.com/langfuse/skills) | Instrumentó las trazas siguiendo la guía de buenas prácticas, envió trazas reales y las auditó dos veces, corrigiendo lo detectado. | La usuaria creó el proyecto de Langfuse y puso las claves en `.env`. |
| Clasificación con IA en tiempo de ejecución | Claude (`claude-sonnet-5-5`) vía Claude Code | Contrasta la clasificación del Agente 1. Solo interpreta texto; si discrepa de las reglas, el caso va a revisión humana. | La usuaria decidió no usar créditos de la API: se usa la sesión de la app de escritorio (proveedor `claude_code`). |
| Grafo del código (`graphify-out/`) | Skill graphify (extracción AST, sin LLM) | Generó el mapa de módulos, dependencias y comunidades del código. | — |

**Revisión humana:** todo commit se hizo con autorización explícita de la usuaria. Ninguna credencial, dato personal real ni envío externo pasó por la IA. Las aprobaciones de planes desde el panel quedan marcadas como simuladas.

[Bitacora_de_prompts_equipo04 ChatGPT.docx](https://github.com/user-attachments/files/33598646/Bitacora_de_prompts_equipo04.ChatGPT.docx)


---

Entrega: tag de git `final-24h` sobre el último commit válido, al cumplirse la hora 24.
