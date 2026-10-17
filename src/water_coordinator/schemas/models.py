"""Contratos de datos entre agentes. Los nombres siguen docs/AGENT_CRITERIA_AND_DECISION_RULES.md."""

from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field

# Panamá no aplica horario de verano: UTC-5 fijo (evita depender de tzdata en Windows).
TZ_PANAMA = timezone(timedelta(hours=-5), "America/Panama")


def nuevo_id(prefijo: str) -> str:
    return f"{prefijo}-{uuid4().hex[:12]}"


def ahora() -> datetime:
    return datetime.now(TZ_PANAMA)


class TipoAfectacion(StrEnum):
    FALTA_DE_AGUA = "falta_de_agua"
    TUBERIA_ROTA = "tuberia_rota"
    AGUA_CONTAMINADA = "agua_contaminada"
    INDETERMINADO = "indeterminado"


class Confianza(StrEnum):
    ALTA = "alta"
    MEDIA = "media"
    BAJA = "baja"
    NINGUNA = "ninguna"


class Estado(StrEnum):
    RECIBIDO = "recibido"
    EN_ANALISIS = "en_analisis"
    PENDIENTE_INFORMACION = "pendiente_de_informacion"
    PENDIENTE_REVISION = "pendiente_de_revision"
    VALIDADO = "validado"
    PROPUESTO = "propuesto"
    PENDIENTE_APROBACION = "pendiente_de_aprobacion"
    APROBADO = "aprobado"
    RECHAZADO = "rechazado"
    CAMBIOS_SOLICITADOS = "cambios_solicitados"
    EJECUTADO = "ejecutado"
    VERIFICADO = "verificado"
    BLOQUEADO = "bloqueado"


class Certeza(StrEnum):
    CONFIRMADA = "confirmada"
    APROXIMADA = "aproximada"
    AMBIGUA = "ambigua"
    NO_VERIFICADA = "no_verificada"


class Categoria(StrEnum):
    HOSPITAL = "hospital"
    POLICLINICA = "policlinica"
    CENTRO_SALUD = "centro_de_salud"
    ESCUELA = "escuela"
    OTRA = "otra"
    INCIERTA = "incierta"


# ---------- Entrada ----------


class ReporteEntrada(BaseModel):
    id_reporte: str = Field(default_factory=lambda: nuevo_id("REP"))
    canal: Literal["whatsapp_simulado", "transcripcion_audio", "transcripcion_video", "archivo_prueba"]
    texto: str = Field(min_length=1)
    recibido_en: datetime
    contacto: str | None = None  # único dato personal previsto: número celular (DEC-21)


class LoteReportes(BaseModel):
    reportes: list[ReporteEntrada]


# ---------- Agente 1 ----------


class DatosReportados(BaseModel):
    """Datos que constan expresamente en el reporte. Nunca se completan con supuestos."""

    instalacion_mencionada: str | None = None
    viviendas_residenciales: int | None = None
    viviendas_rurales: int | None = None
    edificios_apartamentos: int | None = None
    estudiantes_reportados: int | None = None
    personas_reportadas: int | None = None
    vulnerabilidad: dict[str, bool] = Field(default_factory=dict)  # solo criterios con evidencia


class RegistroAfectacion(BaseModel):
    id_afectacion: str = Field(default_factory=lambda: nuevo_id("AFE"))
    id_reporte: str
    tipo_afectacion: TipoAfectacion
    causa_reportada: TipoAfectacion | None = None
    consecuencias_reportadas: list[TipoAfectacion] = Field(default_factory=list)
    tipos_candidatos: list[TipoAfectacion] = Field(default_factory=list)
    fecha_hora_incidente: datetime | None = None
    expresion_fecha_incidente: str | None = None
    fecha_hora_recepcion: datetime
    dias_sin_agua: float | None = None
    ubicacion_reportada: str | None = None
    fuente: str
    descripcion_original: str
    confianza_clasificacion: Confianza
    metodo_clasificacion: str
    evidencia: list[str] = Field(default_factory=list)
    estado: Estado
    datos_faltantes: list[str] = Field(default_factory=list)
    observaciones: list[str] = Field(default_factory=list)
    posibles_duplicados: list[str] = Field(default_factory=list)
    alerta_sanitaria: bool = False
    datos_adicionales: DatosReportados = Field(default_factory=DatosReportados)
    sugerencia_llm: dict | None = None
    contacto: str | None = None


class LoteRegistros(BaseModel):
    registros: list[RegistroAfectacion]


# ---------- Agente 2 ----------


class Coordenadas(BaseModel):
    lat: float
    lon: float
    tipo: Literal["confirmadas", "estimadas"]


