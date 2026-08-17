"""Helpers del generador de proyectos."""
import re
import shutil
import socket
import subprocess
import time
import traceback
from pathlib import Path



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


