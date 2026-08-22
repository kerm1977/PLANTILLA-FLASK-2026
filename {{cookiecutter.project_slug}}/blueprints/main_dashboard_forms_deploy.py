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






async def handle_deploy(request):
if "save_network_config" in request.form:
    cfg = {
        "pa_username": request.form.get("pa_username", "").strip(),
        "project_slug": request.form.get("project_slug", "").strip() or os.path.basename(current_app.root_path),
        "python_version": request.form.get("python_version", PYTHONANYWHERE_PY_VERSIONS[0]),
        "domain": request.form.get("domain", "").strip(),
    }
    save_deploy_config(cfg)
    flash("Configuración de red guardada", "success")
    return redirect(url_for("main.dashboard"))

if "download_wsgi" in request.form:
    cfg = {
        "pa_username": request.form.get("pa_username", "").strip(),
        "project_slug": request.form.get("project_slug", "").strip() or os.path.basename(current_app.root_path),
    }
    content = _build_wsgi_content(cfg)
    return Response(
        content,
        mimetype="text/x-python",
        headers={"Content-Disposition": "attachment; filename=wsgi_pythonanywhere.py"},
    )

if "download_env" in request.form:
    content = _build_env_content(request.form)
    return Response(
        content,
        mimetype="text/plain",
        headers={"Content-Disposition": "attachment; filename=.env"},
    )

if "sync_translations" in request.form:
    try:
        summary = sync_translations()
        added_total = sum(s["added"] for s in summary.values())
        if added_total:
            flash(
                f"Traducciones actualizadas: {added_total} cadena(s) nueva(s) agregadas a "
                f"{', '.join(lang.upper() for lang in summary)}.",
                "success",
            )
        else:
            flash("Las traducciones ya estaban al día, no se encontraron cadenas nuevas.", "success")
    except Exception as e:
        flash(f"Error al actualizar traducciones: {e}", "danger")
    return redirect(url_for("main.dashboard"))

    return redirect(url_for('main.dashboard'))
