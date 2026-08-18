"""Registro centralizado de Blueprints."""
from blueprints.admin import admin_bp
from blueprints.ayuda import ayuda_bp
from blueprints.api import api_bp
from blueprints.auth import auth_bp
from blueprints.generador import generador_bp
from blueprints.main import main_bp
from blueprints.quotes import quotes_bp


def register_blueprints(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(ayuda_bp)
    app.register_blueprint(generador_bp)
    app.register_blueprint(quotes_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_bp, url_prefix="/api")
