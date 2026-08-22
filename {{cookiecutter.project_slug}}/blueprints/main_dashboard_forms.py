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





from .main_dashboard_forms_hero import handle_hero
from .main_dashboard_forms_quote import handle_quote
from .main_dashboard_forms_contact import handle_contact
from .main_dashboard_forms_deploy import handle_deploy
from .main_dashboard_forms_home_media import handle_home_media
from .main_dashboard_forms_forms import handle_forms
from .main_dashboard_forms_legal import handle_legal
from .main_dashboard_forms_noticumbres import handle_noticumbres


async def _handle_post(request):
    if "save_hero_config" in request.form:
        return await handle_hero(request)
    if "add_quote_field" in request.form or "edit_quote_field" in request.form or "delete_quote_field" in request.form or "save_quote_button_config" in request.form:
        return await handle_quote(request)
    if "save_whatsapp_config" in request.form or "save_quote_email_config" in request.form or "save_social_config" in request.form:
        return await handle_contact(request)
    if "save_network_config" in request.form or "download_wsgi" in request.form or "download_env" in request.form or "sync_translations" in request.form:
        return await handle_deploy(request)
    if "move" in request.form or "remove_slot" in request.form or "save_home_media_mode" in request.form or "move_image" in request.form or "remove_image_slot" in request.form or "upload_home_image" in request.form or "home_video" in request.files:
        return await handle_home_media(request)
    if "save_form_fields_config" in request.form or "add_form_field" in request.form or "delete_form_field" in request.form or "toggle_form_field" in request.form:
        return await handle_forms(request)
    if "save_privacy_policy" in request.form or "save_terms_conditions" in request.form:
        return await handle_legal(request)
    if "save_noticumbres_config" in request.form:
        return await handle_noticumbres(request)
    return redirect(url_for('main.dashboard'))
