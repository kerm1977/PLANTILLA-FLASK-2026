"""Vistas de ayuda: instrucciones para ejecutar y generar el proyecto."""
from flask import Blueprint, render_template

ayuda_bp = Blueprint("ayuda", __name__)


@ayuda_bp.route("/ayuda")
async def ayuda():
    return render_template("ayuda/ayuda.html")
