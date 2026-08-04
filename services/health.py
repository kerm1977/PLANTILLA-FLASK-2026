"""Servicio de verificación de salud del sistema."""
from sqlalchemy import text

from models.base import async_session


async def check_database() -> bool:
    """Comprueba que la base de datos asíncrona (aiosqlite) responde."""
    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
