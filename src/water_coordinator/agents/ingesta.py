"""Agente 1 — Ingesta y Validación (DOC §4.1). Nivel 1: crea y clasifica registros; no inventa datos."""

import json
import logging

from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_core.models import ChatCompletionClient, SystemMessage, UserMessage

from water_coordinator.schemas.models import (
    Confianza, DatosReportados, Estado, LoteRegistros, LoteReportes, RegistroAfectacion, ReporteEntrada, TipoAfectacion,
)
from water_coordinator.services.clasificacion import clasificar, extraer_datos, extraer_ubicacion, normalizar
from water_coordinator.services.fechas import dias_entre, fecha_incidente

log = logging.getLogger(__name__)

PROMPT_LLM = (
    "Clasifica un reporte ciudadano sobre agua en Panamá Oeste. Responde SOLO JSON: "
    '{"tipo": "falta_de_agua|tuberia_rota|agua_contaminada|indeterminado", "justificacion": "<breve>"}. '
    "Si una tubería rota causa falta de agua, el tipo es tuberia_rota. No inventes datos."
)


def registrar(rep: ReporteEntrada) -> RegistroAfectacion:
    c = clasificar(rep.texto)
    datos = DatosReportados(**extraer_datos(rep.texto))
    incidente, expr = fecha_incidente(rep.texto, rep.recibido_en)
    ubic = extraer_ubicacion(rep.texto)
    faltan, obs = [], []
    if incidente is None:
        faltan.append("fecha_hora_incidente")  # A1-R4: no se usa la fecha de recepción
    if ubic is None:
        faltan.append("ubicacion_reportada")
    if not any([datos.viviendas_residenciales, datos.viviendas_rurales, datos.edificios_apartamentos,
                datos.instalacion_mencionada, datos.personas_reportadas]):
        faltan.append("unidades o personas afectadas")
    if not c["relevante"]:
        obs.append("Sin palabras clave del dominio (docs/KEYWORDS.md); se conserva el reporte.")
    if c["causa"]:
        obs.append("Tubería rota como causa y falta de agua como consecuencia (A1-R2).")
    if c["tipo"] == TipoAfectacion.INDETERMINADO and len(c["candidatos"]) > 1:
        obs.append(f"Varios tipos no resolubles por regla: {[t.value for t in c['candidatos']]} (revisión humana).")

    if c["revision"]:
        estado = Estado.PENDIENTE_REVISION
    elif c["tipo"] == TipoAfectacion.INDETERMINADO:
        estado = Estado.PENDIENTE_INFORMACION
    else:
        estado = Estado.VALIDADO
    return RegistroAfectacion(
        id_reporte=rep.id_reporte,
        tipo_afectacion=c["tipo"],
        causa_reportada=c["causa"],
        consecuencias_reportadas=c["consecuencias"],
        tipos_candidatos=c["candidatos"],
        fecha_hora_incidente=incidente,
        expresion_fecha_incidente=expr,
        fecha_hora_recepcion=rep.recibido_en,
        dias_sin_agua=dias_entre(incidente, rep.recibido_en) if incidente else None,
        ubicacion_reportada=ubic,
        fuente=rep.canal,
        descripcion_original=rep.texto,
        confianza_clasificacion=c["confianza"],
        metodo_clasificacion="palabras_clave",
        evidencia=c["evidencia"],
        estado=estado,
        datos_faltantes=faltan,
        observaciones=obs,
        alerta_sanitaria=TipoAfectacion.AGUA_CONTAMINADA in c["candidatos"],
        datos_adicionales=datos,
        contacto=rep.contacto,
    )


def vincular_duplicados(regs: list[RegistroAfectacion]) -> None:
    """A1-R5/R6: vincula (no fusiona) registros con misma ubicación y tipo; fechas distintas → pendiente de revisión."""
    for i, a in enumerate(regs):
        for b in regs[i + 1:]:
            if not a.ubicacion_reportada or not b.ubicacion_reportada:
                continue
            if normalizar(a.ubicacion_reportada) != normalizar(b.ubicacion_reportada) or a.tipo_afectacion != b.tipo_afectacion:
                continue
            a.posibles_duplicados.append(b.id_afectacion)
            b.posibles_duplicados.append(a.id_afectacion)
            fa, fb = a.fecha_hora_incidente, b.fecha_hora_incidente
            if fa and fb and abs((fa - fb).total_seconds()) >= 86400:
                for r in (a, b):
                    r.estado = Estado.PENDIENTE_REVISION
                    r.observaciones.append("Fecha del incidente contradictoria con un posible duplicado (A1-R5).")


class AgenteIngesta(RoutedAgent):
    def __init__(self, llm: ChatCompletionClient | None = None):
        super().__init__("Agente 1: ingesta y clasificación de reportes")
        self.llm = llm

    @message_handler
    async def procesar(self, message: LoteReportes, ctx: MessageContext) -> LoteRegistros:
        regs = [registrar(r) for r in message.reportes]
        vincular_duplicados(regs)
        if self.llm:
            for r in regs:
                await self._contrastar_con_llm(r)
        return LoteRegistros(registros=regs)

    async def _contrastar_con_llm(self, reg: RegistroAfectacion) -> None:
        """El modelo solo interpreta; si discrepa de la regla no sobrescribe: baja la confianza y pide revisión."""
        try:
            r = await self.llm.create(
                [SystemMessage(content=PROMPT_LLM), UserMessage(content=reg.descripcion_original, source="reporte")],
                json_output=True,
            )
            sug = json.loads(str(r.content))
            tipo = TipoAfectacion(sug["tipo"])
        except Exception as e:  # noqa: BLE001
            log.warning("Modelo de IA no disponible para %s: %s", reg.id_afectacion, type(e).__name__)
            reg.observaciones.append(f"Modelo de IA no disponible ({type(e).__name__}); se mantiene la clasificación por reglas.")
            return
        reg.sugerencia_llm = {"tipo": tipo.value, "justificacion": str(sug.get("justificacion", ""))[:500]}
        if tipo != reg.tipo_afectacion:
            reg.confianza_clasificacion = Confianza.BAJA
            reg.estado = Estado.PENDIENTE_REVISION
            reg.observaciones.append(f"El modelo de IA sugiere '{tipo.value}' y las reglas '{reg.tipo_afectacion.value}' (revisión humana).")
        else:
            reg.metodo_clasificacion = "palabras_clave+modelo_ia"
