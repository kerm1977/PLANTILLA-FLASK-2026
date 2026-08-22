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






async def handle_legal(request):
if "save_privacy_policy" in request.form:
    cfg = load_privacy_policy()
    cfg["content"] = request.form.get("privacy_content", "").strip()
    save_privacy_policy(cfg)
    flash("Política de privacidad actualizada", "success")
    return redirect(url_for("main.dashboard") + "?section=privacyPolicy")

if "save_terms_conditions" in request.form:
    cfg = load_terms_conditions()
    cfg["content"] = request.form.get("terms_content", "").strip()
    save_terms_conditions(cfg)
    flash("Términos y condiciones actualizados", "success")
    return redirect(url_for("main.dashboard") + "?section=termsConditions")

    return redirect(url_for('main.dashboard'))
