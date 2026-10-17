"""Orquestación con AutoGen (autogen-core): reporte → A1 → A2 → A3 → A4 → A6, con traza completa.

Los agentes no escriben en la base de datos ni modifican resultados ajenos: el orquestador persiste cada salida
validada y registra un evento por agente. La aprobación es una función de control aparte (services/aprobacion.py).
"""

from datetime import datetime

from autogen_core import AgentId, SingleThreadedAgentRuntime
from autogen_core.models import ChatCompletionClient
from pydantic import BaseModel

from water_coordinator.agents.comunicacion import AgenteComunicacion
from water_coordinator.agents.geolocalizacion import AgenteGeolocalizacion
from water_coordinator.agents.ingesta import AgenteIngesta
from water_coordinator.agents.planificacion import AgentePlanificacion
from water_coordinator.agents.priorizacion import AgentePriorizacion
from water_coordinator.persistence.repository import Repositorio
from water_coordinator.schemas.models import (
    Cisterna, ListaPriorizada, LoteMensajes, LotePlanes, LoteRegistros, LoteReportes, LoteUbicaciones, ReporteEntrada,
    SolicitudComunicacion, SolicitudPlanificacion, SolicitudPriorizacion, TipoAfectacion,
)
from water_coordinator.services.flota import disponibles_por_horario, solicitables
from water_coordinator.tools.geocoding import Geocodificador
from water_coordinator.tools.messaging import MessagingProvider, MockMessagingProvider


class ResultadoFlujo(BaseModel):
    registros: LoteRegistros
    ubicaciones: LoteUbicaciones
    prioridades: ListaPriorizada
    planes: LotePlanes
    mensajes: LoteMensajes
    envios: list[dict]


async def procesar(
    reportes: list[ReporteEntrada],
    repo: Repositorio,
    momento: datetime,
    horarios: dict,
    disponibles: list[Cisterna] | None = None,
    llm: ChatCompletionClient | None = None,
    nombre_modelo: str | None = None,
    geo: Geocodificador | None = None,
    mensajeria: MessagingProvider | None = None,
    a_referencia: int = 1000,
) -> ResultadoFlujo:
    for r in reportes:  # originales inmutables
        repo.insertar("reporte", r.id_reporte, r)
        repo.registrar_evento("sistema", "reporte_recibido", r.id_reporte, {"canal": r.canal})

    rt = SingleThreadedAgentRuntime()
    await AgenteIngesta.register(rt, "ingesta", lambda: AgenteIngesta(llm))
    await AgenteGeolocalizacion.register(rt, "geolocalizacion", lambda: AgenteGeolocalizacion(geo))
    await AgentePriorizacion.register(rt, "priorizacion", lambda: AgentePriorizacion(a_referencia))
    await AgentePlanificacion.register(rt, "planificacion", AgentePlanificacion)
    await AgenteComunicacion.register(rt, "comunicacion", AgenteComunicacion)
    rt.start()
    try:
        regs: LoteRegistros = await rt.send_message(LoteReportes(reportes=reportes), AgentId("ingesta", "default"))
        for r in regs.registros:
            repo.guardar("afectacion", r.id_afectacion, r)
            repo.registrar_evento("agente_1", "registro", r.id_afectacion, r.model_dump(mode="json"), modelo=nombre_modelo)

        # §3.3: solo pasan al Agente 2 los registros con tipo; los indeterminados quedan pendientes en el Agente 1.
        transferibles = LoteRegistros(registros=[r for r in regs.registros if r.tipo_afectacion != TipoAfectacion.INDETERMINADO])
        ubic: LoteUbicaciones = await rt.send_message(transferibles, AgentId("geolocalizacion", "default"))
        for u in ubic.ubicaciones:
            repo.guardar("ubicacion", u.id_afectacion, u)
            repo.registrar_evento("agente_2", "ubicacion", u.id_afectacion, u.model_dump(mode="json"))

        lista: ListaPriorizada = await rt.send_message(
            SolicitudPriorizacion(registros=transferibles.registros, ubicaciones=ubic.ubicaciones), AgentId("priorizacion", "default"))
        for pr in lista.prioridades:
            repo.guardar("prioridad", pr.id_afectacion, pr)
            repo.registrar_evento("agente_3", "prioridad", pr.id_afectacion, pr.model_dump(mode="json"))

        disp = disponibles if disponibles is not None else disponibles_por_horario(horarios, momento)
        sol = SolicitudPlanificacion(lista=lista, registros=transferibles.registros, ubicaciones=ubic.ubicaciones,
                                     disponibles=disp, solicitables=solicitables(horarios, momento, disp), momento=momento)
        planes: LotePlanes = await rt.send_message(sol, AgentId("planificacion", "default"))
        for p in planes.planes:
            repo.guardar("plan", p.id_plan, p)
            repo.registrar_evento("agente_4", "plan_propuesto", p.id_plan, p.model_dump(mode="json"))

        msgs: LoteMensajes = await rt.send_message(
            SolicitudComunicacion(registros=regs.registros, planes=planes.planes), AgentId("comunicacion", "default"))
    finally:
        await rt.stop()

    mensajeria = mensajeria or MockMessagingProvider()
    envios = []
    for m in msgs.mensajes:
        repo.guardar("mensaje", m.id_mensaje, m)
        envio = await mensajeria.enviar(m)
        envios.append(envio)
        repo.registrar_evento("agente_6", "mensaje", m.id_afectacion, {"mensaje": m.model_dump(mode="json"), "envio": envio})
    return ResultadoFlujo(registros=regs, ubicaciones=ubic, prioridades=lista, planes=planes, mensajes=msgs, envios=envios)
