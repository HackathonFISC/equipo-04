"""Agente 4: demanda, cobertura, flota y horarios (DOC §4.4.I)."""

from datetime import datetime

import pytest

from conftest import registro
from water_coordinator.agents.planificacion import planificar
from water_coordinator.schemas.models import TZ_PANAMA, Estado, ListaPriorizada, SolicitudPlanificacion
from water_coordinator.services.demanda import calcular_demanda, cobertura, tipo_aprobacion
from water_coordinator.services.flota import cisterna, disponibles_por_horario, registro_flota, solicitables
from water_coordinator.services.parametros import HORARIOS_POR_DEFECTO, cargar_horarios
from water_coordinator.services.prioridad import priorizar


def a_las(h: int, m: int = 0) -> datetime:
    return datetime(2026, 10, 17, h, m, tzinfo=TZ_PANAMA)


def test_escuela_con_promedio():
    d = calcular_demanda(registro("#sinagua en la escuela de Capira"))
    assert d.demanda_diaria_gal == 2800 and d.demanda_estimada_gal == 2800


def test_escuela_con_estudiantes_reportados_no_verificados_usa_promedio_y_lo_dice():
    d = calcular_demanda(registro("#sinagua en la escuela, somos 450 estudiantes"))
    assert d.demanda_diaria_gal == 2800
    assert any("450" in s for s in d.supuestos)


def test_viviendas_rurales():
    assert calcular_demanda(registro("#sinagua 20 viviendas rurales")).demanda_diaria_gal == 2112


def test_duraciones_por_tipo_mas_mitad_del_tiempo_sin_agua():
    falta = calcular_demanda(registro("#sinagua hace 2 días, 10 casas"))
    rota = calcular_demanda(registro("#tuberiarota hace 2 días, 10 casas"))
    contaminada = calcular_demanda(registro("#aguacontaminada hace 2 días, 10 casas"))
    # DEC-C15: duración (1/2/2) + 0,5 × 2 días sin agua hasta el reporte
    assert (falta.dias_planificacion, rota.dias_planificacion, contaminada.dias_planificacion) == (2, 3, 3)
    assert falta.dias_compensados == 1
    assert falta.demanda_estimada_gal == round(10 * 3 * 79.3 * 2, 2)
    assert priorizar(registro("#sinagua hace 2 días, 10 casas")).T == 40  # y también sube la prioridad
    assert any("agua de cisterna está limpia" in s for s in contaminada.supuestos)


def test_sin_fecha_no_hay_compensacion_y_se_avisa():
    d = calcular_demanda(registro("#sinagua 10 casas"))
    assert d.dias_planificacion == 1 and d.dias_compensados == 0
    assert any("subestimada" in s for s in d.supuestos)


def test_instalaciones_de_salud_valor_fijo_diario():
    assert calcular_demanda(registro("#sinagua en el hospital")).demanda_diaria_gal == 13208
    assert calcular_demanda(registro("#sinagua en la policlínica")).demanda_diaria_gal == 4755
    assert calcular_demanda(registro("#sinagua en el centro de salud")).demanda_diaria_gal == 1320


def test_sin_unidades_no_se_inventa_demanda():
    d = calcular_demanda(registro("#sinagua en Capira"))
    assert d.demanda_estimada_gal is None and d.datos_faltantes


@pytest.mark.parametrize("cob,tipo", [(100, "ordinaria"), (85, "cobertura_parcial"), (80, "cobertura_parcial"),
                                       (79.99, "extraordinaria"), (None, "no_aplicable")])
def test_tipo_de_aprobacion_por_cobertura(cob, tipo):
    assert tipo_aprobacion(cob) == tipo


def test_cobertura_parcial_del_documento():
    assert cobertura(8500, 10000) == 85


def test_flota_registrada_71():
    f = registro_flota()
    assert len(f) == 71
    assert sum(c.origen == "organizacion" and c.tipo == "small" for c in f) == 10
    assert sum(c.origen == "subcontratada" and c.tipo == "big" for c in f) == 16
    assert not any(c.capacidad_es_supuesto for c in f)  # el rango del tipo es la capacidad (DEC-C16)


def test_rango_de_carga_por_tipo():
    big, small, desconocido = (cisterna("X", t, "organizacion") for t in ("big", "small", "desconocido"))
    assert (big.capacidad_min_galones, big.capacidad_galones) == (9000, 13000)
    assert (small.capacidad_min_galones, small.capacidad_galones) == (3000, 5500)
    assert desconocido.capacidad_galones == 5500 and desconocido.capacidad_es_supuesto  # menor máximo


@pytest.mark.parametrize("hora,org,sub,demora", [
    (a_las(7), 5, 20, 90), (a_las(10), 5, 20, 40), (a_las(17), 5, 20, 90),
    (a_las(19, 30), 0, 10, 90), (a_las(22), 0, 10, None), (a_las(5, 59), 0, 10, None),
])
def test_horarios(hora, org, sub, demora):
    disp = disponibles_por_horario(HORARIOS_POR_DEFECTO, hora)
    assert sum(c.origen == "organizacion" for c in disp) == org
    assert sum(c.origen == "subcontratada" for c in disp) == sub
    sol = solicitables(HORARIOS_POR_DEFECTO, hora, disp)
    assert (sol[0].demora_minutos if sol else None) == demora


def test_horarios_configurables_por_archivo(tmp_path):
    f = tmp_path / "h.json"
    f.write_text('{"disponibilidad": [], "solicitud_adicional": []}', encoding="utf-8")
    assert cargar_horarios(f)["disponibilidad"] == []
    assert cargar_horarios(None) is HORARIOS_POR_DEFECTO


def _plan(textos, momento):
    regs = [registro(t) for t in textos]
    prs = [priorizar(r) for r in regs]
    disp = disponibles_por_horario(HORARIOS_POR_DEFECTO, momento)
    sol = SolicitudPlanificacion(lista=ListaPriorizada(prioridades=prs), registros=regs, ubicaciones=[], disponibles=disp,
                                 solicitables=solicitables(HORARIOS_POR_DEFECTO, momento, disp), momento=momento)
    return planificar(sol)


def test_noche_no_supera_inventario_y_documenta_deficit():
    planes = _plan(["#sinagua 10 edificios de apartamentos hace 1 día en Arraiján"], a_las(22))  # 118.950 gal > 10 × 5.500
    p = planes[0]
    assert len(p.cisternas_asignadas) == 10 and p.cobertura_pct < 80
    assert p.tipo_aprobacion == "extraordinaria" and p.solicitudes_adicionales == []
    assert any("Déficit" in r for r in p.riesgos_incertidumbres)


def test_sin_doble_asignacion_entre_planes():
    planes = _plan(["#sinagua en el hospital", "#sinagua en la policlínica"], a_las(10))
    ids = [c.id for p in planes for c in p.cisternas_asignadas]
    assert len(ids) == len(set(ids))


def test_plan_siempre_pendiente_de_aprobacion_e_incompleto_sin_ruta():
    p = _plan(["#sinagua en la escuela"], a_las(10))[0]
    assert p.estado == Estado.PENDIENTE_APROBACION and not p.completo and "ruta (Agente 5)" in p.campos_faltantes
