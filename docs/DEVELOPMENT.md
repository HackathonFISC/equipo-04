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

## Pruebas

```bash
uv run pytest -q
```

No necesitan credenciales ni Internet. Las de integración se omiten salvo que actives su variable `RUN_INTEGRATION_*`; ver [INTEGRATIONS.md](INTEGRATIONS.md).

## Grafo del código (graphify)

En Claude Code, con la skill graphify instalada: `/graphify src/water_coordinator --update`. Regenera `graphify-out/` después de cambiar el código; ver [ARCHITECTURE.md](ARCHITECTURE.md#grafo-del-código-graphify).
