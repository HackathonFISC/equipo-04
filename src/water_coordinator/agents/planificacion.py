"""Agente 4 — Planificación de Recursos (DOC §4.4). Nivel 0: propone; nunca asigna ni despacha."""

import math

from autogen_core import MessageContext, RoutedAgent, message_handler

from water_coordinator.schemas.models import Certeza, Estado, LotePlanes, PlanPropuesto, SolicitudAdicional, SolicitudPlanificacion
from water_coordinator.services.demanda import calcular_demanda, cobertura, tipo_aprobacion
from water_coordinator.services.parametros import CAPACIDAD_GAL, VERSION_REGLAS

RUTA_PENDIENTE = {
    "estado": "pendiente",
    "motivo": "Agente 5 fuera de la etapa 1; ubicación de la organización y punto de carga [PEND].",
}


def planificar(sol: SolicitudPlanificacion) -> list[PlanPropuesto]:
    """Asignación en orden de prioridad, sin reutilizar cisternas (A4-R12) ni superar el inventario (A4-R13)."""
    regs = {r.id_afectacion: r for r in sol.registros}
    ubic = {u.id_afectacion: u for u in sol.ubicaciones}
    libres = sorted(sol.disponibles, key=lambda c: -c.capacidad_galones)
    restante_solicitable = {s.origen: s.cantidad for s in sol.solicitables}
    demora = {s.origen: s.demora_minutos for s in sol.solicitables}
    planes = []
    for orden, pr in enumerate(sol.lista.prioridades, start=1):
        reg = regs[pr.id_afectacion]
        dem = calcular_demanda(reg)
        riesgos = ["Disponibilidad según horario [PROV]: parámetro de planificación, no confirmación de vehículos (A4-R11)."]
        riesgos += [f"Prioridad: {m}" for m in pr.motivo_revision]
        if reg.alerta_sanitaria:
            riesgos.append("Posible riesgo sanitario: antes de una operación real se debe validar fuente y potabilidad (A4-R16).")
        u = ubic.get(reg.id_afectacion)
        if u and u.estado_certeza != Certeza.CONFIRMADA:
            riesgos.append(f"Ubicación {u.estado_certeza.value}: la ruta solo podría ser provisional.")
        if reg.estado == Estado.PENDIENTE_REVISION:
            riesgos.append("El registro de la afectación está pendiente de revisión.")

        asignadas, solicitudes, entregable, cob, pendiente = [], [], None, None, None
        if dem.demanda_estimada_gal is not None:
            falta = dem.demanda_estimada_gal
            while falta > 0 and libres:
                c = libres.pop(0)
                asignadas.append(c)
                falta -= c.capacidad_galones
            entregable = min(dem.demanda_estimada_gal, sum(c.capacidad_galones for c in asignadas))
            cob = cobertura(entregable, dem.demanda_estimada_gal)
            pendiente = round(dem.demanda_estimada_gal - entregable, 2)
            if any(c.capacidad_es_supuesto for c in asignadas):
                riesgos.append("Capacidad concreta por unidad no documentada: se usa el mínimo del rango (A4-R15).")
            solicitudes = _solicitudes(pendiente, restante_solicitable, demora)
            if pendiente > 0 and not solicitudes:
                riesgos.append("Déficit sin posibilidad de solicitar más cisternas en este horario.")

        tipo = tipo_aprobacion(cob)
        faltantes = ["ruta (Agente 5)"] + [f"demanda: {f}" for f in dem.datos_faltantes]
        planes.append(PlanPropuesto(
            id_afectacion=reg.id_afectacion,
            creado_en=sol.momento,
            motivo=f"Orden recomendado {orden}: {reg.tipo_afectacion.value}, categoría {pr.categoria_instalacion.value}.",
            prioridad=pr,
            demanda=dem,
            volumen_entregable_gal=entregable,
            cobertura_pct=cob,
            volumen_pendiente_gal=pendiente,
            cisternas_asignadas=asignadas,
            solicitudes_adicionales=solicitudes,
            ruta=RUTA_PENDIENTE,
            tipo_aprobacion=tipo,
            riesgos_incertidumbres=riesgos,
            campos_faltantes=faltantes,
            completo=False,  # sin ruta el paquete no está listo (§3.3)
            estado=Estado.PENDIENTE_APROBACION if cob is not None else Estado.PENDIENTE_INFORMACION,
            version_reglas=VERSION_REGLAS,
        ))
    return planes


def _solicitudes(pendiente: float, restante: dict, demora: dict) -> list[SolicitudAdicional]:
    """Sugiere cuántas cisternas pedir (capacidad mínima Small, conservador). Es una recomendación pendiente de solicitud."""
    if pendiente <= 0:
        return []
    necesarias = math.ceil(pendiente / CAPACIDAD_GAL["small"][0])
    out = []
    for origen in ("organizacion", "subcontratada"):
        n = min(necesarias, restante.get(origen, 0))
        if n:
            out.append(SolicitudAdicional(cantidad=n, origen=origen, demora_minutos=demora[origen]))
            restante[origen] -= n
            necesarias -= n
    return out


class AgentePlanificacion(RoutedAgent):
    def __init__(self):
        super().__init__("Agente 4: planificación de recursos y demanda")

    @message_handler
    async def procesar(self, message: SolicitudPlanificacion, ctx: MessageContext) -> LotePlanes:
        return LotePlanes(planes=planificar(message))
