"""Inicialización desacoplada de extensiones (patrón Application Factory).

Cada extensión se instancia aquí sin app y se vincula en app.py
con init_app(app). Así se evitan importaciones circulares.
"""
from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf import CSRFProtect

bcrypt = Bcrypt()          # Hashing seguro de credenciales locales
cache = Cache()            # Caché en memoria (Redis al escalar)
cors = CORS()              # Permisos cross-origin para la API
csrf = CSRFProtect()       # Protección CSRF en formularios (Flask-WTF)
jwt = JWTManager()         # Access & Refresh tokens para APIs
login_manager = LoginManager()  # Gestión de sesión local
mail = Mail()              # Envío de correos SMTP

login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"


def init_extensions(app):
    """Vincula todas las extensiones a la instancia de Flask."""
    bcrypt.init_app(app)
    cache.init_app(app)
    cors.init_app(app, origins=app.config["CORS_ORIGINS"])
    csrf.init_app(app)
    jwt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    """Carga diferida del usuario para Flask-Login (se activará con auth real)."""
    return None
