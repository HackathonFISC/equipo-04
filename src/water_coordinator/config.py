"""Configuración centralizada. Solo lee variables de entorno; no carga .env ni secretos."""

import os

APP_ENV = os.getenv("APP_ENV", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
