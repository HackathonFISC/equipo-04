# Conexión de proveedores externos

> Nada de esto es necesario para ejecutar el prototipo: sin claves funciona en modo simulado.
>
> Las credenciales van **solo** en `.env`, que está ignorado por git, o en un gestor de secretos. Nunca van en el código, los logs ni los mensajes de error.
>
> Los costos y límites indicados son los conocidos a 2026-10. **Revisa siempre la página oficial de precios antes de activar un servicio.**
>
> Ningún servicio de pago se activa automáticamente.

Después de configurar cada servicio, comprueba que conecta:

```bash
uv run water-coordinator estado --comprobar
```

---

## 1. Mapas: Leaflet + teselas de OpenStreetMap

- **Enlaces:** https://leafletjs.com · Política de teselas OSM: https://operations.osmfoundation.org/policies/tiles/ · Atribución: https://www.openstreetmap.org/copyright
- **Cuenta:** no se necesita.
- **Variables:** `MAP_TILE_URL` (p. ej. `https://tile.openstreetmap.org/{z}/{x}/{y}.png`) y `MAP_ATTRIBUTION`.
- **Límites:**
  - Las teselas públicas de OSM son para uso ligero.
  - Prohibido descargar teselas de forma masiva.
  - La atribución "© OpenStreetMap contributors" debe estar visible.
  - Para uso intensivo hay que usar un proveedor comercial o un servidor propio.
- **Costo:** gratuito con uso moderado.
- **Pasos:** se conecta en `frontend/` cuando esa carpeta se suba. El backend no la modifica.

## 2. Geocodificación: Nominatim

- **Enlaces:** https://nominatim.org · Política: https://operations.osmfoundation.org/policies/nominatim/
- **Cuenta:** no se necesita.
- **Variables:** `GEOCODER_PROVIDER=nominatim`, `NOMINATIM_USER_AGENT` (nombre de la app y un contacto real del equipo) y `NOMINATIM_EMAIL` (opcional).
- **Límites en el servidor público:**
  - **Máximo 1 solicitud por segundo.** El adaptador lo aplica.
  - User-Agent identificable.
  - Resultados en caché. El adaptador los guarda en memoria.
  - Sin consultas masivas ni autocompletado.
- **Costo:** gratuito. Si el volumen crece, se puede instalar Nominatim propio o cambiar de proveedor implementando la interfaz `Geocodificador`.
- **Privacidad:** solo se envía el texto de la ubicación, nunca teléfonos ni el reporte completo.

## 3. Rutas: OSRM

- **Enlaces:** https://project-osrm.org · Servidor propio: https://github.com/Project-OSRM/osrm-backend
- **Cuenta:** no se necesita.
- **Variables:** `OSRM_BASE_URL`, `OSRM_PROFILE=driving` y `ORGANIZACION_LAT/LON` (dato [PEND]).
- **Límites:**
  - `router.project-osrm.org` es un **servidor de demostración**, sin garantía de disponibilidad ni para uso en producción.
  - Para operar conviene un OSRM propio con Docker y un extracto OSM de la región (Geofabrik, Centroamérica).
- **Costo:** gratuito. El servidor propio tiene el costo de su alojamiento.
- **Si falla o no está configurado:** no se calculan distancias y la ruta queda "pendiente". Nunca se inventan distancias.

## 4. Modelos de IA (AutoGen)

| Opción | Variables | Cuenta y costo |
| --- | --- | --- |
| **Ollama local** (gratis) | `MODEL_PROVIDER=openai_compatible`, `MODEL_BASE_URL=http://localhost:11434/v1`, `MODEL_NAME=<modelo descargado>` | Instalar desde https://ollama.com. Sin costo por uso; necesita RAM o GPU. |
| **OpenAI** | `MODEL_PROVIDER=openai`, `MODEL_NAME`, `MODEL_API_KEY` | Clave en https://platform.openai.com/api-keys. Pago por token: https://openai.com/api/pricing |
| **Anthropic (Claude)** | `MODEL_PROVIDER=anthropic`, `MODEL_NAME` (p. ej. `claude-sonnet-5-5`), `MODEL_API_KEY` | Clave en https://console.anthropic.com. Pago por token: https://www.anthropic.com/pricing |
| Otro endpoint compatible con OpenAI | `openai_compatible` + `MODEL_BASE_URL` (+ `MODEL_API_KEY` si lo exige) | Según el proveedor. |

- **Para qué se usa:** el modelo solo **interpreta texto**: contrasta la clasificación del Agente 1. Los cálculos de prioridad, demanda, cobertura y rutas son deterministas y no cambian al cambiar de modelo.
- **Privacidad:** al modelo solo se envía el texto del reporte, nunca el contacto.

## 5. Mensajería: WhatsApp Business Cloud API

