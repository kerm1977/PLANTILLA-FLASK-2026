"""Configuraciones forms."""
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

def _form_fields_config_path():
    return os.path.join(current_app.root_path, "form_fields_config.json")

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

def save_form_fields_config(data):
    with open(_form_fields_config_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
