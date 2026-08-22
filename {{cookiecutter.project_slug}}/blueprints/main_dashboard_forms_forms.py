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






async def handle_forms(request):
if "save_form_fields_config" in request.form:
    cfg = load_form_fields_config()
    cfg["enabled"] = request.form.get("form_fields_enabled") == "1"
    save_form_fields_config(cfg)
    flash("Configuración de formularios actualizada", "success")
    return redirect(url_for("main.dashboard") + "?section=formFields")

if "add_form_field" in request.form:
    name = request.form.get("form_field_name", "").strip()
    data_type = request.form.get("form_field_type", "text")
    if data_type not in FORM_FIELD_TYPES:
        data_type = "text"
    if not name:
        flash("El campo necesita un nombre", "warning")
        return redirect(url_for("main.dashboard"))
    cfg = load_form_fields_config()
    next_id = 1
    if cfg["fields"]:
        next_id = max(f.get("id", 0) for f in cfg["fields"]) + 1
    cfg["fields"].append(
        {
            "id": next_id,
            "name": name,
            "key": _slugify_field_key(name),
            "data_type": data_type,
            "required": request.form.get("form_field_required") == "1",
            "active": True,
        }
    )
    save_form_fields_config(cfg)
    flash("Campo agregado", "success")
    return redirect(url_for("main.dashboard") + "?section=formFields")

if "delete_form_field" in request.form:
    field_id = int(request.form.get("delete_form_field_id", 0))
    cfg = load_form_fields_config()
    cfg["fields"] = [f for f in cfg["fields"] if f.get("id") != field_id]
    save_form_fields_config(cfg)
    flash("Campo eliminado", "success")
    return redirect(url_for("main.dashboard") + "?section=formFields")

if "toggle_form_field" in request.form:
    field_id = int(request.form.get("toggle_form_field_id", 0))
    cfg = load_form_fields_config()
    for f in cfg["fields"]:
        if f.get("id") == field_id:
            f["active"] = not f.get("active", True)
            break
    save_form_fields_config(cfg)
    flash("Estado del campo actualizado", "success")
    return redirect(url_for("main.dashboard") + "?section=formFields")

    return redirect(url_for('main.dashboard'))
