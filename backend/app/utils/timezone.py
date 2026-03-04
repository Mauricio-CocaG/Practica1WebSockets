"""
==============================================================
 CONFIGURACION DE ZONA HORARIA - Bolivia (UTC-4)
==============================================================
 Modulo centralizado para manejo de fechas y horas.
 Todos los timestamps del sistema usan America/La_Paz.

 Uso:
   from app.utils.timezone import now, to_iso, BoliviaFormatter

   # Obtener hora actual de Bolivia
   fecha = now()

   # Convertir datetime UTC a Bolivia
   fecha_bo = utc_to_bolivia(dt_utc)

   # Formato ISO con offset explicito (-04:00)
   cadena = to_iso(fecha)

   # Logging con hora de Bolivia
   import logging
   handler = logging.StreamHandler()
   handler.setFormatter(BoliviaFormatter('%(asctime)s %(message)s'))
==============================================================
"""

import logging
import pytz
from datetime import datetime

# ── Zona horaria oficial de Bolivia ────────────────────────
BOLIVIA_TZ = pytz.timezone('America/La_Paz')


def now() -> datetime:
    """
    Retorna el datetime actual en hora de Bolivia como naive
    (sin tzinfo) para compatibilidad con SQLAlchemy/MySQL.

    Ejemplo: 2026-03-04 11:00:00  (hora Bolivia, UTC-4)
    """
    return datetime.now(BOLIVIA_TZ).replace(tzinfo=None)


def utc_to_bolivia(dt: datetime) -> datetime:
    """
    Convierte un datetime UTC (naive o aware) a hora de Bolivia naive.
    Util para mostrar fechas almacenadas previamente en UTC.
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    return dt.astimezone(BOLIVIA_TZ).replace(tzinfo=None)


def to_iso(dt: datetime) -> str | None:
    """
    Formatea un datetime de Bolivia a cadena ISO 8601 con offset
    explicito -04:00 para que clientes y APIs sepan la zona horaria.

    Ejemplo: '2026-03-04T11:00:00-04:00'
    """
    if dt is None:
        return None
    return dt.isoformat() + '-04:00'


# ==============================================================
# LOGGING CON HORA DE BOLIVIA
# ==============================================================

class BoliviaFormatter(logging.Formatter):
    """
    Formatter de logging que usa la hora de Bolivia en lugar
    de la hora local del servidor.

    Uso:
        fmt = BoliviaFormatter('%(asctime)s [%(levelname)s] %(message)s')
        handler.setFormatter(fmt)
    """

    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None) -> str:
        dt = datetime.fromtimestamp(record.created, tz=BOLIVIA_TZ)
        if datefmt:
            return dt.strftime(datefmt)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
