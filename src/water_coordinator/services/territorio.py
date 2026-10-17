"""Referencia territorial versionada de Panamá Oeste (usada por el Agente 2 y el panel).

Comunidades = corregimientos de La Chorrera y Arraiján (división político-administrativa pública).
Se excluyen los corregimientos cabecera homónimos del distrito para no confundir distrito y comunidad.
Lista pendiente de validación por el equipo; ampliable sin tocar la lógica.
"""

from water_coordinator.services.clasificacion import normalizar

FUENTE = "catálogo territorial interno v2 (distritos y corregimientos de Panamá Oeste)"

DISTRITOS = ["Arraiján", "Capira", "Chame", "La Chorrera", "San Carlos"]

COMUNIDADES = {
    "La Chorrera": ["Barrio Balboa", "Barrio Colón", "El Coco", "Guadalupe", "Puerto Caimito", "Playa Leona",
                    "Herrera", "Hurtado", "Santa Rita"],
    "Arraiján": ["Burunga", "Cerro Silvestre", "Juan Demóstenes Arosemena", "Nuevo Emperador", "Santa Clara",
                 "Veracruz", "Vista Alegre"],
}


def _contiene(texto_norm: str, nombre: str) -> bool:
    return f" {normalizar(nombre)} " in f" {texto_norm} "


def distrito_en(texto: str) -> str | None:
    t = normalizar(texto).replace(",", " ")
    return next((d for d in DISTRITOS if _contiene(t, d)), None)


def comunidad_en(texto: str) -> tuple[str, str] | None:
    """(comunidad, distrito) si el texto nombra una comunidad del catálogo; la más larga gana (p. ej. «Barrio Colón»)."""
    t = normalizar(texto).replace(",", " ")
    candidatas = [(c, d) for d, cs in COMUNIDADES.items() for c in cs if _contiene(t, c)]
    return max(candidatas, key=lambda x: len(x[0])) if candidatas else None


def catalogo() -> list[dict]:
    return [{"comunidad": c, "distrito": d} for d, cs in COMUNIDADES.items() for c in cs]