class UbicacionNormalizada(BaseModel):
    id_afectacion: str
    ubicacion_reportada: str | None
    ubicacion_normalizada: str | None
    coordenadas: Coordenadas | None = None
    estado_certeza: Certeza
    zona_comunidad: str | None = None  # distrito
    comunidad: str | None = None  # corregimiento del catálogo territorial, si se reconoce
    alternativas: list[str] = Field(default_factory=list)
    instalaciones_criticas_cercanas: list[str] = Field(default_factory=list)
    observaciones_geograficas: list[str] = Field(default_factory=list)
    fuente_referencia: str
    estado: Estado


class LoteUbicaciones(BaseModel):
    ubicaciones: list[UbicacionNormalizada]


# ---------- Agente 3 ----------


class Prioridad(BaseModel):
    id_afectacion: str
    categoria_instalacion: Categoria
    nivel_jerarquia: int | None  # 1–5; None si la categoría es incierta
    T: float | None
    V: float | None
    A: float | None
    personas_estimadas: float | None
    puntuacion_P: float | None
    rango_P: tuple[float, float] | None = None
    completo: bool
    factores_explicados: list[str]
    datos_faltantes: list[str] = Field(default_factory=list)
    requiere_revision_humana: bool = False
    motivo_revision: list[str] = Field(default_factory=list)
    version_reglas: str


class SolicitudPriorizacion(BaseModel):
    registros: list[RegistroAfectacion]
    ubicaciones: list[UbicacionNormalizada]


class ListaPriorizada(BaseModel):
    prioridades: list[Prioridad]  # ya ordenadas (recomendación, no garantía de atención)
    empates: list[list[str]] = Field(default_factory=list)


# ---------- Agente 4 ----------


class Cisterna(BaseModel):
    id: str
    tipo: Literal["small", "big", "desconocido"]
    origen: Literal["organizacion", "subcontratada"]
    capacidad_min_galones: float  # carga mínima del tipo
    capacidad_galones: float  # carga máxima: la que se usa para la cobertura
    capacidad_es_supuesto: bool
    tanque_combustible_litros: float | None


class CalculoDemanda(BaseModel):
    id_afectacion: str
    demanda_diaria_gal: float | None
    dias_planificacion: float | None  # duración del tipo + compensación
    dias_compensados: float = 0.0
    demanda_estimada_gal: float | None
    formula: str
    bases: list[str] = Field(default_factory=list)
    supuestos: list[str] = Field(default_factory=list)
    datos_faltantes: list[str] = Field(default_factory=list)


class SolicitudAdicional(BaseModel):
    cantidad: int
    origen: Literal["organizacion", "subcontratada"]
    demora_minutos: int
    estado: Literal["pendiente_de_solicitud"] = "pendiente_de_solicitud"


class PlanPropuesto(BaseModel):
    id_plan: str = Field(default_factory=lambda: nuevo_id("PLAN"))
    id_afectacion: str
    creado_en: datetime
    motivo: str
    prioridad: Prioridad
    demanda: CalculoDemanda
    volumen_entregable_gal: float | None
    cobertura_pct: float | None
    volumen_pendiente_gal: float | None
    cisternas_asignadas: list[Cisterna] = Field(default_factory=list)
    solicitudes_adicionales: list[SolicitudAdicional] = Field(default_factory=list)
    ruta: dict
    tipo_aprobacion: Literal["ordinaria", "cobertura_parcial", "extraordinaria", "no_aplicable"]
    riesgos_incertidumbres: list[str] = Field(default_factory=list)
    campos_faltantes: list[str] = Field(default_factory=list)
    completo: bool
    estado: Estado
    version_reglas: str


class SolicitudPlanificacion(BaseModel):
    lista: ListaPriorizada
    registros: list[RegistroAfectacion]
    ubicaciones: list[UbicacionNormalizada]
    disponibles: list[Cisterna]
    solicitables: list[SolicitudAdicional]
    momento: datetime


class LotePlanes(BaseModel):
    planes: list[PlanPropuesto]


# ---------- Supervisor (función de control) ----------


class DecisionSupervisor(BaseModel):
    id_decision: str = Field(default_factory=lambda: nuevo_id("DEC"))
    id_plan: str
    decision: Literal["aprobado", "rechazado", "cambios_solicitados"]
    supervisor: str = Field(min_length=1)
    simulada: bool
    motivo: str = ""
    fecha: datetime
    version_reglas: str
    huella_plan: str  # sha256 del plan decidido (versión de datos)
    autenticacion: str = "no_verificada"  # mecanismo real [PEND]


# ---------- Agente 6 ----------


class SolicitudComunicacion(BaseModel):
    registros: list[RegistroAfectacion]
    planes: list[PlanPropuesto]


class MensajeSaliente(BaseModel):
    id_mensaje: str = Field(default_factory=lambda: nuevo_id("MSG"))
    id_afectacion: str
    destinatario: str
    texto: str
    tipo: Literal["estado", "cobertura_parcial"]
    estado_referido: Estado


class LoteMensajes(BaseModel):
    mensajes: list[MensajeSaliente]
