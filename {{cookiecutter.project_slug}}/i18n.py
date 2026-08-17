"""Sistema de internacionalización (i18n) basado en JSON.

Las traducciones viven en `translations/<lang>.json`. Cada clave es el texto
en español (idioma por defecto) y el valor es la traducción al idioma
seleccionado. Si no existe traducción, se devuelve el texto original.
"""
from __future__ import annotations

import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path

from flask import g, has_request_context, session, current_app

DEFAULT_LANG = "es"
SUPPORTED_LANGS = ["es", "en", "fr", "it", "pt", "de"]

_BASE_DIR = Path(__file__).resolve().parent
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


class _HTMLTranslator(HTMLParser):
    """Parser que traduce nodos de texto y atributos visibles al vuelo."""

    _VOID_TAGS = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }
    _SKIP_TAGS = {"script", "style"}
    _NO_TRANSLATE_TAGS = {"code", "pre", "textarea"}
    _TRANSlatable_ATTRS = {
        "alt",
        "aria-label",
        "placeholder",
        "title",
    }

    def __init__(self, lang: str) -> None:
        super().__init__()
        self.lang = lang
        self._pattern = _PATTERNS.get(lang)
        self._trans = _resolved(lang)
        self._out: list[str] = []
        # pila de etiquetas activas para distinguir script/style de pre/code
        self._tag_stack: list[str] = []

    def _replace(self, text: str) -> str:
        if not self._pattern:
            return text
        return self._pattern.sub(lambda m: self._trans.get(m.group(1), m.group(1)), text)

    def _in_skip_tag(self) -> bool:
        return any(t in self._tag_stack for t in self._SKIP_TAGS)

    def _in_no_translate_tag(self) -> bool:
        return any(t in self._tag_stack for t in self._NO_TRANSLATE_TAGS)

    def handle_decl(self, decl: str) -> None:
        self._out.append(f"<!{decl}>")

    def handle_comment(self, data: str) -> None:
        self._out.append(f"<!--{data}-->")

    def _format_attrs(self, attrs: list[tuple[str, str | None]]) -> str:
        attr_dict: dict[str, str | None] = {}
        for name, value in attrs:
            attr_dict[name] = value

        parts = []
        for name, value in attr_dict.items():
            if value is None:
                parts.append(name)
                continue
            trans_value = value
            if name in self._TRANSlatable_ATTRS or (
                name == "value" and attr_dict.get("type") in ("submit", "button", "reset")
            ):
                trans_value = self._replace(value)
            parts.append(f'{name}="{html.escape(trans_value, quote=True)}"')
        return "".join(f" {p}" for p in parts)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._tag_stack.append(tag)
        self._out.append(f"<{tag}{self._format_attrs(attrs)}>")

    def handle_endtag(self, tag: str) -> None:
        if tag in self._tag_stack:
            # elimina la última ocurrencia del tag
            idx = len(self._tag_stack) - 1 - self._tag_stack[::-1].index(tag)
            self._tag_stack.pop(idx)
        self._out.append(f"</{tag}>")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self._VOID_TAGS:
            self._out.append(f"<{tag}{self._format_attrs(attrs)} />")
        else:
            self._out.append(f"<{tag}{self._format_attrs(attrs)}></{tag}>")

    def handle_data(self, data: str) -> None:
        if self._in_skip_tag():
            # script/style: no escapar para no romper el código
            self._out.append(data)
            return
        if self._in_no_translate_tag():
            # code/pre/textarea: no traducir pero escapar para conservar el contenido
            self._out.append(html.escape(data))
            return
        self._out.append(html.escape(self._replace(data)))

    def get_html(self) -> str:
        return "".join(self._out)


def translate_html(html_text: str, lang: str | None = None) -> str:
    """Traduce un fragmento HTML completo al idioma indicado."""
    lang = lang or get_locale()
    if lang == DEFAULT_LANG and not _TRANSLATIONS.get("es"):
        return html_text
    if lang == DEFAULT_LANG:
        return html_text
    parser = _HTMLTranslator(lang)
    parser.feed(html_text)
    return parser.get_html()


def init_i18n(app) -> None:
    """Inicializa el sistema de i18n en la aplicación Flask."""
    load_translations()

    @app.before_request
    def _set_lang() -> None:
        g.lang = get_locale()
        if current_app.debug:
            load_translations()

    @app.after_request
    def _translate_response(response) -> None:
        if (
            response.content_type
            and "text/html" in response.content_type
            and get_locale() != DEFAULT_LANG
        ):
            try:
                body = response.get_data(as_text=True)
                translated = translate_html(body, get_locale())
                response.set_data(translated)
            except Exception:
                # En caso de error, servimos la respuesta original.
                pass
        return response

    @app.context_processor
    def _i18n_context() -> dict:
        return {
            "lang": get_locale(),
            "t": t,
            "_": t,
            "languages": SUPPORTED_LANGS,
        }
