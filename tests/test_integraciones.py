"""Integraciones sin credenciales ni Internet: estados NOT_CONFIGURED, bloqueos de envío, redacción de secretos."""

import hashlib
import hmac
import logging

import httpx
import pytest

from water_coordinator.agents.geolocalizacion import ubicar
from water_coordinator.config import Settings
from water_coordinator.main import estado
from water_coordinator.schemas.models import Certeza, MensajeSaliente
from water_coordinator.services.monitoreo import FiltroSecretos
from water_coordinator.tools import llm
from water_coordinator.tools.geocoding import NominatimGeocoder
from water_coordinator.tools.messaging import ErrorMensajeria, WhatsAppCloudApiProvider, verificar_firma_webhook
from water_coordinator.tools.routing import OSRMRouter
from water_coordinator.tools.storage import AlmacenLocal, ErrorAlmacenamiento
from conftest import registro


async def test_sin_credenciales_todo_not_configured(settings):
    estados = {i["nombre"]: i["estado"] for i in await estado(settings, comprobar=True)}
    for nombre in ("modelo_ia", "geocodificacion", "rutas", "transcripcion", "mapas"):
        assert estados[nombre] == "NOT_CONFIGURED", nombre
    assert estados["mensajeria"] == "CONFIGURED"  # simulada
    assert "CONNECTED" not in estados.values()


def test_llm_intercambiable_sin_tocar_logica():
    assert llm.crear_cliente(Settings(_env_file=None)) is None
    s = Settings(_env_file=None, model_provider="openai_compatible", model_name="llama3", model_base_url="http://localhost:11434/v1")
    assert type(llm.crear_cliente(s)).__name__ == "OpenAIChatCompletionClient"
    s = Settings(_env_file=None, model_provider="anthropic", model_name="claude-sonnet-5-5", model_api_key="x" * 10)
    assert type(llm.crear_cliente(s)).__name__ == "AnthropicChatCompletionClient"
    assert llm.faltantes(Settings(_env_file=None, model_provider="openai", model_name="m")) == ["MODEL_API_KEY"]


async def test_whatsapp_no_envia_sin_habilitar(settings):
    m = MensajeSaliente(id_afectacion="A", destinatario="sim:x", texto="t", tipo="estado", estado_referido="propuesto")
    with pytest.raises(ErrorMensajeria, match="desactivado"):
        await WhatsAppCloudApiProvider(settings).enviar(m)


def test_firma_webhook():
    cuerpo, secreto = b'{"x":1}', "secreto-app"
    firma = "sha256=" + hmac.new(secreto.encode(), cuerpo, hashlib.sha256).hexdigest()
    assert verificar_firma_webhook(cuerpo, firma, secreto)
    assert not verificar_firma_webhook(cuerpo, "sha256=00", secreto)
    assert not verificar_firma_webhook(cuerpo, None, secreto)


def test_secretos_no_aparecen_en_logs():
    rec = logging.LogRecord("t", logging.ERROR, "", 0, "token=%s", ("TOKEN-SUPER-SECRETO",), None)
    FiltroSecretos(["TOKEN-SUPER-SECRETO"]).filter(rec)
    assert "TOKEN-SUPER-SECRETO" not in rec.getMessage()
    assert "SUPER" not in repr(Settings(_env_file=None, whatsapp_access_token="TOKEN-SUPER-SECRETO"))


def test_almacen_valida_extension_tamano_y_nombre(tmp_path):
    a = AlmacenLocal(Settings(_env_file=None, storage_dir=tmp_path, storage_max_file_mb=1))
    ruta = a.guardar(b"hola", "../../malicioso.txt")
    assert ruta.parent == tmp_path and "malicioso" not in ruta.name
    with pytest.raises(ErrorAlmacenamiento):
        a.guardar(b"x", "virus.exe")
    with pytest.raises(ErrorAlmacenamiento):
        a.guardar(b"x" * (1024 * 1024 + 1), "grande.txt")
    assert a.purgar_vencidos() == []  # sin política de retención no se borra nada


def _cliente(respuesta: dict | list, status: int = 200) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.MockTransport(lambda req: httpx.Response(status, json=respuesta)))


async def test_nominatim_un_resultado_de_area_es_aproximado():
    geo = NominatimGeocoder("https://x", "pruebas", cliente=_cliente(
        [{"display_name": "Vista Alegre, Arraiján, Panamá Oeste, Panamá", "lat": "8.9", "lon": "-79.7", "place_rank": 20}]))
    u = await ubicar(registro("#sinagua en Vista Alegre, Arraiján"), geo)
    assert u.estado_certeza == Certeza.APROXIMADA and u.coordenadas.tipo == "estimadas"


async def test_nominatim_varios_resultados_es_ambiguo_sin_coordenadas():
    geo = NominatimGeocoder("https://x", "pruebas", cliente=_cliente([
        {"display_name": "A, Panamá Oeste", "lat": "1", "lon": "1", "place_rank": 20},
        {"display_name": "B, Panamá Oeste", "lat": "2", "lon": "2", "place_rank": 20}]))
    u = await ubicar(registro("#sinagua en Santa Rita"), geo)
    assert u.estado_certeza == Certeza.AMBIGUA and u.coordenadas is None and len(u.alternativas) == 2


async def test_geocodificador_caido_no_inventa_coordenadas():
    geo = NominatimGeocoder("https://x", "pruebas", cliente=_cliente({"error": "x"}, 503))
    u = await ubicar(registro("#sinagua en Vista Alegre, Arraiján"), geo)
    assert u.coordenadas is None and u.estado_certeza == Certeza.APROXIMADA  # solo por distrito
    assert any("no disponible" in o for o in u.observaciones_geograficas)


async def test_sin_geocodificador_y_sin_distrito_no_verificada():
    u = await ubicar(registro("#sinagua en Villa Desconocida"), None)
    assert u.estado_certeza == Certeza.NO_VERIFICADA and u.coordenadas is None


async def test_osrm_distancias_por_tramo():
    r = OSRMRouter("https://x", cliente=_cliente({"code": "Ok", "routes": [{"legs": [{"distance": 12345}, {"distance": 1000}]}]}))
    assert await r.distancias_km([(1, 1), (2, 2), (3, 3)]) == [12.345, 1.0]


def test_env_example_carga_sin_errores_y_sin_secretos():
    from pathlib import Path

    s = Settings(_env_file=Path(__file__).parents[1] / ".env.example")
    assert s.model_provider == "none" and s.organizacion_lat is None and s.horarios_file is None
    assert s.storage_retention_days is None and s.model_api_key is None and not s.whatsapp_send_enabled
