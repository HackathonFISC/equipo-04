"""Persistencia con SQLAlchemy Core: SQLite por defecto, PostgreSQL cambiando DATABASE_URL.

- `documentos`: estado actual de cada objeto (reporte, afectación, plan…) como JSON.
- `eventos`: traza solo de adición (quién, qué, cuándo, versión de reglas, modelo usado).
"""

import json
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel
from sqlalchemy import Column, Integer, MetaData, String, Table, Text, create_engine, insert, select, update
from sqlalchemy.exc import IntegrityError

from water_coordinator.schemas.models import ahora
from water_coordinator.services.parametros import VERSION_REGLAS

M = TypeVar("M", bound=BaseModel)

meta = MetaData()
documentos = Table(
    "documentos", meta,
    Column("tipo", String(40), primary_key=True),
    Column("id", String(64), primary_key=True),
    Column("datos", Text, nullable=False),
    Column("actualizado_en", String(40), nullable=False),
)
eventos = Table(
    "eventos", meta,
    Column("seq", Integer, primary_key=True, autoincrement=True),
    Column("fecha", String(40), nullable=False),
    Column("agente", String(40), nullable=False),
    Column("tipo", String(40), nullable=False),
    Column("ref_id", String(64)),
    Column("version_reglas", String(80), nullable=False),
    Column("modelo", String(120)),
    Column("datos", Text, nullable=False),
)


class ErrorPersistencia(RuntimeError):
    pass


class Repositorio:
    def __init__(self, url: str):
        if url.startswith("sqlite:///") and not url.endswith(":memory:"):
            Path(url.removeprefix("sqlite:///")).parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(url)
        meta.create_all(self.engine)

    def insertar(self, tipo: str, id_: str, obj: BaseModel) -> None:
        """Alta inmutable (originales): falla si ya existe en lugar de sobrescribir."""
        try:
            with self.engine.begin() as c:
                c.execute(insert(documentos).values(tipo=tipo, id=id_, datos=obj.model_dump_json(), actualizado_en=ahora().isoformat()))
        except IntegrityError as e:
            raise ErrorPersistencia(f"{tipo} {id_} ya existe; los originales no se sobrescriben.") from e

    def guardar(self, tipo: str, id_: str, obj: BaseModel) -> None:
        with self.engine.begin() as c:
            fila = {"datos": obj.model_dump_json(), "actualizado_en": ahora().isoformat()}
            if c.execute(update(documentos).where(documentos.c.tipo == tipo, documentos.c.id == id_).values(**fila)).rowcount == 0:
                c.execute(insert(documentos).values(tipo=tipo, id=id_, **fila))

    def obtener(self, tipo: str, id_: str, cls: type[M]) -> M | None:
        with self.engine.connect() as c:
            fila = c.execute(select(documentos.c.datos).where(documentos.c.tipo == tipo, documentos.c.id == id_)).first()
        return cls.model_validate_json(fila[0]) if fila else None

    def listar(self, tipo: str, cls: type[M]) -> list[M]:
        with self.engine.connect() as c:
            filas = c.execute(select(documentos.c.datos).where(documentos.c.tipo == tipo)).all()
        return [cls.model_validate_json(f[0]) for f in filas]

    def registrar_evento(self, agente: str, tipo: str, ref_id: str | None, datos: dict, modelo: str | None = None) -> None:
        with self.engine.begin() as c:
            c.execute(insert(eventos).values(
                fecha=ahora().isoformat(), agente=agente, tipo=tipo, ref_id=ref_id,
                version_reglas=VERSION_REGLAS, modelo=modelo, datos=json.dumps(datos, ensure_ascii=False, default=str),
            ))

    def eventos(self, ref_id: str | None = None) -> list[dict]:
        q = select(eventos).order_by(eventos.c.seq)
        if ref_id:
            q = q.where(eventos.c.ref_id == ref_id)
        with self.engine.connect() as c:
            return [dict(f._mapping) | {"datos": json.loads(f.datos)} for f in c.execute(q)]
