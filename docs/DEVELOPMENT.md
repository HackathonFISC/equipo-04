# Desarrollo en Windows

## Requisitos

- **uv** (probado con 0.12.23). Gestiona Python: el proyecto usa CPython 3.14.8 instalado por uv.
- **Git.**
- No uses `python` ni `py` directamente: en esta máquina `python` no está en el PATH y `py` apunta a 3.4. Usa siempre `uv run …`.
- **Certificados TLS:** un antivirus o proxy intercepta TLS. `pyproject.toml` ya trae `[tool.uv] system-certs = true`, que es local al proyecto. Fuera del proyecto, añade `--system-certs` o define `UV_SYSTEM_CERTS=1`.

## Instalación

```bash
uv sync
```

Esto instala las dependencias en `.venv/` local, sin tocar nada global. Extras opcionales:

```bash
uv sync --extra transcripcion-local    # Whisper local (faster-whisper)
uv sync --extra transcripcion-google   # Google Speech-to-Text
```

## Configuración

Copia `.env.example` a `.env` y completa solo lo que vayas a activar. Sin `.env`, todo funciona en modo simulado. Detalles por proveedor en [API_SETUP.md](API_SETUP.md).

## Ejecutar

```bash
uv run water-coordinator demo
uv run water-coordinator demo --sin-aprobacion
uv run water-coordinator aprobar PLAN-xxxx --decision aprobado --supervisor "Nombre" --simulada
uv run water-coordinator estado
uv run water-coordinator estado --comprobar
uv run water-coordinator traza PLAN-xxxx
```

| Comando | Qué hace |
| --- | --- |
| `demo` | Flujo completo con `data/simulados/reportes.json` y aprobación simulada de prueba. |
| `demo --sin-aprobacion` | Igual, pero deja los planes pendientes de aprobación. |
| `aprobar … --simulada` | Registra la decisión del supervisor sobre un plan. |
| `estado` | Estado de las integraciones. |
| `estado --comprobar` | Igual, con llamadas reales a los servicios configurados. |
| `traza PLAN-xxxx` | Eventos registrados para ese id (o para un `AFE-…`). |

La base SQLite queda en `storage/water.db`, que está ignorada por git. Para una base temporal:

```bash
DATABASE_URL=sqlite:///C:/ruta/temporal.db uv run water-coordinator demo
```

## API y panel del supervisor (local)

Se usan dos terminales, ambas desde la raíz del repo.

1. **Backend (API FastAPI):**

   ```bash
   uv run uvicorn water_coordinator.api.app:app --reload --host 127.0.0.1 --port 8000
   ```

   - Salud: http://127.0.0.1:8000/health
   - Documentación interactiva (Swagger): **http://127.0.0.1:8000/docs**
2. **Frontend (archivos estáticos):**

   ```bash
   uv run python -m http.server 5500 --bind 127.0.0.1 -d frontend
   ```

   Abrir http://127.0.0.1:5500/admin.html y http://127.0.0.1:5500/gestion.html. Abrirlos como `file://` **no funciona**: el navegador bloquea las peticiones y CORS solo permite `http://127.0.0.1:5500` y `http://localhost:5500` (`CORS_ORIGINS`).
3. **Datos de prueba:** la base empieza vacía, así que hay que cargar datos de una de estas dos formas:
   - Con el demo, sin llamadas externas:

     ```bash
     MODEL_PROVIDER=none GEOCODER_PROVIDER=none uv run water-coordinator demo --sin-aprobacion
     ```

     En PowerShell, define antes las variables con `$env:MODEL_PROVIDER="none"; $env:GEOCODER_PROVIDER="none"`. Estos datos van marcados como simulados.
   - Con `POST /api/incidents` desde `/docs`.

En VS Code o en la app de Claude, `.claude/launch.json` define las configuraciones `api` y `frontend` con estos mismos comandos.

| Endpoint | Uso |
| --- | --- |
| `GET /health` | Estado de la API, la base de datos y Langfuse. |
| `GET /api/incidents?estado=&tipo=` | Afectaciones procesadas, con prioridad y plan. Sin contactos ni textos originales. |
| `POST /api/incidents` | Registra un reporte (canal de prueba) y ejecuta el pipeline para ese reporte. |
| `GET /api/messages` | Mensajes propuestos por el Agente 6 (`envio: simulado_no_enviado`) y el estado actual de su plan. |
| `GET /api/faq` | Preguntas frecuentes del panel. |
| `GET /api/agent-events?limite=20` | Últimos eventos de traza de los agentes (sin su contenido). |
| `POST /api/plans/{id}/decision` | Decisión del supervisor. **Siempre se registra como simulada**: no hay autenticación. |

**La API no tiene autenticación.** Solo escucha en `127.0.0.1`: no la expongas a la red.

## Pruebas

```bash
uv run pytest -q
```

No necesitan credenciales ni Internet. Las de integración se omiten salvo que actives su variable `RUN_INTEGRATION_*`; ver [INTEGRATIONS.md](INTEGRATIONS.md).

## Grafo del código (graphify)

En Claude Code, con la skill graphify instalada: `/graphify src/water_coordinator --update`. Regenera `graphify-out/` después de cambiar el código; ver [ARCHITECTURE.md](ARCHITECTURE.md#grafo-del-código-graphify).

## Langfuse (opcional)

Se activa en `.env` con `LANGFUSE_TRACING_ENABLED=true` y las claves del proyecto; los detalles están en [API_SETUP.md](API_SETUP.md#10-observabilidad-langfuse). Para comprobar que funciona:

```bash
uv run water-coordinator demo
```

La salida incluye `"langfuse": "activo"` y un `id_ejecucion`. En el proyecto de Langfuse aparecerá la traza `water-coordinator.pipeline`, con la sesión igual a ese `id_ejecucion` y observaciones para A1, A2, A3, A4 y A6.
