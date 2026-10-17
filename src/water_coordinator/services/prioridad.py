"""Reglas deterministas del Agente 3: jerarquía, T, V, A, P, orden y empates."""

import math

from water_coordinator.schemas.models import Categoria, Prioridad, RegistroAfectacion
from water_coordinator.services import parametros as p


def redondear_medio(x: float) -> float:
    """Redondeo al 0,5 más cercano, mitades hacia arriba (DEC-C01)."""
    return math.floor(x * 2 + 0.5) / 2


def factor_T(dias_sin_agua: float | None) -> float | None:
    """DEC-02 [CONF]: T = min(100, días/5 × 100), redondeado a 0,5."""
    if dias_sin_agua is None:
        return None
    return redondear_medio(min(100.0, dias_sin_agua / p.T_DIAS_MAXIMO * 100))


def factor_V(vulnerabilidad: dict[str, bool]) -> float | None:
    """DEC-C04: base = mayor criterio presente; +10 por cada modificador; tope 100. Sin evidencia → None (no cero)."""
    bases = [v for k, v in p.V_BASE.items() if vulnerabilidad.get(k)]
    if not bases:
        return None
    extra = sum(v for k, v in p.V_MODIFICADORES.items() if vulnerabilidad.get(k))
    return redondear_medio(min(100.0, max(bases) + extra))


def personas_estimadas(reg: RegistroAfectacion) -> tuple[float | None, list[str]]:
    """DEC-16/23: promedios de ocupación por unidad conocida. El dato reportado no verificado solo se usa si no hay unidades."""
    d = reg.datos_adicionales
    partes, bases = 0.0, []
    if d.edificios_apartamentos:
        partes += d.edificios_apartamentos * p.OCUPACION_EDIFICIO_APARTAMENTOS
        bases.append(f"{d.edificios_apartamentos} edificios × {p.OCUPACION_EDIFICIO_APARTAMENTOS} personas (promedio)")
    if d.viviendas_residenciales:
        partes += d.viviendas_residenciales * p.OCUPACION_VIVIENDA_RESIDENCIAL
        bases.append(f"{d.viviendas_residenciales} viviendas residenciales × {p.OCUPACION_VIVIENDA_RESIDENCIAL} (promedio)")
    if d.viviendas_rurales:
        partes += d.viviendas_rurales * p.OCUPACION_VIVIENDA_RURAL
        bases.append(f"{d.viviendas_rurales} viviendas rurales × {p.OCUPACION_VIVIENDA_RURAL} (promedio)")
    if d.instalacion_mencionada == "escuela":
        partes += p.ESTUDIANTES_PROMEDIO_ESCUELA
        bases.append(f"escuela: {p.ESTUDIANTES_PROMEDIO_ESCUELA} estudiantes (promedio)")
    if bases:
        return partes, bases
    if d.personas_reportadas:
        return float(d.personas_reportadas), [f"{d.personas_reportadas} personas según el reporte (no verificado)"]
    return None, []


def factor_A(personas: float | None, referencia: int = 1000) -> float | None:
    """DEC-C05: A = min(100, personas / referencia × 100), redondeado a 0,5. Máximos validados por lugar [PEND]."""
    if personas is None:
        return None
    return redondear_medio(min(100.0, personas / referencia * 100))


def categoria(reg: RegistroAfectacion) -> Categoria:
    inst = reg.datos_adicionales.instalacion_mencionada
    return Categoria(inst) if inst else Categoria.OTRA


def priorizar(reg: RegistroAfectacion, a_referencia: int = 1000) -> Prioridad:
    cat = categoria(reg)
    nivel = p.JERARQUIA.get(cat.value)
    T = factor_T(reg.dias_sin_agua)
    V = factor_V(reg.datos_adicionales.vulnerabilidad)
    personas, bases_a = personas_estimadas(reg)
    A = factor_A(personas, a_referencia)
    faltan = [n for n, v in (("T (fecha del incidente)", T), ("V (criterios de vulnerabilidad)", V), ("A (personas afectadas)", A)) if v is None]
    explic = [
        f"Categoría: {cat.value}; nivel jerárquico: {nivel if nivel else 'sin determinar'}.",
        f"T = {T}" + (f" ({reg.dias_sin_agua:.2f} días sin agua)" if T is not None else " (sin fecha del incidente)"),
        f"V = {V} (criterios: {sorted(k for k, v in reg.datos_adicionales.vulnerabilidad.items() if v) or 'ninguno con evidencia'})",
        f"A = {A} ({'; '.join(bases_a) or 'sin datos de personas'})",
    ]
    revision, motivos = False, []
    P, rango, completo = None, None, not faltan
    if cat == Categoria.INCIERTA:
        revision = True
        motivos.append("Categoría de instalación incierta (A3-R3).")
    if nivel == 5 or cat == Categoria.INCIERTA:
        if faltan:
            # A3-R6: no se asigna cero; se presenta el rango posible y se pide revisión.
            lo = sum(p.PESOS_P[k] * (v if v is not None else 0) for k, v in (("T", T), ("V", V), ("A", A)))
            hi = sum(p.PESOS_P[k] * (v if v is not None else 100) for k, v in (("T", T), ("V", V), ("A", A)))
            rango = (lo, hi)
            revision = True
            motivos.append("P incompleto: faltan " + ", ".join(faltan) + ".")
        else:
            P = p.PESOS_P["T"] * T + p.PESOS_P["V"] * V + p.PESOS_P["A"] * A
            explic.append(f"P = 0,50×{T} + 0,25×{V} + 0,25×{A} = {P}")
    else:
        completo = True  # niveles 1–4: el orden lo fija la jerarquía; P no aplica
        explic.append("P no aplica: instalación crítica ordenada por jerarquía.")
    return Prioridad(
        id_afectacion=reg.id_afectacion,
        categoria_instalacion=cat,
        nivel_jerarquia=nivel,
        T=T, V=V, A=A,
        personas_estimadas=personas,
        puntuacion_P=P,
        rango_P=rango,
        completo=completo,
        factores_explicados=explic,
        datos_faltantes=faltan,
        requiere_revision_humana=revision,
        motivo_revision=motivos,
        version_reglas=p.VERSION_REGLAS,
    )


def ordenar(prioridades: list[Prioridad], registros: dict[str, RegistroAfectacion]) -> tuple[list[Prioridad], list[list[str]]]:
    """Orden recomendado: jerarquía; en nivel 5, P (o el punto medio del rango). Desempate DEC-03: días sin agua, luego personas.

    Las categorías inciertas van al final de su posible nivel y quedan en revisión. Los empates que persisten se devuelven.
    """

    def clave(pr: Prioridad):
        dias = registros[pr.id_afectacion].dias_sin_agua
        # P incompleto: se ordena por el punto medio del rango (neutral: ni premia ni penaliza la falta de datos).
        p_val = pr.puntuacion_P if pr.puntuacion_P is not None else (sum(pr.rango_P) / 2 if pr.rango_P else -1)
        return (pr.nivel_jerarquia or 6, -p_val if pr.nivel_jerarquia in (5, None) else 0,
                -(dias if dias is not None else -1), -(pr.personas_estimadas or -1))

    orden = sorted(prioridades, key=clave)
    empates, grupo = [], [orden[0]] if orden else []
    for a, b in zip(orden, orden[1:]):
        if clave(a) == clave(b):
            grupo.append(b)
        else:
            if len(grupo) > 1:
                empates.append([x.id_afectacion for x in grupo])
            grupo = [b]
    if len(grupo) > 1:
        empates.append([x.id_afectacion for x in grupo])
    return orden, empates
