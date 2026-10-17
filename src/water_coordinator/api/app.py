"""Aplicación FastAPI del panel del supervisor (solo para uso local).

Iniciar: uv run uvicorn water_coordinator.api.app:app --reload --host 127.0.0.1 --port 8000
Documentación interactiva: http://127.0.0.1:8000/docs
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from water_coordinator import __version__
from water_coordinator.api.rutas import router
from water_coordinator.config import Settings, get_settings
from water_coordinator.services.monitoreo import configurar_logs
from water_coordinator.services.observabilidad import crear_observabilidad

log = logging.getLogger(__name__)


def create_app(s: Settings | None = None) -> FastAPI:
    s = s or get_settings()

    @asynccontextmanager
    async def ciclo(app: FastAPI):
        configurar_logs(s)
        app.state.obs = crear_observabilidad(s)
        yield
        app.state.obs.vaciar()

    app = FastAPI(title="AquaAlerta · API del supervisor", version=__version__, lifespan=ciclo,
                  description="API local del prototipo. Sin autenticación: las decisiones se registran como simuladas.")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in s.cors_origins.split(",") if o.strip()],
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    @app.exception_handler(SQLAlchemyError)
    async def bd_no_disponible(request: Request, exc: SQLAlchemyError):
        log.error("Base de datos no disponible: %s", type(exc).__name__)
        return JSONResponse(status_code=503, content={"detail": "Base de datos no disponible."})

    @app.exception_handler(Exception)
    async def error_interno(request: Request, exc: Exception):
        log.error("Error no controlado en %s: %s", request.url.path, type(exc).__name__)
        return JSONResponse(status_code=500, content={"detail": "Error interno del servidor."})

    app.include_router(router)
    return app


app = create_app()
