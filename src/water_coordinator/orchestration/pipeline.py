"""Orquestación con AutoGen (autogen-core): reporte → A1 → A2 → A3 → A4 → A6, con traza completa.

Los agentes no escriben en la base de datos ni modifican resultados ajenos: el orquestador persiste cada salida
validada y registra un evento por agente. La aprobación es una función de control aparte (services/aprobacion.py).
Cada ejecución tiene un `id_ejecucion` que enlaza la traza local con la traza de Langfuse (si está activada).
"""

from collections import Counter
from datetime import datetime

from autogen_core import AgentId, SingleThreadedAgentRuntime
from opentelemetry.trace import NoOpTracerProvider
from autogen_core.models import ChatCompletionClient
from pydantic import BaseModel

from water_coordinator.agents.comunicacion import AgenteComunicacion
from water_coordinator.config import Settings
from water_coordinator.services.parametros import cargar_horarios
from water_coordinator.tools import geocoding, llm
from water_coordinator.agents.geolocalizacion import AgenteGeolocalizacion
from water_coordinator.agents.ingesta import AgenteIngesta
from water_coordinator.agents.planificacion import AgentePlanificacion
from water_coordinator.agents.priorizacion import AgentePriorizacion
from water_coordinator.persistence.repository import Repositorio
from water_coordinator.schemas.models import (
    Cisterna, ListaPriorizada, LoteMensajes, LotePlanes, LoteRegistros, LoteReportes, LoteUbicaciones, ReporteEntrada,
    SolicitudComunicacion, SolicitudPlanificacion, SolicitudPriorizacion, TipoAfectacion,
)
from water_coordinator.schemas.models import nuevo_id
from water_coordinator.services.flota import disponibles_por_horario, solicitables
from water_coordinator.services.observabilidad import ETAPAS, Observabilidad
from water_coordinator.services.parametros import VERSION_REGLAS
from water_coordinator.tools.geocoding import Geocodificador
from water_coordinator.tools.messaging import MessagingProvider, MockMessagingProvider


class ResultadoFlujo(BaseModel):
    id_ejecucion: str
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
    obs: Observabilidad | None = None,
    origen: str = "cli-demo",
    modelo: str | None = None,
) -> ResultadoFlujo:
    obs = obs or Observabilidad(None)
    id_ejecucion = nuevo_id("EJE")
    for r in reportes:  # originales inmutables
        repo.insertar("reporte", r.id_reporte, r)
        repo.registrar_evento("sistema", "reporte_recibido", r.id_reporte, {"canal": r.canal, "id_ejecucion": id_ejecucion})

    meta = {"n_reportes": str(len(reportes)), "modelo_ia": nombre_modelo or "ninguno",
            "geocodificador": getattr(geo, "nombre", "ninguno")}
    # Entrada de la traza: qué llegó (sin textos ni contactos). Salida: qué propuso el sistema para cada afectación.
    entrada = {"reportes": len(reportes), "canales": dict(Counter(r.canal for r in reportes)),
               "momento_planificacion": momento.isoformat()}
    with obs.ejecucion(id_ejecucion, VERSION_REGLAS, origen, meta, entrada) as traza:
        res = await _ejecutar(id_ejecucion, reportes, repo, momento, horarios, disponibles, llm, nombre_modelo, geo,
                              mensajeria, a_referencia, obs, modelo)
        planes = {p.id_afectacion: p for p in res.planes.planes}
        traza.resultado({
            "afectaciones": [{"id_afectacion": r.id_afectacion, "tipo": r.tipo_afectacion.value,
                              "estado": (planes[r.id_afectacion].estado if r.id_afectacion in planes else r.estado).value,
                              "cobertura_pct": planes[r.id_afectacion].cobertura_pct if r.id_afectacion in planes else None,
                              "tipo_aprobacion": planes[r.id_afectacion].tipo_aprobacion if r.id_afectacion in planes else None}
                             for r in res.registros.registros],
            "mensajes_simulados": len(res.mensajes.mensajes),
            "requieren_aprobacion": sum(1 for p in res.planes.planes if p.estado.value == "pendiente_de_aprobacion"),
        })
    return res


