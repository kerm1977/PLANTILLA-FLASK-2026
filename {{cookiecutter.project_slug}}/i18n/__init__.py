"""API pública del sistema de i18n."""
from __future__ import annotations

from i18n.core import (
    DEFAULT_LANG,
    SUPPORTED_LANGS,
    get_locale,
    load_translations,
    set_locale,
    t,
)
from i18n.parser import translate_html
from i18n.sync import extract_source_strings, sync_translations, translation_status


def init_i18n(app):
    """Inicializa el sistema de i18n en la aplicación Flask."""
    load_translations()

    @app.before_request
    def _set_lang() -> None:
        from flask import g

        g.lang = get_locale()
        if current_app.debug:
            load_translations()

    @app.after_request
    def _translate_response(response):
        from flask import current_app

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
                pass
        return response

    @app.context_processor
    def _i18n_context():
        return {
            "lang": get_locale(),
            "t": t,
            "_": t,
            "languages": SUPPORTED_LANGS,
        }
