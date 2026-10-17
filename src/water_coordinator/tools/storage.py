"""Almacenamiento local de reportes y medios, con límite de tamaño, extensiones permitidas y retención configurable."""

import time
from pathlib import Path
from uuid import uuid4

from water_coordinator.config import Settings
from water_coordinator.tools.estado import EstadoIntegracion as E
from water_coordinator.tools.estado import InformeIntegracion, informe


class ErrorAlmacenamiento(ValueError):
    pass


class AlmacenLocal:
    def __init__(self, s: Settings):
        self.dir = Path(s.storage_dir)
        self.max_bytes = s.storage_max_file_mb * 1024 * 1024
        self.extensiones = {e.strip().lower() for e in s.storage_allowed_extensions.split(",") if e.strip()}
        self.retencion_dias = s.storage_retention_days

    def guardar(self, contenido: bytes, nombre_original: str) -> Path:
        ext = Path(nombre_original).suffix.lower()
        if ext not in self.extensiones:
            raise ErrorAlmacenamiento(f"Extensión no permitida: {ext or '(ninguna)'}")
        if len(contenido) > self.max_bytes:
            raise ErrorAlmacenamiento("Archivo supera STORAGE_MAX_FILE_MB.")
        self.dir.mkdir(parents=True, exist_ok=True)
        destino = self.dir / f"{uuid4().hex}{ext}"  # el nombre original no se usa en la ruta (evita path traversal)
        destino.write_bytes(contenido)
        return destino

    def purgar_vencidos(self) -> list[Path]:
        """Solo actúa si se configura STORAGE_RETENTION_DAYS (política de retención [PEND])."""
        if not self.retencion_dias or not self.dir.exists():
            return []
        limite = time.time() - self.retencion_dias * 86400
        borrados = [f for f in self.dir.iterdir() if f.is_file() and f.stat().st_mtime < limite]
        for f in borrados:
            f.unlink()
        return borrados


async def estado(s: Settings, comprobar: bool = False) -> InformeIntegracion:
    ret = f"{s.storage_retention_days} días" if s.storage_retention_days else "sin borrado automático (política [PEND])"
    return informe("archivos", "local", E.CONFIGURED, f"{s.storage_dir} | máx {s.storage_max_file_mb} MB | retención: {ret}")
