"""Configuraciones hero."""
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

def _hero_config_path():
    return os.path.join(current_app.root_path, "hero_config.json")

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

def save_hero_config(data):
    with open(_hero_config_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
