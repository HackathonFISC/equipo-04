"""Función de control del supervisor humano (no es un agente). Registra decisiones; nunca marca nada como ejecutado."""

import hashlib

from water_coordinator.persistence.repository import Repositorio
from water_coordinator.schemas.models import DecisionSupervisor, Estado, PlanPropuesto, ahora
from water_coordinator.services.parametros import VERSION_REGLAS

ESTADO_POR_DECISION = {
    "aprobado": Estado.APROBADO,
    "rechazado": Estado.RECHAZADO,
    "cambios_solicitados": Estado.CAMBIOS_SOLICITADOS,
}


class ErrorAprobacion(ValueError):
    pass


def huella(plan: PlanPropuesto) -> str:
    return hashlib.sha256(plan.model_dump_json(exclude={"estado"}).encode()).hexdigest()


def registrar_decision(
    repo: Repositorio, id_plan: str, decision: str, supervisor: str, simulada: bool, motivo: str = ""
) -> DecisionSupervisor:
    plan = repo.obtener("plan", id_plan, PlanPropuesto)
    if plan is None:
        raise ErrorAprobacion(f"No existe el plan {id_plan}.")
    if plan.estado != Estado.PENDIENTE_APROBACION:
        raise ErrorAprobacion(f"El plan {id_plan} está '{plan.estado}', no pendiente de aprobación.")
    if decision not in ESTADO_POR_DECISION:
        raise ErrorAprobacion(f"Decisión no válida: {decision}.")
    if decision == "aprobado" and not plan.completo and not simulada:
        raise ErrorAprobacion("Un paquete incompleto no puede aprobarse en real (§3.3); solo en simulación de prueba.")
    if decision == "aprobado" and plan.tipo_aprobacion == "extraordinaria" and not motivo.strip():
        raise ErrorAprobacion("La aprobación extraordinaria (<80 %) exige justificación registrada (DEC-07).")

    dec = DecisionSupervisor(
        id_plan=id_plan, decision=decision, supervisor=supervisor, simulada=simulada, motivo=motivo,
        fecha=ahora(), version_reglas=VERSION_REGLAS, huella_plan=huella(plan),
        autenticacion="simulacion_de_prueba" if simulada else "no_verificada",
    )
    anterior = plan.estado
    plan.estado = ESTADO_POR_DECISION[decision]
    repo.guardar("decision", dec.id_decision, dec)
    repo.guardar("plan", plan.id_plan, plan)
    repo.registrar_evento(
        "supervisor", "decision", id_plan,
        {"decision": dec.model_dump(mode="json"), "estado_anterior": anterior, "estado_nuevo": plan.estado},
    )
    return dec
