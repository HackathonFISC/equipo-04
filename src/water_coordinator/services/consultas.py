"""Lecturas para el panel del supervisor. Combinan documentos ya persistidos; nunca ejecutan el pipeline.

Se excluyen contactos y textos originales de los reportes: el panel no los necesita para supervisar.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from water_coordinator.persistence.repository import Repositorio
from water_coordinator.services.territorio import catalogo
from water_coordinator.schemas.models import (
    Categoria, Certeza, Confianza, Coordenadas, DecisionSupervisor, Estado, MensajeSaliente, PlanPropuesto, Prioridad,
    RegistroAfectacion, ReporteEntrada, TipoAfectacion, UbicacionNormalizada,
)

CANALES_SIMULADOS = {"whatsapp_simulado", "archivo_prueba"}


class PlanResumen(BaseModel):
    id_plan: str
    estado: Estado
    tipo_aprobacion: str
    demanda_estimada_gal: float | None
    cobertura_pct: float | None
    cisternas_asignadas: int
    completo: bool
    campos_faltantes: list[str]
    ultima_decision: Literal["aprobado", "rechazado", "cambios_solicitados"] | None = None
    decision_simulada: bool | None = None


class IncidenteVista(BaseModel):
    id_afectacion: str
    id_reporte: str
    canal: str | None
    simulado: bool
    recibido_en: datetime
    tipo_afectacion: TipoAfectacion
    confianza_clasificacion: Confianza
    metodo_clasificacion: str
    estado_registro: Estado
    estado_actual: Estado  # el del plan si existe; si no, el del registro
    ubicacion_reportada: str | None
    zona: str | None = None  # distrito
    comunidad: str | None = None
    personas_estimadas: float | None = None
    certeza_ubicacion: Certeza | None = None
    coordenadas: Coordenadas | None = None  # solo si las dio el geocodificador; nunca inventadas
    categoria: Categoria | None = None
    nivel_jerarquia: int | None = None
    T: float | None = None
    V: float | None = None
    A: float | None = None
    P: float | None = None
    rango_P: tuple[float, float] | None = None
    requiere_revision_humana: bool = False
    alerta_sanitaria: bool
    plan: PlanResumen | None = None


class MensajeVista(BaseModel):
    id_mensaje: str
    id_afectacion: str
    id_plan: str | None
    tipo: Literal["estado", "cobertura_parcial"]
    texto: str
    estado_al_redactar: Estado
    estado_plan_actual: Estado | None
    envio: Literal["simulado_no_enviado"] = "simulado_no_enviado"


class EventoVista(BaseModel):
    seq: int
    fecha: str
    agente: str
    tipo: str
    ref_id: str | None
    version_reglas: str


def _por_afectacion(planes: list[PlanPropuesto]) -> dict[str, PlanPropuesto]:
    """Último plan de cada afectación (por fecha de creación)."""
    out: dict[str, PlanPropuesto] = {}
    for p in sorted(planes, key=lambda p: p.creado_en):
        out[p.id_afectacion] = p
    return out


def _ultimas_decisiones(repo: Repositorio) -> dict[str, DecisionSupervisor]:
    out: dict[str, DecisionSupervisor] = {}
    for d in sorted(repo.listar("decision", DecisionSupervisor), key=lambda d: d.fecha):
        out[d.id_plan] = d
    return out


def _resumen_plan(p: PlanPropuesto, decisiones: dict[str, DecisionSupervisor]) -> PlanResumen:
    d = decisiones.get(p.id_plan)
    return PlanResumen(
        id_plan=p.id_plan, estado=p.estado, tipo_aprobacion=p.tipo_aprobacion,
        demanda_estimada_gal=p.demanda.demanda_estimada_gal, cobertura_pct=p.cobertura_pct,
        cisternas_asignadas=len(p.cisternas_asignadas), completo=p.completo, campos_faltantes=p.campos_faltantes,
        ultima_decision=d.decision if d else None, decision_simulada=d.simulada if d else None,
    )


def listar_incidentes(repo: Repositorio, estado: Estado | None = None, tipo: TipoAfectacion | None = None) -> list[IncidenteVista]:
    reportes = {r.id_reporte: r for r in repo.listar("reporte", ReporteEntrada)}
    ubic = {u.id_afectacion: u for u in repo.listar("ubicacion", UbicacionNormalizada)}
    prio = {p.id_afectacion: p for p in repo.listar("prioridad", Prioridad)}
    planes = _por_afectacion(repo.listar("plan", PlanPropuesto))
    decisiones = _ultimas_decisiones(repo)
    out = []
    for r in repo.listar("afectacion", RegistroAfectacion):
        rep, u, pr, plan = reportes.get(r.id_reporte), ubic.get(r.id_afectacion), prio.get(r.id_afectacion), planes.get(r.id_afectacion)
        canal = rep.canal if rep else None
        v = IncidenteVista(
            id_afectacion=r.id_afectacion, id_reporte=r.id_reporte, canal=canal,
            simulado=canal in CANALES_SIMULADOS or (r.contacto or "").startswith("sim:"),
            recibido_en=r.fecha_hora_recepcion, tipo_afectacion=r.tipo_afectacion,
            confianza_clasificacion=r.confianza_clasificacion, metodo_clasificacion=r.metodo_clasificacion,
            estado_registro=r.estado, estado_actual=plan.estado if plan else r.estado,
            ubicacion_reportada=r.ubicacion_reportada, alerta_sanitaria=r.alerta_sanitaria,
            zona=u.zona_comunidad if u else None, comunidad=u.comunidad if u else None, certeza_ubicacion=u.estado_certeza if u else None,
            coordenadas=u.coordenadas if u else None,
            plan=_resumen_plan(plan, decisiones) if plan else None,
        )
        if pr:
            v = v.model_copy(update={
                "categoria": pr.categoria_instalacion, "nivel_jerarquia": pr.nivel_jerarquia, "T": pr.T, "V": pr.V,
                "A": pr.A, "P": pr.puntuacion_P, "personas_estimadas": pr.personas_estimadas, "rango_P": pr.rango_P, "requiere_revision_humana": pr.requiere_revision_humana,
            })
        if (estado is None or v.estado_actual == estado) and (tipo is None or v.tipo_afectacion == tipo):
            out.append(v)
    return sorted(out, key=lambda v: v.recibido_en, reverse=True)


def listar_mensajes(repo: Repositorio) -> list[MensajeVista]:
    planes = _por_afectacion(repo.listar("plan", PlanPropuesto))
    out = []
    for m in repo.listar("mensaje", MensajeSaliente):
        plan = planes.get(m.id_afectacion)
        out.append(MensajeVista(
            id_mensaje=m.id_mensaje, id_afectacion=m.id_afectacion, id_plan=plan.id_plan if plan else None,
            tipo=m.tipo, texto=m.texto, estado_al_redactar=m.estado_referido,
            estado_plan_actual=plan.estado if plan else None,
        ))
    return out


def listar_eventos(repo: Repositorio, limite: int) -> list[EventoVista]:
    """Últimos eventos de traza, sin su contenido (que puede incluir contactos)."""
    # shortcut: lee toda la tabla y recorta en memoria; paginar en SQL si la traza crece.
    eventos = repo.eventos()[-limite:]
    return [EventoVista(seq=e["seq"], fecha=e["fecha"], agente=e["agente"], tipo=e["tipo"], ref_id=e["ref_id"],
                        version_reglas=e["version_reglas"]) for e in reversed(eventos)]


class ComunidadVista(BaseModel):
    comunidad: str
    distrito: str
    incidentes: int
    estado_reciente: Estado | None  # estado actual del incidente más reciente; None si no hay reportes
    tipos: list[TipoAfectacion]
    personas_estimadas: float | None  # suma de las estimaciones del Agente 3 (promedios de ocupación)
    ultima_actualizacion: datetime | None


def listar_comunidades(repo: Repositorio) -> list[ComunidadVista]:
    """Catálogo territorial con los incidentes procesados que el Agente 2 asoció a cada comunidad."""
    incidentes = listar_incidentes(repo)  # ya ordenados del más reciente al más antiguo
    out = []
    for c in catalogo():
        propios = [i for i in incidentes if i.comunidad == c["comunidad"] and i.zona == c["distrito"]]
        personas = [i.personas_estimadas for i in propios if i.personas_estimadas is not None]
        out.append(ComunidadVista(
            comunidad=c["comunidad"], distrito=c["distrito"], incidentes=len(propios),
            estado_reciente=propios[0].estado_actual if propios else None,
            tipos=sorted({i.tipo_afectacion for i in propios}, key=list(TipoAfectacion).index),
            personas_estimadas=sum(personas) if personas else None,
            ultima_actualizacion=propios[0].recibido_en if propios else None,
        ))
    return out
