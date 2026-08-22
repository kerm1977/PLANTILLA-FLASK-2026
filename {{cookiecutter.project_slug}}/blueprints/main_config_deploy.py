"""Configuraciones deploy."""
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

def save_deploy_config(data):
    with open(_deploy_config_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
