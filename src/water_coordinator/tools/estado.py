"""Estado de cada integración. CONNECTED solo se informa tras una comprobación real (`status --check`)."""

from enum import StrEnum

from pydantic import BaseModel


class EstadoIntegracion(StrEnum):
    NOT_CONFIGURED = "NOT_CONFIGURED"
    CONFIGURED = "CONFIGURED"
    CONNECTED = "CONNECTED"
    ERROR = "ERROR"
    DISABLED = "DISABLED"


class InformeIntegracion(BaseModel):
    nombre: str
    proveedor: str
    estado: EstadoIntegracion
    detalle: str


def informe(nombre: str, proveedor: str, estado: EstadoIntegracion, detalle: str) -> InformeIntegracion:
    return InformeIntegracion(nombre=nombre, proveedor=proveedor, estado=estado, detalle=detalle)
