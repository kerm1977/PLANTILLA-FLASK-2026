"""Generador de proyectos web a partir de la plantilla Cookiecutter."""
import re
import shutil
import socket
import subprocess
import time
import traceback
from pathlib import Path

from flask import Blueprint, flash, redirect, render_template, request, url_for

generador_bp = Blueprint("generador", __name__)


def _slugify(name: str) -> str:
    """Convierte un nombre de proyecto en un slug válido."""
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", name.lower())
    slug = re.sub(r"_+", "_", slug).strip("_-")
    if not slug or slug[0].isdigit():
        slug = "proyecto_" + slug
    return slug


def _root_dir() -> Path:
    """Ruta raíz del repositorio (donde está cookiecutter.json)."""
    return Path(__file__).resolve().parent.parent.parent


def _get_port(site: Path) -> int:
    """Lee el puerto configurado en app.py del sitio."""
    app_file = site / "app.py"
    if app_file.exists():
        text = app_file.read_text(encoding="utf-8")
        match = re.search(r"port\s*=\s*(\d+)", text)
        if match:
            return int(match.group(1))
    return 5000


def _is_port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def _start_site(site: Path, port: int) -> None:
    """Arranca el servidor Flask del sitio generado."""
    python = site.parent.parent / "venv" / "Scripts" / "python.exe"
    if not python.exists():
        python = site.parent.parent / "venv" / "bin" / "python"
    if not python.exists():
        python = Path("python")
    subprocess.Popen(
        [
            str(python),
            "-m",
            "flask",
            "--app",
            "app",
            "run",
            "--port",
            str(port),
        ],
        cwd=str(site),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )


def _kill_process_on_port(port: int) -> None:
    """Finaliza el proceso que esté escuchando en el puerto indicado."""
    cmd = (
        f"Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue | "
        f"ForEach-Object {{ Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }}"
    )
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", cmd],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except Exception:
        pass


def _kill_site_processes(site: Path) -> None:
    """Mata los procesos que tengan archivos del sitio abiertos."""
    try:
        import psutil
    except ImportError:
        return
    site_str = str(site.resolve()).lower()
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            for file in proc.open_files():
                if file.path.lower().startswith(site_str):
                    proc.terminate()
                    time.sleep(0.2)
                    if proc.is_running():
                        proc.kill()
                    break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue


@generador_bp.route("/generar", methods=["GET", "POST"])
def generar():
    if request.method == "POST":
        project_name = request.form.get("project_name", "").strip()
        author_name = request.form.get("author_name", "Anónimo").strip()
        author_email = request.form.get("author_email", "anon@example.com").strip()
        description = request.form.get("description", "").strip()
        css_framework = request.form.get("css_framework", "bootstrap").strip().lower()

        try:
            port = int(request.form.get("port", "5000").strip())
            if not 1024 <= port <= 65535:
                raise ValueError
        except ValueError:
            flash("El puerto debe ser un número entre 1024 y 65535.", "danger")
            return redirect(url_for("generador.generar"))

        if css_framework not in {"bootstrap", "foundation", "bulma", "tailwind"}:
            flash("Framework CSS no válido.", "danger")
            return redirect(url_for("generador.generar"))

        if not project_name:
            flash("El nombre del proyecto es obligatorio.", "danger")
            return redirect(url_for("generador.generar"))

        project_slug = _slugify(project_name)

        extra_context = {
            "project_name": project_name,
            "project_slug": project_slug,
            "description": description or "Sitio web generado desde PLANTILLA-FLASK-2026.",
            "author_name": author_name,
            "author_email": author_email,
            "port": str(port),
            "css_framework": css_framework,
            "use_celery": "yes" if request.form.get("use_celery") else "no",
            "use_redis": "yes" if request.form.get("use_redis") else "no",
            "use_sentry": "yes" if request.form.get("use_sentry") else "no",
            "use_github_actions": "yes" if request.form.get("use_github_actions") else "no",
        }

        root = _root_dir()
        if not (root / "cookiecutter.json").exists():
            flash(
                "No se encontró cookiecutter.json. "
                "No puedes generar sitios desde esta instancia.",
                "danger",
            )
            return redirect(url_for("generador.generar"))

        output_dir = root / "sitios"
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            from cookiecutter.main import cookiecutter as _cookiecutter
            _cookiecutter(
                str(root),
                extra_context=extra_context,
                no_input=True,
                output_dir=str(output_dir),
                overwrite_if_exists=False,
            )
            flash(
                f"Sitio '{project_name}' generado en /sitios/{project_slug}",
                "success",
            )
            return redirect(url_for("generador.lista_sitios"))
        except Exception as exc:  # noqa: BLE001
            traceback.print_exc()
            flash(f"Error generando el sitio: {exc}", "danger")
            return redirect(url_for("generador.generar"))

    return render_template("generador/generar.html")


@generador_bp.route("/sitios")
def lista_sitios():
    root = _root_dir()
    sitios_dir = root / "sitios"
    sitios = []
    if sitios_dir.exists():
        for d in sorted(sitios_dir.iterdir()):
            if d.is_dir():
                sitios.append({"name": d.name, "path": str(d), "port": _get_port(d)})
    return render_template("generador/lista.html", sitios=sitios)


@generador_bp.route("/sitios/<slug>/ejecutar")
def ejecutar_sitio(slug):
    """Arranca el sitio generado y lo abre en su puerto."""
    site = _root_dir() / "sitios" / slug
    if not site.is_dir():
        flash("Sitio no encontrado.", "danger")
        return redirect(url_for("generador.lista_sitios"))

    port = _get_port(site)
    if not _is_port_open(port):
        _start_site(site, port)
        for _ in range(10):
            if _is_port_open(port):
                break
            time.sleep(0.5)
        else:
            flash("No se pudo iniciar el sitio.", "danger")
            return redirect(url_for("generador.lista_sitios"))

    return redirect(f"http://127.0.0.1:{port}/")


@generador_bp.route("/sitios/<slug>/eliminar", methods=["GET", "POST"])
def eliminar_sitio(slug):
    """Elimina un sitio generado tras cuatro confirmaciones."""
    site = _root_dir() / "sitios" / slug
    if not site.is_dir():
        flash("Sitio no encontrado.", "danger")
        return redirect(url_for("generador.lista_sitios"))

    if request.method == "POST":
        paso = int(request.form.get("paso", "1"))
        if request.form.get("confirmar") and paso == 4:
            _kill_site_processes(site)
            port = _get_port(site)
            if port != 5000:
                _kill_process_on_port(port)
            deleted = False
            for _ in range(5):
                try:
                    shutil.rmtree(site)
                    deleted = True
                    break
                except PermissionError:
                    time.sleep(0.5)
            if deleted:
                flash(f"El sitio '{slug}' ha sido eliminado permanentemente.", "success")
            else:
                flash(
                    f"No se pudo eliminar '{slug}'. "
                    "Detén el servidor manualmente e inténtalo de nuevo.",
                    "danger",
                )
            return redirect(url_for("generador.lista_sitios"))
        return render_template("generador/eliminar.html", slug=slug, site_name=slug, paso=paso)

    paso = int(request.args.get("paso", "1"))
    return render_template("generador/eliminar.html", slug=slug, site_name=slug, paso=paso)
