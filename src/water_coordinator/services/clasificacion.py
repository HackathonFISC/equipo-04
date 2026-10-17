"""Clasificación determinista por palabras clave (fuente: docs/KEYWORDS.md).

Escala de confianza (DEC-C03):
- alta: hashtag del tipo, o 2+ expresiones distintas del tipo, sin conflicto.
- media: una sola expresión del tipo.
- baja: tipo resuelto con conflicto o desacuerdo con el modelo de IA.
- ninguna: tipo indeterminado.
"""

import re
import unicodedata

from water_coordinator.schemas.models import Confianza, TipoAfectacion

HASHTAGS = {
    "#sinagua": TipoAfectacion.FALTA_DE_AGUA,
    "#faltadeagua": TipoAfectacion.FALTA_DE_AGUA,
    "#nohayagua": TipoAfectacion.FALTA_DE_AGUA,
    "#tuberiarota": TipoAfectacion.TUBERIA_ROTA,
    "#fugadeagua": TipoAfectacion.TUBERIA_ROTA,
    "#aguacontaminada": TipoAfectacion.AGUA_CONTAMINADA,
    "#aguasucia": TipoAfectacion.AGUA_CONTAMINADA,
}
# Etiquetas de relevancia: marcan el reporte como del dominio, pero no fijan un tipo.
HASHTAGS_RELEVANCIA = {"#idaan", "#panamaoeste", "#cisterna", "#carrotanque"}

# Expresiones (texto escrito o transcripción de voz), ya sin tildes y en minúsculas.
EXPRESIONES = {
    TipoAfectacion.FALTA_DE_AGUA: [
        "sin agua", "falta de agua", "no hay agua", "no llega el agua", "no ha llegado el agua",
        "no sale agua", "no cae agua", "se fue el agua", "corte de agua", "sin servicio de agua",
        "estamos secos", "la pluma no tiene agua", "hashtag sin agua", "numeral sin agua",
    ],
    TipoAfectacion.TUBERIA_ROTA: [
        "tuberia rota", "tubo roto", "se rompio la tuberia", "se rompio el tubo", "fuga de agua",
        "botando agua", "esta botando agua", "tuberia danada", "rotura de tuberia", "derrame de agua",
        "hashtag tuberia rota", "numeral tuberia rota",
    ],
    TipoAfectacion.AGUA_CONTAMINADA: [
        "agua contaminada", "agua sucia", "agua turbia", "agua amarilla", "agua color cafe",
        "agua marron", "agua con mal olor", "el agua huele mal", "agua con olor", "agua con sabor raro",
        "agua con lodo", "hashtag agua contaminada",
    ],
}
RELEVANCIA_VOZ = ["idaan", "i de a a ene", "idan", "carro cisterna", "carro tanque"]


def normalizar(texto: str) -> str:
    sin_tildes = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", sin_tildes.lower()).strip()


def clasificar(texto: str) -> dict:
    """Devuelve tipo, causa, consecuencias, candidatos, confianza, evidencia y si requiere revisión."""
    t = normalizar(texto)
    tags = set(re.findall(r"#\w+", t))
    hits: dict[TipoAfectacion, list[str]] = {}
    for tag in tags & HASHTAGS.keys():
        hits.setdefault(HASHTAGS[tag], []).append(tag)
    for tipo, frases in EXPRESIONES.items():
        for f in frases:
            if re.search(rf"\b{re.escape(f)}\b", t):
                hits.setdefault(tipo, []).append(f)
    relevante = bool(hits) or bool(tags & HASHTAGS_RELEVANCIA) or any(v in t for v in RELEVANCIA_VOZ)
    evidencia = sorted({e for lst in hits.values() for e in lst})
    candidatos = sorted(hits, key=list(TipoAfectacion).index)

    causa, consecuencias = None, []
    tipos = set(hits)
    # A1-R2 [CONF]: si una tubería rota causa falta de agua, la principal es la tubería rota.
    if {TipoAfectacion.TUBERIA_ROTA, TipoAfectacion.FALTA_DE_AGUA} <= tipos:
        causa, consecuencias = TipoAfectacion.TUBERIA_ROTA, [TipoAfectacion.FALTA_DE_AGUA]
        tipos.discard(TipoAfectacion.FALTA_DE_AGUA)

    if len(tipos) == 1:
        tipo = tipos.pop()
        lst = hits[tipo]
        fuerte = any(e.startswith("#") for e in lst) or len(set(lst)) >= 2
        confianza = Confianza.ALTA if fuerte else Confianza.MEDIA
        revision = False
    elif not tipos:
        tipo, confianza, revision = TipoAfectacion.INDETERMINADO, Confianza.NINGUNA, relevante
    else:
        # Combinación no cubierta por A1-R2: no se elige en silencio.
        tipo, confianza, revision = TipoAfectacion.INDETERMINADO, Confianza.NINGUNA, True
    return {
        "tipo": tipo,
        "causa": causa,
        "consecuencias": consecuencias,
        "candidatos": candidatos,
        "confianza": confianza,
        "evidencia": evidencia,
        "relevante": relevante,
        "revision": revision,
    }


