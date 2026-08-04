"""Vista del panel administrativo (solo maqueta por ahora)."""
from flask import Blueprint, render_template

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/")
async def panel():
    return render_template("panel/admin.html")
