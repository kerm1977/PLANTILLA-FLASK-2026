"""Validaciones y sanitizadores centralizados del proyecto.

Este módulo agrupa la lógica de normalización de datos para formularios.
Cualquier cambio en las reglas de sanitización debe hacerse aquí para que
se aplique automáticamente en el cotizador, el registro y futuros formularios.
"""
import re


def _normalize(value: str | None) -> str:
    return (value or "").strip()


def name(value: str | None) -> str | None:
    """Nombre/apellido: primera letra de cada palabra en mayúscula."""
    v = _normalize(value)
    return v.title() if v else None


def email(value: str | None) -> str | None:
    """Correo electrónico: minúsculas sin espacios."""
    v = _normalize(value)
    return v.lower() if v else None


def digits(value: str | None) -> str | None:
    """Solo dígitos numéricos (teléfono, número de personas, etc.)."""
    v = _normalize(value)
    return re.sub(r"\D", "", v) if v is not None else None


# Mapeo de campos del cotizador a su sanitizador
COTIZADOR_FIELDS = {
    "first_name": name,
    "last_name": name,
    "email": email,
    "whatsapp": digits,
    "people_count": digits,
}

# Mapeo de campos del formulario de registro
REGISTRO_FIELDS = {
    "first_name": name,
    "first_last_name": name,
    "second_last_name": name,
    "email": email,
    "phone_number": digits,
}


def sanitize(value: str | None, sanitizer: callable) -> str | None:
    """Aplica un sanitizador con protección ante None."""
    if sanitizer is None:
        return _normalize(value)
    return sanitizer(value)
