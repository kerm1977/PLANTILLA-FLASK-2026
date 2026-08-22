"""Sistema de internacionalización (i18n) - funciones principales."""
from __future__ import annotations

import json
import re
from pathlib import Path

from flask import current_app, g, has_request_context, session

DEFAULT_LANG = "es"
SUPPORTED_LANGS = ["es", "en", "fr", "it", "pt", "de"]

_BASE_DIR = Path(__file__).resolve().parent.parent
_TRANSLATIONS: dict[str, dict[str, str]] = {}
_PATTERNS: dict[str, re.Pattern | None] = {}


def _load_json(lang: str) -> dict[str, str]:
    path = _BASE_DIR / "translations" / f"{lang}.json"
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, dict) else {}


def load_translations() -> None:
    """Carga los archivos JSON de traducción y compila los patrones de búsqueda."""
    global _TRANSLATIONS, _PATTERNS
    _TRANSLATIONS = {lang: _load_json(lang) for lang in SUPPORTED_LANGS}
    _PATTERNS = {}
    for lang in SUPPORTED_LANGS:
        if lang == DEFAULT_LANG:
            _PATTERNS[lang] = None
            continue
        trans = _resolved(lang)
        if trans:
            # Ordenamos por longitud descendente para que coincidan primero
            # las frases completas y no las palabras más cortas.
            keys = sorted(trans.keys(), key=len, reverse=True)
            pattern = "|".join(re.escape(k) for k in keys)
            _PATTERNS[lang] = re.compile(
                r"(?<!\w)(" + pattern + r")(?!\w)", re.UNICODE
            )
        else:
            _PATTERNS[lang] = None


def _resolved(lang: str) -> dict[str, str]:
    """Devuelve un diccionario con la cadena de reserva incluida.

    - Si el idioma es `es` se devuelve el propio diccionario (vacío).
    - Para otros idiomas: clave -> texto resuelto (idioma, luego inglés,
      finalmente español).
    """
    if lang == DEFAULT_LANG:
        return {}
    result: dict[str, str] = {}
    es = _TRANSLATIONS.get("es", {})
    en = _TRANSLATIONS.get("en", {})
    target = _TRANSLATIONS.get(lang, {})
    all_keys = set(es) | set(en) | set(target)
    for key in all_keys:
        result[key] = target.get(key) or en.get(key) or key
    return result
def get_locale() -> str:
    """Idioma activo de la sesión o el idioma por defecto."""
    if has_request_context():
        return session.get("lang", DEFAULT_LANG) or DEFAULT_LANG
    return DEFAULT_LANG


def set_locale(lang: str) -> None:
    """Guarda el idioma en la sesión si está soportado."""
    if lang in SUPPORTED_LANGS:
        session["lang"] = lang


def t(key: str, **kwargs) -> str:
    """Traduce una clave (texto en español) al idioma activo.

    Soporta marcadores de posición con `.format(**kwargs)`.
    """
    lang = get_locale()
    if lang == DEFAULT_LANG:
        text = _TRANSLATIONS.get("es", {}).get(key, key)
    else:
        text = (
            _TRANSLATIONS.get(lang, {}).get(key)
            or _TRANSLATIONS.get("en", {}).get(key)
            or _TRANSLATIONS.get("es", {}).get(key)
            or key
        )
    if kwargs:
        return text.format(**kwargs)
    return text

