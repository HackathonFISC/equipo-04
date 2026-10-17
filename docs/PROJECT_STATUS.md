# Estado del proyecto

**Fase actual:** construcción, etapa 1 (versión funcional mínima). Última actualización: 2026-10-17.

## Trabajo realizado

### 2026-10-16: preparación del repositorio

- Estructura `src/`, la documentación inicial, `.env.example`, `.gitignore` y `.claude/CLAUDE.md`.
- Commit `7c7f9c2`.

### 2026-10-17: construcción, etapa 1

- **Documento de criterios** rev.4 copiado sin cambios a `docs/AGENT_CRITERIA_AND_DECISION_RULES.md`.
- **Agentes AutoGen:**
  - A1 Ingesta: clasificación por palabras clave, fecha del incidente, datos reportados y duplicados; contraste opcional con el modelo de IA.
  - A2 Geolocalización: certeza explícita, distritos de Panamá Oeste y Nominatim opcional.
  - A3 Priorización: jerarquía; T, V y A redondeados a 0,5; P, rango si faltan datos, empates.
  - A4 Planificación: demanda 1/2/2 días, flota de 71 cisternas, horarios, cobertura y tipo de aprobación.
  - A6 Comunicación: plantillas de estado y de cobertura parcial; mensajería simulada.
- **Reglas del Agente 5** (clasificación de rutas, límite de 1.000 km, excepción) y adaptador OSRM, fuera del flujo de la etapa 1.
- **Función de control del supervisor:** aprobación, rechazo o cambios; simulada o real; nunca marca "ejecutado".
- **Persistencia:** SQLAlchemy sobre SQLite, preparada para PostgreSQL. Traza solo de adición y reportes originales inmutables.
- **Adaptadores sin credenciales:** modelo de IA (OpenAI, compatible con OpenAI/Ollama, Anthropic), Nominatim, OSRM, WhatsApp (simulado y Cloud API), Whisper local, Google STT, almacenamiento local y logs JSON con redacción de secretos.
- **CLI:** `demo`, `aprobar`, `estado` y `traza`.
- **Datos simulados:** `data/simulados/reportes.json`, 6 reportes con contactos ficticios `sim:*`.
- **Documentación nueva:** `KEYWORDS.md`, `API_SETUP.md`, `INTEGRATIONS.md` y `DEVELOPMENT.md`. Actualizados: `DECISIONS`, `ARCHITECTURE`, `TOOLING`, `ROADMAP`, `REQUIREMENTS` y `.claude/CLAUDE.md`.
- **Grafo del código** con graphify en `graphify-out/` (ver ARCHITECTURE.md).
- `frontend/` **no se tocó** (D-009). `README.md` no se tocó.
- Commit `ab881a0` (etapa 1).

### 2026-10-17: respuestas a los conflictos

- **DEC-C15:** demanda = diaria × (duración + 0,5 × días sin agua hasta el reporte).
- **DEC-C16:** Small 3.000–5.500 gal y Big 9.000–13.000 gal. Se planifica con el máximo; si el tipo no se conoce, con 5.500 gal.
- Pruebas y demo actualizadas. La versión de reglas pasa a `criterios-1.0-rev.4+dec-c16-2026-10-17`.

## Decisiones

- **Confirmadas:** D-001 a D-009 y DEC-C01 a DEC-C16 en [DECISIONS.md](DECISIONS.md).
- **Conflictos:**
  - C-01: resuelto con DEC-C15 (compensación de la mitad del tiempo sin agua en la demanda).
  - C-03: resuelto con DEC-C16 (rango de carga por tipo).
  - C-02: horarios reiterados por la usuaria; se mantienen.
- **Supuestos de prototipo:** P-001 a P-012.

## Dependencias instaladas (`.venv` local, no global)

| Grupo | Paquetes |
| --- | --- |
| Ejecución | `autogen-core` 0.7.5, `autogen-ext[openai,anthropic]` 0.7.5, `pydantic` 2.14, `pydantic-settings` 2.16, `sqlalchemy` 2.1.5, `httpx` |
| Desarrollo | `pytest` 9.1, `pytest-asyncio` 1.4 |
| Opcionales (no instalados) | `faster-whisper` (`transcripcion-local`), `google-cloud-speech` (`transcripcion-google`) |
| Herramienta externa | `graphifyy` 0.9.82, instalado con `uv tool` en el perfil del usuario (no en el proyecto) para generar el grafo |

## Comprobaciones ejecutadas (2026-10-17)

| Comprobación | Resultado |
| --- | --- |
| `uv sync` | OK, con `system-certs` por la intercepción TLS. |
| `uv run pytest -q` | **77 aprobadas, 5 omitidas** (integración sin credenciales), en unos 7 s (tras DEC-C15 y DEC-C16). |
| `uv run water-coordinator demo` (base temporal) | Flujo completo: 6 reportes → 5 afectaciones priorizadas (1 indeterminada retenida en A1) → 5 planes → 5 mensajes simulados (1 de cobertura parcial, al 98,5 %) → 5 aprobaciones simuladas registradas. |
| `uv run water-coordinator estado --comprobar` | Modelo de IA, geocodificación, rutas, transcripción y mapas: `NOT_CONFIGURED`. Mensajería simulada, base de datos y archivos: `CONFIGURED`. Monitoreo externo: `DISABLED`. Ninguno `CONNECTED`. |
| Servicios reales | **Ninguno probado:** no hay credenciales. |
| graphify (AST) | 347 nodos, 699 aristas, 19 comunidades. Aviso: 146 aristas a símbolos externos y 70 colapsadas. |

## Problemas encontrados

- **Primera ejecución de la suite:** quedó colgada más de 5 minutos. Al repetirla archivo por archivo y luego completa terminó en unos 7 s, y no se volvió a reproducir. La causa no está confirmada; lo más probable es la primera importación o compilación del entorno.
- **Nombres de handlers:** AutoGen exige que el parámetro del `message_handler` se llame `message`. Corregido.
- **Logs de AutoGen:** en nivel INFO incluían los mensajes completos, con contactos. Ahora se silencian en INFO.
- **Variables vacías:** las de `.env.example` rompían los campos numéricos. Corregido con `env_ignore_empty`.
- **Caché de graphify:** se creó una caché dentro de `src/`. Se eliminó y se añadió a `.gitignore`.

## Bloqueos

- El Agente 5 no puede entrar al flujo sin la ubicación de la organización ni los datos de autonomía.

## Próximos pasos

1. Confirmar la lectura de C-02 (19:00–20:00).
2. Incorporar DEC-C01 a DEC-C16 al documento de criterios (rev.5), si el equipo lo aprueba. DEC-C15 contradice DEC-01 del documento.
3. Elegir proveedor de IA (Ollama local es gratis) y configurar Nominatim.
4. Etapa 2: Agente 5 en el flujo e interfaz del supervisor en el frontend.
5. Ampliar las evals a 15 casos o más, con métrica (requisito de entrega).
