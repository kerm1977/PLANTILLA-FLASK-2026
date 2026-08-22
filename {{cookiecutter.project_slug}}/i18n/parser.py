"""Traducción de fragmentos HTML."""
from __future__ import annotations

import html
import re
from html.parser import HTMLParser

from i18n.core import DEFAULT_LANG, _PATTERNS, _resolved, get_locale

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
