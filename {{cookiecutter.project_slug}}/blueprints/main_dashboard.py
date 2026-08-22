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




@main_bp.route("/dashboard", methods=["GET", "POST"])
@superuser_required
async def dashboard():
    if request.method == "POST":
        return await _handle_post(request)

    async with async_session() as s:
        result = await s.execute(select(QuoteField).order_by(QuoteField.step, QuoteField.position))
        quote_fields = result.scalars().all()

    return render_template(
        "panel/dashboard.html",
        privacy_config=load_privacy_policy(),
        terms_config=load_terms_conditions(),
        home_slots=get_home_video_slots(),
        home_image_slots=get_home_image_slots(),
        home_media_config=load_home_media_config(),
        home_image_intervals=HOME_IMAGE_INTERVALS,
        translation_status=translation_status(),
        deploy_config=load_deploy_config(),
        pa_python_versions=PYTHONANYWHERE_PY_VERSIONS,
        hero_config=load_hero_config(),
        social_config=load_social_config(),
        quote_email_config=load_quote_email_config(),
        quote_fields=quote_fields,
        quote_field_types=QUOTE_FIELD_TYPES,
        form_fields_config=load_form_fields_config(),
        form_field_types=FORM_FIELD_TYPES,
        form_field_type_labels=FORM_FIELD_TYPE_LABELS,
        noticumbres_config=load_noticumbres(),
    )

