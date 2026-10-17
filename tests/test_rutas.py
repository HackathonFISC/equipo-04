"""Agente 5 (reglas): recorrido completo, límite de 1.000 km, capacidad y autonomía (DOC §4.5.I)."""

from water_coordinator.schemas.models import Certeza
from water_coordinator.services.rutas import clasificar_ruta

OK = [Certeza.CONFIRMADA]


def tramos(a, b, c):
    return {"organizacion_a_recogida": a, "recogida_a_afectaciones": b, "afectaciones_a_organizacion": c}


def test_ruta_normal_factible_pero_autonomia_pendiente():
    r = clasificar_ruta(tramos(100, 200, 120), OK, 3000, 3000)
    assert r["total_km"] == 420 and r["clasificaciones"] == ["factible", "pendiente_de_verificacion"]


def test_falta_el_regreso():
    r = clasificar_ruta({"organizacion_a_recogida": 1, "recogida_a_afectaciones": 1}, OK, 1, 3000)
    assert r["clasificaciones"] == ["error_de_construccion"]


def test_mas_de_1000_sin_emergencia_no_es_ordinaria():
    assert clasificar_ruta(tramos(400, 400, 250), OK, 1, 3000)["clasificaciones"] == ["no_apta_como_ordinaria"]


def test_mas_de_1000_con_emergencia_requiere_excepcion():
    r = clasificar_ruta(tramos(400, 400, 250), OK, 1, 3000, emergencia=True)
    assert "requiere_autorizacion_por_excepcion" in r["clasificaciones"] and "factible" not in r["clasificaciones"]


def test_ubicacion_aproximada_da_provisional():
    assert "provisional" in clasificar_ruta(tramos(1, 1, 1), [Certeza.APROXIMADA], 1, 3000)["clasificaciones"]


def test_volumen_supera_capacidad_maxima_small():
    assert clasificar_ruta(tramos(1, 1, 1), OK, 6000, 5500)["clasificaciones"] == ["inviable"]


def test_nunca_dice_optima():
    r = clasificar_ruta(tramos(1, 1, 1), OK, 1, 3000, autonomia_validada=True)
    assert r["clasificaciones"] == ["factible"] and "optima" not in str(r)
