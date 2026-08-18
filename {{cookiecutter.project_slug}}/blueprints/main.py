"""Vistas principales: home, dashboard y perfil."""
import glob
import json
import os
import re
from functools import wraps

from flask import Blueprint, Response, current_app, flash, redirect, render_template, request, session, url_for
from sqlalchemy import func, select

from i18n import set_locale, sync_translations, translation_status
from models import QuoteField, QuoteSubmission, User, async_session

main_bp = Blueprint("main", __name__)

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


def _slugify_field_key(text):
    slug = re.sub(r"[^a-z0-9]+", "_", text.strip().lower()).strip("_")
    return slug or "campo"


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


def _hero_config_path():
    return os.path.join(current_app.root_path, "hero_config.json")


def load_hero_config():
    """Textos y ajustes del overlay 'Bienvenido' que se muestra sobre el video del home."""
    path = _hero_config_path()
    default = {
        "title": "Bienvenido",
        "description": "Descubre lo que la app ofrece.",
        "button_text": "Ver más",
        "align": "center",
        "title_size": "md",
        "description_size": "md",
        "button_size": "md",
        "button_bg_color_light": "#ffffff",
        "button_text_color_light": "#333333",
        "button_bg_color_dark": "#2a2a2e",
        "button_text_color_dark": "#f1f3f8",
        "button_hover_bg_color_light": "#f1f1f1",
        "button_hover_text_color_light": "#222222",
        "button_hover_bg_color_dark": "#3a3a3f",
        "button_hover_text_color_dark": "#ffffff",
        "button_radius": "6",
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


def save_hero_config(data):
    with open(_hero_config_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def _privacy_policy_path():
    return os.path.join(current_app.root_path, "privacy_policy.json")


def load_privacy_policy():
    path = _privacy_policy_path()
    default = {
        "update_date": "",
        "summary": "",
        "sections": [],
        "contact": "",
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


def save_privacy_policy(data):
    with open(_privacy_policy_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def _terms_conditions_path():
    return os.path.join(current_app.root_path, "terms_conditions.json")


def load_terms_conditions():
    path = _terms_conditions_path()
    default = {
        "title": "Términos y Condiciones del Servicio",
        "subtitle": "",
        "update_date": "",
        "summary": "",
        "sections": [],
        "contact": "",
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


def save_terms_conditions(data):
    with open(_terms_conditions_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def _whatsapp_config_path():
    return os.path.join(current_app.root_path, "whatsapp_config.json")


def _quote_email_config_path():
    return os.path.join(current_app.root_path, "quote_email_config.json")


def load_whatsapp_config():
    """Número de teléfono usado por el botón flotante de WhatsApp."""
    path = _whatsapp_config_path()
    default = {"phone": ""}
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "phone" not in data:
                data["phone"] = default["phone"]
            return data
    except Exception:
        return default


def load_quote_email_config():
    """Correo electrónico al que se envían las cotizaciones."""
    path = _quote_email_config_path()
    default = {"email": ""}
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "email" not in data:
                data["email"] = default["email"]
            return data
    except Exception:
        return default


def save_whatsapp_config(data):
    with open(_whatsapp_config_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def save_quote_email_config(data):
    with open(_quote_email_config_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def _quote_button_config_path():
    return os.path.join(current_app.root_path, "quote_button_config.json")


def load_quote_button_config():
    """Estado del botón del cotizador en el menú."""
    path = _quote_button_config_path()
    default = {"visible": True}
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "visible" not in data:
                data["visible"] = default["visible"]
            return data
    except Exception:
        return default


def save_quote_button_config(data):
    with open(_quote_button_config_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def _form_fields_config_path():
    return os.path.join(current_app.root_path, "form_fields_config.json")


def load_form_fields_config():
    """Configuración del formulario dinámico de registro."""
    path = _form_fields_config_path()
    default = {
        "enabled": True,
        "fields": [
            {"id": 1, "name": "Nombre", "key": "first_name", "data_type": "text", "required": True, "active": True},
            {"id": 2, "name": "Primer apellido", "key": "first_last_name", "data_type": "text", "required": True, "active": True},
            {"id": 3, "name": "Segundo apellido", "key": "second_last_name", "data_type": "text", "required": False, "active": True},
            {"id": 4, "name": "Teléfono", "key": "phone_number", "data_type": "tel", "required": True, "active": True},
            {"id": 5, "name": "Usuario", "key": "username", "data_type": "text", "required": False, "active": True},
            {"id": 6, "name": "Número de usuario", "key": "user_number", "data_type": "text", "required": False, "active": True},
            {"id": 7, "name": "País", "key": "country", "data_type": "text", "required": False, "active": False},
        ],
    }
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return default
        if "enabled" not in data:
            data["enabled"] = default["enabled"]
        if "fields" not in data or not isinstance(data["fields"], list):
            data["fields"] = default["fields"]
        return data
    except Exception:
        return default


def save_form_fields_config(data):
    with open(_form_fields_config_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


SOCIAL_NETWORKS = ["instagram", "facebook", "x", "tiktok"]


def _social_config_path():
    return os.path.join(current_app.root_path, "social_config.json")


def load_social_config():
    """Enlaces y estado (activo/inactivo) de cada red social."""
    path = _social_config_path()
    default = {net: {"url": "", "enabled": False} for net in SOCIAL_NETWORKS}
    if not os.path.exists(path):
        return default
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        for net in SOCIAL_NETWORKS:
            if net in data:
                default[net].update(data[net])
    except Exception:
        pass
    return default


def save_social_config(data):
    with open(_social_config_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def _videos_dir():
    path = os.path.join(current_app.root_path, "static", "videos")
    os.makedirs(path, exist_ok=True)
    return path


def _slot_file(slot):
    """Devuelve la ruta del archivo existente para ese slot (o None)."""
    matches = glob.glob(os.path.join(_videos_dir(), f"slot_{slot}.*"))
    return matches[0] if matches else None


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


def _images_dir():
    path = os.path.join(current_app.root_path, "static", "images", "home")
    os.makedirs(path, exist_ok=True)
    return path


def _image_slot_file(slot):
    """Devuelve la ruta del archivo existente para ese slot de imagen (o None)."""
    matches = glob.glob(os.path.join(_images_dir(), f"img_{slot}.*"))
    return matches[0] if matches else None


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


def _home_media_config_path():
    return os.path.join(current_app.root_path, "home_media_config.json")


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


def login_required(f):
    @wraps(f)
    async def decorated(*args, **kwargs):
        if not session.get("user_id"):
            flash("Inicia sesión para continuar", "warning")
            return redirect(url_for("auth.login"))
        return await f(*args, **kwargs)

    return decorated


def superuser_required(f):
    @wraps(f)
    async def decorated(*args, **kwargs):
        if not session.get("is_superuser"):
            flash("Acceso restringido a superusuarios", "danger")
            return redirect(url_for("auth.login"))
        return await f(*args, **kwargs)

    return decorated


@main_bp.app_context_processor
def _inject_whatsapp_config():
    return {"whatsapp_config": load_whatsapp_config()}


@main_bp.app_context_processor
def _inject_quote_button_config():
    return {"quote_button_config": load_quote_button_config()}


@main_bp.route("/set-lang/<lang>")
async def set_lang(lang):
    set_locale(lang)
    next_url = request.args.get("next") or request.referrer or url_for("main.home")
    return redirect(next_url)


@main_bp.route("/")
async def home():
    media_config = load_home_media_config()
    if media_config["mode"] == "images":
        images = [s["url"] for s in get_home_image_slots() if s["url"]]
        if images:
            return render_template(
                "home.html",
                home_media_mode="images",
                home_images=images,
                home_image_interval=media_config["interval"],
                hero_config=load_hero_config(),
            )
    slots = get_home_video_slots()
    playlist = [s["url"] for s in slots if s["url"]]
    if not playlist:
        playlist = [url_for("static", filename="wq.mp4")]
    return render_template(
        "home.html",
        home_media_mode="video",
        home_videos=playlist,
        hero_config=load_hero_config(),
    )


@main_bp.route("/dashboard", methods=["GET", "POST"])
@superuser_required
async def dashboard():
    if request.method == "POST":
        if "save_hero_config" in request.form:
            cfg = {
                "title": request.form.get("hero_title", "").strip() or "Bienvenido",
                "description": request.form.get("hero_description", "").strip(),
                "button_text": request.form.get("hero_button_text", "").strip() or "Ver más",
                "align": request.form.get("hero_align", "center"),
                "title_size": request.form.get("hero_title_size", "md"),
                "description_size": request.form.get("hero_description_size", "md"),
                "button_size": request.form.get("hero_button_size", "md"),
                "button_bg_color_light": request.form.get("hero_button_bg_color_light", "#ffffff"),
                "button_text_color_light": request.form.get("hero_button_text_color_light", "#333333"),
                "button_bg_color_dark": request.form.get("hero_button_bg_color_dark", "#2a2a2e"),
                "button_text_color_dark": request.form.get("hero_button_text_color_dark", "#f1f3f8"),
                "button_hover_bg_color_light": request.form.get("hero_button_hover_bg_color_light", "#f1f1f1"),
                "button_hover_text_color_light": request.form.get("hero_button_hover_text_color_light", "#222222"),
                "button_hover_bg_color_dark": request.form.get("hero_button_hover_bg_color_dark", "#3a3a3f"),
                "button_hover_text_color_dark": request.form.get("hero_button_hover_text_color_dark", "#ffffff"),
                "button_radius": request.form.get("hero_button_radius", "6"),
            }
            save_hero_config(cfg)
            flash("Sección Hero actualizada", "success")
            return redirect(url_for("main.dashboard"))

        if "add_quote_field" in request.form:
            label = request.form.get("quote_label", "").strip()
            field_type = request.form.get("quote_field_type", "text")
            if field_type not in QUOTE_FIELD_TYPES:
                field_type = "text"
            if not label:
                flash("La pregunta necesita un texto", "warning")
                return redirect(url_for("main.dashboard"))
            try:
                step = int(request.form.get("quote_step", 1))
            except ValueError:
                step = 1
            help_text = request.form.get("quote_help_text", "").strip() or None
            required = request.form.get("quote_required") == "1"
            options_raw = request.form.get("quote_options", "")
            options = [o.strip() for o in options_raw.splitlines() if o.strip()] or None
            max_choices_raw = request.form.get("quote_max_choices", "").strip()
            max_choices = int(max_choices_raw) if max_choices_raw.isdigit() else None
            base_key = _slugify_field_key(label)
            async with async_session() as s:
                result = await s.execute(
                    select(func.max(QuoteField.position)).where(QuoteField.step == step)
                )
                max_pos = result.scalar() or 0
                key = base_key
                suffix = 1
                while (await s.execute(select(QuoteField).where(QuoteField.field_key == key))).scalar_one_or_none():
                    suffix += 1
                    key = f"{base_key}_{suffix}"
                s.add(QuoteField(
                    step=step,
                    position=max_pos + 1,
                    field_key=key,
                    field_type=field_type,
                    label=label,
                    help_text=help_text,
                    required=required,
                    options=options,
                    max_choices=max_choices,
                ))
                await s.commit()
            flash("Pregunta agregada al cotizador", "success")
            return redirect(url_for("main.dashboard"))

        if "edit_quote_field" in request.form:
            field_id = int(request.form.get("quote_field_id", 0))
            label = request.form.get("quote_label", "").strip()
            field_type = request.form.get("quote_field_type", "text")
            if field_type not in QUOTE_FIELD_TYPES:
                field_type = "text"
            try:
                step = int(request.form.get("quote_step", 1))
            except ValueError:
                step = 1
            help_text = request.form.get("quote_help_text", "").strip() or None
            required = request.form.get("quote_required") == "1"
            options_raw = request.form.get("quote_options", "")
            options = [o.strip() for o in options_raw.splitlines() if o.strip()] or None
            max_choices_raw = request.form.get("quote_max_choices", "").strip()
            max_choices = int(max_choices_raw) if max_choices_raw.isdigit() else None
            async with async_session() as s:
                field = await s.get(QuoteField, field_id)
                if field:
                    field.step = step
                    field.field_type = field_type
                    field.label = label or field.label
                    field.help_text = help_text
                    field.required = required
                    field.options = options
                    field.max_choices = max_choices
                    await s.commit()
                    flash("Pregunta actualizada", "success")
                else:
                    flash("Pregunta no encontrada", "danger")
            return redirect(url_for("main.dashboard"))

        if "delete_quote_field" in request.form:
            field_id = int(request.form.get("delete_quote_field", 0))
            async with async_session() as s:
                field = await s.get(QuoteField, field_id)
                if field:
                    await s.delete(field)
                    await s.commit()
                    flash("Pregunta eliminada del cotizador", "success")
            return redirect(url_for("main.dashboard"))

        if "save_quote_button_config" in request.form:
            visible = request.form.get("quote_button_visible") == "1"
            save_quote_button_config({"visible": visible})
            flash("Configuración del cotizador actualizada", "success")
            return redirect(url_for("main.dashboard"))

        if "save_whatsapp_config" in request.form:
            phone = request.form.get("whatsapp_phone", "").strip()
            phone = "".join(ch for ch in phone if ch.isdigit())
            save_whatsapp_config({"phone": phone})
            flash("Número de WhatsApp actualizado", "success")
            return redirect(url_for("main.dashboard"))

        if "save_quote_email_config" in request.form:
            email = request.form.get("quote_email", "").strip()
            save_quote_email_config({"email": email})
            flash("Correo de cotizaciones actualizado", "success")
            return redirect(url_for("main.dashboard"))

        if "save_social_config" in request.form:
            social_cfg = {}
            for net in SOCIAL_NETWORKS:
                social_cfg[net] = {
                    "url": request.form.get(f"social_{net}_url", "").strip(),
                    "enabled": request.form.get(f"social_{net}_enabled") == "1",
                }
            save_social_config(social_cfg)
            flash("Redes sociales actualizadas", "success")
            return redirect(url_for("main.dashboard"))

        if "save_network_config" in request.form:
            cfg = {
                "pa_username": request.form.get("pa_username", "").strip(),
                "project_slug": request.form.get("project_slug", "").strip() or os.path.basename(current_app.root_path),
                "python_version": request.form.get("python_version", PYTHONANYWHERE_PY_VERSIONS[0]),
                "domain": request.form.get("domain", "").strip(),
            }
            save_deploy_config(cfg)
            flash("Configuración de red guardada", "success")
            return redirect(url_for("main.dashboard"))

        if "download_wsgi" in request.form:
            cfg = {
                "pa_username": request.form.get("pa_username", "").strip(),
                "project_slug": request.form.get("project_slug", "").strip() or os.path.basename(current_app.root_path),
            }
            content = _build_wsgi_content(cfg)
            return Response(
                content,
                mimetype="text/x-python",
                headers={"Content-Disposition": "attachment; filename=wsgi_pythonanywhere.py"},
            )

        if "download_env" in request.form:
            content = _build_env_content(request.form)
            return Response(
                content,
                mimetype="text/plain",
                headers={"Content-Disposition": "attachment; filename=.env"},
            )

        if "sync_translations" in request.form:
            try:
                summary = sync_translations()
                added_total = sum(s["added"] for s in summary.values())
                if added_total:
                    flash(
                        f"Traducciones actualizadas: {added_total} cadena(s) nueva(s) agregadas a "
                        f"{', '.join(lang.upper() for lang in summary)}.",
                        "success",
                    )
                else:
                    flash("Las traducciones ya estaban al día, no se encontraron cadenas nuevas.", "success")
            except Exception as e:
                flash(f"Error al actualizar traducciones: {e}", "danger")
            return redirect(url_for("main.dashboard"))

        if "move" in request.form:
            try:
                a = int(request.form.get("slot_a", 0))
                b = int(request.form.get("slot_b", 0))
                file_a = _slot_file(a)
                file_b = _slot_file(b)
                tmp_a = f"{file_a}.tmp" if file_a else None
                if file_a:
                    os.replace(file_a, tmp_a)
                if file_b:
                    ext_b = file_b.rsplit(".", 1)[-1]
                    os.replace(file_b, os.path.join(_videos_dir(), f"slot_{a}.{ext_b}"))
                if tmp_a:
                    ext_a = file_a.rsplit(".", 1)[-1]
                    os.replace(tmp_a, os.path.join(_videos_dir(), f"slot_{b}.{ext_a}"))
                flash("Orden actualizado", "success")
            except Exception as e:
                flash(f"Error al reordenar: {e}", "danger")
            return redirect(url_for("main.dashboard"))

        if "remove_slot" in request.form:
            slot = int(request.form.get("remove_slot", 0))
            f = _slot_file(slot)
            if f:
                try:
                    os.remove(f)
                    flash("Video eliminado", "success")
                except Exception as e:
                    flash(f"Error al eliminar el video: {e}", "danger")
            return redirect(url_for("main.dashboard"))

        if "save_home_media_mode" in request.form:
            mode = request.form.get("home_media_mode", "video")
            if mode not in ("video", "images"):
                mode = "video"
            try:
                interval = int(request.form.get("home_media_interval", 10))
            except ValueError:
                interval = 10
            if interval not in HOME_IMAGE_INTERVALS:
                interval = 10
            save_home_media_config({"mode": mode, "interval": interval})
            flash("Contenido inicial actualizado", "success")
            return redirect(url_for("main.dashboard"))

        if "move_image" in request.form:
            try:
                a = int(request.form.get("img_slot_a", 0))
                b = int(request.form.get("img_slot_b", 0))
                file_a = _image_slot_file(a)
                file_b = _image_slot_file(b)
                tmp_a = f"{file_a}.tmp" if file_a else None
                if file_a:
                    os.replace(file_a, tmp_a)
                if file_b:
                    ext_b = file_b.rsplit(".", 1)[-1]
                    os.replace(file_b, os.path.join(_images_dir(), f"img_{a}.{ext_b}"))
                if tmp_a:
                    ext_a = file_a.rsplit(".", 1)[-1]
                    os.replace(tmp_a, os.path.join(_images_dir(), f"img_{b}.{ext_a}"))
                flash("Orden actualizado", "success")
            except Exception as e:
                flash(f"Error al reordenar: {e}", "danger")
            return redirect(url_for("main.dashboard"))

        if "remove_image_slot" in request.form:
            slot = int(request.form.get("remove_image_slot", 0))
            f = _image_slot_file(slot)
            if f:
                try:
                    os.remove(f)
                    flash("Imagen eliminada", "success")
                except Exception as e:
                    flash(f"Error al eliminar la imagen: {e}", "danger")
            return redirect(url_for("main.dashboard"))

        if "upload_home_image" in request.form:
            image = request.files.get("home_image")
            slot = next((n for n in range(1, HOME_IMAGE_SLOTS + 1) if not _image_slot_file(n)), None)
            if slot is None:
                flash("Ya hay 6 imágenes. Elimina una para poder agregar otra.", "warning")
                return redirect(url_for("main.dashboard"))
            if not image or image.filename == "":
                flash("Selecciona un archivo de imagen", "warning")
                return redirect(url_for("main.dashboard"))
            ext = image.filename.rsplit(".", 1)[-1].lower() if "." in image.filename else ""
            if ext not in ALLOWED_IMAGE_EXT:
                flash("Formato no permitido. Usa jpg, png o webp.", "danger")
                return redirect(url_for("main.dashboard"))
            try:
                dest = os.path.join(_images_dir(), f"img_{slot}.{ext}")
                image.save(dest)
                flash(f"Imagen {slot} agregada", "success")
            except Exception as e:
                flash(f"Error al subir la imagen: {e}", "danger")
            return redirect(url_for("main.dashboard"))

        if "save_form_fields_config" in request.form:
            cfg = load_form_fields_config()
            cfg["enabled"] = request.form.get("form_fields_enabled") == "1"
            save_form_fields_config(cfg)
            flash("Configuración de formularios actualizada", "success")
            return redirect(url_for("main.dashboard") + "?section=formFields")

        if "add_form_field" in request.form:
            name = request.form.get("form_field_name", "").strip()
            data_type = request.form.get("form_field_type", "text")
            if data_type not in FORM_FIELD_TYPES:
                data_type = "text"
            if not name:
                flash("El campo necesita un nombre", "warning")
                return redirect(url_for("main.dashboard"))
            cfg = load_form_fields_config()
            next_id = 1
            if cfg["fields"]:
                next_id = max(f.get("id", 0) for f in cfg["fields"]) + 1
            cfg["fields"].append(
                {
                    "id": next_id,
                    "name": name,
                    "key": _slugify_field_key(name),
                    "data_type": data_type,
                    "required": request.form.get("form_field_required") == "1",
                    "active": True,
                }
            )
            save_form_fields_config(cfg)
            flash("Campo agregado", "success")
            return redirect(url_for("main.dashboard") + "?section=formFields")

        if "delete_form_field" in request.form:
            field_id = int(request.form.get("delete_form_field_id", 0))
            cfg = load_form_fields_config()
            cfg["fields"] = [f for f in cfg["fields"] if f.get("id") != field_id]
            save_form_fields_config(cfg)
            flash("Campo eliminado", "success")
            return redirect(url_for("main.dashboard") + "?section=formFields")

        if "toggle_form_field" in request.form:
            field_id = int(request.form.get("toggle_form_field_id", 0))
            cfg = load_form_fields_config()
            for f in cfg["fields"]:
                if f.get("id") == field_id:
                    f["active"] = not f.get("active", True)
                    break
            save_form_fields_config(cfg)
            flash("Estado del campo actualizado", "success")
            return redirect(url_for("main.dashboard") + "?section=formFields")

        if "home_video" in request.files:
            video = request.files.get("home_video")
            slot = next((n for n in range(1, HOME_VIDEO_SLOTS + 1) if not _slot_file(n)), None)
            if slot is None:
                flash("Ya hay 3 videos. Elimina uno para poder agregar otro.", "warning")
                return redirect(url_for("main.dashboard"))
            if not video or video.filename == "":
                flash("Selecciona un archivo de video", "warning")
                return redirect(url_for("main.dashboard"))
            ext = video.filename.rsplit(".", 1)[-1].lower() if "." in video.filename else ""
            if ext not in ALLOWED_VIDEO_EXT:
                flash("Formato no permitido. Usa mp4, webm u ogg.", "danger")
                return redirect(url_for("main.dashboard"))
            try:
                dest = os.path.join(_videos_dir(), f"slot_{slot}.{ext}")
                video.save(dest)
                flash(f"Video {slot} agregado", "success")
            except Exception as e:
                flash(f"Error al subir el video: {e}", "danger")
            return redirect(url_for("main.dashboard"))

        if "save_privacy_policy" in request.form:
            cfg = load_privacy_policy()
            cfg["update_date"] = request.form.get("privacy_update_date", "").strip()
            cfg["summary"] = request.form.get("privacy_summary", "").strip()
            cfg["contact"] = request.form.get("privacy_contact", "").strip()
            for i, _ in enumerate(cfg["sections"]):
                title = request.form.get(f"privacy_title_{i}", "").strip()
                content = request.form.get(f"privacy_content_{i}", "").strip()
                if i < len(cfg["sections"]):
                    cfg["sections"][i]["title"] = title
                    cfg["sections"][i]["content"] = content
            save_privacy_policy(cfg)
            flash("Política de privacidad actualizada", "success")
            return redirect(url_for("main.dashboard") + "?section=privacyPolicy")

        if "add_privacy_section" in request.form:
            cfg = load_privacy_policy()
            title = request.form.get("new_privacy_title", "").strip()
            content = request.form.get("new_privacy_content", "").strip()
            if title or content:
                cfg["sections"].append({"title": title, "content": content})
                save_privacy_policy(cfg)
                flash("Nuevo punto agregado a la política", "success")
            return redirect(url_for("main.dashboard") + "?section=privacyPolicy")

        if "delete_privacy_section" in request.form:
            cfg = load_privacy_policy()
            try:
                index = int(request.form.get("delete_privacy_index", -1))
                if 0 <= index < len(cfg["sections"]):
                    cfg["sections"].pop(index)
                    save_privacy_policy(cfg)
                    flash("Punto eliminado", "success")
            except Exception:
                pass
            return redirect(url_for("main.dashboard") + "?section=privacyPolicy")

        if "save_terms_conditions" in request.form:
            cfg = load_terms_conditions()
            cfg["title"] = request.form.get("terms_title", "").strip()
            cfg["subtitle"] = request.form.get("terms_subtitle", "").strip()
            cfg["update_date"] = request.form.get("terms_update_date", "").strip()
            cfg["summary"] = request.form.get("terms_summary", "").strip()
            cfg["contact"] = request.form.get("terms_contact", "").strip()
            for i, _ in enumerate(cfg["sections"]):
                title = request.form.get(f"terms_title_{i}", "").strip()
                content = request.form.get(f"terms_content_{i}", "").strip()
                if i < len(cfg["sections"]):
                    cfg["sections"][i]["title"] = title
                    cfg["sections"][i]["content"] = content
            save_terms_conditions(cfg)
            flash("Términos y condiciones actualizados", "success")
            return redirect(url_for("main.dashboard") + "?section=termsConditions")

        if "add_terms_section" in request.form:
            cfg = load_terms_conditions()
            title = request.form.get("new_terms_title", "").strip()
            content = request.form.get("new_terms_content", "").strip()
            if title or content:
                cfg["sections"].append({"title": title, "content": content})
                save_terms_conditions(cfg)
                flash("Nuevo punto agregado a términos", "success")
            return redirect(url_for("main.dashboard") + "?section=termsConditions")

        if "delete_terms_section" in request.form:
            cfg = load_terms_conditions()
            try:
                index = int(request.form.get("delete_terms_index", -1))
                if 0 <= index < len(cfg["sections"]):
                    cfg["sections"].pop(index)
                    save_terms_conditions(cfg)
                    flash("Punto de términos eliminado", "success")
            except Exception:
                pass
            return redirect(url_for("main.dashboard") + "?section=termsConditions")

    async with async_session() as s:
        result = await s.execute(select(QuoteField).order_by(QuoteField.step, QuoteField.position))
        quote_fields = result.scalars().all()

    return render_template(
        "panel/dashboard.html",
        privacy_config=load_privacy_policy(),
        terms_config=load_terms_conditions(),
        home_slots=get_home_video_slots(),
        home_image_slots=get_home_image_slots(),
        home_media_config=load_home_media_config(),
        home_image_intervals=HOME_IMAGE_INTERVALS,
        translation_status=translation_status(),
        deploy_config=load_deploy_config(),
        pa_python_versions=PYTHONANYWHERE_PY_VERSIONS,
        hero_config=load_hero_config(),
        social_config=load_social_config(),
        quote_email_config=load_quote_email_config(),
        quote_fields=quote_fields,
        quote_field_types=QUOTE_FIELD_TYPES,
        form_fields_config=load_form_fields_config(),
        form_field_types=FORM_FIELD_TYPES,
        form_field_type_labels=FORM_FIELD_TYPE_LABELS,
    )


@main_bp.route("/perfil", methods=["GET", "POST"])
@login_required
async def perfil():
    if request.method == "POST":
        try:
            async with async_session() as s:
                user = await s.get(User, session["user_id"])
                user.first_name = request.form.get("first_name", "").strip() or None
                user.first_last_name = request.form.get("first_last_name", "").strip() or None
                user.second_last_name = request.form.get("second_last_name", "").strip() or None
                user.phone_number = request.form.get("phone_number", "").strip() or None
                user.country = request.form.get("country", "").strip() or None
                user.email = request.form.get("email", "").strip() or user.email
                user.username = request.form.get("username", "").strip() or None
                user.user_number = request.form.get("user_number", "").strip() or None
                await s.commit()
            flash("Perfil actualizado", "success")
        except Exception as e:
            flash(f"Error al actualizar el perfil: {e}", "danger")
        return redirect(url_for("main.perfil"))
    async with async_session() as s:
        user = await s.get(User, session["user_id"])
        user_count = (await s.execute(select(func.count(User.id)))).scalar()
    cfg = load_form_fields_config()
    extra = json.loads(user.extra_data or "{}")
    user_columns = {"first_name", "first_last_name", "second_last_name", "phone_number", "country", "email", "username", "user_number"}
    extra_fields = [f for f in cfg["fields"] if f.get("active") and f["key"] not in user_columns]
    return render_template(
        "panel/perfil.html",
        user=user,
        user_count=user_count,
        extra=extra,
        extra_fields=extra_fields,
    )


@main_bp.route("/usuarios", methods=["GET", "POST"])
@superuser_required
async def usuarios():
    if request.method == "POST":
        if "delete_quote_submission" in request.form:
            quote_id = int(request.form.get("delete_quote_submission", 0))
            if quote_id:
                async with async_session() as s:
                    quote = await s.get(QuoteSubmission, quote_id)
                    if quote:
                        await s.delete(quote)
                        await s.commit()
                        flash("Cotización eliminada", "success")
                    else:
                        flash("Cotización no encontrada", "danger")
            return redirect(url_for("main.usuarios"))
        return redirect(url_for("main.usuarios"))
    async with async_session() as s:
        all_users = (await s.execute(select(User).order_by(User.id))).scalars().all()
        quote_rows = (await s.execute(select(QuoteSubmission))).scalars().all()
        quote_user_ids = {q.user_id for q in quote_rows if q.user_id}
        quote_list = [
            {
                "id": q.id,
                "user_id": q.user_id,
                "created_at": q.created_at,
                "data": q.data,
            }
            for q in quote_rows
        ]
    return render_template(
        "panel/usuarios.html",
        users=all_users,
        quote_submissions=quote_list,
        quote_user_ids=quote_user_ids,
        can_assign_top=bool(session.get("is_top_superuser")),
    )


@main_bp.route("/usuarios/<int:user_id>", methods=["GET", "POST"])
@superuser_required
async def usuario_detalle(user_id):
    if request.method == "POST":
        async with async_session() as s:
            u = await s.get(User, user_id)
            if not u:
                flash("Usuario no encontrado", "danger")
                return redirect(url_for("main.usuarios"))
            u.first_name = request.form.get("first_name", "").strip() or None
            u.first_last_name = request.form.get("first_last_name", "").strip() or None
            u.second_last_name = request.form.get("second_last_name", "").strip() or None
            u.phone_number = request.form.get("phone_number", "").strip() or None
            u.country = request.form.get("country", "").strip() or None
            u.email = request.form.get("email", "").strip() or u.email
            u.username = request.form.get("username", "").strip() or None
            u.user_number = request.form.get("user_number", "").strip() or None
            can_assign_top = bool(session.get("is_top_superuser"))
            u_top = u.is_top_superuser
            if not u_top and can_assign_top:
                u.is_superuser = "is_superuser" in request.form
            if not u_top:
                u.is_active = "is_active" in request.form
            await s.commit()
            flash("Usuario actualizado", "success")
        return redirect(url_for("main.usuario_detalle", user_id=user_id))
    async with async_session() as s:
        u = await s.get(User, user_id)
    if not u:
        flash("Usuario no encontrado", "danger")
        return redirect(url_for("main.usuarios"))
    cfg = load_form_fields_config()
    extra = json.loads(u.extra_data or "{}")
    user_columns = {"first_name", "first_last_name", "second_last_name", "phone_number", "country", "email", "username", "user_number"}
    extra_fields = [f for f in cfg["fields"] if f.get("active") and f["key"] not in user_columns]
    return render_template(
        "panel/usuario_detalle.html",
        u=u,
        extra=extra,
        extra_fields=extra_fields,
        can_assign_top=bool(session.get("is_top_superuser")),
    )


@main_bp.route("/movil")
async def movil():
    return render_template("movil.html")


@main_bp.route("/caminatas")
async def caminatas():
    return render_template("caminatas.html")


@main_bp.route("/contacto")
async def contacto():
    return render_template("contacto.html")


@main_bp.route("/quienes-somos")
async def quienes_somos():
    return render_template("quienes_somos.html")


@main_bp.route("/blog")
async def blog():
    return render_template("blog.html")


@main_bp.route("/afiliados")
async def afiliados():
    return render_template("afiliados.html")


@main_bp.route("/terminos-y-condiciones")
async def terminos():
    return render_template(
        "terminos_y_condiciones.html",
        terms=load_terms_conditions(),
    )


@main_bp.route("/politica-de-privacidad")
async def privacidad():
    return render_template(
        "politica_de_privacidad.html",
        privacy=load_privacy_policy(),
    )
