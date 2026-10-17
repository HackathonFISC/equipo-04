"""Transcripción intercambiable: Whisper local (faster-whisper, extra opcional) o Google Cloud Speech-to-Text (opcional, de pago).

El resultado indica siempre si se ejecutó localmente o en un proveedor remoto.
"""

import importlib.util
from pathlib import Path
from typing import Literal, Protocol

from pydantic import BaseModel

from water_coordinator.config import Settings
from water_coordinator.tools.estado import EstadoIntegracion as E
from water_coordinator.tools.estado import InformeIntegracion, informe


class Transcripcion(BaseModel):
    texto: str
    proveedor: str
    ejecucion: Literal["local", "remoto"]
    idioma: str | None = None
    archivo: str


class Transcriptor(Protocol):
    async def transcribir(self, ruta: Path) -> Transcripcion: ...


class WhisperLocal:
    def __init__(self, modelo: str, dispositivo: str):
        from faster_whisper import WhisperModel  # extra opcional: transcripcion-local

        self.modelo = WhisperModel(modelo, device=dispositivo, compute_type="int8")

    async def transcribir(self, ruta: Path) -> Transcripcion:
        segmentos, info = self.modelo.transcribe(str(ruta), language="es")
        return Transcripcion(texto=" ".join(s.text.strip() for s in segmentos), proveedor="whisper_local",
                             ejecucion="local", idioma=info.language, archivo=ruta.name)


class GoogleSpeech:
    def __init__(self, idioma: str):
        from google.cloud import speech  # extra opcional: transcripcion-google

        self.speech, self.cliente, self.idioma = speech, speech.SpeechClient(), idioma

    async def transcribir(self, ruta: Path) -> Transcripcion:
        audio = self.speech.RecognitionAudio(content=ruta.read_bytes())
        cfg = self.speech.RecognitionConfig(language_code=self.idioma)
        r = self.cliente.recognize(config=cfg, audio=audio)
        texto = " ".join(x.alternatives[0].transcript for x in r.results if x.alternatives)
        return Transcripcion(texto=texto, proveedor="google_stt", ejecucion="remoto", idioma=self.idioma, archivo=ruta.name)


def _instalado(modulo: str) -> bool:
    try:
        return importlib.util.find_spec(modulo) is not None
    except ModuleNotFoundError:
        return False


def crear_transcriptor(s: Settings) -> Transcriptor | None:
    if s.transcription_provider == "whisper_local" and _instalado("faster_whisper"):
        return WhisperLocal(s.whisper_model, s.whisper_device)
    if s.transcription_provider == "google" and _instalado("google.cloud.speech") and s.google_application_credentials:
        return GoogleSpeech(s.google_stt_language)
    return None


async def estado(s: Settings, comprobar: bool = False) -> InformeIntegracion:
    p = s.transcription_provider
    if p == "none":
        return informe("transcripcion", "none", E.NOT_CONFIGURED, "TRANSCRIPTION_PROVIDER=none: se usan transcripciones de prueba en texto.")
    if p == "whisper_local":
        if not _instalado("faster_whisper"):
            return informe("transcripcion", p, E.NOT_CONFIGURED, "Instalar el extra: uv sync --extra transcripcion-local")
        return informe("transcripcion", p, E.CONFIGURED, f"Modelo {s.whisper_model} en {s.whisper_device} (local; descarga el modelo la primera vez).")
    if p == "google":
        falta = [n for n, ok in (("extra transcripcion-google", _instalado("google.cloud.speech")),
                                  ("GOOGLE_APPLICATION_CREDENTIALS", bool(s.google_application_credentials))) if not ok]
        if falta:
            return informe("transcripcion", p, E.NOT_CONFIGURED, f"Faltan: {', '.join(falta)}")
        return informe("transcripcion", p, E.CONFIGURED, "Remoto (de pago); sin comprobar conexión.")
    return informe("transcripcion", p, E.ERROR, "Proveedor desconocido.")
