"""Parámetros aprobados. Cada valor indica su origen: documento de criterios (DOC) o decisión registrada (DEC-* en docs/DECISIONS.md)."""

import json
from pathlib import Path

VERSION_REGLAS = "criterios-1.0-rev.4+dec-c16-2026-10-17"

# DEC-05/24/27 [CONF] — duración de planificación en días por tipo.
DURACION_DIAS = {"falta_de_agua": 1, "tuberia_rota": 2, "agua_contaminada": 2}
# DEC-C15 — se suma a la duración la mitad de los días sin agua hasta el reporte.
FACTOR_COMPENSACION = 0.5

# DOC §4.4.C [CONF] — demanda diaria de referencia (galones/día).
GAL_PERSONA_URBANA = 79.3
GAL_PERSONA_RURAL = 26.4
GAL_ESTUDIANTE = 4.0
GAL_DIA_INSTALACION = {"hospital": 13208.0, "policlinica": 4755.0, "centro_de_salud": 1320.0}

# Promedios de ocupación por edificio/vivienda/escuela; no representan la población total de una comunidad.
OCUPACION_EDIFICIO_APARTAMENTOS = 100
OCUPACION_VIVIENDA_RESIDENCIAL = 3
OCUPACION_VIVIENDA_RURAL = 4
ESTUDIANTES_PROMEDIO_ESCUELA = 700

# DOC §4.3 [CONF] — jerarquía y pesos de P.
JERARQUIA = {"hospital": 1, "policlinica": 2, "centro_de_salud": 3, "escuela": 4, "otra": 5}
PESOS_P = {"T": 0.50, "V": 0.25, "A": 0.25}
T_DIAS_MAXIMO = 5

# DEC-C04 (usuaria, 2026-10-17) — conversión de V a 0–100.
V_BASE = {"salud_cercana": 100, "escuela_cercana": 80, "area_rural": 60, "area_residencial": 40}
V_MODIFICADORES = {"comunidad_antigua": 10, "poblacion_infantil_joven": 10}

# Cobertura (DOC §4.4.E A4-R6..R8) [CONF].
COBERTURA_MINIMA_PCT = 80.0

# DEC-C16 — toda cisterna de un tipo carga entre el mínimo y el máximo de su rango (galones).
CAPACIDAD_GAL = {"small": (3000.0, 5500.0), "big": (9000.0, 13000.0)}
# Tipo no indicado (p. ej. disponibilidad por horario): se toma el menor máximo (Small) para no sobrestimar.
CAPACIDAD_TIPO_DESCONOCIDO = (CAPACIDAD_GAL["small"][0], min(r[1] for r in CAPACIDAD_GAL.values()))
# DEC-09 [CONF] — tanque de combustible (litros). No se infiere autonomía.
TANQUE_LITROS = {"small": 400.0, "big": 600.0}

# DEC-C06 (usuaria, 2026-10-17) — composición de la flota (71 cisternas).
FLOTA = {
    ("organizacion", "small"): 10,
    ("organizacion", "big"): 5,
    ("subcontratada", "small"): 40,
    ("subcontratada", "big"): 16,
}

# DOC §4.5 [PROV] — límite operativo de recorrido completo.
LIMITE_RUTA_KM = 1000.0

# DEC-08 + DEC-C07 [PROV] — horarios. Intervalos contiguos [inicio, fin) en horas; "fin" < "inicio" cruza medianoche.
HORARIOS_POR_DEFECTO = {
    "disponibilidad": [
        {"inicio": "06:00", "fin": "19:00", "organizacion": 5, "subcontratada": 20},
        {"inicio": "19:00", "fin": "06:00", "organizacion": 0, "subcontratada": 10},
    ],
    "solicitud_adicional": [
        {"inicio": "06:00", "fin": "08:00", "demora_minutos": 90},
        {"inicio": "08:00", "fin": "16:00", "demora_minutos": 40},
        {"inicio": "16:00", "fin": "20:00", "demora_minutos": 90},
        {"inicio": "20:00", "fin": "06:00", "demora_minutos": None},
    ],
}


def cargar_horarios(ruta: Path | None) -> dict:
    """Horarios vigentes: los por defecto, salvo que se configure un archivo que los reemplace."""
    if ruta is None:
        return HORARIOS_POR_DEFECTO
    datos = json.loads(Path(ruta).read_text(encoding="utf-8"))
    if set(datos) != {"disponibilidad", "solicitud_adicional"}:
        raise ValueError("El archivo de horarios debe tener 'disponibilidad' y 'solicitud_adicional'.")
    return datos
