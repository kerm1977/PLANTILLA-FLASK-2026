"""Carga y guardado de configuraciones JSON."""
from __future__ import annotations
import glob
import json
import os
import re
import uuid
from datetime import datetime
from pathlib import Path

from flask import current_app


ALLOWED_VIDEO_EXT = {"mp4", "webm", "ogg"}

HOME_VIDEO_SLOTS = 3

ALLOWED_IMAGE_EXT = {"jpg", "jpeg", "png", "webp"}

HOME_IMAGE_SLOTS = 6

HOME_IMAGE_INTERVALS = [5, 10, 15, 20, 25]

PYTHONANYWHERE_PY_VERSIONS = ["3.13", "3.12", "3.11", "3.10", "3.9"]

QUOTE_FIELD_TYPES = [
    "text",
    "email",
    "tel",
    "number",
    "textarea",
    "single_choice",
    "multi_choice",
    "yes_no",
    "info",
]

FORM_FIELD_TYPES = [
    "text",
    "email",
    "tel",
    "number",
    "date",
    "textarea",
    "select",
    "checkbox",
]

FORM_FIELD_TYPE_LABELS = {
    "text": "Texto",
    "email": "Correo electrónico",
    "tel": "Teléfono",
    "number": "Número",
    "date": "Fecha",
    "textarea": "Párrafo",
    "select": "Lista desplegable",
    "checkbox": "Casilla",
}


__all__ = ['_build_env_content', '_build_wsgi_content', '_deploy_config_path', '_form_fields_config_path', '_hero_config_path', '_home_media_config_path', '_image_slot_file', '_images_dir', '_privacy_policy_path', '_quote_button_config_path', '_quote_email_config_path', '_slot_file', '_slugify_field_key', '_social_config_path', '_terms_conditions_path', '_videos_dir', '_whatsapp_config_path', 'get_home_image_slots', 'get_home_video_slots', 'load_deploy_config', 'load_form_fields_config', 'load_hero_config', 'load_home_media_config', 'load_privacy_policy', 'load_quote_button_config', 'load_quote_email_config', 'load_social_config', 'load_terms_conditions', 'load_whatsapp_config', 'save_deploy_config', 'save_form_fields_config', 'save_hero_config', 'save_home_media_config', 'save_privacy_policy', 'save_quote_button_config', 'save_quote_email_config', 'save_social_config', 'save_terms_conditions', 'save_whatsapp_config', 'ALLOWED_VIDEO_EXT', 'HOME_VIDEO_SLOTS', 'ALLOWED_IMAGE_EXT', 'HOME_IMAGE_SLOTS', 'HOME_IMAGE_INTERVALS', 'PYTHONANYWHERE_PY_VERSIONS', 'QUOTE_FIELD_TYPES', 'FORM_FIELD_TYPES', 'FORM_FIELD_TYPE_LABELS']

def _build_env_content(form):
    lines = [
        f"FLASK_ENV=production",
        f"SECRET_KEY={form.get('secret_key', '').strip()}",
        f"JWT_SECRET_KEY={form.get('jwt_secret_key', '').strip()}",
        f"DATABASE_URL={form.get('database_url', '').strip()}",
        f"CACHE_TYPE={form.get('cache_type', 'SimpleCache').strip()}",
        f"CORS_ORIGINS={form.get('cors_origins', '*').strip()}",
        f"MAIL_SERVER={form.get('mail_server', '').strip()}",
        f"MAIL_PORT={form.get('mail_port', '25').strip()}",
        f"MAIL_USE_TLS={form.get('mail_use_tls', 'false').strip()}",
        f"MAIL_USERNAME={form.get('mail_username', '').strip()}",
        f"MAIL_PASSWORD={form.get('mail_password', '').strip()}",
    ]
    return "\n".join(lines) + "\n"

def _build_wsgi_content(cfg):
    username = cfg["pa_username"] or "TU_USUARIO"
    slug = cfg["project_slug"]
    return f"""import sys
import os

project_home = '/home/{username}/{slug}'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from dotenv import load_dotenv
load_dotenv(os.path.join(project_home, '.env'))

os.environ.setdefault('FLASK_ENV', 'production')

from app import app as application
"""

