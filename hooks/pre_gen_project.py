"""Hook ejecutado antes de generar el proyecto con Cookiecutter."""
import re
import sys

PROJECT_REGEX = r"^[_a-zA-Z][_a-zA-Z0-9]+$"
project_slug = "{{ cookiecutter.project_slug }}"

if not re.match(PROJECT_REGEX, project_slug):
    print(f"ERROR: {project_slug} no es un slug de Python válido.")
    sys.exit(1)

if project_slug in ["flask", "app", "test"]:
    print(f"ERROR: '{project_slug}' es un nombre reservado.")
    sys.exit(1)
