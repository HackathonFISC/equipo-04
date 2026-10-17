"""Flujo completo con datos simulados, aprobación simulada, trazabilidad y Agente 6."""

import json
from pathlib import Path

import pytest

from conftest import RECIBIDO, registro, reporte
from water_coordinator.agents.comunicacion import mensaje_cobertura_parcial, mensaje_estado
from water_coordinator.main import demo
from water_coordinator.orchestration.pipeline import procesar
from water_coordinator.persistence.repository import ErrorPersistencia
from water_coordinator.schemas.models import Estado, ReporteEntrada
from water_coordinator.services.aprobacion import ErrorAprobacion, registrar_decision
from water_coordinator.services.parametros import HORARIOS_POR_DEFECTO, VERSION_REGLAS
from water_coordinator.tools.messaging import MockMessagingProvider

DATOS = Path(__file__).parents[1] / "data/simulados/reportes.json"


async def _flujo(repo, textos):
    mock = MockMessagingProvider()
    res = await procesar([reporte(t) for t in textos], repo, RECIBIDO, HORARIOS_POR_DEFECTO, mensajeria=mock)
    return res, mock


async def test_flujo_completo_trazable(repo):
    res, mock = await _flujo(repo, ["#sinagua en la escuela de Capira desde ayer", "¿A qué hora abren la oficina?"])
    assert len(res.registros.registros) == 2
    assert len(res.planes.planes) == 1  # el indeterminado no pasa a planificación
    plan = res.planes.planes[0]
    assert plan.estado == Estado.PENDIENTE_APROBACION and plan.version_reglas == VERSION_REGLAS
    agentes = {e["agente"] for e in repo.eventos()}
    assert {"sistema", "agente_1", "agente_2", "agente_3", "agente_4", "agente_6"} <= agentes
    assert all(not e["enviado_externamente"] for e in res.envios) and len(mock.bandeja) == 2


async def test_aprobacion_simulada_registrada_y_nunca_ejecutada(repo):
    res, _ = await _flujo(repo, ["#sinagua en la escuela de Capira desde ayer"])
    plan = res.planes.planes[0]
    dec = registrar_decision(repo, plan.id_plan, "aprobado", "SIMULACION-PRUEBA", simulada=True)
    guardado = repo.obtener("plan", plan.id_plan, type(plan))
    assert guardado.estado == Estado.APROBADO and dec.autenticacion == "simulacion_de_prueba"
    assert any(e["tipo"] == "decision" for e in repo.eventos(plan.id_plan))
    with pytest.raises(ErrorAprobacion):  # no se decide dos veces
        registrar_decision(repo, plan.id_plan, "aprobado", "SIMULACION-PRUEBA", simulada=True)


async def test_paquete_incompleto_no_se_aprueba_en_real(repo):
    res, _ = await _flujo(repo, ["#sinagua en la escuela de Capira desde ayer"])
    with pytest.raises(ErrorAprobacion, match="incompleto"):
        registrar_decision(repo, res.planes.planes[0].id_plan, "aprobado", "Supervisora", simulada=False)


async def test_extraordinaria_exige_justificacion(repo):
    res, _ = await _flujo(repo, ["#sinagua 15 edificios de apartamentos en Arraiján hace 1 día"])  # 178.425 gal; 25 × 5.500 = 77 %
    plan = res.planes.planes[0]
    assert plan.tipo_aprobacion == "extraordinaria"
    with pytest.raises(ErrorAprobacion, match="justificación"):
        registrar_decision(repo, plan.id_plan, "aprobado", "SIMULACION-PRUEBA", simulada=True)


async def test_rechazo_se_registra(repo):
    res, _ = await _flujo(repo, ["#sinagua en la escuela de Capira desde ayer"])
    registrar_decision(repo, res.planes.planes[0].id_plan, "rechazado", "SIMULACION-PRUEBA", simulada=True, motivo="prueba")
    assert repo.obtener("plan", res.planes.planes[0].id_plan, type(res.planes.planes[0])).estado == Estado.RECHAZADO


def test_originales_no_se_sobrescriben(repo):
    r = reporte("#sinagua")
    repo.insertar("reporte", r.id_reporte, r)
    with pytest.raises(ErrorPersistencia):
        repo.insertar("reporte", r.id_reporte, r)


async def test_mensaje_cobertura_parcial_cinco_elementos(repo):
    res, _ = await _flujo(repo, ["#sinagua en la escuela de Capira desde ayer"])
    plan = res.planes.planes[0].model_copy(update={"volumen_entregable_gal": 8500.0, "cobertura_pct": 85.0, "volumen_pendiente_gal": 1500.0})
    plan.demanda.demanda_estimada_gal = 10000.0
    texto = mensaje_cobertura_parcial(plan, res.registros.registros[0])
    for frag in ("PARCIAL", "8,500", "85 %", "10,000", "1,500", "pendiente de aprobación", "no constituye una confirmación"):
        assert frag in texto


def test_mensaje_estado_no_confirma_entregas_ni_horas():
    reg = registro("#aguacontaminada en Capira")
    t = mensaje_estado(None, reg)
    assert "No hay hora de llegada confirmada" in t and "no ha sido validada" in t and "entregad" not in t


async def test_demo_con_datos_simulados(settings):
    out = await demo(settings, DATOS, aprobar=True)
    assert out["planes"] and out["mensajes_simulados"]
    assert all(d.get("simulada") for d in out["decisiones"] if "error" not in d)
    datos = json.loads(DATOS.read_text(encoding="utf-8"))
    assert all(r["contacto"] is None or r["contacto"].startswith("sim:") for r in datos["reportes"])


def test_validacion_de_entrada():
    with pytest.raises(ValueError):
        ReporteEntrada(canal="whatsapp_simulado", texto="", recibido_en=RECIBIDO)
    with pytest.raises(ValueError):
        ReporteEntrada(canal="correo", texto="x", recibido_en=RECIBIDO)
