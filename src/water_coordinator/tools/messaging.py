"""Mensajería intercambiable (DEC-20/25): MessagingProvider con implementación simulada y adaptador de WhatsApp Cloud API.

Ningún mensaje sale del sistema salvo que WhatsApp esté configurado Y WHATSAPP_SEND_ENABLED=true (aprobación explícita).
"""

import hashlib
import hmac
from typing import Protocol

import httpx

from water_coordinator.config import Settings
from water_coordinator.schemas.models import MensajeSaliente
from water_coordinator.tools.estado import EstadoIntegracion as E
from water_coordinator.tools.estado import InformeIntegracion, informe


class ErrorMensajeria(RuntimeError):
    pass


class MessagingProvider(Protocol):
    nombre: str

    async def enviar(self, mensaje: MensajeSaliente) -> dict: ...


class MockMessagingProvider:
    """Bandeja de salida en memoria. No usa red."""

    nombre = "mock"

    def __init__(self):
        self.bandeja: list[MensajeSaliente] = []

    async def enviar(self, mensaje: MensajeSaliente) -> dict:
        self.bandeja.append(mensaje)
        return {"proveedor": "mock", "enviado_externamente": False, "id_mensaje": mensaje.id_mensaje}


class WhatsAppCloudApiProvider:
    nombre = "whatsapp_cloud"
    URL = "https://graph.facebook.com/{version}/{phone_id}/messages"

    def __init__(self, s: Settings, cliente: httpx.AsyncClient | None = None):
        self.s, self.cliente = s, cliente

    async def enviar(self, mensaje: MensajeSaliente) -> dict:
        if not self.s.whatsapp_send_enabled:
            raise ErrorMensajeria("Envío real desactivado (WHATSAPP_SEND_ENABLED=false). Requiere aprobación explícita.")
        if faltantes_whatsapp(self.s):
            raise ErrorMensajeria("WhatsApp no configurado: " + ", ".join(faltantes_whatsapp(self.s)))
        url = self.URL.format(version=self.s.whatsapp_api_version, phone_id=self.s.whatsapp_phone_number_id)
        cuerpo = {"messaging_product": "whatsapp", "to": mensaje.destinatario, "type": "text", "text": {"body": mensaje.texto}}
        headers = {"Authorization": f"Bearer {self.s.whatsapp_access_token.get_secret_value()}"}
        cliente = self.cliente or httpx.AsyncClient(timeout=15)
        try:
            r = await cliente.post(url, json=cuerpo, headers=headers)
        finally:
            if self.cliente is None:
                await cliente.aclose()
        if r.status_code >= 400:
            raise ErrorMensajeria(f"WhatsApp respondió HTTP {r.status_code}")  # sin cuerpo: puede reflejar datos
        return {"proveedor": "whatsapp_cloud", "enviado_externamente": True, "respuesta": r.json()}


def verificar_firma_webhook(cuerpo: bytes, firma_header: str | None, app_secret: str) -> bool:
    """Valida X-Hub-Signature-256 de los webhooks entrantes de Meta (frontera de confianza)."""
    if not firma_header or not firma_header.startswith("sha256=") or not app_secret:
        return False
    esperado = hmac.new(app_secret.encode(), cuerpo, hashlib.sha256).hexdigest()
    return hmac.compare_digest(esperado, firma_header.removeprefix("sha256="))


def faltantes_whatsapp(s: Settings) -> list[str]:
    pares = [("WHATSAPP_ACCESS_TOKEN", s.whatsapp_access_token), ("WHATSAPP_PHONE_NUMBER_ID", s.whatsapp_phone_number_id),
             ("WHATSAPP_APP_SECRET", s.whatsapp_app_secret), ("WHATSAPP_VERIFY_TOKEN", s.whatsapp_verify_token)]
    return [n for n, v in pares if not v]


def crear_mensajeria(s: Settings) -> MessagingProvider:
    if s.messaging_provider == "whatsapp_cloud":
        return WhatsAppCloudApiProvider(s)
    return MockMessagingProvider()


async def estado(s: Settings, comprobar: bool = False) -> InformeIntegracion:
    if s.messaging_provider != "whatsapp_cloud":
        return informe("mensajeria", "mock", E.CONFIGURED, "Simulada: no se envían mensajes reales. WhatsApp Cloud API: NOT_CONFIGURED.")
    if f := faltantes_whatsapp(s):
        return informe("mensajeria", "whatsapp_cloud", E.NOT_CONFIGURED, f"Faltan: {', '.join(f)}")
    if not s.whatsapp_send_enabled:
        return informe("mensajeria", "whatsapp_cloud", E.DISABLED, "Credenciales presentes; envío desactivado (WHATSAPP_SEND_ENABLED=false).")
    if not comprobar:
        return informe("mensajeria", "whatsapp_cloud", E.CONFIGURED, "Envío habilitado; sin comprobar conexión.")
    try:  # lectura del número (no envía mensajes)
        url = f"https://graph.facebook.com/{s.whatsapp_api_version}/{s.whatsapp_phone_number_id}"
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(url, headers={"Authorization": f"Bearer {s.whatsapp_access_token.get_secret_value()}"})
        ok = r.status_code < 400
        return informe("mensajeria", "whatsapp_cloud", E.CONNECTED if ok else E.ERROR, f"HTTP {r.status_code}")
    except Exception as e:  # noqa: BLE001
        return informe("mensajeria", "whatsapp_cloud", E.ERROR, type(e).__name__)
