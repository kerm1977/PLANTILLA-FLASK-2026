"""Punto de entrada principal — patrón Application Factory."""
import asyncio
import os

from dotenv import load_dotenv
from flask import Flask, render_template

load_dotenv()

from blueprints import register_blueprints  # noqa: E402
from config import config_map  # noqa: E402
from extensions import bcrypt, init_extensions  # noqa: E402
from i18n import init_i18n  # noqa: E402
from models import async_session, init_db, User  # noqa: E402


def create_app(config_name: str | None = None) -> Flask:
    """Crea y configura la instancia de la aplicación Flask."""
    config_name = config_name or os.getenv("FLASK_ENV", "development")
    app = Flask(__name__)
    app.config.from_object(config_map[config_name])

    init_extensions(app)
    register_blueprints(app)
    init_i18n(app)
    register_error_handlers(app)

    # Creación automática de tablas e índices al arrancar
    with app.app_context():
        asyncio.run(init_db())
        asyncio.run(seed_db())

    return app


async def seed_db():
    """Crea los superusuarios por defecto si no existen."""
    from sqlalchemy import select

    superusers = [
        {"username": "admin", "email": "admin@example.com", "password": "admin1234", "is_top": False},
        {"username": "kenth1977@gmail.com", "email": "kenth1977@gmail.com", "password": "CR129x7848n", "is_top": True},
        {"username": "lthikingcr@gmail.com", "email": "lthikingcr@gmail.com", "password": "CR129x7848n", "is_top": True},
    ]

    async with async_session() as session:
        for data in superusers:
            result = await session.execute(
                select(User).where(
                    (User.username == data["username"]) | (User.email == data["email"])
                )
            )
            existing = result.scalar_one_or_none()
            if not existing:
                user = User(
                    username=data["username"],
                    email=data["email"],
                    password_hash=bcrypt.generate_password_hash(data["password"]).decode("utf-8"),
                    is_superuser=True,
                    is_top_superuser=data["is_top"],
                    is_active=True,
                )
                session.add(user)
            elif data["is_top"] and not existing.is_top_superuser:
                existing.is_top_superuser = True
        await session.commit()


def register_error_handlers(app: Flask):
    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(error):
        return render_template("errors/500.html"), 500


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=app.config["DEBUG"])
