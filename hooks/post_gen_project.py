"""Hook ejecutado después de generar el proyecto con Cookiecutter."""
import shutil
import urllib.request
from pathlib import Path

PROJECT_DIR = Path.cwd()


def remove(filepath):
    """Elimina archivos o carpetas opcionales del proyecto generado."""
    path = PROJECT_DIR / filepath
    if path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


# Opcional: eliminar archivos de Celery si no se solicitó
{% if cookiecutter.use_celery != "yes" -%}
remove("services/tasks.py")
{% endif %}

# Opcional: eliminar configuración de Sentry si no se solicitó
{% if cookiecutter.use_sentry != "yes" -%}
remove("services/sentry.py")
{% endif %}

# Crear .env a partir de .env.example con los secretos generados
env_example = PROJECT_DIR / ".env.example"
env_file = PROJECT_DIR / ".env"
if env_example.exists() and not env_file.exists():
    content = env_example.read_text(encoding="utf-8")
    content = content.replace("SECRET_KEY=", f'SECRET_KEY={{ cookiecutter.secret_key }}')
    content = content.replace("JWT_SECRET_KEY=", f'JWT_SECRET_KEY={{ cookiecutter.jwt_secret_key }}')
    env_file.write_text(content, encoding="utf-8")

# Aplicar puerto personalizado
port = int("{{ cookiecutter.port }}")
app_path = PROJECT_DIR / "app.py"
if app_path.exists():
    content = app_path.read_text(encoding="utf-8")
    content = content.replace("port=5000", f"port={port}")
    app_path.write_text(content, encoding="utf-8")

# Aplicar framework CSS
def download(url, path):
    """Descarga un recurso y lo guarda dentro del proyecto generado."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=30) as response:
        path.write_bytes(response.read())


framework = "{{ cookiecutter.css_framework }}"
base_path = PROJECT_DIR / "templates" / "base.html"
static_dir = PROJECT_DIR / "static" / "vendor"
if base_path.exists() and framework != "bootstrap":
    content = base_path.read_text(encoding="utf-8")
    bootstrap_dir = static_dir / "bootstrap"
    if bootstrap_dir.is_dir():
        shutil.rmtree(bootstrap_dir)

    if framework == "foundation":
        css_url = "https://cdn.jsdelivr.net/npm/foundation-sites@6.8.1/dist/css/foundation.min.css"
        js_url = "https://cdn.jsdelivr.net/npm/foundation-sites@6.8.1/dist/js/foundation.min.js"
        css_path = static_dir / "foundation" / "css" / "foundation.min.css"
        js_path = static_dir / "foundation" / "js" / "foundation.min.js"
        download(css_url, css_path)
        download(js_url, js_path)
        new_css = '{% raw %}href="{{ url_for(\'static\', filename=\'vendor/foundation/css/foundation.min.css\') }}"{% endraw %}'
        new_js = '{% raw %}src="{{ url_for(\'static\', filename=\'vendor/foundation/js/foundation.min.js\') }}"{% endraw %}'
    elif framework == "bulma":
        css_url = "https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css"
        css_path = static_dir / "bulma" / "css" / "bulma.min.css"
        download(css_url, css_path)
        new_css = '{% raw %}href="{{ url_for(\'static\', filename=\'vendor/bulma/css/bulma.min.css\') }}"{% endraw %}'
        new_js = None
    elif framework == "tailwind":
        js_url = "https://cdn.tailwindcss.com"
        js_path = static_dir / "tailwind" / "js" / "tailwind.js"
        download(js_url, js_path)
        new_css = None
        new_js = '{% raw %}src="{{ url_for(\'static\', filename=\'vendor/tailwind/js/tailwind.js\') }}"{% endraw %}'
    else:
        new_css = new_js = None

    if new_css is not None:
        content = content.replace(
            '{% raw %}href="{{ url_for(\'static\', filename=\'vendor/bootstrap/css/bootstrap.min.css\') }}"{% endraw %}',
            new_css,
        )
    else:
        content = content.replace(
            '{% raw %}    <link rel="stylesheet" href="{{ url_for(\'static\', filename=\'vendor/bootstrap/css/bootstrap.min.css\') }}">{% endraw %}',
            "",
        )

    if new_js is not None:
        content = content.replace(
            '{% raw %}src="{{ url_for(\'static\', filename=\'vendor/bootstrap/js/bootstrap.bundle.min.js\') }}"{% endraw %}',
            new_js,
        )
    else:
        content = content.replace(
            '{% raw %}    <script src="{{ url_for(\'static\', filename=\'vendor/bootstrap/js/bootstrap.bundle.min.js\') }}"></script>{% endraw %}',
            "",
        )

    base_path.write_text(content, encoding="utf-8")

print(f"Proyecto '{{ cookiecutter.project_name }}' generado en {PROJECT_DIR}")
