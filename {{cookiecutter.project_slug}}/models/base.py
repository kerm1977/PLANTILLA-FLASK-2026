"""Motor asíncrono de base de datos (SQLAlchemy 2.0 + aiosqlite)."""
import os

from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///app.db")

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    """Clase base declarativa para todos los modelos."""


async def init_db():
    """Crea tablas e índices automáticamente al arrancar la aplicación."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        try:
            await conn.exec_driver_sql(
                "ALTER TABLE users ADD COLUMN is_top_superuser BOOLEAN DEFAULT 0 NOT NULL"
            )
        except Exception:
            pass


async def close_db():
    """Cierre limpio del motor asíncrono."""
    await engine.dispose()
