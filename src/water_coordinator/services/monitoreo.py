"""Logs estructurados (JSON) con redacción de secretos. Proveedores externos (p. ej. Sentry) opcionales y desactivados."""

import json
import logging

from pydantic import SecretStr

from water_coordinator.config import Settings


class FiltroSecretos(logging.Filter):
    """Reemplaza cualquier valor secreto configurado por *** antes de escribir el log."""

    def __init__(self, secretos: list[str]):
        super().__init__()
        self.secretos = [s for s in secretos if s and len(s) >= 4]

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        for s in self.secretos:
            msg = msg.replace(s, "***")
        record.msg, record.args = msg, None
        if record.exc_info:
            texto = logging.Formatter().formatException(record.exc_info)
            for s in self.secretos:
                texto = texto.replace(s, "***")
            record.exc_text, record.exc_info = texto, None
        return True


class FormatoJSON(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        datos = {"ts": self.formatTime(record), "nivel": record.levelname, "logger": record.name, "msg": record.getMessage()}
        if record.exc_text:
            datos["error"] = record.exc_text
        return json.dumps(datos, ensure_ascii=False)


def secretos_de(settings: Settings) -> list[str]:
    return [v.get_secret_value() for v in settings.__dict__.values() if isinstance(v, SecretStr)]


def configurar_logs(settings: Settings) -> None:
    h = logging.StreamHandler()
    h.setFormatter(FormatoJSON())
    h.addFilter(FiltroSecretos(secretos_de(settings)))
    raiz = logging.getLogger()
    raiz.handlers[:] = [h]
    raiz.setLevel(settings.log_level.upper())
    # Los eventos de AutoGen incluyen los mensajes completos (con contactos): no se registran en INFO.
    for nombre in ("autogen_core", "autogen_core.events", "httpx"):
        logging.getLogger(nombre).setLevel(logging.WARNING)