async def _ejecutar(id_ejecucion, reportes, repo, momento, horarios, disponibles, llm, nombre_modelo, geo, mensajeria,
                    a_referencia, obs: Observabilidad, modelo: str | None) -> ResultadoFlujo:
    # Sin trazas internas de AutoGen: evitan duplicar la traza y llevan el contenido completo de los mensajes.
    rt = SingleThreadedAgentRuntime(tracer_provider=NoOpTracerProvider())
    await AgenteIngesta.register(rt, "ingesta", lambda: AgenteIngesta(llm, obs, modelo))
    await AgenteGeolocalizacion.register(rt, "geolocalizacion", lambda: AgenteGeolocalizacion(geo))
    await AgentePriorizacion.register(rt, "priorizacion", lambda: AgentePriorizacion(a_referencia))
    await AgentePlanificacion.register(rt, "planificacion", AgentePlanificacion)
    await AgenteComunicacion.register(rt, "comunicacion", AgenteComunicacion)
    rt.start()
    try:
        with obs.etapa(ETAPAS["A1"], {"reportes": len(reportes), "canales": dict(Counter(r.canal for r in reportes))}) as et:
            regs: LoteRegistros = await rt.send_message(LoteReportes(reportes=reportes), AgentId("ingesta", "default"))
            et.resultado(_conteo(regs.registros, "tipo_afectacion", "estado", "confianza_clasificacion"),
                         modelo_ia=nombre_modelo or "ninguno")
        for r in regs.registros:
            repo.guardar("afectacion", r.id_afectacion, r)
            repo.registrar_evento("agente_1", "registro", r.id_afectacion, r.model_dump(mode="json"), modelo=nombre_modelo)

        # §3.3: solo pasan al Agente 2 los registros con tipo; los indeterminados quedan pendientes en el Agente 1.
        transferibles = LoteRegistros(registros=[r for r in regs.registros if r.tipo_afectacion != TipoAfectacion.INDETERMINADO])
        with obs.etapa(ETAPAS["A2"], {"registros": len(transferibles.registros),
                                      "geocodificador": getattr(geo, "nombre", "ninguno")}) as et:
            ubic: LoteUbicaciones = await rt.send_message(transferibles, AgentId("geolocalizacion", "default"))
            et.resultado(_conteo(ubic.ubicaciones, "estado_certeza", "estado"))
        for u in ubic.ubicaciones:
            repo.guardar("ubicacion", u.id_afectacion, u)
            repo.registrar_evento("agente_2", "ubicacion", u.id_afectacion, u.model_dump(mode="json"))

        with obs.etapa(ETAPAS["A3"], {"registros": len(transferibles.registros)}) as et:
            lista: ListaPriorizada = await rt.send_message(
                SolicitudPriorizacion(registros=transferibles.registros, ubicaciones=ubic.ubicaciones),
                AgentId("priorizacion", "default"))
            et.resultado({"orden": [{"id": pr.id_afectacion, "categoria": pr.categoria_instalacion.value,
                                     "nivel": pr.nivel_jerarquia, "T": pr.T, "V": pr.V, "A": pr.A, "P": pr.puntuacion_P,
                                     "completo": pr.completo, "revision": pr.requiere_revision_humana}
                                    for pr in lista.prioridades], "empates": len(lista.empates)})
        for pr in lista.prioridades:
            repo.guardar("prioridad", pr.id_afectacion, pr)
            repo.registrar_evento("agente_3", "prioridad", pr.id_afectacion, pr.model_dump(mode="json"))

        disp = disponibles if disponibles is not None else disponibles_por_horario(horarios, momento)
        sol = SolicitudPlanificacion(lista=lista, registros=transferibles.registros, ubicaciones=ubic.ubicaciones,
                                     disponibles=disp, solicitables=solicitables(horarios, momento, disp), momento=momento)
        with obs.etapa(ETAPAS["A4"], {"afectaciones": len(lista.prioridades), "cisternas_disponibles": len(disp)}) as et:
            planes: LotePlanes = await rt.send_message(sol, AgentId("planificacion", "default"))
            et.resultado({"planes": [{"id_plan": p.id_plan, "id_afectacion": p.id_afectacion,
                                      "demanda_gal": p.demanda.demanda_estimada_gal, "cobertura_pct": p.cobertura_pct,
                                      "tipo_aprobacion": p.tipo_aprobacion, "estado": p.estado.value,
                                      "cisternas": len(p.cisternas_asignadas)} for p in planes.planes]})
        for p in planes.planes:
            repo.guardar("plan", p.id_plan, p)
            repo.registrar_evento("agente_4", "plan_propuesto", p.id_plan, p.model_dump(mode="json"))

        with obs.etapa(ETAPAS["A6"], {"planes": len(planes.planes)}) as et:
            msgs: LoteMensajes = await rt.send_message(
                SolicitudComunicacion(registros=regs.registros, planes=planes.planes), AgentId("comunicacion", "default"))
            et.resultado({**_conteo(msgs.mensajes, "tipo"), "envio": "simulado_no_enviado"})
    finally:
        await rt.stop()

    mensajeria = mensajeria or MockMessagingProvider()
    envios = []
    for m in msgs.mensajes:
        repo.guardar("mensaje", m.id_mensaje, m)
        envio = await mensajeria.enviar(m)
        envios.append(envio)
        repo.registrar_evento("agente_6", "mensaje", m.id_afectacion, {"mensaje": m.model_dump(mode="json"), "envio": envio})
    return ResultadoFlujo(id_ejecucion=id_ejecucion, registros=regs, ubicaciones=ubic, prioridades=lista, planes=planes, mensajes=msgs, envios=envios)


async def procesar_configurado(s: Settings, reportes: list[ReporteEntrada], repo: Repositorio, momento: datetime,
                               obs: Observabilidad | None = None, origen: str = "cli-demo") -> ResultadoFlujo:
    """El pipeline con los proveedores configurados en Settings (CLI y API). La mensajería siempre es simulada."""
    return await procesar(
        reportes, repo, momento, cargar_horarios(s.horarios_file), llm=llm.crear_cliente(s), nombre_modelo=llm.nombre_modelo(s),
        geo=geocoding.crear_geocodificador(s), mensajeria=MockMessagingProvider(), a_referencia=s.a_personas_referencia, obs=obs,
        origen=origen, modelo=s.model_name or None,
    )


def _conteo(objetos: list, *campos: str) -> dict:
    """Resumen sin datos personales: cuántos objetos hay por valor de cada campo."""
    return {"total": len(objetos)} | {c: dict(Counter(str(getattr(o, c)) for o in objetos)) for c in campos}
