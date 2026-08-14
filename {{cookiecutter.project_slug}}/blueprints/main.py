"""Vistas principales: home, dashboard y perfil."""
from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
async def home():
    return render_template("home.html")


@main_bp.route("/dashboard")
async def dashboard():
    return render_template("panel/dashboard.html")


@main_bp.route("/perfil")
async def perfil():
    return render_template("panel/perfil.html")


@main_bp.route("/movil")
async def movil():
    return render_template("movil.html")
