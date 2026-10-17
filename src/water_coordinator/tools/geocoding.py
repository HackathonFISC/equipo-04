"""Geocodificación intercambiable. Inicial: Nominatim (OpenStreetMap).

Política de uso de Nominatim: máx. 1 solicitud/s, User-Agent identificable, caché de resultados, atribución a OSM.
Solo se envía el texto de la ubicación; nunca teléfonos ni el reporte completo.
"""

import asyncio
import time
from typing import Protocol

import httpx
from pydantic import BaseModel

from water_coordinator.config import Settings
from water_coordinator.tools.estado import EstadoIntegracion as E
from water_coordinator.tools.estado import InformeIntegracion, informe


class ResultadoGeocodificacion(BaseModel):
    nombre: str
    lat: float
    lon: float
    nivel_punto: bool  # True si es dirección/edificio (punto preciso); False si es área (barrio, ciudad)
    fuente: str


class Geocodificador(Protocol):
    nombre: str

    async def buscar(self, consulta: str) -> list[ResultadoGeocodificacion]: ...


class NominatimGeocoder:
    nombre = "nominatim"

    def __init__(self, base_url: str, user_agent: str, email: str = "", cliente: httpx.AsyncClient | None = None):
        self.base_url, self.headers, self.email = base_url.rstrip("/"), {"User-Agent": user_agent}, email
        self.cliente = cliente
        self.cache: dict[str, list[ResultadoGeocodificacion]] = {}
        self._ultima = 0.0
        self._lock = asyncio.Lock()

    async def buscar(self, consulta: str) -> list[ResultadoGeocodificacion]:
        if consulta in self.cache:
            return self.cache[consulta]
        async with self._lock:
            espera = 1.0 - (time.monotonic() - self._ultima)
            if espera > 0:
                await asyncio.sleep(espera)
            params = {"q": consulta, "format": "jsonv2", "countrycodes": "pa", "limit": 5, "addressdetails": 0}
            if self.email:
                params["email"] = self.email
            cliente = self.cliente or httpx.AsyncClient(timeout=10)
            try:
                r = await cliente.get(f"{self.base_url}/search", params=params, headers=self.headers)
                r.raise_for_status()
            finally:
                self._ultima = time.monotonic()
                if self.cliente is None:
                    await cliente.aclose()
        res = [
            ResultadoGeocodificacion(
                nombre=x["display_name"], lat=float(x["lat"]), lon=float(x["lon"]),
                nivel_punto=int(x.get("place_rank", 0)) >= 28, fuente="OpenStreetMap/Nominatim",
            )
            for x in r.json()
        ]
        self.cache[consulta] = res
        return res


def crear_geocodificador(s: Settings) -> Geocodificador | None:
    if s.geocoder_provider == "nominatim" and s.nominatim_user_agent:
        return NominatimGeocoder(s.nominatim_base_url, s.nominatim_user_agent, s.nominatim_email)
    return None


async def estado(s: Settings, comprobar: bool = False) -> InformeIntegracion:
    if s.geocoder_provider == "none":
        return informe("geocodificacion", "none", E.NOT_CONFIGURED, "GEOCODER_PROVIDER=none: ubicaciones quedan 'no verificadas' o 'aproximadas'.")
    if not s.nominatim_user_agent:
        return informe("geocodificacion", "nominatim", E.NOT_CONFIGURED, "Falta NOMINATIM_USER_AGENT (identificación con contacto, exigida por la política de uso).")
    if not comprobar:
        return informe("geocodificacion", "nominatim", E.CONFIGURED, s.nominatim_base_url)
    try:
        r = await crear_geocodificador(s).buscar("La Chorrera, Panamá Oeste")
        return informe("geocodificacion", "nominatim", E.CONNECTED, f"{len(r)} resultados de prueba.")
    except Exception as e:  # noqa: BLE001
        return informe("geocodificacion", "nominatim", E.ERROR, type(e).__name__)
