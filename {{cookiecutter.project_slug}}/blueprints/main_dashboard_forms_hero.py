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






async def handle_hero(request):
if "save_hero_config" in request.form:
    cfg = {
        "title": request.form.get("hero_title", "").strip() or "Bienvenido",
        "description": request.form.get("hero_description", "").strip(),
        "button_text": request.form.get("hero_button_text", "").strip() or "Ver más",
        "align": request.form.get("hero_align", "center"),
        "title_size": request.form.get("hero_title_size", "md"),
        "description_size": request.form.get("hero_description_size", "md"),
        "button_size": request.form.get("hero_button_size", "md"),
        "button_bg_color_light": request.form.get("hero_button_bg_color_light", "#ffffff"),
        "button_text_color_light": request.form.get("hero_button_text_color_light", "#333333"),
        "button_bg_color_dark": request.form.get("hero_button_bg_color_dark", "#2a2a2e"),
        "button_text_color_dark": request.form.get("hero_button_text_color_dark", "#f1f3f8"),
        "button_hover_bg_color_light": request.form.get("hero_button_hover_bg_color_light", "#f1f1f1"),
        "button_hover_text_color_light": request.form.get("hero_button_hover_text_color_light", "#222222"),
        "button_hover_bg_color_dark": request.form.get("hero_button_hover_bg_color_dark", "#3a3a3f"),
        "button_hover_text_color_dark": request.form.get("hero_button_hover_text_color_dark", "#ffffff"),
        "button_radius": request.form.get("hero_button_radius", "6"),
    }
    save_hero_config(cfg)
    flash("Sección Hero actualizada", "success")
    return redirect(url_for("main.dashboard"))

    return redirect(url_for('main.dashboard'))
