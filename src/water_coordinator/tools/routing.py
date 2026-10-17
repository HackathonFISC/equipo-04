"""Cálculo de rutas intercambiable. Inicial: OSRM. El servidor público de demostración no garantiza disponibilidad."""

from typing import Protocol

import httpx

from water_coordinator.config import Settings
from water_coordinator.tools.estado import EstadoIntegracion as E
from water_coordinator.tools.estado import InformeIntegracion, informe


class Enrutador(Protocol):
    nombre: str

    async def distancias_km(self, puntos: list[tuple[float, float]]) -> list[float]:
        """Distancia por tramo entre puntos consecutivos (lat, lon). Lanza excepción si el servicio falla."""
        ...


class OSRMRouter:
    nombre = "osrm"

    def __init__(self, base_url: str, perfil: str = "driving", cliente: httpx.AsyncClient | None = None):
        self.base_url, self.perfil, self.cliente = base_url.rstrip("/"), perfil, cliente

    async def distancias_km(self, puntos: list[tuple[float, float]]) -> list[float]:
        if len(puntos) < 2:
            raise ValueError("Se necesitan al menos dos puntos.")
        coords = ";".join(f"{lon},{lat}" for lat, lon in puntos)  # OSRM usa lon,lat
        cliente = self.cliente or httpx.AsyncClient(timeout=20)
        try:
            r = await cliente.get(f"{self.base_url}/route/v1/{self.perfil}/{coords}", params={"overview": "false"})
            r.raise_for_status()
        finally:
            if self.cliente is None:
                await cliente.aclose()
        datos = r.json()
        if datos.get("code") != "Ok":
            raise RuntimeError(f"OSRM respondió {datos.get('code')}")
        return [round(leg["distance"] / 1000, 3) for leg in datos["routes"][0]["legs"]]


def crear_enrutador(s: Settings) -> Enrutador | None:
    return OSRMRouter(s.osrm_base_url, s.osrm_profile) if s.osrm_base_url else None


async def estado(s: Settings, comprobar: bool = False) -> InformeIntegracion:
    if not s.osrm_base_url:
        return informe("rutas", "osrm", E.NOT_CONFIGURED, "Falta OSRM_BASE_URL. Sin rutas no se calculan distancias (no se inventan).")
    detalle = s.osrm_base_url
    if s.organizacion_lat is None or s.organizacion_lon is None:
        detalle += " | Falta ubicación de la organización (ORGANIZACION_LAT/LON) [PEND]"
    if not comprobar:
        return informe("rutas", "osrm", E.CONFIGURED, detalle)
    try:
        # Dos puntos públicos de referencia (La Chorrera ↔ Arraiján, centros aproximados) solo para comprobar el servicio.
        km = await crear_enrutador(s).distancias_km([(8.8803, -79.7833), (8.9516, -79.6600)])
        return informe("rutas", "osrm", E.CONNECTED, f"Tramo de prueba: {km[0]} km.")
    except Exception as e:  # noqa: BLE001
        return informe("rutas", "osrm", E.ERROR, type(e).__name__)
