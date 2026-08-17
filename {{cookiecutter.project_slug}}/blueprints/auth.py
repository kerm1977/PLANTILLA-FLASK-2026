"""Vistas de autenticación: login, registro y recuperación."""
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_wtf import FlaskForm
from sqlalchemy import select
from wtforms import (
    BooleanField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
)
from wtforms.validators import DataRequired, EqualTo, Length, Optional

from extensions import bcrypt
from models import User, async_session

auth_bp = Blueprint("auth", __name__)


class LoginForm(FlaskForm):
    email = StringField(
        "Correo electrónico",
        validators=[DataRequired(), Length(max=255)],
    )
    password = PasswordField("Contraseña", validators=[DataRequired()])
    remember = BooleanField("Recordarme")
    submit = SubmitField("Ingresar")


class RegisterForm(FlaskForm):
    first_name = StringField(
        "Nombre", validators=[DataRequired(), Length(max=80)]
    )
    first_last_name = StringField(
        "Primer apellido", validators=[DataRequired(), Length(max=80)]
    )
    second_last_name = StringField(
        "Segundo apellido (opcional)",
        validators=[Optional(), Length(max=80)],
    )
    phone_number = StringField(
        "Teléfono", validators=[DataRequired(), Length(max=40)]
    )
    email = StringField(
        "Correo electrónico",
        validators=[DataRequired(), Length(max=255)],
    )
    username = StringField(
        "Usuario", validators=[Optional(), Length(max=80)]
    )
    user_number = StringField(
        "Número de usuario", validators=[Optional(), Length(max=80)]
    )
    password = PasswordField(
        "Contraseña", validators=[DataRequired(), Length(min=6)]
    )
    confirm = PasswordField(
        "Confirmar contraseña",
        validators=[
            DataRequired(),
            EqualTo("password", message="Las contraseñas no coinciden"),
        ],
    )
    role = SelectField(
        "Tipo de usuario",
        choices=[
            ("regular", "Usuario regular"),
            ("admin", "Administrador"),
            ("top", "Superusuario principal"),
        ],
        default="regular",
    )
    submit = SubmitField("Crear cuenta")

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators=extra_validators):
            return False
        has_username = bool(self.username.data and self.username.data.strip())
        has_number = bool(
            self.user_number.data and self.user_number.data.strip()
        )
        if not has_username and not has_number:
            self.username.errors.append(
                "Debes indicar un usuario o un número de usuario"
            )
            self.user_number.errors.append(
                "Debes indicar un usuario o un número de usuario"
            )
            return False
        if has_username and has_number:
            self.username.errors.append(
                "Indica solo usuario o solo número de usuario, no ambos"
            )
            self.user_number.errors.append(
                "Indica solo usuario o solo número de usuario, no ambos"
            )
            return False
        return True


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
    can_assign_role = bool(session.get("is_superuser"))
    can_assign_top = bool(session.get("is_top_superuser"))
    referrer = request.referrer or ""
    if (
        not can_assign_role
        and url_for("auth.login") not in referrer
        and url_for("auth.registro") not in referrer
    ):
        return redirect(url_for("auth.login"))
    form = RegisterForm()
    if not can_assign_top:
        form.role.choices = [
            c for c in form.role.choices if c[0] != "top"
        ]
    if form.validate_on_submit():
        async with async_session() as s:
            email = form.email.data.strip().lower()
            username = form.username.data.strip() or None
            user_number = form.user_number.data.strip() or None
            filters = [User.email == email]
            if username:
                filters.append(User.username == username)
            if user_number:
                filters.append(User.user_number == user_number)
            result = await s.execute(
                select(User).where(*[f for f in filters if f is not None])
            )
            existing = result.scalar_one_or_none()
            if existing:
                flash(
                    "El correo, usuario o número ya está registrado", "danger"
                )
            else:
                user = User(
                    first_name=form.first_name.data.strip(),
                    first_last_name=form.first_last_name.data.strip(),
                    second_last_name=form.second_last_name.data.strip()
                    or None,
                    phone_number=form.phone_number.data.strip(),
                    email=email,
                    username=username,
                    user_number=user_number,
                    password_hash=bcrypt.generate_password_hash(
                        form.password.data
                    ).decode("utf-8"),
                    is_superuser=can_assign_role and form.role.data in ("admin", "top"),
                    is_top_superuser=can_assign_top and form.role.data == "top",
                    is_active=True,
                )
                s.add(user)
                await s.commit()
                if can_assign_role:
                    flash("Usuario creado", "success")
                    return redirect(url_for("main.usuarios"))
                flash("Cuenta creada. Ahora inicia sesión.", "success")
                return redirect(url_for("auth.login"))
    return render_template("auth/registro.html", form=form, can_assign_role=can_assign_role)


@auth_bp.route("/recuperar")
async def recuperar():
    return render_template("auth/recuperar.html")


@auth_bp.route("/logout")
async def logout():
    session.clear()
    flash("Sesión cerrada", "info")
    return redirect(url_for("main.home"))
