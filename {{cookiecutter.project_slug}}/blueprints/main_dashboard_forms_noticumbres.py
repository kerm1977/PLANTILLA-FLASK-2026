"""Ruta del panel de administración."""
from __future__ import annotations
import json
import os
from datetime import datetime

from flask import Response, current_app, flash, redirect, render_template, request, session, url_for
from sqlalchemy import func, select

from blueprints.main import main_bp, superuser_required
from blueprints.main_config import *  # noqa: F401, F403
from blueprints.main_noticumbres import load_noticumbres, save_noticumbres
from i18n import sync_translations, translation_status
from models import QuoteField, User, async_session






async def handle_noticumbres(request):
if "save_noticumbres_config" in request.form:
    data = load_noticumbres()
    data.setdefault("config", {})
    data["config"]["update_time"] = request.form.get("noticumbres_update_time", "").strip()
    try:
        data["config"]["max_posts"] = int(request.form.get("noticumbres_max_posts", "0") or "0")
    except ValueError:
        data["config"]["max_posts"] = 0
    save_noticumbres(data)
    flash("Configuración de noticias actualizada", "success")
    return redirect(url_for("main.dashboard") + "?section=noticumbresAdmin")


    return redirect(url_for('main.dashboard'))