def _deploy_config_path():
    return os.path.join(current_app.root_path, "deploy_config.json")

def _form_fields_config_path():
    return os.path.join(current_app.root_path, "form_fields_config.json")

def _hero_config_path():
    return os.path.join(current_app.root_path, "hero_config.json")

def _home_media_config_path():
    return os.path.join(current_app.root_path, "home_media_config.json")

def _image_slot_file(slot):
    """Devuelve la ruta del archivo existente para ese slot de imagen (o None)."""
    matches = glob.glob(os.path.join(_images_dir(), f"img_{slot}.*"))
    return matches[0] if matches else None

def _images_dir():
    path = os.path.join(current_app.root_path, "static", "images", "home")
    os.makedirs(path, exist_ok=True)
    return path

def _privacy_policy_path():
    return os.path.join(current_app.root_path, "privacy_policy.json")

def _quote_button_config_path():
    return os.path.join(current_app.root_path, "quote_button_config.json")

def _quote_email_config_path():
    return os.path.join(current_app.root_path, "quote_email_config.json")

def _slot_file(slot):
    """Devuelve la ruta del archivo existente para ese slot (o None)."""
    matches = glob.glob(os.path.join(_videos_dir(), f"slot_{slot}.*"))
    return matches[0] if matches else None

def _slugify_field_key(text):
    slug = re.sub(r"[^a-z0-9]+", "_", text.strip().lower()).strip("_")
    return slug or "campo"

def _social_config_path():
    return os.path.join(current_app.root_path, "social_config.json")

def _terms_conditions_path():
    return os.path.join(current_app.root_path, "terms_conditions.json")

def _videos_dir():
    path = os.path.join(current_app.root_path, "static", "videos")
    os.makedirs(path, exist_ok=True)
    return path

def _whatsapp_config_path():
    return os.path.join(current_app.root_path, "whatsapp_config.json")

def get_home_image_slots():
    """Devuelve lista de dicts {slot, url, filename} para los slots de imagen 1..N."""
    slots = []
    for slot in range(1, HOME_IMAGE_SLOTS + 1):
        f = _image_slot_file(slot)
        url = None
        if f:
            url = url_for("static", filename=f"images/home/{os.path.basename(f)}")
        slots.append({"slot": slot, "url": url, "filename": os.path.basename(f) if f else None})
    return slots

def get_home_video_slots():
    """Devuelve lista de dicts {slot, url, filename} para los slots 1..N."""
    slots = []
    for slot in range(1, HOME_VIDEO_SLOTS + 1):
        f = _slot_file(slot)
        url = None
        if f:
            url = url_for("static", filename=f"videos/{os.path.basename(f)}")
        slots.append({"slot": slot, "url": url, "filename": os.path.basename(f) if f else None})
    return slots

def load_deploy_config():
    """Datos no sensibles de despliegue en PythonAnywhere (usuario, rutas, etc.)."""
    path = _deploy_config_path()
    default = {
        "pa_username": "",
        "project_slug": os.path.basename(current_app.root_path),
        "python_version": PYTHONANYWHERE_PY_VERSIONS[0],
        "domain": "",
    }
    if not os.path.exists(path):
        return default
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        default.update(data)
    except Exception:
        pass
    return default

def load_form_fields_config():
    """Configuración del formulario dinámico de registro."""
    path = _form_fields_config_path()
    default = {
        "enabled": True,
        "fields": [
            {"id": 1, "name": "Nombre", "key": "first_name", "data_type": "text", "required": True, "active": True},
            {"id": 2, "name": "Primer apellido", "key": "first_last_name", "data_type": "text", "required": True, "active": True},
            {"id": 3, "name": "Segundo apellido", "key": "second_last_name", "data_type": "text", "required": False, "active": True},
            {"id": 4, "name": "Teléfono", "key": "phone_number", "data_type": "tel", "required": True, "active": True},
            {"id": 5, "name": "Usuario", "key": "username", "data_type": "text", "required": False, "active": True},
            {"id": 6, "name": "Número de usuario", "key": "user_number", "data_type": "text", "required": False, "active": True},
            {"id": 7, "name": "País", "key": "country", "data_type": "text", "required": False, "active": False},
        ],
    }
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return default
        if "enabled" not in data:
            data["enabled"] = default["enabled"]
        if "fields" not in data or not isinstance(data["fields"], list):
            data["fields"] = default["fields"]
        return data
    except Exception:
        return default

