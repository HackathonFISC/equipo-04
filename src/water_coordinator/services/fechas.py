"""Identificación de la fecha del incidente en el texto (Agente 1, DEC-C02).

Nunca usa la fecha de recepción como sustituto: si no hay expresión reconocible devuelve None.
"""

import re
from datetime import datetime, timedelta

from water_coordinator.services.clasificacion import _PALABRAS, normalizar

DIAS_SEMANA = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
_N = r"(\d+|" + "|".join(_PALABRAS) + r")"


def _n(s: str) -> int:
    return int(s) if s.isdigit() else _PALABRAS[s]


def fecha_incidente(texto: str, recibido: datetime) -> tuple[datetime | None, str | None]:
    t = normalizar(texto)
    if m := re.search(rf"\bhace {_N} (dias?|horas?|semanas?)\b", t):
        n, u = _n(m.group(1)), m.group(2)
        delta = timedelta(hours=n) if u.startswith("hora") else timedelta(days=n * (7 if u.startswith("semana") else 1))
        return recibido - delta, m.group(0)
    if m := re.search(r"\b(desde )?(antier|anteayer|antes de ayer)\b", t):
        return recibido - timedelta(days=2), m.group(0)
    if m := re.search(r"\b(desde )?(ayer|anoche)\b", t):
        return recibido - timedelta(days=1), m.group(0)
    if m := re.search(r"\b(desde )?(hoy|esta manana|esta tarde)\b", t):
        return recibido.replace(hour=6 if "manana" in m.group(0) else 0, minute=0, second=0, microsecond=0), m.group(0)
    if m := re.search(r"\bdesde el (" + "|".join(DIAS_SEMANA) + r")\b", t):
        atras = (recibido.weekday() - DIAS_SEMANA.index(m.group(1))) % 7 or 7
        return (recibido - timedelta(days=atras)).replace(hour=0, minute=0, second=0, microsecond=0), m.group(0)
    if m := re.search(r"\b(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?\b", t):
        return _fecha(int(m.group(1)), int(m.group(2)), m.group(3), recibido), m.group(0)
    if m := re.search(r"\b(\d{1,2}) de (" + "|".join(MESES) + r")\b", t):
        return _fecha(int(m.group(1)), MESES.index(m.group(2)) + 1, None, recibido), m.group(0)
    return None, None


def _fecha(dia: int, mes: int, anio: str | None, recibido: datetime) -> datetime | None:
    a = recibido.year if anio is None else int(anio) + (2000 if len(anio) == 2 else 0)
    try:
        f = recibido.replace(year=a, month=mes, day=dia, hour=0, minute=0, second=0, microsecond=0)
    except ValueError:
        return None
    if anio is None and f > recibido:  # "12 de diciembre" recibido en enero → año anterior
        f = f.replace(year=a - 1)
    return f if f <= recibido else None


def dias_entre(inicio: datetime, fin: datetime) -> float:
    return max(0.0, (fin - inicio).total_seconds() / 86400)
