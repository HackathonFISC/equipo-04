"""Reglas deterministas del Agente 4: demanda, cobertura y tipo de aprobación."""

from water_coordinator.schemas.models import CalculoDemanda, RegistroAfectacion, TipoAfectacion
from water_coordinator.services import parametros as p


def calcular_demanda(reg: RegistroAfectacion) -> CalculoDemanda:
    """A4-R1/R3 [CONF]: demanda = demanda diaria × días de planificación del tipo.

    El tiempo sin agua NO se suma (DEC-01): solo afecta a la prioridad.
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
    if reg.dias_sin_agua is None:
        supuestos.append("Fecha del incidente desconocida: no afecta a la demanda (DEC-01), sí a la prioridad.")

    completa = bool(bases) and dias is not None and d.instalacion_mencionada != "incierta"
    return CalculoDemanda(
        id_afectacion=reg.id_afectacion,
        demanda_diaria_gal=round(diaria, 2) if completa else None,
        dias_planificacion=dias,
        demanda_estimada_gal=round(diaria * dias, 2) if completa else None,
        formula="demanda_estimada = demanda_diaria × días_planificación(tipo)",
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