# ---------- Datos reportados (solo lo que consta en el texto) ----------

_NUM = r"(\d+|un|una|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez)"
_PALABRAS = {"un": 1, "una": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5, "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10}

INSTALACIONES = [
    ("policlinica", "policlinica"),
    ("centro de salud", "centro_de_salud"),
    ("subcentro de salud", "centro_de_salud"),
    ("hospital", "hospital"),
    ("escuela", "escuela"),
    ("colegio", "escuela"),
    ("centro educativo", "escuela"),
    ("clinica", "incierta"),  # A3-R3: "clínica" no permite fijar la categoría
]


def _numero(s: str) -> int:
    return int(s) if s.isdigit() else _PALABRAS[s]


def _contar(t: str, patron: str) -> int | None:
    m = re.search(rf"\b{_NUM}\s+{patron}", t)
    return _numero(m.group(1)) if m else None


def extraer_datos(texto: str) -> dict:
    t = normalizar(texto)
    instalacion = next((cat for clave, cat in INSTALACIONES if re.search(rf"\b{clave}\b", t)), None)
    rural = bool(re.search(r"\brural(es)?\b|\bdel campo\b", t))
    viviendas = _contar(t, r"(?:viviendas|casas)")
    datos = {
        "instalacion_mencionada": instalacion,
        "viviendas_rurales": viviendas if rural else None,
        "viviendas_residenciales": viviendas if not rural else None,
        "edificios_apartamentos": _contar(t, r"edificios?(?: de apartamentos)?"),
        "estudiantes_reportados": _contar(t, r"(?:estudiantes|alumnos)"),
        "personas_reportadas": _contar(t, r"personas"),
    }
    vul = {}
    if instalacion in ("hospital", "policlinica", "centro_de_salud"):
        vul["salud_cercana"] = True
    if instalacion == "escuela":
        vul["escuela_cercana"] = True
    if rural:
        vul["area_rural"] = True
    if re.search(r"\b(residencial|barriada|urbanizacion|apartamentos|edificios?)\b", t) or datos["viviendas_residenciales"]:
        vul["area_residencial"] = True
    if re.search(r"\b(comunidad antigua|barrio antiguo|casas antiguas)\b", t):
        vul["comunidad_antigua"] = True
    if re.search(r"\b(ninos|ninas|bebes|jovenes|estudiantes|alumnos)\b", t):
        vul["poblacion_infantil_joven"] = True
    datos["vulnerabilidad"] = vul
    return datos


_UBICACION = re.compile(
    r"\b(?:en|desde|ubicad[oa]s? en|sector|barriada|comunidad de)\s+((?:la |el |los |las )?[A-ZÁÉÍÓÚÑ][\wÁÉÍÓÚÑáéíóúñ]*(?:[ ,]+(?:de |del |la |el )?[A-ZÁÉÍÓÚÑ][\wÁÉÍÓÚÑáéíóúñ]*)*)"
)


def extraer_ubicacion(texto: str) -> str | None:
    """Ubicación tal como fue reportada (nombres propios tras 'en', 'sector', etc.). No geolocaliza."""
    m = _UBICACION.search(texto)
    return m.group(1).strip(" ,.") if m else None
