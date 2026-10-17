"""Cliente de modelo de IA intercambiable (AutoGen ChatCompletionClient), configurado por variables de entorno.

La lógica de negocio solo recibe un `ChatCompletionClient | None`; cambiar de proveedor no la modifica.
"""

from autogen_core.models import ChatCompletionClient, ModelInfo, UserMessage

from water_coordinator.config import Settings
from water_coordinator.tools.estado import EstadoIntegracion as E
from water_coordinator.tools.estado import InformeIntegracion, informe

# Capacidades mínimas que se declaran para modelos de endpoints compatibles con OpenAI (Ollama, vLLM, etc.).
MODEL_INFO_GENERICO = ModelInfo(vision=False, function_calling=False, json_output=True, family="unknown", structured_output=False)


def faltantes(s: Settings) -> list[str]:
    falta = [] if s.model_name else ["MODEL_NAME"]
    if s.model_provider in ("openai", "anthropic") and not s.model_api_key:
        falta.append("MODEL_API_KEY")
    if s.model_provider == "openai_compatible" and not s.model_base_url:
        falta.append("MODEL_BASE_URL")
    return falta


def crear_cliente(s: Settings) -> ChatCompletionClient | None:
    """None si no hay proveedor configurado: el sistema funciona con reglas deterministas."""
    if s.model_provider == "none" or faltantes(s):
        return None
    clave = s.model_api_key.get_secret_value() if s.model_api_key else None
    if s.model_provider == "anthropic":
        from autogen_ext.models.anthropic import AnthropicChatCompletionClient

        # autogen-ext 0.7.x requiere anthropic<1: el SDK 1.x ya no acepta el `temperature` que autogen-ext envía siempre.
        cabeceras = {"anthropic-workspace-id": s.model_workspace_id} if s.model_workspace_id else None
        return AnthropicChatCompletionClient(model=s.model_name, api_key=clave, default_headers=cabeceras)
    from autogen_ext.models.openai import OpenAIChatCompletionClient

    if s.model_provider == "openai_compatible":
        return OpenAIChatCompletionClient(model=s.model_name, api_key=clave or "no-requerida", base_url=s.model_base_url,
                                          model_info=MODEL_INFO_GENERICO)
    if s.model_provider == "openai":
        return OpenAIChatCompletionClient(model=s.model_name, api_key=clave)
    raise ValueError(f"MODEL_PROVIDER desconocido: {s.model_provider}")


def nombre_modelo(s: Settings) -> str | None:
    return f"{s.model_provider}:{s.model_name}" if crear_cliente(s) else None


async def estado(s: Settings, comprobar: bool = False) -> InformeIntegracion:
    if s.model_provider == "none":
        return informe("modelo_ia", "none", E.NOT_CONFIGURED, "MODEL_PROVIDER=none: se usan reglas deterministas.")
    if f := faltantes(s):
        return informe("modelo_ia", s.model_provider, E.NOT_CONFIGURED, f"Faltan: {', '.join(f)}")
    if not comprobar:
        return informe("modelo_ia", s.model_provider, E.CONFIGURED, f"Modelo {s.model_name}; sin comprobar conexión.")
    try:
        r = await crear_cliente(s).create([UserMessage(content="Responde solo: ok", source="status")])
        return informe("modelo_ia", s.model_provider, E.CONNECTED, f"Respuesta recibida ({len(str(r.content))} caracteres).")
    except Exception as e:  # noqa: BLE001 — se informa el tipo, nunca credenciales
        return informe("modelo_ia", s.model_provider, E.ERROR, type(e).__name__)
