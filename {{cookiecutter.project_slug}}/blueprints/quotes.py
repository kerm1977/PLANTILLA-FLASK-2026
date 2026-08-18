"""Formulario público del Cotizador (wizard) y almacenamiento de respuestas."""
import asyncio
import json
import secrets

from utils import validators as v

from flask import Blueprint, current_app, redirect, render_template, request, url_for
from flask_mail import Message
from sqlalchemy import select

from blueprints.main import load_quote_email_config
from extensions import bcrypt, mail
from models import QuoteField, QuoteSubmission, User, async_session

quotes_bp = Blueprint("quotes", __name__)


async def _get_ordered_fields():
    async with async_session() as s:
        result = await s.execute(
            select(QuoteField).order_by(QuoteField.step, QuoteField.position)
        )
        return result.scalars().all()


def _group_by_step(fields):
    steps = []
    current_step = None
    current_list = None
    for f in fields:
        if f.step != current_step:
            current_step = f.step
            current_list = []
            steps.append({"step": current_step, "fields": current_list})
        current_list.append(f)
    return steps


async def _ensure_user_from_quote(s, data):
    """Crea un usuario automáticamente con los datos personales del cotizador."""
    email = (data.get("email") or "").strip()
    if not email:
        return None

    result = await s.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user:
        return user.id

    raw_password = secrets.token_urlsafe(24)
    user = User(
        first_name=(data.get("first_name") or "").strip() or None,
        first_last_name=(data.get("last_name") or "").strip() or None,
        country=(data.get("country") or "").strip() or None,
        phone_number=(data.get("whatsapp") or "").strip() or None,
        email=email,
        username=email,
        password_hash=bcrypt.generate_password_hash(raw_password).decode("utf-8"),
        is_superuser=False,
        is_top_superuser=False,
        is_active=True,
    )
    s.add(user)
    await s.flush()
    return user.id


def _format_quote_email_body(data):
    lines = ["Nueva cotización recibida", "=" * 30, ""]
    for key, value in data.items():
        if isinstance(value, list):
            value = ", ".join(value) or "—"
        lines.append(f"{key}: {value}")
    return "\n".join(lines)


async def _send_quote_email(data):
    """Envía la cotización al correo configurado en el dashboard."""
    quote_email = load_quote_email_config().get("email", "").strip()
    if not quote_email:
        current_app.logger.warning("No hay correo de cotizaciones configurado")
        return
    if data.get("contact_method") != "Correo electrónico":
        return

    sender = current_app.config.get("MAIL_DEFAULT_SENDER", "no-reply@localhost")
    user_email = data.get("email", "")
    msg = Message(
        subject="Nueva cotización - Cumbres CR",
        sender=sender,
        recipients=[quote_email],
        reply_to=[user_email] if user_email else None,
        body=_format_quote_email_body(data),
    )
    try:
        await asyncio.to_thread(mail.send, msg)
    except Exception as exc:
        current_app.logger.error("Error enviando cotización por correo: %s", exc)


@quotes_bp.route("/cotizador", methods=["GET", "POST"])
async def cotizador():
    fields = await _get_ordered_fields()

    if request.method == "POST":
        data = {}
        for f in fields:
            if f.field_type == "info":
                continue
            if f.field_type == "multi_choice":
                data[f.field_key] = request.form.getlist(f.field_key)
                continue

            value = request.form.get(f.field_key, "")
            data[f.field_key] = v.sanitize(value, v.COTIZADOR_FIELDS.get(f.field_key))

        async with async_session() as s:
            user_id = await _ensure_user_from_quote(s, data)
            s.add(QuoteSubmission(data=data, user_id=user_id))
            await s.commit()

        await _send_quote_email(data)
        return redirect(url_for("quotes.cotizador_gracias"))

    steps = _group_by_step(fields)
    return render_template("cotizador.html", steps=steps)


@quotes_bp.route("/cotizador/gracias")
async def cotizador_gracias():
    return render_template("cotizador_gracias.html")
