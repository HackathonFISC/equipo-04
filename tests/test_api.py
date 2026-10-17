"""API FastAPI: arranque, lecturas, escrituras, errores, aprobación simulada, CORS y ausencia de secretos."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from water_coordinator.api.app import create_app
from water_coordinator.api.rutas import get_repo
from water_coordinator.config import Settings, get_settings
from water_coordinator.persistence.repository import Repositorio

SECRETOS = {"model_api_key": "sk-ant-PRUEBA-SECRETA-123", "whatsapp_access_token": "EAA-TOKEN-PRUEBA-456",
            "langfuse_secret_key": "sk-lf-PRUEBA-789"}
CONTACTO = "sim:contacto-privado-001"


@pytest.fixture
def cliente(tmp_path):
    s = Settings(_env_file=None, database_url=f"sqlite:///{tmp_path / 'api.db'}", **SECRETOS)
    repo = Repositorio(s.database_url)
    app = create_app(s)
    app.dependency_overrides[get_repo] = lambda: repo
    app.dependency_overrides[get_settings] = lambda: s
    with TestClient(app) as c:
        yield c


def reportar(c, texto="#sinagua en la escuela de Capira desde ayer", **extra):
    return c.post("/api/incidents", json={"canal": "archivo_prueba", "texto": texto, "contacto": CONTACTO, **extra})


def test_health(cliente):
    r = cliente.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok" and r.json()["base_de_datos"] == "ok"
    assert r.json()["langfuse"] == "desactivado"


def test_docs_disponibles(cliente):
    assert cliente.get("/docs").status_code == 200
    assert "/api/incidents" in cliente.get("/openapi.json").json()["paths"]


@pytest.mark.parametrize("ruta", ["/api/incidents", "/api/messages", "/api/agent-events"])
def test_lecturas_vacias(cliente, ruta):
    r = cliente.get(ruta)
    assert r.status_code == 200 and r.json() == {"total": 0, "items": []}


def test_faq(cliente):
    items = cliente.get("/api/faq").json()["items"]
    assert len(items) >= 5 and all(set(i) == {"pregunta", "respuesta"} for i in items)


def test_registrar_y_consultar(cliente):
    r = reportar(cliente)
    assert r.status_code == 201
    datos = r.json()
    assert datos["planes"][0]["estado"] == "pendiente_de_aprobacion" and "lote" in datos["advertencia"]

    inc = cliente.get("/api/incidents").json()
    assert inc["total"] == 1
    item = inc["items"][0]
    assert item["simulado"] and item["categoria"] == "escuela" and item["plan"]["completo"] is False

    msgs = cliente.get("/api/messages").json()["items"]
    assert msgs and all(m["envio"] == "simulado_no_enviado" for m in msgs)
    assert cliente.get("/api/agent-events?limite=5").json()["total"] == 5


def test_filtros_validados(cliente):
    reportar(cliente)
    assert cliente.get("/api/incidents?estado=pendiente_de_aprobacion").json()["total"] == 1
    assert cliente.get("/api/incidents?tipo=tuberia_rota").json()["total"] == 0
    assert cliente.get("/api/incidents?estado=inventado").status_code == 422
    assert cliente.get("/api/agent-events?limite=0").status_code == 422


@pytest.mark.parametrize("cuerpo", [
    {"canal": "archivo_prueba", "texto": ""},
    {"canal": "correo", "texto": "x"},
    {"canal": "archivo_prueba", "texto": "x", "simulado": False},  # campos extra prohibidos
    {"canal": "archivo_prueba", "texto": "x", "id_reporte": "../malo"},
])
def test_registro_invalido(cliente, cuerpo):
    assert cliente.post("/api/incidents", json=cuerpo).status_code == 422


def test_reporte_duplicado_409(cliente):
    assert reportar(cliente, id_reporte="REP-PRUEBA-1").status_code == 201
    r = reportar(cliente, id_reporte="REP-PRUEBA-1")
    assert r.status_code == 409 and "no se duplica" in r.json()["detail"]


def _plan(c, texto="#sinagua en la escuela de Capira desde ayer"):
    return reportar(c, texto).json()["planes"][0]["id_plan"]


def test_decision_siempre_simulada_y_no_repetible(cliente):
    id_plan = _plan(cliente)
    r = cliente.post(f"/api/plans/{id_plan}/decision", json={"decision": "aprobado", "supervisor": "Prueba"})
    assert r.status_code == 200 and r.json()["simulada"] is True and r.json()["autenticacion"] == "simulacion_de_prueba"
    item = cliente.get("/api/incidents").json()["items"][0]
    assert item["estado_actual"] == "aprobado" and item["plan"]["decision_simulada"] is True
    assert cliente.post(f"/api/plans/{id_plan}/decision", json={"decision": "rechazado", "supervisor": "Prueba"}).status_code == 409


def test_no_se_puede_pedir_aprobacion_real(cliente):
    id_plan = _plan(cliente)
    r = cliente.post(f"/api/plans/{id_plan}/decision", json={"decision": "aprobado", "supervisor": "X", "simulada": False})
    assert r.status_code == 422


def test_decision_plan_inexistente_404(cliente):
    assert cliente.post("/api/plans/PLAN-nada/decision", json={"decision": "aprobado", "supervisor": "X"}).status_code == 404


def test_extraordinaria_exige_motivo(cliente):
    id_plan = _plan(cliente, "#sinagua 15 edificios de apartamentos en Arraiján hace 1 día")
    r = cliente.post(f"/api/plans/{id_plan}/decision", json={"decision": "aprobado", "supervisor": "X"})
    assert r.status_code == 409 and "justificación" in r.json()["detail"]


def test_bd_caida_503_sin_detalles(tmp_path):
    class RepoRoto(Repositorio):
        def listar(self, *a, **k):
            raise OperationalError("SELECT secreto", {}, Exception("ruta/interna.db"))

    s = Settings(_env_file=None, database_url=f"sqlite:///{tmp_path / 'x.db'}")
    app = create_app(s)
    app.dependency_overrides[get_repo] = lambda: RepoRoto(s.database_url)
    with TestClient(app) as c:
        r = c.get("/api/incidents")
    assert r.status_code == 503 and r.json() == {"detail": "Base de datos no disponible."}


def test_health_degradado_si_bd_no_responde(tmp_path):
    class RepoSinMotor:
        class engine:
            @staticmethod
            def connect():
                raise OperationalError("x", {}, Exception())

    app = create_app(Settings(_env_file=None))
    app.dependency_overrides[get_repo] = lambda: RepoSinMotor()
    with TestClient(app) as c:
        r = c.get("/health")
    assert r.status_code == 200 and r.json()["base_de_datos"] == "no_disponible"


def test_cors_solo_origenes_locales(cliente):
    ok = cliente.get("/api/faq", headers={"Origin": "http://localhost:5500"})
    assert ok.headers.get("access-control-allow-origin") == "http://localhost:5500"
    ajeno = cliente.get("/api/faq", headers={"Origin": "https://ejemplo.invalid"})
    assert "access-control-allow-origin" not in ajeno.headers


def test_respuestas_sin_secretos_ni_contactos(cliente):
    id_plan = _plan(cliente)
    cliente.post(f"/api/plans/{id_plan}/decision", json={"decision": "aprobado", "supervisor": "Prueba"})
    textos = [cliente.get(r).text for r in ("/health", "/api/incidents", "/api/messages", "/api/agent-events",
                                             "/api/faq", "/openapi.json")]
    for t in textos:
        for secreto in SECRETOS.values():
            assert secreto not in t
        assert CONTACTO not in t
