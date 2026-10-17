from datetime import datetime

import pytest

from water_coordinator.agents.ingesta import registrar
from water_coordinator.config import Settings
from water_coordinator.persistence.repository import Repositorio
from water_coordinator.schemas.models import TZ_PANAMA, ReporteEntrada

RECIBIDO = datetime(2026, 10, 17, 10, 0, tzinfo=TZ_PANAMA)  # sábado


@pytest.fixture
def settings() -> Settings:
    return Settings(_env_file=None, database_url="sqlite:///:memory:")


@pytest.fixture
def repo() -> Repositorio:
    return Repositorio("sqlite:///:memory:")


def reporte(texto: str, recibido: datetime = RECIBIDO, contacto: str | None = "sim:prueba") -> ReporteEntrada:
    return ReporteEntrada(canal="archivo_prueba", texto=texto, recibido_en=recibido, contacto=contacto)


def registro(texto: str, recibido: datetime = RECIBIDO):
    return registrar(reporte(texto, recibido))
