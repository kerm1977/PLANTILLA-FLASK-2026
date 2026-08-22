"""Configuraciones core."""
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

def _slugify_field_key(text):
    slug = re.sub(r"[^a-z0-9]+", "_", text.strip().lower()).strip("_")
    return slug or "campo"

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
