"""Trazas del pipeline en Langfuse (SDK v5, basado en OpenTelemetry).

Una ejecución del pipeline = una traza; cada agente = una observación hija (A1, A2, A3, A4, A6).
Solo se envían resúmenes operativos (identificadores aleatorios, tipos, estados, cifras). Nunca textos de reportes,
contactos ni secretos. Cualquier fallo de Langfuse se registra en el log y no interrumpe el pipeline.
"""

import logging
import re
from contextlib import contextmanager
from typing import Any, Iterator

from water_coordinator.config import Settings

log = logging.getLogger(__name__)

NOMBRE_TRAZA = "procesar-reportes"
# Nombres de observación: verbo + objeto, estables (los usan filtros y evaluadores en Langfuse).
ETAPAS = {"A1": "clasificar-reportes", "A2": "geolocalizar-afectaciones", "A3": "priorizar-afectaciones",
          "A4": "planificar-recursos", "A6": "redactar-mensajes"}

# Defensa en profundidad: aunque el código no envía contactos, se enmascaran patrones de contacto/teléfono.
_PATRONES_SENSIBLES = [re.compile(r"\bsim:[\w\-]+"), re.compile(r"\+?507[\s-]?\d{3,4}[\s-]?\d{4}"),
                       re.compile(r"\b\d{4}-\d{4}\b")]


def enmascarar(*, data: Any, **_: Any) -> Any:
    """MaskFunction de Langfuse: reemplaza contactos y teléfonos en cualquier texto enviado."""
    if isinstance(data, str):
        for p in _PATRONES_SENSIBLES:
            data = p.sub("[oculto]", data)
        return data
    if isinstance(data, dict):
        return {k: enmascarar(data=v) for k, v in data.items()}
    if isinstance(data, (list, tuple)):
        return [enmascarar(data=v) for v in data]
    return data


class Etapa:
    """Observación de una etapa. Sin cliente (Langfuse desactivado) no hace nada."""

    def __init__(self, span: Any | None):
        self.span = span

    def resultado(self, salida: Any, usage: dict[str, int] | None = None, **metadata: Any) -> None:
        self._actualizar(output=salida, metadata=metadata or None, usage_details=usage)

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
        self._etapa_actual: Etapa | None = None  # para anidar generations bajo el agente que las pidió

    @property
    def activa(self) -> bool:
        return self.cliente is not None

    @contextmanager
    def ejecucion(self, id_ejecucion: str, version_reglas: str, origen: str, metadata: dict[str, str],
                  entrada: dict | None = None) -> Iterator[Etapa]:
        """Traza raíz de una ejecución del pipeline (una unidad de trabajo), con atributos propagados a las etapas.

        Sin session_id: las ejecuciones no tienen continuidad entre sí. El id_ejecucion va en metadata para filtrar.
        """
        metadata = {"id_ejecucion": id_ejecucion, **metadata}
        with self._observacion(NOMBRE_TRAZA, "chain", entrada, metadata=metadata) as etapa:
            ctx = None
            if self.cliente is not None:
                try:
                    from langfuse import propagate_attributes

                    ctx = propagate_attributes(trace_name=NOMBRE_TRAZA, version=version_reglas,
                                               tags=["prototipo", origen], metadata=metadata)
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

    @contextmanager
    def etapa(self, nombre: str, entrada: dict | None = None) -> Iterator[Etapa]:
        with self._observacion(nombre, "agent", entrada) as etapa:
            anterior, self._etapa_actual = self._etapa_actual, etapa
            try:
                yield etapa
            finally:
                self._etapa_actual = anterior

    def generacion(self, nombre: str, modelo: str, entrada: Any):
        """Llamada a un modelo de IA: tipo generation, con el nombre del modelo para que Langfuse calcule el costo.

        Se anida explícitamente bajo la etapa en curso: el runtime de AutoGen ejecuta los agentes en otra tarea
        y el contexto de OpenTelemetry no llega hasta ella.
        """
        padre = self._etapa_actual.span if self._etapa_actual else None
        return self._observacion(nombre, "generation", entrada, padre=padre, model=modelo)

    @contextmanager
    def _observacion(self, nombre: str, tipo: str, entrada: Any, padre: Any = None, **extra: Any) -> Iterator[Etapa]:
        cm = span = None
        if self.cliente is not None:
            origen = padre if hasattr(padre, "start_as_current_observation") else self.cliente
            try:
                cm = origen.start_as_current_observation(name=nombre, as_type=tipo, input=entrada, **extra)
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

        import os

        from water_coordinator import __version__

        os.environ.setdefault("OTEL_SERVICE_NAME", "water-coordinator")  # si no, Langfuse muestra "unknown_service"
        cliente = Langfuse(
            release=__version__,
            public_key=s.langfuse_public_key.get_secret_value(),
            secret_key=s.langfuse_secret_key.get_secret_value(),
            base_url=s.langfuse_base_url,
            environment=s.app_env,
            tracing_enabled=True,
            # Solo spans propios: los spans internos de AutoGen o de clientes de IA llevan el contenido de los mensajes.
            should_export_span=is_langfuse_span,
            mask=enmascarar,
        )
        return Observabilidad(cliente)
    except Exception as e:  # noqa: BLE001
        log.warning("Langfuse no disponible (%s); se continúa sin trazas.", type(e).__name__)
        return Observabilidad(None)
