"""Agente 1: clasificación, fecha del incidente, datos faltantes, duplicados y modelo de IA (DOC §4.1.I)."""

import json
import re
from datetime import timedelta
from pathlib import Path

from autogen_ext.models.replay import ReplayChatCompletionClient

from conftest import RECIBIDO, registro, reporte
from water_coordinator.agents.ingesta import AgenteIngesta, vincular_duplicados
from water_coordinator.services.observabilidad import Observabilidad
from water_coordinator.schemas.models import Confianza, Estado, TipoAfectacion as T
from water_coordinator.services.clasificacion import EXPRESIONES, HASHTAGS, HASHTAGS_RELEVANCIA, clasificar


def test_hashtags_clasifican_con_confianza_alta():
    assert clasificar("#sinagua en mi casa")["tipo"] == T.FALTA_DE_AGUA
    assert clasificar("#tuberiarota frente al súper")["tipo"] == T.TUBERIA_ROTA
    assert clasificar("#faltadeagua")["confianza"] == Confianza.ALTA


def test_voz_transcrita_sin_tildes_ni_hashtag():
    c = clasificar("Se rompió el tubo y está botando agua en la calle")
    assert c["tipo"] == T.TUBERIA_ROTA and c["confianza"] == Confianza.ALTA
    assert clasificar("la pluma no tiene agua")["confianza"] == Confianza.MEDIA


def test_tuberia_rota_que_causa_falta_de_agua_usa_la_causa():
    c = clasificar("Tubería rota y ahora no hay agua")
    assert c["tipo"] == T.TUBERIA_ROTA
    assert c["consecuencias"] == [T.FALTA_DE_AGUA]


def test_combinacion_no_cubierta_queda_indeterminada_y_en_revision():
    c = clasificar("No hay agua y la poca que sale es agua sucia")
    assert c["tipo"] == T.INDETERMINADO and c["revision"]


def test_idaan_es_relevante_pero_no_fija_tipo():
    c = clasificar("#idaan necesito información")
    assert c["relevante"] and c["tipo"] == T.INDETERMINADO


def test_fecha_del_incidente_desde_texto_y_no_desde_recepcion():
    r = registro("#sinagua en Vista Alegre, Arraiján hace 3 días")
    assert r.fecha_hora_incidente == RECIBIDO - timedelta(days=3)
    assert r.dias_sin_agua == 3


def test_sin_fecha_del_incidente_queda_nula_y_faltante():
    r = registro("#sinagua en Vista Alegre, Arraiján")
    assert r.fecha_hora_incidente is None and r.dias_sin_agua is None
    assert "fecha_hora_incidente" in r.datos_faltantes


def test_desde_el_lunes_y_fechas_explicitas():
    assert registro("#sinagua desde el lunes").dias_sin_agua == 5 + 10 / 24  # sábado 10:00 → lunes 00:00
    assert registro("#sinagua desde el 15/10").fecha_hora_incidente.day == 15
    assert registro("#sinagua desde el 14 de octubre").fecha_hora_incidente.day == 14


def test_no_inventa_personas():
    r = registro("#sinagua en Capira")
    assert r.datos_adicionales.personas_reportadas is None
    assert "unidades o personas afectadas" in r.datos_faltantes


def test_contaminacion_activa_alerta_sanitaria():
    r = registro("#aguacontaminada sale agua turbia")
    assert r.alerta_sanitaria and r.tipo_afectacion == T.AGUA_CONTAMINADA


def test_original_se_conserva():
    texto = "  #sinagua   texto original con   espacios "
    assert registro(texto).descripcion_original == texto


def test_duplicados_se_vinculan_sin_fusionar_y_contradiccion_en_revision():
    a = registro("#sinagua en Vista Alegre, Arraiján hace 1 día")
    b = registro("#sinagua en Vista Alegre, Arraiján hace 4 días")
    vincular_duplicados([a, b])
    assert a.posibles_duplicados == [b.id_afectacion] and b.posibles_duplicados == [a.id_afectacion]
    assert a.estado == b.estado == Estado.PENDIENTE_REVISION


async def test_desacuerdo_del_modelo_baja_confianza_sin_sobrescribir():
    llm = ReplayChatCompletionClient([json.dumps({"tipo": "agua_contaminada", "justificacion": "x"})])
    agente = AgenteIngesta.__new__(AgenteIngesta)
    agente.llm, agente.obs, agente.modelo = llm, Observabilidad(None), "modelo-prueba"
    reg = registro("#sinagua en Capira")
    await agente._contrastar_con_llm(reg)
    assert reg.tipo_afectacion == T.FALTA_DE_AGUA
    assert reg.confianza_clasificacion == Confianza.BAJA and reg.estado == Estado.PENDIENTE_REVISION
    assert reg.sugerencia_llm["tipo"] == "agua_contaminada"


def test_keywords_md_y_codigo_coinciden():
    """docs/KEYWORDS.md documenta exactamente los hashtags que usa el código."""
    md = Path(__file__).parents[1].joinpath("docs/KEYWORDS.md").read_text(encoding="utf-8")
    en_doc = set(re.findall(r"`(#\w+)`", md))
    assert en_doc == set(HASHTAGS) | HASHTAGS_RELEVANCIA
    for frases in EXPRESIONES.values():
        for f in frases:
            assert f"`{f}`" in md, f


def test_ubicacion_termina_en_el_punto():
    from water_coordinator.services.clasificacion import extraer_ubicacion

    assert extraer_ubicacion("Somos 3 edificios en Nuevo Chorrillo, Arraiján. Empezó el lunes.") == "Nuevo Chorrillo, Arraiján"
    assert extraer_ubicacion("Le hablo de la escuela en Barrio Colón, La Chorrera. Se rompió la tubería") == "Barrio Colón, La Chorrera"
    assert extraer_ubicacion("en Vista Alegre, Arraiján no hay agua") == "Vista Alegre, Arraiján"
