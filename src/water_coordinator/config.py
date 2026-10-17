"""Configuración centralizada. Lee variables de entorno y, si existe, el archivo `.env` local.

Los secretos usan `SecretStr`: no aparecen en `repr`, logs ni mensajes de error.
"""

from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # env_ignore_empty: las variables vacías de .env.example equivalen a "no configurado" (valor por defecto).
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore", env_ignore_empty=True)

    app_env: str = "development"
    log_level: str = "INFO"

    # Modelos de IA (AutoGen). provider: none | openai | openai_compatible | anthropic
    model_provider: str = "none"
    model_name: str = ""
    model_api_key: SecretStr | None = None
    model_base_url: str = ""
    # Solo Anthropic: ID del workspace si la clave no está asociada a uno (cabecera anthropic-workspace-id).
    model_workspace_id: str = ""

    # Geocodificación (Nominatim). provider: none | nominatim
    geocoder_provider: str = "none"
    nominatim_base_url: str = "https://nominatim.openstreetmap.org"
    nominatim_user_agent: str = ""
    nominatim_email: str = ""

    # Rutas (OSRM). Vacío = no configurado.
    osrm_base_url: str = ""
    osrm_profile: str = "driving"
    organizacion_lat: float | None = None
    organizacion_lon: float | None = None

    # Mapas (Leaflet + teselas OSM) — los consume el frontend.
    map_tile_url: str = ""
    map_attribution: str = "&copy; OpenStreetMap contributors"

    # Mensajería. provider: mock | whatsapp_cloud
    messaging_provider: str = "mock"
    whatsapp_access_token: SecretStr | None = None
    whatsapp_phone_number_id: str = ""
    whatsapp_api_version: str = "v21.0"
    whatsapp_app_secret: SecretStr | None = None
    whatsapp_verify_token: SecretStr | None = None
    whatsapp_send_enabled: bool = False

    # Transcripción. provider: none | whisper_local | google
    transcription_provider: str = "none"
    whisper_model: str = "small"
    whisper_device: str = "cpu"
    google_application_credentials: str = ""
    google_stt_language: str = "es-US"

    # Base de datos (SQLAlchemy). SQLite local; PostgreSQL cambiando la URL.
    database_url: str = "sqlite:///./storage/water.db"

    # Archivos locales
    storage_dir: Path = Path("./storage/media")
    storage_max_file_mb: int = 25
    storage_allowed_extensions: str = ".txt,.json,.ogg,.opus,.mp3,.m4a,.wav,.mp4"
    storage_retention_days: int | None = None  # política de retención [PEND]: sin borrado automático

    # Monitoreo externo opcional
    sentry_dsn: SecretStr | None = None

    # Observabilidad del pipeline en Langfuse (desactivada por defecto)
    langfuse_tracing_enabled: bool = False
    langfuse_public_key: SecretStr | None = None
    langfuse_secret_key: SecretStr | None = None
    langfuse_base_url: str = ""

    # API HTTP local: orígenes del frontend permitidos por CORS (separados por comas)
    cors_origins: str = "http://127.0.0.1:5500,http://localhost:5500"

    # Parámetros operativos
    horarios_file: Path | None = None  # JSON que reemplaza los horarios por defecto
    a_personas_referencia: int = 1000


def usar_certificados_del_sistema() -> None:
    """Verifica TLS con el almacén de certificados del sistema operativo (como el navegador).

    En esta máquina un antivirus/proxy intercepta TLS y su certificado raíz solo está en el almacén de Windows.
    """
    import truststore

    truststore.inject_into_ssl()


@lru_cache
def get_settings() -> Settings:
    return Settings()
