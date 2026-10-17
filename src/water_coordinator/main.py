"""CLI del prototipo. Ningún comando despacha cisternas ni envía mensajes reales por defecto.

  water-coordinator demo [--datos RUTA] [--sin-aprobacion]
  water-coordinator aprobar PLAN_ID --decision aprobado|rechazado|cambios_solicitados --supervisor NOMBRE [--simulada] [--motivo TEXTO]
  water-coordinator estado [--comprobar]
  water-coordinator traza ID
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

from water_coordinator import __version__
from water_coordinator.config import Settings, get_settings
from water_coordinator.orchestration.pipeline import procesar_configurado
from water_coordinator.persistence.repository import Repositorio
from water_coordinator.schemas.models import ReporteEntrada
from water_coordinator.services.aprobacion import ErrorAprobacion, registrar_decision
from water_coordinator.services.monitoreo import configurar_logs
from water_coordinator.services.observabilidad import crear_observabilidad, faltantes_langfuse
from water_coordinator.tools import geocoding, llm, messaging, routing, storage, transcription
from water_coordinator.tools.estado import EstadoIntegracion, informe

DATOS_DEMO = Path("data/simulados/reportes.json")
SUPERVISOR_SIMULADO = "SIMULACION-PRUEBA"  # DEC-19: solo pruebas; no sustituye a un supervisor real


async def demo(s: Settings, ruta: Path, aprobar: bool) -> dict:
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    momento = datetime.fromisoformat(datos["momento_planificacion"])
    reportes = [ReporteEntrada(**r) for r in datos["reportes"]]
    repo = Repositorio(s.database_url)
    obs = crear_observabilidad(s)
    try:
        res = await procesar_configurado(s, reportes, repo, momento, obs)
    finally:
        obs.vaciar()  # comando de corta duración: enviar lo pendiente a Langfuse antes de salir
    decisiones = []
    if aprobar:
        for p in res.planes.planes:
            try:
                d = registrar_decision(repo, p.id_plan, "aprobado", SUPERVISOR_SIMULADO, simulada=True,
                                       motivo="Aprobación simulada de prueba (DEC-19); no autoriza ejecución real.")
                decisiones.append({"id_plan": p.id_plan, "decision": d.decision, "simulada": d.simulada})
            except ErrorAprobacion as e:
                decisiones.append({"id_plan": p.id_plan, "error": str(e)})
    return {
        "afectaciones": [
            {"id": pr.id_afectacion, "categoria": pr.categoria_instalacion, "nivel": pr.nivel_jerarquia, "T": pr.T, "V": pr.V,
             "A": pr.A, "P": pr.puntuacion_P, "rango_P": pr.rango_P, "revision": pr.requiere_revision_humana}
            for pr in res.prioridades.prioridades
        ],
        "planes": [
            {"id_plan": p.id_plan, "afectacion": p.id_afectacion, "demanda_gal": p.demanda.demanda_estimada_gal,
             "cobertura_pct": p.cobertura_pct, "tipo_aprobacion": p.tipo_aprobacion, "estado": p.estado,
             "cisternas": len(p.cisternas_asignadas), "faltantes": p.campos_faltantes}
            for p in res.planes.planes
        ],
        "mensajes_simulados": [{"para": m.destinatario, "tipo": m.tipo, "texto": m.texto} for m in res.mensajes.mensajes],
        "decisiones": decisiones,
        "base_de_datos": s.database_url,
        "id_ejecucion": res.id_ejecucion,
        "langfuse": "activo" if obs.activa else "desactivado",
    }


async def estado(s: Settings, comprobar: bool) -> list[dict]:
    informes = [await m.estado(s, comprobar) for m in (llm, geocoding, routing, messaging, transcription, storage)]
    bd = "postgresql" if s.database_url.startswith("postgres") else "sqlite"
    informes.append(informe("base_de_datos", bd, EstadoIntegracion.CONFIGURED, s.database_url.split("@")[-1]))
    mapa = EstadoIntegracion.CONFIGURED if s.map_tile_url else EstadoIntegracion.NOT_CONFIGURED
    informes.append(informe("mapas", "leaflet+osm", mapa, "MAP_TILE_URL para el frontend (frontend aún no integrado)."))
    if not s.langfuse_tracing_enabled:
        informes.append(informe("observabilidad", "langfuse", EstadoIntegracion.DISABLED, "LANGFUSE_TRACING_ENABLED=false."))
    elif f := faltantes_langfuse(s):
        informes.append(informe("observabilidad", "langfuse", EstadoIntegracion.NOT_CONFIGURED, f"Faltan: {', '.join(f)}"))
    else:
        informes.append(informe("observabilidad", "langfuse", EstadoIntegracion.CONFIGURED,
                                "Trazas activas; verificar en el proyecto de Langfuse tras ejecutar `demo`."))
    mon = EstadoIntegracion.CONFIGURED if s.sentry_dsn else EstadoIntegracion.DISABLED
    informes.append(informe("monitoreo_externo", "sentry", mon, "Opcional; logs JSON locales siempre activos."))
    return [i.model_dump(mode="json") for i in informes]


def main(argv: list[str] | None = None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(prog="water-coordinator", description=f"water-coordinator {__version__}")
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("demo", help="Ejecuta el flujo completo con datos simulados")
    d.add_argument("--datos", type=Path, default=DATOS_DEMO)
    d.add_argument("--sin-aprobacion", action="store_true")
    a = sub.add_parser("aprobar", help="Registra la decisión del supervisor sobre un plan")
    a.add_argument("id_plan")
    a.add_argument("--decision", required=True, choices=["aprobado", "rechazado", "cambios_solicitados"])
    a.add_argument("--supervisor", required=True)
    a.add_argument("--simulada", action="store_true")
    a.add_argument("--motivo", default="")
    e = sub.add_parser("estado", help="Estado de las integraciones")
    e.add_argument("--comprobar", action="store_true", help="Hace una llamada real a cada servicio configurado")
    t = sub.add_parser("traza", help="Eventos registrados para un id")
    t.add_argument("id")
    args = ap.parse_args(argv)

    s = get_settings()
    configurar_logs(s)
    if args.cmd == "demo":
        out = asyncio.run(demo(s, args.datos, not args.sin_aprobacion))
    elif args.cmd == "aprobar":
        try:
            dec = registrar_decision(Repositorio(s.database_url), args.id_plan, args.decision, args.supervisor, args.simulada, args.motivo)
        except ErrorAprobacion as err:
            print(f"Error: {err}", file=sys.stderr)
            return 2
        out = dec.model_dump(mode="json")
    elif args.cmd == "estado":
        out = asyncio.run(estado(s, args.comprobar))
    else:
        out = Repositorio(s.database_url).eventos(args.id)
    print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