- **Enlaces:** https://developers.facebook.com/docs/whatsapp/cloud-api/overview · Precios: https://developers.facebook.com/docs/whatsapp/pricing · Términos: https://www.whatsapp.com/legal/meta-terms-whatsapp-business
- **Requisitos (los tiene que hacer la usuaria):**
  1. Portafolio comercial de Meta (Business Manager), verificado si corresponde.
  2. Una app en https://developers.facebook.com con el producto WhatsApp.
  3. Una cuenta de WhatsApp Business (WABA) y un número empresarial registrado. Ese número no puede estar en uso en la app de WhatsApp.
  4. Un **token de acceso de sistema** (permanente) con los permisos `whatsapp_business_messaging` y `whatsapp_business_management`.
  5. App Secret (para validar webhooks) y un Verify Token que elijas tú.
  6. Un backend público con **HTTPS** para el webhook entrante. No existe todavía: requiere aprobar un framework de API.
- **Variables:** `MESSAGING_PROVIDER=whatsapp_cloud`, `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_APP_SECRET`, `WHATSAPP_VERIFY_TOKEN`, `WHATSAPP_API_VERSION`.
- **Seguridad:** `WHATSAPP_SEND_ENABLED=false` mientras no haya **aprobación explícita** para enviar. Mientras siga en `false`, el adaptador se niega a enviar.
- **Costo:**
  - Meta cobra según la categoría del mensaje y el país, con su tarifa vigente.
  - El alojamiento del webhook también puede costar.
  - El modo simulado no tiene costo.
- **Implementado:**
  - Envío de texto (bloqueado por defecto).
  - Validación de la firma `X-Hub-Signature-256` de los webhooks.
  - Comprobación de conexión de solo lectura.
- **Pendiente:**
  - Endpoint del webhook.
  - Plantillas aprobadas por Meta (fuera de la ventana de 24 h solo se pueden enviar plantillas).
  - Consentimiento de los usuarios.

## 6. Transcripción

### Whisper local (primera opción)

- **Enlaces:** https://github.com/SYSTRAN/faster-whisper
- **Instalación:** `uv sync --extra transcripcion-local`. Descarga el modelo de Hugging Face la primera vez.
- **Variables:** `TRANSCRIPTION_PROVIDER=whisper_local`, `WHISPER_MODEL` (`small` por defecto) y `WHISPER_DEVICE` (`cpu` o `cuda`).
- **Costo:** gratuito.
- **Privacidad:** el audio no sale de la máquina. El resultado indica `ejecucion: "local"`.

### Google Cloud Speech-to-Text (opcional)

- **Enlaces:** https://cloud.google.com/speech-to-text · Precios: https://cloud.google.com/speech-to-text/pricing
- **Requisitos:**
  1. Un proyecto de Google Cloud **con facturación activa**.
  2. La API Speech-to-Text habilitada.
  3. Una cuenta de servicio con su clave JSON, guardada fuera del repo.
- **Instalación:** `uv sync --extra transcripcion-google`.
- **Variables:** `TRANSCRIPTION_PROVIDER=google`, `GOOGLE_APPLICATION_CREDENTIALS` y `GOOGLE_STT_LANGUAGE`.
- **Costo:** de pago por minuto de audio, con un nivel gratuito limitado según la tarifa vigente.
- **Privacidad:** el audio se envía a Google. El resultado indica `ejecucion: "remoto"`.

## 7. Base de datos

- **SQLite** (por defecto): `DATABASE_URL=sqlite:///./storage/water.db`. No necesita cuenta.
- **PostgreSQL:** `DATABASE_URL=postgresql+psycopg://usuario:clave@host:5432/bd` y `uv add psycopg[binary]`. Las tablas (`documentos`, `eventos`) se crean solas. La clave va en `.env`.

## 8. Archivos

- **Variables:** `STORAGE_DIR`, `STORAGE_MAX_FILE_MB`, `STORAGE_ALLOWED_EXTENSIONS` y `STORAGE_RETENTION_DAYS` (vacío = no se borra nada, porque la política está [PEND]).
- **Nombres de archivo:** los archivos se guardan con un nombre aleatorio. El nombre original nunca forma parte de la ruta.

## 9. Monitoreo

- **Logs:** se escriben en formato JSON a la salida estándar. Los valores de todas las variables secretas se reemplazan por `***`, también en las trazas de error.
- **Eventos de AutoGen:** sus payloads, que incluyen contactos, no se registran en nivel INFO.
- **Sentry u otros:** opcionales y sin implementar. `SENTRY_DSN` queda reservado.

---

## Lista de pasos que debe hacer la usuaria

1. **Ollama (si quieres IA gratis):** instalarlo, descargar un modelo y rellenar las tres variables `MODEL_*`.
2. **Nominatim:** poner un `NOMINATIM_USER_AGENT` con un correo real del equipo y `GEOCODER_PROVIDER=nominatim`.
3. **OSRM:** decidir entre el demo público (solo pruebas) o un servidor propio, y confirmar la **ubicación de la organización**.
4. **WhatsApp:** crear el portafolio de Meta, la app, la WABA y el número; generar el token de sistema; aprobar un backend HTTPS para el webhook. Dejar `WHATSAPP_SEND_ENABLED=false` hasta aprobarlo explícitamente.
5. **Whisper:** ejecutar `uv sync --extra transcripcion-local` y poner `TRANSCRIPTION_PROVIDER=whisper_local`.
6. **Google STT (opcional):** crear un proyecto con facturación, una cuenta de servicio y su JSON.
7. **Mapas:** integrar Leaflet en `frontend/` cuando esa carpeta se suba.
