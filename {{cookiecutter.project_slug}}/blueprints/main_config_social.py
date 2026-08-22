"""Configuraciones social."""
from __future__ import annotations
import glob
import json
import os
import re
import uuid
from datetime import datetime
from pathlib import Path

from flask import current_app

from blueprints.main_config import (
    HOME_IMAGE_INTERVALS,
    FORM_FIELD_TYPES,
    HOME_VIDEO_SLOTS,
    ALLOWED_IMAGE_EXT,
    HOME_IMAGE_SLOTS,
    FORM_FIELD_TYPE_LABELS,
    ALLOWED_VIDEO_EXT,
    QUOTE_FIELD_TYPES,
    PYTHONANYWHERE_PY_VERSIONS,
)

def _quote_button_config_path():
    return os.path.join(current_app.root_path, "quote_button_config.json")

def _quote_email_config_path():
    return os.path.join(current_app.root_path, "quote_email_config.json")

def _social_config_path():
    return os.path.join(current_app.root_path, "social_config.json")

def _whatsapp_config_path():
    return os.path.join(current_app.root_path, "whatsapp_config.json")

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

def save_whatsapp_config(data):
    with open(_whatsapp_config_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
