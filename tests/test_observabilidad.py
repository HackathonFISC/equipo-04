"""Instrumentación de Langfuse: desactivada por defecto, tolerante a fallos y sin datos sensibles."""

import json
import logging
from contextlib import contextmanager

from conftest import RECIBIDO, reporte
from water_coordinator.config import Settings
from water_coordinator.orchestration.pipeline import procesar
from water_coordinator.services.observabilidad import Observabilidad, crear_observabilidad
from water_coordinator.services.parametros import HORARIOS_POR_DEFECTO

TEXTO_PRIVADO = "#sinagua en la escuela de Capira desde ayer, llamar a Juana Pérez"
CONTACTO = "sim:contacto-privado-001"


class SpanFalso:
    def __init__(self, registro, nombre):
        self.registro, self.nombre = registro, nombre

    def update(self, **campos):
        self.registro.append(("update", self.nombre, campos))


class ClienteFalso:
    """Imita la API usada de Langfuse v5 y guarda todo lo que se le enviaría."""

    def __init__(self):
        self.registro, self.vaciado = [], 0

    def start_as_current_observation(self, *, name, as_type="span", input=None, **extra):
        self.registro.append(("start", name, {"as_type": as_type, "input": input, **extra}))

        @contextmanager
        def cm():
            yield SpanFalso(self.registro, name)

        return cm()

    def flush(self):
        self.vaciado += 1


class ClienteRoto:
    def start_as_current_observation(self, **_):
        raise ConnectionError("langfuse caído")

    def flush(self):
        raise ConnectionError("langfuse caído")


async def _ejecutar(repo, obs):
    r = reporte(TEXTO_PRIVADO, contacto=CONTACTO)
    return await procesar([r], repo, RECIBIDO, HORARIOS_POR_DEFECTO, obs=obs)


def test_desactivada_por_defecto_y_sin_claves():
    assert not crear_observabilidad(Settings(_env_file=None)).activa
    assert not crear_observabilidad(Settings(_env_file=None, langfuse_tracing_enabled=True)).activa  # faltan claves


async def test_pipeline_funciona_sin_langfuse(repo):
    res = await _ejecutar(repo, Observabilidad(None))
    assert res.planes.planes and res.id_ejecucion.startswith("EJE-")


async def test_traza_con_etapas_de_cada_agente_y_sin_datos_sensibles(repo):
    cliente = ClienteFalso()
    res = await _ejecutar(repo, Observabilidad(cliente))
    abiertos = [n for tipo, n, _ in cliente.registro if tipo == "start"]
    assert abiertos == ["procesar-reportes", "clasificar-reportes", "geolocalizar-afectaciones", "priorizar-afectaciones",
                        "planificar-recursos", "redactar-mensajes"]
    raiz = next(d for t, n, d in cliente.registro if t == "start" and n == "procesar-reportes")
    assert raiz["metadata"]["id_ejecucion"] == res.id_ejecucion and raiz["input"]["reportes"] == 1
    enviado = json.dumps(cliente.registro, default=str, ensure_ascii=False)
    assert "Juana" not in enviado and CONTACTO not in enviado and TEXTO_PRIVADO not in enviado
    assert '"envio": "simulado_no_enviado"' in enviado


async def test_langfuse_caido_no_interrumpe(repo, caplog):
    obs = Observabilidad(ClienteRoto())
    with caplog.at_level(logging.WARNING):
        res = await _ejecutar(repo, obs)
        obs.vaciar()
    assert res.planes.planes
    assert any("Langfuse" in r.getMessage() for r in caplog.records)


async def test_error_del_pipeline_se_marca_y_se_propaga(repo):
    cliente = ClienteFalso()
    obs = Observabilidad(cliente)
    try:
        with obs.etapa("clasificar-reportes"):
            raise ValueError("fallo de prueba")
    except ValueError:
        pass
    else:
        raise AssertionError("la excepción debía propagarse")
    assert ("update", "clasificar-reportes", {"level": "ERROR", "status_message": "ValueError"}) in cliente.registro


def test_vaciar_llama_flush():
    cliente = ClienteFalso()
    Observabilidad(cliente).vaciar()
    assert cliente.vaciado == 1


async def test_cliente_real_con_servidor_inaccesible_no_rompe(repo, caplog):
    """SDK real de Langfuse apuntando a un puerto cerrado: el pipeline termina y los secretos no salen en los logs."""
    s = Settings(_env_file=None, langfuse_tracing_enabled=True, langfuse_public_key="pk-lf-PRUEBA-111",
                 langfuse_secret_key="sk-lf-PRUEBA-222", langfuse_base_url="http://127.0.0.1:9")
    obs = crear_observabilidad(s)
    assert obs.activa
    with caplog.at_level(logging.DEBUG):
        res = await _ejecutar(repo, obs)
        obs.vaciar()
        obs.cliente.shutdown()
    assert res.planes.planes
    assert "sk-lf-PRUEBA-222" not in caplog.text


async def test_llamada_al_modelo_es_generation_con_modelo_y_tokens(repo):
    import json as _json

    from autogen_core.models import CreateResult, RequestUsage
    from autogen_ext.models.replay import ReplayChatCompletionClient

    respuesta = CreateResult(finish_reason="stop", content=_json.dumps({"tipo": "falta_de_agua", "justificacion": "x"}),
                             usage=RequestUsage(prompt_tokens=120, completion_tokens=9), cached=False)
    cliente = ClienteFalso()
    r = reporte(TEXTO_PRIVADO, contacto=CONTACTO)
    await procesar([r], repo, RECIBIDO, HORARIOS_POR_DEFECTO, llm=ReplayChatCompletionClient([respuesta]),
                   obs=Observabilidad(cliente), modelo="claude-sonnet-5-5")
    gen = next(d for t, n, d in cliente.registro if t == "start" and n == "contrastar-clasificacion")
    assert gen["as_type"] == "generation" and gen["model"] == "claude-sonnet-5-5"
    salida = next(d for t, n, d in cliente.registro if t == "update" and n == "contrastar-clasificacion")
    assert salida["usage_details"] == {"input": 120, "output": 9}
    assert "Juana" not in _json.dumps(cliente.registro, default=str, ensure_ascii=False)


def test_mascara_oculta_contactos_y_telefonos():
    from water_coordinator.services.observabilidad import enmascarar

    datos = {"a": "llamar a sim:usuario-001 o al +507 6123-4567", "b": ["6123-4567", 3]}
    assert enmascarar(data=datos) == {"a": "llamar a [oculto] o al [oculto]", "b": ["[oculto]", 3]}
