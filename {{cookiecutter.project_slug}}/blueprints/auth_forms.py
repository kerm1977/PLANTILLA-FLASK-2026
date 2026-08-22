"""Formularios de autenticación."""
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
)
from wtforms.validators import DataRequired, EqualTo, Length, Optional

from utils import validators as v


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


class DynamicRegisterForm(FlaskForm):
    submit = SubmitField("Crear cuenta")
