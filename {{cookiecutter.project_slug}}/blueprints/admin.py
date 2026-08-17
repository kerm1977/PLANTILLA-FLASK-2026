"""Panel administrativo para superusuarios."""
from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_wtf import FlaskForm
from sqlalchemy import select
from wtforms import BooleanField, PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length

from extensions import bcrypt
from models import User, async_session

admin_bp = Blueprint("admin", __name__)


TOP_SUPERUSERS = ["kenth1977@gmail.com", "lthikingcr@gmail.com"]


def superuser_required(f):
    @wraps(f)
    async def decorated(*args, **kwargs):
        if not session.get("is_superuser"):
            flash("Acceso restringido a superusuarios", "danger")
            return redirect(url_for("auth.login"))
        return await f(*args, **kwargs)

    return decorated


class ChangePasswordForm(FlaskForm):
    user_id = SelectField("Usuario", coerce=int, validators=[DataRequired()])
    current_password = PasswordField("Contraseña actual", validators=[DataRequired()])
    new_password = PasswordField(
        "Nueva contraseña", validators=[DataRequired(), Length(min=6)]
    )
    confirm_password = PasswordField("Verificar contraseña", validators=[DataRequired()])
    submit = SubmitField("Cambiar contraseña")


class ProfileForm(FlaskForm):
    first_name = StringField("Nombre", validators=[Length(max=120)])
    first_last_name = StringField("Primer apellido", validators=[Length(max=120)])
    second_last_name = StringField("Segundo apellido", validators=[Length(max=120)])
    phone_number = StringField("Teléfono", validators=[Length(max=50)])
    email = StringField("Correo", validators=[DataRequired(), Length(max=255)])
    username = StringField("Usuario", validators=[Length(max=80)])
    user_number = StringField("Número de usuario", validators=[Length(max=50)])
    submit = SubmitField("Guardar")


class DeleteProfileForm(FlaskForm):
    submit = SubmitField("Eliminar cuenta")


class ManageUserForm(FlaskForm):
    is_superuser = BooleanField("Superusuario")
    is_active = BooleanField("Activo")
    submit = SubmitField("Guardar")


@admin_bp.route("/", methods=["GET", "POST"])
@superuser_required
async def panel():
    form = ChangePasswordForm()
    async with async_session() as s:
        result = await s.execute(select(User).order_by(User.id))
        users = result.scalars().all()
        current_user = await s.get(User, session.get("user_id"))

    form.user_id.choices = [
        (u.id, f"{u.username} ({u.email})") for u in users
    ]

    edit_form = ProfileForm(obj=current_user)
    delete_form = DeleteProfileForm()
    manage_form = ManageUserForm()

    if form.validate_on_submit():
        if not bcrypt.check_password_hash(
            current_user.password_hash, form.current_password.data
        ):
            flash("Contraseña actual incorrecta", "danger")
            return redirect(url_for("admin.panel"))
        if form.new_password.data == form.current_password.data:
            return render_template(
                "panel/admin.html",
                users=users,
                form=form,
                current_user=current_user,
                edit_form=edit_form,
                delete_form=delete_form,
                manage_form=manage_form,
                top_superusers=TOP_SUPERUSERS,
                same_password_error=True,
            )
        if form.new_password.data != form.confirm_password.data:
            flash("Las contraseñas no coinciden", "danger")
            return redirect(url_for("admin.panel"))
        async with async_session() as s:
            user = await s.get(User, form.user_id.data)
            if user:
                user.password_hash = bcrypt.generate_password_hash(
                    form.new_password.data
                ).decode("utf-8")
                await s.commit()
                flash(f"Contraseña de {user.username} actualizada", "success")
                return redirect(url_for("admin.panel"))
    return render_template(
        "panel/admin.html",
        users=users,
        form=form,
        current_user=current_user,
        edit_form=edit_form,
        delete_form=delete_form,
        manage_form=manage_form,
        top_superusers=TOP_SUPERUSERS,
    )


@admin_bp.route("/editar", methods=["POST"])
@superuser_required
async def edit_profile():
    form = ProfileForm()
    if form.validate_on_submit():
        async with async_session() as s:
            user = await s.get(User, session.get("user_id"))
            if user:
                user.first_name = form.first_name.data
                user.first_last_name = form.first_last_name.data
                user.second_last_name = form.second_last_name.data
                user.phone_number = form.phone_number.data
                user.email = form.email.data
                user.username = form.username.data
                user.user_number = form.user_number.data
                await s.commit()
                flash("Perfil actualizado", "success")
    else:
        flash("Error al actualizar el perfil", "danger")
    return redirect(url_for("admin.panel"))


@admin_bp.route("/eliminar", methods=["POST"])
@superuser_required
async def delete_profile():
    form = DeleteProfileForm()
    if form.validate_on_submit():
        async with async_session() as s:
            user = await s.get(User, session.get("user_id"))
            if user:
                await s.delete(user)
                await s.commit()
                session.clear()
                flash("Cuenta eliminada", "info")
                return redirect(url_for("main.home"))
    flash("No se pudo eliminar la cuenta", "danger")
    return redirect(url_for("admin.panel"))


@admin_bp.route("/editar_usuario", methods=["POST"])
@superuser_required
async def edit_user():
    form = ManageUserForm()
    user_id = int(request.form.get("user_id", 0))
    if form.validate_on_submit() and user_id:
        async with async_session() as s:
            user = await s.get(User, user_id)
            if not user:
                flash("Usuario no encontrado", "danger")
                return redirect(url_for("admin.panel"))
            if user.email in TOP_SUPERUSERS:
                flash("No puedes modificar a un superusuario principal", "danger")
                return redirect(url_for("admin.panel"))
            user.is_active = bool(request.form.get("is_active"))
            if session.get("is_superuser") and session.get("email") in TOP_SUPERUSERS:
                user.is_superuser = bool(request.form.get("is_superuser"))
            await s.commit()
            flash(f"Usuario {user.username or user.email} actualizado", "success")
    else:
        flash("Error al actualizar el usuario", "danger")
    return redirect(url_for("admin.panel"))
