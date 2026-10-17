"""Agente 3 — Priorización (DOC §4.3). Cálculo determinista; el orden es una recomendación."""

from autogen_core import MessageContext, RoutedAgent, message_handler

from water_coordinator.schemas.models import Certeza, ListaPriorizada, SolicitudPriorizacion
from water_coordinator.services.prioridad import ordenar, priorizar


class AgentePriorizacion(RoutedAgent):
    def __init__(self, a_referencia: int = 1000):
        super().__init__("Agente 3: priorización de afectaciones")
        self.a_referencia = a_referencia

    @message_handler
    async def procesar(self, message: SolicitudPriorizacion, ctx: MessageContext) -> ListaPriorizada:
        regs = {r.id_afectacion: r for r in message.registros}
        ubic = {u.id_afectacion: u for u in message.ubicaciones}
        prioridades = []
        for r in message.registros:
            pr = priorizar(r, self.a_referencia)
            u = ubic.get(r.id_afectacion)
            if u and u.estado_certeza == Certeza.AMBIGUA and pr.nivel_jerarquia and pr.nivel_jerarquia < 5:
                pr.requiere_revision_humana = True
                pr.motivo_revision.append("Ubicación ambigua de una instalación crítica.")
            prioridades.append(pr)
        orden, empates = ordenar(prioridades, regs)
        for grupo in empates:
            for pr in orden:
                if pr.id_afectacion in grupo:
                    pr.requiere_revision_humana = True
                    pr.motivo_revision.append("Empate persistente tras desempate por días y personas (DEC-03).")
        return ListaPriorizada(prioridades=orden, empates=empates)
