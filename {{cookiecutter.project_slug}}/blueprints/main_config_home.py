"""Configuraciones home."""
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

def _slot_file(slot):
    """Devuelve la ruta del archivo existente para ese slot (o None)."""
    matches = glob.glob(os.path.join(_videos_dir(), f"slot_{slot}.*"))
    return matches[0] if matches else None

def _videos_dir():
    path = os.path.join(current_app.root_path, "static", "videos")
    os.makedirs(path, exist_ok=True)
    return path

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

def save_home_media_config(data):
    with open(_home_media_config_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
