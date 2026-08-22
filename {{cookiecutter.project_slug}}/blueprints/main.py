"""Blueprint principal y re-exportaciones."""
from __future__ import annotations
from functools import wraps

from flask import Blueprint, flash, redirect, session, url_for

main_bp = Blueprint("main", __name__)


def login_required(f):
    @wraps(f)
    async def decorated(*args, **kwargs):
        if not session.get("user_id"):
            flash("Inicia sesión para continuar", "warning")
            return redirect(url_for("auth.login"))
        return await f(*args, **kwargs)

    return decorated

def superuser_required(f):
    @wraps(f)
    async def decorated(*args, **kwargs):
        if not session.get("is_superuser"):
            flash("Acceso restringido a superusuarios", "danger")
            return redirect(url_for("auth.login"))
        return await f(*args, **kwargs)

    return decorated

def _inject_whatsapp_config():
    return {"whatsapp_config": load_whatsapp_config()}

def _inject_quote_button_config():
    return {"quote_button_config": load_quote_button_config()}


from blueprints.main_config import *  # noqa: E402, F401, F403
import blueprints.main_dashboard  # noqa: E402, F401
import blueprints.main_noticumbres  # noqa: E402, F401
import blueprints.main_public  # noqa: E402, F401