def load_hero_config():
    """Textos y ajustes del overlay 'Bienvenido' que se muestra sobre el video del home."""
    path = _hero_config_path()
    default = {
        "title": "Bienvenido",
        "description": "Descubre lo que la app ofrece.",
        "button_text": "Ver más",
        "align": "center",
        "title_size": "md",
        "description_size": "md",
        "button_size": "md",
        "button_bg_color_light": "#ffffff",
        "button_text_color_light": "#333333",
        "button_bg_color_dark": "#2a2a2e",
        "button_text_color_dark": "#f1f3f8",
        "button_hover_bg_color_light": "#f1f1f1",
        "button_hover_text_color_light": "#222222",
        "button_hover_bg_color_dark": "#3a3a3f",
        "button_hover_text_color_dark": "#ffffff",
        "button_radius": "6",
    }
    if not os.path.exists(path):
        return default
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        default.update(data)
    except Exception:
        pass
    return default

def load_home_media_config():
    """Modo del contenido inicial (video o imágenes) e intervalo del carrusel."""
    path = _home_media_config_path()
    default = {"mode": "video", "interval": 10}
    if not os.path.exists(path):
        return default
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        default.update(data)
    except Exception:
        pass
    return default

def load_privacy_policy():
    path = _privacy_policy_path()
    default = {"content": ""}
    if not os.path.exists(path):
        return default
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        default.update(data)
    except Exception:
        pass
    return default

def load_quote_button_config():
    """Estado del botón del cotizador en el menú."""
    path = _quote_button_config_path()
    default = {"visible": True}
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "visible" not in data:
                data["visible"] = default["visible"]
            return data
    except Exception:
        return default

def load_quote_email_config():
    """Correo electrónico al que se envían las cotizaciones."""
    path = _quote_email_config_path()
    default = {"email": ""}
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "email" not in data:
                data["email"] = default["email"]
            return data
    except Exception:
        return default

def load_social_config():
    """Enlaces y estado (activo/inactivo) de cada red social."""
    path = _social_config_path()
    default = {net: {"url": "", "enabled": False} for net in SOCIAL_NETWORKS}
    if not os.path.exists(path):
        return default
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        for net in SOCIAL_NETWORKS:
            if net in data:
                default[net].update(data[net])
    except Exception:
        pass
    return default

def load_terms_conditions():
    path = _terms_conditions_path()
    default = {"content": ""}
    if not os.path.exists(path):
        return default
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        default.update(data)
    except Exception:
        pass
    return default

def load_whatsapp_config():
    """Número de teléfono usado por el botón flotante de WhatsApp."""
    path = _whatsapp_config_path()
    default = {"phone": ""}
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "phone" not in data:
                data["phone"] = default["phone"]
            return data
    except Exception:
        return default

def save_deploy_config(data):
    with open(_deploy_config_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

def save_form_fields_config(data):
    with open(_form_fields_config_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

def save_hero_config(data):
    with open(_hero_config_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

def save_home_media_config(data):
    with open(_home_media_config_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

def save_privacy_policy(data):
    with open(_privacy_policy_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

def save_quote_button_config(data):
    with open(_quote_button_config_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

def save_quote_email_config(data):
    with open(_quote_email_config_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

def save_social_config(data):
    with open(_social_config_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

def save_terms_conditions(data):
    with open(_terms_conditions_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

def save_whatsapp_config(data):
    with open(_whatsapp_config_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

