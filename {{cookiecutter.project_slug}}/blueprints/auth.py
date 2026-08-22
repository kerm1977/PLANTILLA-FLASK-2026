"""Vistas de autenticación: login, registro y recuperación."""
import json

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from sqlalchemy import select

from blueprints.auth_forms import DynamicRegisterForm, LoginForm, RegisterForm
from extensions import bcrypt
from models import User, async_session

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
async def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        async with async_session() as s:
            result = await s.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()
        if user and user.is_active and bcrypt.check_password_hash(
            user.password_hash, form.password.data
        ):
            session["user_id"] = user.id
            session["username"] = (
                user.username or user.user_number or user.email
            )
            session["email"] = user.email
            session["is_superuser"] = user.is_superuser
            session["is_top_superuser"] = user.is_top_superuser
            if form.remember.data:
                session.permanent = True
            flash(f"Bienvenido, {session['username']}", "success")
            return redirect(url_for("main.home"))
        flash("Credenciales inválidas", "danger")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/registro", methods=["GET", "POST"])
async def registro():
    from blueprints.main import load_form_fields_config

    can_assign_role = bool(session.get("is_superuser"))
    can_assign_top = bool(session.get("is_top_superuser"))
    referrer = request.referrer or ""
    if (
        not can_assign_role
        and url_for("auth.login") not in referrer
        and url_for("auth.registro") not in referrer
    ):
        return redirect(url_for("auth.login"))

    cfg = load_form_fields_config()
    registro_fields = [f for f in cfg["fields"] if f.get("active")] if cfg.get("enabled") else []

    form = DynamicRegisterForm()
    if form.validate_on_submit():
        errors = []
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        confirm = request.form.get("confirm", "").strip()
        if not email:
            errors.append("El correo es requerido")
        if not password or len(password) < 6:
            errors.append("La contraseña debe tener al menos 6 caracteres")
        if password != confirm:
            errors.append("Las contraseñas no coinciden")
        for field in registro_fields:
            if field.get("required"):
                if field.get("data_type") == "checkbox":
                    if field["key"] not in request.form:
                        errors.append(f"{field['name']} es requerido")
                else:
                    if not request.form.get(field["key"], "").strip():
                        errors.append(f"{field['name']} es requerido")
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template(
                "auth/registro.html",
                form=form,
                can_assign_role=can_assign_role,
                can_assign_top=can_assign_top,
                registro_fields=registro_fields,
            )

        active_keys = {f["key"] for f in registro_fields}

        first_name = v.name(request.form.get("first_name", "")) or None if "first_name" in active_keys else None
        first_last_name = v.name(request.form.get("first_last_name", "")) or None if "first_last_name" in active_keys else None
        second_last_name = v.name(request.form.get("second_last_name", "")) or None if "second_last_name" in active_keys else None
        phone_number = v.digits(request.form.get("phone_number", "")) or None if "phone_number" in active_keys else None
        username = request.form.get("username", "").strip() or None if "username" in active_keys else None
        user_number = request.form.get("user_number", "").strip() or None if "user_number" in active_keys else None
        country = request.form.get("country", "").strip() or None if "country" in active_keys else None

        extra = {}
        user_columns = {"first_name", "first_last_name", "second_last_name", "phone_number", "country", "email", "username", "user_number"}
        for field in registro_fields:
            key = field["key"]
            if key in user_columns:
                continue
            if field.get("data_type") == "checkbox":
                extra[key] = "1" if key in request.form else ""
            else:
                extra[key] = request.form.get(key, "").strip()

        role = request.form.get("role", "regular") if can_assign_role else "regular"
        is_superuser = can_assign_role and role in ("admin", "top")
        is_top_superuser = can_assign_top and role == "top"

        async with async_session() as s:
            filters = [User.email == email]
            if username:
                filters.append(User.username == username)
            if user_number:
                filters.append(User.user_number == user_number)
            result = await s.execute(select(User).where(*[f for f in filters if f is not None]))
            existing = result.scalar_one_or_none()
            if existing:
                flash("El correo, usuario o número ya está registrado", "danger")
            else:
                user = User(
                    first_name=first_name,
                    first_last_name=first_last_name,
                    second_last_name=second_last_name,
                    phone_number=phone_number,
                    country=country,
                    email=email,
                    username=username,
                    user_number=user_number,
                    extra_data=json.dumps(extra) if extra else None,
                    password_hash=bcrypt.generate_password_hash(password).decode("utf-8"),
                    is_superuser=is_superuser,
                    is_top_superuser=is_top_superuser,
                    is_active=True,
                )
                s.add(user)
                await s.commit()
                if can_assign_role:
                    flash("Usuario creado", "success")
                    return redirect(url_for("main.usuarios"))
                flash("Cuenta creada. Ahora inicia sesión.", "success")
                return redirect(url_for("auth.login"))
    return render_template(
        "auth/registro.html",
        form=form,
        can_assign_role=can_assign_role,
        can_assign_top=can_assign_top,
        registro_fields=registro_fields,
    )


@auth_bp.route("/recuperar")
async def recuperar():
    return render_template("auth/recuperar.html")


@auth_bp.route("/logout")
async def logout():
    session.clear()
    flash("Sesión cerrada", "info")
    return redirect(url_for("main.home"))
