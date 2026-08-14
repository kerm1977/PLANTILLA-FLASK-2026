# PLANTILLA-FLASK-2026

Plantilla base para aplicaciones Flask con arquitectura escalable, base de datos asíncrona, autenticación, seguridad, extensiones desacopladas y frontend responsive mobile-first con Bootstrap 5.3.3 y Bootstrap Icons servidos 100% localmente (sin CDN).

## Características

- **Application Factory** con `app.py` como punto de entrada.
- **SQLAlchemy 2.0 async** con `aiosqlite`.
- **Extensiones desacopladas** en `extensions.py`: Bcrypt, Login, JWT, CORS, CSRF, Caché, Mail.
- **Blueprints** para `main`, `auth`, `admin` y `api`.
- **Vistas maquetadas** (solo nombre centrado): Home, Login, Registro, Dashboard, Perfil, Admin, 404 y 500.
- **Botón "Back to Home"** `btn-warning` en todas las vistas excepto Home.
- **Health checks** en `/api/health`.
- **Tests** con `pytest` (10 pruebas pasando).

## Estructura

```
flask_template/
├── app.py
├── config.py
├── extensions.py
├── models/
├── blueprints/
├── services/
├── static/
│   ├── css/
│   ├── js/
│   └── vendor/
│       ├── bootstrap/
│       └── bootstrap-icons/
├── templates/
├── tests/
└── venv/
```

## Instalación

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Ejecutar

```powershell
.\venv\Scripts\python.exe app.py
```

La app estará en `http://127.0.0.1:5000`.

## Tests

```powershell
.\venv\Scripts\python.exe -m pytest tests/ -v
```

## Nota técnica

Se fijó `greenlet==3.2.4` porque versiones posteriores crashean con Python 3.13 en Windows para esta máquina.
