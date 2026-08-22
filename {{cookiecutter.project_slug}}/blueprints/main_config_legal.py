"""Configuraciones legal."""
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

def _privacy_policy_path():
    return os.path.join(current_app.root_path, "privacy_policy.json")

def _terms_conditions_path():
    return os.path.join(current_app.root_path, "terms_conditions.json")

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

def save_privacy_policy(data):
    with open(_privacy_policy_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

def save_terms_conditions(data):
    with open(_terms_conditions_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
