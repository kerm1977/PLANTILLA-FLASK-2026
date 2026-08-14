"""Punto de entrada principal — patrón Application Factory."""
import asyncio
import os

from dotenv import load_dotenv
from flask import Flask, render_template

load_dotenv()

from blueprints import register_blueprints  # noqa: E402
from config import config_map  # noqa: E402
from extensions import init_extensions  # noqa: E402
from models import init_db  # noqa: E402


def create_app(config_name: str | None = None) -> Flask:
    """Crea y configura la instancia de la aplicación Flask."""
    config_name = config_name or os.getenv("FLASK_ENV", "development")
    app = Flask(__name__)
    app.config.from_object(config_map[config_name])

    init_extensions(app)
    register_blueprints(app)
    register_error_handlers(app)

    # Creación automática de tablas e índices al arrancar
    with app.app_context():
        asyncio.run(init_db())

    return app


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
