"""Reglas deterministas del Agente 4: demanda, cobertura y tipo de aprobación."""

from water_coordinator.schemas.models import CalculoDemanda, RegistroAfectacion, TipoAfectacion
from water_coordinator.services import parametros as p


def calcular_demanda(reg: RegistroAfectacion) -> CalculoDemanda:
    """A4-R1/R3: demanda = demanda diaria × (duración del tipo + 50 % de los días sin agua hasta el reporte).

    DEC-C15 (usuaria, 2026-10-17) reemplaza a DEC-01 del documento: el tiempo sin agua sube la prioridad (T)
    y además se compensa la mitad en la demanda. Los días sin agua se cuentan del incidente a la recepción.
    """
    d = reg.datos_adicionales
    bases, supuestos, faltan = [], [], []
    diaria = 0.0
    if d.instalacion_mencionada in p.GAL_DIA_INSTALACION:
        diaria += p.GAL_DIA_INSTALACION[d.instalacion_mencionada]
        bases.append(f"{d.instalacion_mencionada}: {p.GAL_DIA_INSTALACION[d.instalacion_mencionada]} gal/día (valor fijo)")
    if d.instalacion_mencionada == "escuela":
        diaria += p.ESTUDIANTES_PROMEDIO_ESCUELA * p.GAL_ESTUDIANTE
        bases.append(f"escuela: {p.ESTUDIANTES_PROMEDIO_ESCUELA} estudiantes (promedio) × {p.GAL_ESTUDIANTE} gal")
        if d.estudiantes_reportados:
            supuestos.append(
                f"El reporte indica {d.estudiantes_reportados} estudiantes (no verificado); se usa el promedio hasta verificarlo."
            )
    if d.edificios_apartamentos:
        diaria += d.edificios_apartamentos * p.OCUPACION_EDIFICIO_APARTAMENTOS * p.GAL_PERSONA_URBANA
        bases.append(f"{d.edificios_apartamentos} edificios × {p.OCUPACION_EDIFICIO_APARTAMENTOS} × {p.GAL_PERSONA_URBANA} gal")
    if d.viviendas_residenciales:
        diaria += d.viviendas_residenciales * p.OCUPACION_VIVIENDA_RESIDENCIAL * p.GAL_PERSONA_URBANA
        bases.append(f"{d.viviendas_residenciales} viviendas × {p.OCUPACION_VIVIENDA_RESIDENCIAL} × {p.GAL_PERSONA_URBANA} gal")
    if d.viviendas_rurales:
        diaria += d.viviendas_rurales * p.OCUPACION_VIVIENDA_RURAL * p.GAL_PERSONA_RURAL
        bases.append(f"{d.viviendas_rurales} viviendas rurales × {p.OCUPACION_VIVIENDA_RURAL} × {p.GAL_PERSONA_RURAL} gal")

    if d.instalacion_mencionada == "incierta":
        faltan.append("categoría de instalación incierta (no se usa valor fijo)")
    if not bases:
        faltan.append("unidades afectadas (viviendas, edificios, escuela o instalación de salud)")
    dias = p.DURACION_DIAS.get(reg.tipo_afectacion.value)
    if dias is None:
        faltan.append("tipo de afectación determinado")
    if reg.tipo_afectacion == TipoAfectacion.AGUA_CONTAMINADA:
        supuestos.append("Supuesto de planificación (DEC-17): el agua de cisterna está limpia; no es certificación sanitaria.")
    compensacion = 0.0
    if reg.dias_sin_agua is None:
        supuestos.append("Fecha del incidente desconocida: sin compensación temporal; la demanda puede estar subestimada (A4-R4).")
    else:
        compensacion = round(p.FACTOR_COMPENSACION * reg.dias_sin_agua, 4)

    completa = bool(bases) and dias is not None and d.instalacion_mencionada != "incierta"
    total_dias = dias + compensacion if dias is not None else None
    return CalculoDemanda(
        id_afectacion=reg.id_afectacion,
        demanda_diaria_gal=round(diaria, 2) if completa else None,
        dias_planificacion=total_dias,
        dias_compensados=compensacion,
        demanda_estimada_gal=round(diaria * total_dias, 2) if completa else None,
        formula="demanda_estimada = demanda_diaria × (duración(tipo) + 0,5 × días_sin_agua_hasta_el_reporte)",
        bases=bases,
        supuestos=supuestos,
        datos_faltantes=faltan,
    )


def cobertura(entregable: float, demanda: float) -> float:
    return round(entregable / demanda * 100, 2)


def tipo_aprobacion(cob: float | None) -> str:
    """A4-R6..R8 [CONF]. Todo plan requiere aprobación (DEC-18)."""
    if cob is None:
        return "no_aplicable"
    if cob >= 100:
        return "ordinaria"
    if cob >= p.COBERTURA_MINIMA_PCT:
        return "cobertura_parcial"
    return "extraordinaria"
