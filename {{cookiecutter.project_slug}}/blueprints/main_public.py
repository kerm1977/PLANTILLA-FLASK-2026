"""Rutas públicas y de usuario: home, perfil, usuarios, páginas."""
from __future__ import annotations

import json

from flask import (
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import login_required
from sqlalchemy import func, select

from i18n import set_locale

from blueprints.main import (
    get_home_image_slots,
    get_home_video_slots,
    load_form_fields_config,
    load_hero_config,
    load_home_media_config,
    load_privacy_policy,
    load_terms_conditions,
    main_bp,
    superuser_required,
)
from models import QuoteSubmission, User, async_session


@main_bp.route("/set-lang/<lang>")
async def set_lang(lang):
    set_locale(lang)
    next_url = request.args.get("next") or request.referrer or url_for("main.home")
    return redirect(next_url)


@main_bp.route("/")
async def home():
    media_config = load_home_media_config()
    if media_config["mode"] == "images":
        images = [s["url"] for s in get_home_image_slots() if s["url"]]
        if images:
            return render_template(
                "home.html",
                home_media_mode="images",
                home_images=images,
                home_image_interval=media_config["interval"],
                hero_config=load_hero_config(),
            )
    slots = get_home_video_slots()
    playlist = [s["url"] for s in slots if s["url"]]
    if not playlist:
        playlist = [url_for("static", filename="wq.mp4")]
    return render_template(
        "home.html",
        home_media_mode="video",
        home_videos=playlist,
        hero_config=load_hero_config(),
    )


@main_bp.route("/perfil", methods=["GET", "POST"])
@login_required
async def perfil():
    if request.method == "POST":
        try:
            async with async_session() as s:
                user = await s.get(User, session["user_id"])
                user.first_name = request.form.get("first_name", "").strip() or None
                user.first_last_name = request.form.get("first_last_name", "").strip() or None
                user.second_last_name = request.form.get("second_last_name", "").strip() or None
                user.phone_number = request.form.get("phone_number", "").strip() or None
                user.country = request.form.get("country", "").strip() or None
                user.email = request.form.get("email", "").strip() or user.email
                user.username = request.form.get("username", "").strip() or None
                user.user_number = request.form.get("user_number", "").strip() or None
                await s.commit()
            flash("Perfil actualizado", "success")
        except Exception as e:
            flash(f"Error al actualizar el perfil: {e}", "danger")
        return redirect(url_for("main.perfil"))
    async with async_session() as s:
        user = await s.get(User, session["user_id"])
        user_count = (await s.execute(select(func.count(User.id)))).scalar()
    cfg = load_form_fields_config()
    extra = json.loads(user.extra_data or "{}")
    user_columns = {"first_name", "first_last_name", "second_last_name", "phone_number", "country", "email", "username", "user_number"}
    extra_fields = [f for f in cfg["fields"] if f.get("active") and f["key"] not in user_columns]
    return render_template(
        "panel/perfil.html",
        user=user,
        user_count=user_count,
        extra=extra,
        extra_fields=extra_fields,
    )


@main_bp.route("/usuarios", methods=["GET", "POST"])
@superuser_required
async def usuarios():
    if request.method == "POST":
        if "delete_quote_submission" in request.form:
            quote_id = int(request.form.get("delete_quote_submission", 0))
            if quote_id:
                async with async_session() as s:
                    quote = await s.get(QuoteSubmission, quote_id)
                    if quote:
                        await s.delete(quote)
                        await s.commit()
                        flash("Cotización eliminada", "success")
                    else:
                        flash("Cotización no encontrada", "danger")
            return redirect(url_for("main.usuarios"))
        return redirect(url_for("main.usuarios"))
    async with async_session() as s:
        all_users = (await s.execute(select(User).order_by(User.id))).scalars().all()
        quote_rows = (await s.execute(select(QuoteSubmission))).scalars().all()
        quote_user_ids = {q.user_id for q in quote_rows if q.user_id}
        quote_list = [
            {
                "id": q.id,
                "user_id": q.user_id,
                "created_at": q.created_at,
                "data": q.data,
            }
            for q in quote_rows
        ]
    return render_template(
        "panel/usuarios.html",
        users=all_users,
        quote_submissions=quote_list,
        quote_user_ids=quote_user_ids,
        can_assign_top=bool(session.get("is_top_superuser")),
    )


@main_bp.route("/usuarios/<int:user_id>", methods=["GET", "POST"])
@superuser_required
async def usuario_detalle(user_id):
    if request.method == "POST":
        async with async_session() as s:
            u = await s.get(User, user_id)
            if not u:
                flash("Usuario no encontrado", "danger")
                return redirect(url_for("main.usuarios"))
            u.first_name = request.form.get("first_name", "").strip() or None
            u.first_last_name = request.form.get("first_last_name", "").strip() or None
            u.second_last_name = request.form.get("second_last_name", "").strip() or None
            u.phone_number = request.form.get("phone_number", "").strip() or None
            u.country = request.form.get("country", "").strip() or None
            u.email = request.form.get("email", "").strip() or u.email
            u.username = request.form.get("username", "").strip() or None
            u.user_number = request.form.get("user_number", "").strip() or None
            can_assign_top = bool(session.get("is_top_superuser"))
            u_top = u.is_top_superuser
            if not u_top and can_assign_top:
                u.is_superuser = "is_superuser" in request.form
            if not u_top:
                u.is_active = "is_active" in request.form
            await s.commit()
            flash("Usuario actualizado", "success")
        return redirect(url_for("main.usuario_detalle", user_id=user_id))
    async with async_session() as s:
        u = await s.get(User, user_id)
    if not u:
        flash("Usuario no encontrado", "danger")
        return redirect(url_for("main.usuarios"))
    cfg = load_form_fields_config()
    extra = json.loads(u.extra_data or "{}")
    user_columns = {"first_name", "first_last_name", "second_last_name", "phone_number", "country", "email", "username", "user_number"}
    extra_fields = [f for f in cfg["fields"] if f.get("active") and f["key"] not in user_columns]
    return render_template(
        "panel/usuario_detalle.html",
        u=u,
        extra=extra,
        extra_fields=extra_fields,
        can_assign_top=bool(session.get("is_top_superuser")),
    )


@main_bp.route("/movil")
async def movil():
    return render_template("movil.html")


@main_bp.route("/caminatas")
async def caminatas():
    return render_template("caminatas.html")


@main_bp.route("/contacto")
async def contacto():
    return render_template("contacto.html")


@main_bp.route("/quienes-somos")
async def quienes_somos():
    return render_template("quienes_somos.html")


@main_bp.route("/afiliados")
async def afiliados():
    return render_template("afiliados.html")


@main_bp.route("/terminos-y-condiciones")
async def terminos():
    return render_template(
        "terminos_y_condiciones.html",
        terms=load_terms_conditions(),
    )


@main_bp.route("/politica-de-privacidad")
async def privacidad():
    return render_template(
        "politica_de_privacidad.html",
        privacy=load_privacy_policy(),
    )
