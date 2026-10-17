"""Trazas del pipeline en Langfuse (SDK v5, basado en OpenTelemetry).

Una ejecución del pipeline = una traza; cada agente = una observación hija (A1, A2, A3, A4, A6).
Solo se envían resúmenes operativos (identificadores aleatorios, tipos, estados, cifras). Nunca textos de reportes,
contactos ni secretos. Cualquier fallo de Langfuse se registra en el log y no interrumpe el pipeline.
"""

import logging
from contextlib import contextmanager
from typing import Any, Iterator

from water_coordinator.config import Settings

log = logging.getLogger(__name__)


class Etapa:
    """Observación de una etapa. Sin cliente (Langfuse desactivado) no hace nada."""

    def __init__(self, span: Any | None):
        self.span = span

    def resultado(self, salida: dict, **metadata: Any) -> None:
        self._actualizar(output=salida, metadata=metadata or None)

    def error(self, exc: BaseException) -> None:
        self._actualizar(level="ERROR", status_message=type(exc).__name__)

    def _actualizar(self, **campos: Any) -> None:
        if self.span is None:
            return
        try:
            self.span.update(**{k: v for k, v in campos.items() if v is not None})
        except Exception as e:  # noqa: BLE001
            log.warning("Langfuse: no se pudo actualizar la observación (%s)", type(e).__name__)


class Observabilidad:
    def __init__(self, cliente: Any | None = None):
        self.cliente = cliente

    @property
    def activa(self) -> bool:
        return self.cliente is not None

    @contextmanager
    def ejecucion(self, id_ejecucion: str, version_reglas: str, metadata: dict[str, str]) -> Iterator[Etapa]:
        """Traza raíz de una ejecución del pipeline, con atributos propagados a las etapas."""
        with self._observacion("pipeline", "chain", {"id_ejecucion": id_ejecucion, **metadata}) as etapa:
            ctx = None
            if self.cliente is not None:
                try:
                    from langfuse import propagate_attributes

                    ctx = propagate_attributes(trace_name="water-coordinator.pipeline", session_id=id_ejecucion,
                                               version=version_reglas, tags=["prototipo"], metadata=metadata)
                    ctx.__enter__()
                except Exception as e:  # noqa: BLE001
                    log.warning("Langfuse: no se pudieron propagar atributos (%s)", type(e).__name__)
                    ctx = None
            try:
                yield etapa
            finally:
                if ctx is not None:
                    try:
                        ctx.__exit__(None, None, None)
                    except Exception as e:  # noqa: BLE001
                        log.warning("Langfuse: cierre de atributos fallido (%s)", type(e).__name__)

    def etapa(self, nombre: str, entrada: dict | None = None):
        return self._observacion(nombre, "agent", entrada)

    @contextmanager
    def _observacion(self, nombre: str, tipo: str, entrada: dict | None) -> Iterator[Etapa]:
        cm = span = None
        if self.cliente is not None:
            try:
                cm = self.cliente.start_as_current_observation(name=nombre, as_type=tipo, input=entrada)
                span = cm.__enter__()
            except Exception as e:  # noqa: BLE001
                log.warning("Langfuse: no se pudo abrir '%s' (%s)", nombre, type(e).__name__)
                cm = span = None
        etapa = Etapa(span)
        try:
            yield etapa
        except BaseException as exc:
            etapa.error(exc)
            raise
        finally:
            if cm is not None:
                try:
                    cm.__exit__(None, None, None)
                except Exception as e:  # noqa: BLE001
                    log.warning("Langfuse: no se pudo cerrar '%s' (%s)", nombre, type(e).__name__)

    def vaciar(self) -> None:
        """Envía los eventos pendientes (necesario en comandos CLI de corta duración)."""
        if self.cliente is None:
            return
        try:
            self.cliente.flush()
        except Exception as e:  # noqa: BLE001
            log.warning("Langfuse: flush fallido (%s)", type(e).__name__)


def faltantes_langfuse(s: Settings) -> list[str]:
    pares = [("LANGFUSE_PUBLIC_KEY", s.langfuse_public_key), ("LANGFUSE_SECRET_KEY", s.langfuse_secret_key),
             ("LANGFUSE_BASE_URL", s.langfuse_base_url)]
    return [n for n, v in pares if not v]


def crear_observabilidad(s: Settings) -> Observabilidad:
    if not s.langfuse_tracing_enabled or faltantes_langfuse(s):
        return Observabilidad(None)
    try:
        from langfuse import Langfuse, is_langfuse_span

        cliente = Langfuse(
            public_key=s.langfuse_public_key.get_secret_value(),
            secret_key=s.langfuse_secret_key.get_secret_value(),
            base_url=s.langfuse_base_url,
            environment=s.app_env,
            tracing_enabled=True,
            # Solo spans propios: los spans internos de AutoGen o de clientes de IA llevan el contenido de los mensajes.
            should_export_span=is_langfuse_span,
        )
        return Observabilidad(cliente)
    except Exception as e:  # noqa: BLE001
        log.warning("Langfuse no disponible (%s); se continúa sin trazas.", type(e).__name__)
        return Observabilidad(None)
