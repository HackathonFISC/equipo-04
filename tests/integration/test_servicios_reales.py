"""Pruebas contra servicios reales. Se activan una a una con RUN_INTEGRATION_<PROVEEDOR>=1 y la configuración de .env.

Ninguna envía mensajes de WhatsApp ni genera gastos salvo la de modelo de IA (una petición mínima).
"""

import os

import pytest

from water_coordinator.config import Settings
from water_coordinator.tools import geocoding, llm, messaging, routing, transcription

pytestmark = pytest.mark.integration


def activa(nombre: str):
    return pytest.mark.skipif(os.getenv(f"RUN_INTEGRATION_{nombre}") != "1", reason=f"RUN_INTEGRATION_{nombre}=1 no definido")


@pytest.fixture
def s() -> Settings:
    return Settings()


@activa("LLM")
async def test_modelo_ia(s):
    assert (await llm.estado(s, comprobar=True)).estado == "CONNECTED"


@activa("NOMINATIM")
async def test_nominatim(s):
    assert (await geocoding.estado(s, comprobar=True)).estado == "CONNECTED"


@activa("OSRM")
async def test_osrm(s):
    assert (await routing.estado(s, comprobar=True)).estado == "CONNECTED"


@activa("WHATSAPP")
async def test_whatsapp_lectura_sin_envio(s):
    assert (await messaging.estado(s, comprobar=True)).estado == "CONNECTED"


@activa("WHISPER")
async def test_whisper_local(s, tmp_path):
    ruta = os.getenv("WHISPER_AUDIO_PRUEBA")
    if not ruta:
        pytest.skip("Definir WHISPER_AUDIO_PRUEBA con un audio de prueba sin datos personales.")
    from pathlib import Path

    t = await transcription.crear_transcriptor(s).transcribir(Path(ruta))
    assert t.ejecucion == "local" and t.texto
