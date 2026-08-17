"""Vistas principales: home, dashboard y perfil."""
import glob
import json
import os
from functools import wraps

from flask import Blueprint, Response, current_app, flash, redirect, render_template, request, session, url_for
from sqlalchemy import func, select

from i18n import set_locale, sync_translations, translation_status
from models import User, async_session

main_bp = Blueprint("main", __name__)

ALLOWED_VIDEO_EXT = {"mp4", "webm", "ogg"}
HOME_VIDEO_SLOTS = 3
PYTHONANYWHERE_PY_VERSIONS = ["3.13", "3.12", "3.11", "3.10", "3.9"]


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


@main_bp.route("/set-lang/<lang>")
async def set_lang(lang):
    set_locale(lang)
    next_url = request.args.get("next") or request.referrer or url_for("main.home")
    return redirect(next_url)


@main_bp.route("/")
async def home():
    slots = get_home_video_slots()
    playlist = [s["url"] for s in slots if s["url"]]
    if not playlist:
        playlist = [url_for("static", filename="wq.mp4")]
    return render_template("home.html", home_videos=playlist)


@main_bp.route("/dashboard", methods=["GET", "POST"])
@superuser_required
async def dashboard():
    if request.method == "POST":
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
    return render_template(
        "panel/dashboard.html",
        home_slots=get_home_video_slots(),
        translation_status=translation_status(),
        deploy_config=load_deploy_config(),
        pa_python_versions=PYTHONANYWHERE_PY_VERSIONS,
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
        active = (await s.execute(select(func.count(User.id)).where(User.is_active == True))).scalar()
    return render_template("panel/perfil.html", user=user, active_count=active)


@main_bp.route("/usuarios")
@superuser_required
async def usuarios():
    async with async_session() as s:
        all_users = (await s.execute(select(User).order_by(User.id))).scalars().all()
    return render_template(
        "panel/usuarios.html",
        users=all_users,
        can_assign_top=bool(session.get("is_top_superuser")),
    )


@main_bp.route("/usuarios/<int:user_id>")
@superuser_required
async def usuario_detalle(user_id):
    async with async_session() as s:
        u = await s.get(User, user_id)
    if not u:
        flash("Usuario no encontrado", "danger")
        return redirect(url_for("main.usuarios"))
    return render_template("panel/usuario_detalle.html", u=u)


@main_bp.route("/movil")
async def movil():
    return render_template("movil.html")


@main_bp.route("/caminatas")
async def caminatas():
    return render_template("caminatas.html")
