"""Reglas deterministas del Agente 5 (clasificación de rutas). El cálculo de distancias lo hace un RoutingProvider."""

from water_coordinator.schemas.models import Certeza
from water_coordinator.services import parametros as p


def clasificar_ruta(
    tramos_km: dict[str, float],
    certezas: list[Certeza],
    volumen_gal: float,
    capacidad_gal: float,
    autonomia_validada: bool = False,
    emergencia: bool = False,
    limite_km: float = p.LIMITE_RUTA_KM,
) -> dict:
    """Recorrido: salida → recogida de agua → afectaciones → regreso a la organización (DOC §4.5, A5-R1..R7).

    `tramos_km` debe incluir 'organizacion_a_recogida', 'recogida_a_afectaciones' (incluye todas las paradas) y
    'afectaciones_a_organizacion'.
    """
    requeridos = ("organizacion_a_recogida", "recogida_a_afectaciones", "afectaciones_a_organizacion")
    faltan = [t for t in requeridos if t not in tramos_km]
    if faltan:
        return {"clasificaciones": ["error_de_construccion"], "motivo": f"Faltan tramos: {faltan} (A5-R1)", "total_km": None}
    if volumen_gal > capacidad_gal:
        return {"clasificaciones": ["inviable"], "motivo": "Volumen asignado supera la capacidad de agua (A5-R7).", "total_km": None}

    total = round(sum(tramos_km[t] for t in requeridos), 2)
    clases = []
    if total > limite_km:
        if emergencia:
            clases.append("requiere_autorizacion_por_excepcion")
        else:
            return {"clasificaciones": ["no_apta_como_ordinaria"], "total_km": total,
                    "motivo": f"Recorrido completo {total} km > {limite_km} km sin emergencia (A5-R4); devolver al Agente 4."}
    if any(c != Certeza.CONFIRMADA for c in certezas):
        clases.append("provisional")
    if not autonomia_validada:
        clases.append("pendiente_de_verificacion")  # A5-R6: el tanque 400/600 L no permite inferir autonomía
    if not clases:
        clases.append("factible")
    elif total <= limite_km and "provisional" not in clases:
        clases.insert(0, "factible")
    return {"clasificaciones": clases, "total_km": total, "motivo": ""}
