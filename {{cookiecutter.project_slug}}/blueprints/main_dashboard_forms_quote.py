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






async def handle_quote(request):
if "add_quote_field" in request.form:
    label = request.form.get("quote_label", "").strip()
    field_type = request.form.get("quote_field_type", "text")
    if field_type not in QUOTE_FIELD_TYPES:
        field_type = "text"
    if not label:
        flash("La pregunta necesita un texto", "warning")
        return redirect(url_for("main.dashboard"))
    try:
        step = int(request.form.get("quote_step", 1))
    except ValueError:
        step = 1
    help_text = request.form.get("quote_help_text", "").strip() or None
    required = request.form.get("quote_required") == "1"
    options_raw = request.form.get("quote_options", "")
    options = [o.strip() for o in options_raw.splitlines() if o.strip()] or None
    max_choices_raw = request.form.get("quote_max_choices", "").strip()
    max_choices = int(max_choices_raw) if max_choices_raw.isdigit() else None
    base_key = _slugify_field_key(label)
    async with async_session() as s:
        result = await s.execute(
            select(func.max(QuoteField.position)).where(QuoteField.step == step)
        )
        max_pos = result.scalar() or 0
        key = base_key
        suffix = 1
        while (await s.execute(select(QuoteField).where(QuoteField.field_key == key))).scalar_one_or_none():
            suffix += 1
            key = f"{base_key}_{suffix}"
        s.add(QuoteField(
            step=step,
            position=max_pos + 1,
            field_key=key,
            field_type=field_type,
            label=label,
            help_text=help_text,
            required=required,
            options=options,
            max_choices=max_choices,
        ))
        await s.commit()
    flash("Pregunta agregada al cotizador", "success")
    return redirect(url_for("main.dashboard"))

if "edit_quote_field" in request.form:
    field_id = int(request.form.get("quote_field_id", 0))
    label = request.form.get("quote_label", "").strip()
    field_type = request.form.get("quote_field_type", "text")
    if field_type not in QUOTE_FIELD_TYPES:
        field_type = "text"
    try:
        step = int(request.form.get("quote_step", 1))
    except ValueError:
        step = 1
    help_text = request.form.get("quote_help_text", "").strip() or None
    required = request.form.get("quote_required") == "1"
    options_raw = request.form.get("quote_options", "")
    options = [o.strip() for o in options_raw.splitlines() if o.strip()] or None
    max_choices_raw = request.form.get("quote_max_choices", "").strip()
    max_choices = int(max_choices_raw) if max_choices_raw.isdigit() else None
    async with async_session() as s:
        field = await s.get(QuoteField, field_id)
        if field:
            field.step = step
            field.field_type = field_type
            field.label = label or field.label
            field.help_text = help_text
            field.required = required
            field.options = options
            field.max_choices = max_choices
            await s.commit()
            flash("Pregunta actualizada", "success")
        else:
            flash("Pregunta no encontrada", "danger")
    return redirect(url_for("main.dashboard"))

if "delete_quote_field" in request.form:
    field_id = int(request.form.get("delete_quote_field", 0))
    async with async_session() as s:
        field = await s.get(QuoteField, field_id)
        if field:
            await s.delete(field)
            await s.commit()
            flash("Pregunta eliminada del cotizador", "success")
    return redirect(url_for("main.dashboard"))

if "save_quote_button_config" in request.form:
    visible = request.form.get("quote_button_visible") == "1"
    save_quote_button_config({"visible": visible})
    flash("Configuración del cotizador actualizada", "success")
    return redirect(url_for("main.dashboard"))

    return redirect(url_for('main.dashboard'))
