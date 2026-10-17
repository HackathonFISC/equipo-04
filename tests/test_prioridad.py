"""Agente 3: jerarquía, T, V, A, P, datos faltantes y empates (DOC §4.3.I)."""

from conftest import registro
from water_coordinator.schemas.models import Categoria
from water_coordinator.services.prioridad import factor_A, factor_T, factor_V, ordenar, priorizar, redondear_medio


def test_T_lineal_con_tope_y_redondeo_a_medio():
    assert factor_T(2) == 40
    assert factor_T(5) == 100 and factor_T(9) == 100
    assert factor_T(0.153) == 3.0  # 3,06 → 3,0
    assert redondear_medio(2.25) == 2.5 and redondear_medio(2.74) == 2.5 and redondear_medio(2.75) == 3.0
    assert factor_T(None) is None


def test_V_usa_el_mayor_criterio_mas_modificadores_y_no_inventa():
    assert factor_V({"area_residencial": True}) == 40
    assert factor_V({"area_rural": True, "area_residencial": True}) == 60
    assert factor_V({"salud_cercana": True, "comunidad_antigua": True}) == 100  # tope
    assert factor_V({"area_residencial": True, "poblacion_infantil_joven": True}) == 50
    assert factor_V({}) is None
    assert factor_V({"comunidad_antigua": True}) is None  # modificador sin criterio base


def test_A_por_promedios_de_ocupacion():
    r = registro("#sinagua 20 viviendas rurales en Capira")
    pr = priorizar(r)
    assert pr.personas_estimadas == 80 and pr.A == 8
    assert factor_A(2500) == 100


def test_formula_P_del_documento():
    # DOC: T=80, V=60, A=40 → P=65
    r = registro("#sinagua hace 4 días, 20 viviendas rurales en Capira")  # T=80, V=60, A=8
    pr = priorizar(r, a_referencia=200)  # 80 personas / 200 → A=40
    assert (pr.T, pr.V, pr.A, pr.puntuacion_P) == (80, 60, 40, 65)


def test_faltante_no_es_cero_y_da_rango_con_revision():
    pr = priorizar(registro("#sinagua 20 viviendas rurales en Capira"))  # sin fecha → T faltante
    assert pr.T is None and pr.puntuacion_P is None and not pr.completo
    assert pr.rango_P == (17.0, 67.0)
    assert pr.requiere_revision_humana


def test_jerarquia_hospital_antes_que_residencial_con_P_alto():
    hosp = registro("#sinagua en el hospital de La Chorrera")
    res = registro("#sinagua hace 9 días, 30 edificios de apartamentos con niños en Arraiján")
    prs = [priorizar(hosp), priorizar(res)]
    orden, _ = ordenar(prs, {hosp.id_afectacion: hosp, res.id_afectacion: res})
    assert orden[0].categoria_instalacion == Categoria.HOSPITAL


def test_jerarquia_de_salud_y_escuela():
    regs = [registro(t) for t in ("#sinagua en la escuela", "#sinagua en el centro de salud", "#sinagua en la policlínica", "#sinagua en el hospital")]
    orden, _ = ordenar([priorizar(r) for r in regs], {r.id_afectacion: r for r in regs})
    assert [p.nivel_jerarquia for p in orden] == [1, 2, 3, 4]


def test_clinica_es_categoria_incierta_con_revision():
    pr = priorizar(registro("#sinagua en la clínica del barrio"))
    assert pr.categoria_instalacion == Categoria.INCIERTA and pr.requiere_revision_humana


def test_empate_se_desempata_por_dias_y_se_reporta_si_persiste():
    a = registro("#sinagua hace 2 días, 10 casas en Capira")
    b = registro("#sinagua hace 2 días, 10 casas en Chame")
    orden, empates = ordenar([priorizar(a), priorizar(b)], {a.id_afectacion: a, b.id_afectacion: b})
    assert empates == [[orden[0].id_afectacion, orden[1].id_afectacion]]
