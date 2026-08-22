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






async def handle_contact(request):
if "save_whatsapp_config" in request.form:
    phone = request.form.get("whatsapp_phone", "").strip()
    phone = "".join(ch for ch in phone if ch.isdigit())
    save_whatsapp_config({"phone": phone})
    flash("Número de WhatsApp actualizado", "success")
    return redirect(url_for("main.dashboard"))

if "save_quote_email_config" in request.form:
    email = request.form.get("quote_email", "").strip()
    save_quote_email_config({"email": email})
    flash("Correo de cotizaciones actualizado", "success")
    return redirect(url_for("main.dashboard"))

if "save_social_config" in request.form:
    social_cfg = {}
    for net in SOCIAL_NETWORKS:
        social_cfg[net] = {
            "url": request.form.get(f"social_{net}_url", "").strip(),
            "enabled": request.form.get(f"social_{net}_enabled") == "1",
        }
    save_social_config(social_cfg)
    flash("Redes sociales actualizadas", "success")
    return redirect(url_for("main.dashboard"))

    return redirect(url_for('main.dashboard'))
