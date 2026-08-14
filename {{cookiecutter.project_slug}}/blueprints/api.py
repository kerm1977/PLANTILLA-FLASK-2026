"""API REST: health checks y futuros endpoints JSON."""
from flask import Blueprint, jsonify

from services.health import check_database

api_bp = Blueprint("api", __name__)


@api_bp.route("/health")
async def health():
    """Endpoint de salud: verifica app y base de datos asíncrona."""
    db_ok = await check_database()
    status = 200 if db_ok else 503
    return jsonify(app="ok", database="ok" if db_ok else "error"), status


@api_bp.route("/status")
async def status():
    return jsonify(status="ok", version="0.1.0")
