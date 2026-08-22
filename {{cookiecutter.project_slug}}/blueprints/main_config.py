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

HOME_IMAGE_INTERVALS = [5, 10, 15, 20, 25]

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

HOME_VIDEO_SLOTS = 3

ALLOWED_IMAGE_EXT = {"jpg", "jpeg", "png", "webp"}

HOME_IMAGE_SLOTS = 6

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

ALLOWED_VIDEO_EXT = {"mp4", "webm", "ogg"}

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

PYTHONANYWHERE_PY_VERSIONS = ["3.13", "3.12", "3.11", "3.10", "3.9"]


from .main_config_deploy import (
    _build_env_content,
    _build_wsgi_content,
    _deploy_config_path,
    load_deploy_config,
    save_deploy_config,
)

from .main_config_forms import (
    _form_fields_config_path,
    load_form_fields_config,
    save_form_fields_config,
)

from .main_config_hero import (
    _hero_config_path,
    load_hero_config,
    save_hero_config,
)

from .main_config_home import (
    _home_media_config_path,
    _image_slot_file,
    _images_dir,
    _slot_file,
    _videos_dir,
    get_home_image_slots,
    get_home_video_slots,
    load_home_media_config,
    save_home_media_config,
)

from .main_config_legal import (
    _privacy_policy_path,
    _terms_conditions_path,
    load_privacy_policy,
    load_terms_conditions,
    save_privacy_policy,
    save_terms_conditions,
)

from .main_config_social import (
    _quote_button_config_path,
    _quote_email_config_path,
    _social_config_path,
    _whatsapp_config_path,
    load_quote_button_config,
    load_quote_email_config,
    load_social_config,
    load_whatsapp_config,
    save_quote_button_config,
    save_quote_email_config,
    save_social_config,
    save_whatsapp_config,
)

from .main_config_core import (
    _slugify_field_key,
    ALLOWED_VIDEO_EXT,
    HOME_VIDEO_SLOTS,
    ALLOWED_IMAGE_EXT,
    HOME_IMAGE_SLOTS,
    HOME_IMAGE_INTERVALS,
    PYTHONANYWHERE_PY_VERSIONS,
    QUOTE_FIELD_TYPES,
    FORM_FIELD_TYPES,
    FORM_FIELD_TYPE_LABELS,
)

__all__ = ['_build_env_content', '_build_wsgi_content', '_deploy_config_path', '_form_fields_config_path', '_hero_config_path', '_home_media_config_path', '_image_slot_file', '_images_dir', '_privacy_policy_path', '_quote_button_config_path', '_quote_email_config_path', '_slot_file', '_slugify_field_key', '_social_config_path', '_terms_conditions_path', '_videos_dir', '_whatsapp_config_path', 'get_home_image_slots', 'get_home_video_slots', 'load_deploy_config', 'load_form_fields_config', 'load_hero_config', 'load_home_media_config', 'load_privacy_policy', 'load_quote_button_config', 'load_quote_email_config', 'load_social_config', 'load_terms_conditions', 'load_whatsapp_config', 'save_deploy_config', 'save_form_fields_config', 'save_hero_config', 'save_home_media_config', 'save_privacy_policy', 'save_quote_button_config', 'save_quote_email_config', 'save_social_config', 'save_terms_conditions', 'save_whatsapp_config', 'ALLOWED_VIDEO_EXT', 'HOME_VIDEO_SLOTS', 'ALLOWED_IMAGE_EXT', 'HOME_IMAGE_SLOTS', 'HOME_IMAGE_INTERVALS', 'PYTHONANYWHERE_PY_VERSIONS', 'QUOTE_FIELD_TYPES', 'FORM_FIELD_TYPES', 'FORM_FIELD_TYPE_LABELS']
