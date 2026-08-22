"""Utilidades de sincronización y extracción de textos."""
from __future__ import annotations

import re
from pathlib import Path

from i18n.core import _load_json, _resolved, load_translations

_STRING_PATTERN = re.compile(r"""_\(\s*['"]((?:[^'"\\\\]|\\\\.)*)['"]""")

_STRING_PATTERN = re.compile(r"""_\(\s*['"]((?:[^'"\\]|\\.)*)['"]""")


def _iter_source_files():
    for folder, exts in (("templates", (".html",)), ("blueprints", (".py",))):
        base = _BASE_DIR / folder
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.suffix in exts:
                yield path
    for name in ("app.py",):
        path = _BASE_DIR / name
        if path.exists():
            yield path


def extract_source_strings() -> set[str]:
    """Recorre plantillas y blueprints buscando llamadas a `_('texto')`."""
    found: set[str] = set()
    for path in _iter_source_files():
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        for m in _STRING_PATTERN.finditer(text):
            key = m.group(1).replace("\\'", "'").replace('\\"', '"')
            if key:
                found.add(key)
    return found


def translation_status() -> dict[str, dict[str, int]]:
    """Cantidad de claves totales y sin traducir por idioma (excluye `es`)."""
    status = {}
    for lang in SUPPORTED_LANGS:
        if lang == DEFAULT_LANG:
            continue
        data = _load_json(lang)
        missing = sum(1 for v in data.values() if not v)
        status[lang] = {"total": len(data), "missing": missing}
    return status


def sync_translations() -> dict[str, dict[str, int]]:
    """Agrega a cada archivo de idioma las claves nuevas encontradas en el código.

    No sobrescribe traducciones existentes; las claves nuevas quedan en `null`
    (pendientes de traducir). Devuelve un resumen `{lang: {added, missing}}`.
    """
    keys = extract_source_strings()
    summary: dict[str, dict[str, int]] = {}
    for lang in SUPPORTED_LANGS:
        if lang == DEFAULT_LANG:
            continue
        path = _BASE_DIR / "translations" / f"{lang}.json"
        data = _load_json(lang)
        added = 0
        for key in keys:
            if key not in data:
                data[key] = None
                added += 1
        ordered = dict(sorted(data.items(), key=lambda kv: kv[0].lower()))
        with open(path, "w", encoding="utf-8") as f:
            json.dump(ordered, f, ensure_ascii=False, indent=2)
            f.write("\n")
        missing = sum(1 for v in ordered.values() if not v)
        summary[lang] = {"added": added, "missing": missing}
    load_translations()
    return summary
