"""Agente 2 — Geolocalización (DOC §4.2). Nunca presenta una ubicación estimada como confirmada."""

import logging

from autogen_core import MessageContext, RoutedAgent, message_handler

from water_coordinator.schemas.models import (
    Certeza, Coordenadas, Estado, LoteRegistros, LoteUbicaciones, RegistroAfectacion, UbicacionNormalizada,
)
from water_coordinator.services.clasificacion import normalizar
from water_coordinator.tools.geocoding import Geocodificador

log = logging.getLogger(__name__)

# Referencia territorial versionada: distritos de la provincia de Panamá Oeste.
DISTRITOS_PANAMA_OESTE = ["Arraiján", "Capira", "Chame", "La Chorrera", "San Carlos"]
FUENTE_DISTRITOS = "distritos de Panamá Oeste (lista interna v1)"


def zona_por_distrito(texto: str) -> str | None:
    t = normalizar(texto)
    return next((d for d in DISTRITOS_PANAMA_OESTE if normalizar(d) in t), None)


async def ubicar(reg: RegistroAfectacion, geo: Geocodificador | None) -> UbicacionNormalizada:
    base = {"id_afectacion": reg.id_afectacion, "ubicacion_reportada": reg.ubicacion_reportada}
    mencion = reg.datos_adicionales.instalacion_mencionada
    cercanas = [f"{mencion} (mencionada en el reporte; no verificada)"] if mencion and mencion != "incierta" else []
    if not reg.ubicacion_reportada:
        return UbicacionNormalizada(**base, ubicacion_normalizada=None, estado_certeza=Certeza.NO_VERIFICADA,
                                    fuente_referencia="ninguna", estado=Estado.PENDIENTE_INFORMACION,
                                    instalaciones_criticas_cercanas=cercanas,
                                    observaciones_geograficas=["Sin datos territoriales: se solicita aclaración (A2-R4)."])
    normal = " ".join(reg.ubicacion_reportada.split())
    zona = zona_por_distrito(normal)
    obs = ["Umbral de cercanía a instalaciones críticas [PEND]; solo se listan las mencionadas en el reporte."]
    certeza, coords, fuente, alternativas, estado = Certeza.NO_VERIFICADA, None, "ninguna", [], Estado.VALIDADO
    if zona:
        certeza, fuente = Certeza.APROXIMADA, FUENTE_DISTRITOS
        obs.append(f"Zona asociada por nombre de distrito: {zona} (A2-R2).")
    else:
        obs.append("No se reconoce un distrito de Panamá Oeste en el texto.")

    if geo is not None:
        try:
            res = await geo.buscar(f"{normal}, Panamá Oeste, Panamá")
        except Exception as e:  # noqa: BLE001 — sin servicio no se inventan coordenadas
            log.warning("Geocodificador no disponible: %s", type(e).__name__)
            obs.append(f"Geocodificador no disponible ({type(e).__name__}); sin coordenadas.")
            res = None
        if res is not None and len({r.nombre for r in res}) > 1:
            certeza, alternativas = Certeza.AMBIGUA, [r.nombre for r in res]
            obs.append("Varias ubicaciones posibles; no se elige en silencio (A2-R3).")
            if cercanas:
                estado = Estado.PENDIENTE_REVISION
        elif res:
            r = res[0]
            confirmada = r.nivel_punto
            certeza = Certeza.CONFIRMADA if confirmada else Certeza.APROXIMADA
            coords = Coordenadas(lat=r.lat, lon=r.lon, tipo="confirmadas" if confirmada else "estimadas")
            fuente = r.fuente
            if "panama oeste" not in normalizar(r.nombre):
                estado = Estado.PENDIENTE_REVISION
                obs.append("El resultado no indica Panamá Oeste: posible incoherencia territorial (A2-R6).")
        elif res == []:
            obs.append("El geocodificador no devolvió resultados.")
    elif not zona:
        obs.append("Geocodificador no configurado.")
    return UbicacionNormalizada(**base, ubicacion_normalizada=normal, coordenadas=coords, estado_certeza=certeza,
                                zona_comunidad=zona, alternativas=alternativas, instalaciones_criticas_cercanas=cercanas,
                                observaciones_geograficas=obs, fuente_referencia=fuente, estado=estado)


class AgenteGeolocalizacion(RoutedAgent):
    def __init__(self, geo: Geocodificador | None = None):
        super().__init__("Agente 2: geolocalización y validación territorial")
        self.geo = geo

    @message_handler
    async def procesar(self, message: LoteRegistros, ctx: MessageContext) -> LoteUbicaciones:
        return LoteUbicaciones(ubicaciones=[await ubicar(r, self.geo) for r in message.registros])
