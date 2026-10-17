"""Endpoints HTTP del panel del supervisor. Solo traducen HTTP ↔ servicios existentes; no contienen reglas de negocio."""

from datetime import datetime
from functools import lru_cache
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import text

from water_coordinator import __version__
from water_coordinator.config import Settings, get_settings
from water_coordinator.orchestration.pipeline import procesar_configurado
from water_coordinator.persistence.repository import ErrorPersistencia, Repositorio
from water_coordinator.schemas.models import DecisionSupervisor, Estado, ReporteEntrada, TipoAfectacion, ahora
from water_coordinator.services.aprobacion import ErrorAprobacion, registrar_decision
from water_coordinator.services.consultas import (
    ComunidadVista, EventoVista, IncidenteVista, MensajeVista, listar_comunidades, listar_eventos, listar_incidentes,
    listar_mensajes,
)
from water_coordinator.services.faq import FAQ
from water_coordinator.services.observabilidad import Observabilidad

router = APIRouter()


@lru_cache
def _repo(url: str) -> Repositorio:
    return Repositorio(url)


def get_repo(s: Settings = Depends(get_settings)) -> Repositorio:
    return _repo(s.database_url)


def get_obs(request: Request) -> Observabilidad:
    return getattr(request.app.state, "obs", None) or Observabilidad(None)


# ---------- Contratos HTTP (envuelven los modelos existentes) ----------


class Lista[T](BaseModel):
    total: int
    items: list[T]


class Faq(BaseModel):
    pregunta: str
    respuesta: str


class ReporteNuevo(BaseModel):
    """Reporte que llega a la API. Mismos canales que `ReporteEntrada`; no se aceptan campos extra."""

    model_config = ConfigDict(extra="forbid")
    id_reporte: str | None = Field(default=None, pattern=r"^[A-Za-z0-9\-]{3,64}$",
                                   description="Opcional. Si se repite, se rechaza para no duplicar el reporte.")
    canal: Literal["whatsapp_simulado", "transcripcion_audio", "transcripcion_video", "archivo_prueba"]
    texto: str = Field(min_length=1, max_length=2000)
    recibido_en: datetime | None = Field(default=None, description="Por defecto, ahora (hora de Panamá).")
    contacto: str | None = Field(default=None, max_length=40, description="Único dato personal previsto (DEC-21).")


class ResultadoRegistro(BaseModel):
    id_ejecucion: str
    id_reporte: str
    afectaciones: list[dict]
    planes: list[dict]
    advertencia: str


class DecisionPanel(BaseModel):
    """Decisión desde el panel. Siempre se registra como simulada: no hay autenticación del supervisor."""

    model_config = ConfigDict(extra="forbid")
    decision: Literal["aprobado", "rechazado", "cambios_solicitados"]
    supervisor: str = Field(min_length=1, max_length=80)
    motivo: str = Field(default="", max_length=500)


# ---------- Endpoints ----------


@router.get("/health", tags=["sistema"])
def health(repo: Repositorio = Depends(get_repo), obs: Observabilidad = Depends(get_obs)) -> dict:
    try:
        with repo.engine.connect() as c:
            c.execute(text("SELECT 1"))
        bd = "ok"
    except Exception:  # noqa: BLE001 — sin detalles internos en la respuesta
        bd = "no_disponible"
    return {"status": "ok" if bd == "ok" else "degradado", "version": __version__, "base_de_datos": bd,
            "langfuse": "activo" if obs.activa else "desactivado"}


@router.get("/api/incidents", tags=["panel"])
def incidentes(
    estado: Estado | None = Query(None, description="Filtra por el estado actual (del plan si existe)."),
    tipo: TipoAfectacion | None = Query(None),
    repo: Repositorio = Depends(get_repo),
) -> Lista[IncidenteVista]:
    items = listar_incidentes(repo, estado, tipo)
    return Lista(total=len(items), items=items)


@router.post("/api/incidents", status_code=201, tags=["panel"])
async def registrar_incidente(body: ReporteNuevo, repo: Repositorio = Depends(get_repo),
                              s: Settings = Depends(get_settings), obs: Observabilidad = Depends(get_obs)) -> ResultadoRegistro:
    datos = body.model_dump(exclude_none=True)
    datos.setdefault("recibido_en", ahora())
    reporte = ReporteEntrada(**datos)
    try:
        res = await procesar_configurado(s, [reporte], repo, reporte.recibido_en, obs, origen="api")
    except ErrorPersistencia:
        raise HTTPException(409, f"El reporte {reporte.id_reporte} ya existe; no se duplica.")
    finally:
        obs.vaciar()
    return ResultadoRegistro(
        id_ejecucion=res.id_ejecucion, id_reporte=reporte.id_reporte,
        afectaciones=[{"id_afectacion": r.id_afectacion, "tipo_afectacion": r.tipo_afectacion, "estado": r.estado}
                      for r in res.registros.registros],
        planes=[{"id_plan": p.id_plan, "estado": p.estado, "tipo_aprobacion": p.tipo_aprobacion, "cobertura_pct": p.cobertura_pct}
                for p in res.planes.planes],
        advertencia="Cada reporte se planifica en su propio lote: el Agente 4 no conoce las cisternas asignadas en "
                    "lotes anteriores (limitación documentada).",
    )


@router.get("/api/communities", tags=["panel"])
def comunidades(repo: Repositorio = Depends(get_repo)) -> Lista[ComunidadVista]:
    """Catálogo de comunidades de La Chorrera y Arraiján con sus incidentes procesados."""
    items = listar_comunidades(repo)
    return Lista(total=len(items), items=items)


@router.get("/api/messages", tags=["panel"])
def mensajes(repo: Repositorio = Depends(get_repo)) -> Lista[MensajeVista]:
    items = listar_mensajes(repo)
    return Lista(total=len(items), items=items)


@router.get("/api/faq", tags=["panel"])
def faq() -> Lista[Faq]:
    return Lista(total=len(FAQ), items=[Faq(**f) for f in FAQ])


@router.get("/api/agent-events", tags=["panel"])
def eventos(limite: int = Query(20, ge=1, le=200), repo: Repositorio = Depends(get_repo)) -> Lista[EventoVista]:
    items = listar_eventos(repo, limite)
    return Lista(total=len(items), items=items)


@router.post("/api/plans/{id_plan}/decision", tags=["panel"])
def decidir(id_plan: str, body: DecisionPanel, repo: Repositorio = Depends(get_repo)) -> DecisionSupervisor:
    try:
        return registrar_decision(repo, id_plan, body.decision, body.supervisor, simulada=True, motivo=body.motivo)
    except ErrorAprobacion as e:
        raise HTTPException(404 if "No existe" in str(e) else 409, str(e))
