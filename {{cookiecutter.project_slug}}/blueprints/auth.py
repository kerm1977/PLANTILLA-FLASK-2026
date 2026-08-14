"""Vistas de autenticación: login y registro (solo maqueta por ahora)."""
from flask import Blueprint, render_template

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login")
async def login():
    return render_template("auth/login.html")


@auth_bp.route("/registro")
async def registro():
    return render_template("auth/registro.html")
