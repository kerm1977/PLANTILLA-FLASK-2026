"""Vistas principales: home, dashboard y perfil."""
from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from i18n import set_locale
from models import User, async_session

main_bp = Blueprint("main", __name__)


def login_required(f):
    @wraps(f)
    async def decorated(*args, **kwargs):
        if not session.get("user_id"):
            flash("Inicia sesión para continuar", "warning")
            return redirect(url_for("auth.login"))
        return await f(*args, **kwargs)

    return decorated


@main_bp.route("/set-lang/<lang>")
async def set_lang(lang):
    set_locale(lang)
    return redirect(request.referrer or url_for("main.home"))


@main_bp.route("/")
async def home():
    return render_template("home.html")


@main_bp.route("/dashboard")
@login_required
async def dashboard():
    return render_template("panel/dashboard.html")


@main_bp.route("/perfil")
@login_required
async def perfil():
    async with async_session() as s:
        user = await s.get(User, session["user_id"])
    return render_template("panel/perfil.html", user=user)


@main_bp.route("/movil")
async def movil():
    return render_template("movil.html")


@main_bp.route("/caminatas")
async def caminatas():
    return render_template("caminatas.html")
