"""Agente 6 — Comunicación y Seguimiento (DOC §4.6). Solo usa datos registrados; nunca confirma entregas."""

from autogen_core import MessageContext, RoutedAgent, message_handler

from water_coordinator.schemas.models import Estado, LoteMensajes, MensajeSaliente, PlanPropuesto, RegistroAfectacion, SolicitudComunicacion

ESTADO_LEGIBLE = {
    Estado.PENDIENTE_APROBACION: "propuesto y pendiente de aprobación del supervisor",
    Estado.PENDIENTE_INFORMACION: "pendiente de información",
    Estado.APROBADO: "aprobado (aún no ejecutado)",
    Estado.RECHAZADO: "rechazado por el supervisor",
    Estado.CAMBIOS_SOLICITADOS: "en revisión: el supervisor solicitó cambios",
}
TIPO_LEGIBLE = {"falta_de_agua": "falta de agua", "tuberia_rota": "tubería rota", "agua_contaminada": "agua contaminada",
                "indeterminado": "afectación sin tipo determinado"}


def mensaje_cobertura_parcial(plan: PlanPropuesto, reg: RegistroAfectacion) -> str:
    """Los cinco elementos de REQ §9 / A6-R4."""
    zona = reg.ubicacion_reportada or plan.id_afectacion
    return (
        f"Para la afectación {plan.id_afectacion} ({zona}), el plan PROPUESTO prevé un suministro PARCIAL de aproximadamente "
        f"{plan.volumen_entregable_gal:,.0f} galones, equivalente al {plan.cobertura_pct:.0f} % de la necesidad estimada de "
        f"{plan.demanda.demanda_estimada_gal:,.0f} galones. Quedarían pendientes unos {plan.volumen_pendiente_gal:,.0f} galones. "
        "Este plan está pendiente de aprobación y no constituye una confirmación de entrega."
    )


def mensaje_estado(plan: PlanPropuesto | None, reg: RegistroAfectacion) -> str:
    estado = plan.estado if plan else reg.estado
    texto = (f"Reporte registrado como {TIPO_LEGIBLE[reg.tipo_afectacion.value]} (ref. {reg.id_afectacion}). "
             f"Estado: {ESTADO_LEGIBLE.get(estado, estado.value.replace('_', ' '))}.")
    if estado == Estado.PENDIENTE_INFORMACION and reg.datos_faltantes:
        texto += " Nos ayudaría saber: " + ", ".join(f.replace("_", " ") for f in reg.datos_faltantes) + "."
    if reg.alerta_sanitaria:
        texto += " La calidad del agua no ha sido validada por las autoridades competentes."  # A6-R10
    return texto + " No hay hora de llegada confirmada."  # A6-R5


def redactar(sol: SolicitudComunicacion) -> list[MensajeSaliente]:
    planes = {p.id_afectacion: p for p in sol.planes}
    out = []
    for reg in sol.registros:
        if not reg.contacto:
            continue
        plan = planes.get(reg.id_afectacion)
        parcial = plan is not None and plan.tipo_aprobacion == "cobertura_parcial" and plan.estado == Estado.PENDIENTE_APROBACION
        out.append(MensajeSaliente(
            id_afectacion=reg.id_afectacion, destinatario=reg.contacto,
            texto=mensaje_cobertura_parcial(plan, reg) if parcial else mensaje_estado(plan, reg),
            tipo="cobertura_parcial" if parcial else "estado", estado_referido=plan.estado if plan else reg.estado,
        ))
    return out


class AgenteComunicacion(RoutedAgent):
    def __init__(self):
        super().__init__("Agente 6: comunicación y seguimiento")

    @message_handler
    async def procesar(self, message: SolicitudComunicacion, ctx: MessageContext) -> LoteMensajes:
        return LoteMensajes(mensajes=redactar(message))
