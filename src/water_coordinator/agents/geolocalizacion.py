"""Agente 2 — Geolocalización (DOC §4.2). Nunca presenta una ubicación estimada como confirmada."""

import logging

from autogen_core import MessageContext, RoutedAgent, message_handler

from water_coordinator.schemas.models import (
    Certeza, Coordenadas, Estado, LoteRegistros, LoteUbicaciones, RegistroAfectacion, UbicacionNormalizada,
)
from water_coordinator.services.clasificacion import normalizar
from water_coordinator.services.territorio import FUENTE, comunidad_en, distrito_en
from water_coordinator.tools.geocoding import Geocodificador

log = logging.getLogger(__name__)


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
    zona, comunidad = distrito_en(normal), None
    obs = ["Umbral de cercanía a instalaciones críticas [PEND]; solo se listan las mencionadas en el reporte."]
    certeza, coords, fuente, alternativas, estado = Certeza.NO_VERIFICADA, None, "ninguna", [], Estado.VALIDADO
    if c := comunidad_en(normal):
        comunidad, distrito_cat = c
        if zona and zona != distrito_cat:
            # Comunidad y distrito incompatibles: se conservan ambas lecturas (A2-R3 / §4.2.C).
            certeza, alternativas = Certeza.AMBIGUA, [f"{comunidad}, {distrito_cat}", zona]
            obs.append(f"La comunidad {comunidad} pertenece a {distrito_cat}, pero el texto dice {zona}.")
        else:
            zona = distrito_cat
            certeza = Certeza.APROXIMADA
            obs.append(f"Comunidad asociada por catálogo: {comunidad} ({distrito_cat}) (A2-R2).")
        fuente = FUENTE
    elif zona:
        certeza, fuente = Certeza.APROXIMADA, FUENTE
        obs.append(f"Zona asociada por nombre de distrito: {zona} (A2-R2).")
    else:
        obs.append("No se reconoce un distrito ni una comunidad del catálogo en el texto.")

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
        elif res and certeza != Certeza.AMBIGUA:
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
                                zona_comunidad=zona, comunidad=comunidad, alternativas=alternativas, instalaciones_criticas_cercanas=cercanas,
                                observaciones_geograficas=obs, fuente_referencia=fuente, estado=estado)


class AgenteGeolocalizacion(RoutedAgent):
    def __init__(self, geo: Geocodificador | None = None):
        super().__init__("Agente 2: geolocalización y validación territorial")
        self.geo = geo

    @message_handler
    async def procesar(self, message: LoteRegistros, ctx: MessageContext) -> LoteUbicaciones:
        return LoteUbicaciones(ubicaciones=[await ubicar(r, self.geo) for r in message.registros])
