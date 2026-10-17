"""Flota y disponibilidad horaria (Agente 4)."""

from datetime import datetime, time

from water_coordinator.schemas.models import Cisterna, SolicitudAdicional
from water_coordinator.services import parametros as p


def registro_flota() -> list[Cisterna]:
    """Las 71 cisternas registradas (DEC-C06). Capacidad concreta por unidad no documentada → mínimo del rango (A4-R15)."""
    unidades = []
    for (origen, tipo), n in p.FLOTA.items():
        pref = ("ORG" if origen == "organizacion" else "SUB") + ("-S" if tipo == "small" else "-B")
        unidades += [cisterna(f"{pref}-{i:02d}", tipo, origen) for i in range(1, n + 1)]
    return unidades


def cisterna(id_: str, tipo: str, origen: str, capacidad: float | None = None) -> Cisterna:
    if capacidad is not None:
        return Cisterna(id=id_, tipo=tipo, origen=origen, capacidad_galones=capacidad, capacidad_es_supuesto=False,
                        tanque_combustible_litros=p.TANQUE_LITROS.get(tipo))
    # Tipo desconocido: se usa la menor capacidad posible de toda la flota para no sobrestimar.
    minimo = p.CAPACIDAD_GAL[tipo][0] if tipo in p.CAPACIDAD_GAL else min(r[0] for r in p.CAPACIDAD_GAL.values())
    return Cisterna(id=id_, tipo=tipo, origen=origen, capacidad_galones=minimo, capacidad_es_supuesto=True,
                    tanque_combustible_litros=p.TANQUE_LITROS.get(tipo))


def _en_intervalo(h: time, inicio: str, fin: str) -> bool:
    i, f = time.fromisoformat(inicio), time.fromisoformat(fin)
    return i <= h < f if i < f else (h >= i or h < f)


def tramo(intervalos: list[dict], momento: datetime) -> dict:
    h = momento.timetz().replace(tzinfo=None)
    for it in intervalos:
        if _en_intervalo(h, it["inicio"], it["fin"]):
            return it
    raise ValueError(f"Horario sin cobertura para {h}; los intervalos deben ser contiguos (DEC-08).")


def disponibles_por_horario(horarios: dict, momento: datetime) -> list[Cisterna]:
    """Disponibilidad mínima según horario [PROV]. Parámetro de planificación, no evidencia de vehículos libres (A4-R11).

    El horario no indica el tipo de cada unidad → tipo 'desconocido' con capacidad mínima.
    """
    t = tramo(horarios["disponibilidad"], momento)
    out = []
    for origen in ("organizacion", "subcontratada"):
        pref = "ORG" if origen == "organizacion" else "SUB"
        out += [cisterna(f"{pref}-DISP-{i:02d}", "desconocido", origen) for i in range(1, t[origen] + 1)]
    return out


def solicitables(horarios: dict, momento: datetime, disponibles: list[Cisterna]) -> list[SolicitudAdicional]:
    """Cuántas unidades más pueden pedirse ahora y con qué demora. No se pide más que la flota registrada (A4-R13)."""
    demora = tramo(horarios["solicitud_adicional"], momento)["demora_minutos"]
    if demora is None:
        return []
    out = []
    for origen in ("organizacion", "subcontratada"):
        total = sum(n for (o, _), n in p.FLOTA.items() if o == origen)
        restante = total - sum(1 for c in disponibles if c.origen == origen)
        if restante > 0:
            out.append(SolicitudAdicional(cantidad=restante, origen=origen, demora_minutos=demora))
    return out
