"""Punto de entrada principal — patrón Application Factory."""
import asyncio
import os

from dotenv import load_dotenv
from flask import Flask, render_template

load_dotenv()

from blueprints import register_blueprints  # noqa: E402
from config import config_map  # noqa: E402
from cotizador_countries import COUNTRY_OPTIONS  # noqa: E402
from extensions import bcrypt, init_extensions  # noqa: E402
from i18n import init_i18n  # noqa: E402
from models import QuoteField, async_session, init_db, User  # noqa: E402


def create_app(config_name: str | None = None) -> Flask:
    """Crea y configura la instancia de la aplicación Flask."""
    config_name = config_name or os.getenv("FLASK_ENV", "development")
    app = Flask(__name__)
    app.config.from_object(config_map[config_name])

    init_extensions(app)
    register_blueprints(app)
    init_i18n(app)
    register_error_handlers(app)

    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

    @app.after_request
    def set_cache_control(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    @app.context_processor
    def inject_footer_data():
        from blueprints.main import load_social_config

        return {
            "social_config": load_social_config(),
            "social_icons": {
                "instagram": "instagram",
                "facebook": "facebook",
                "x": "twitter-x",
                "tiktok": "tiktok",
            },
        }

    # Creación automática de tablas e índices al arrancar
    with app.app_context():
        asyncio.run(init_db())
        asyncio.run(seed_db())
        asyncio.run(seed_quote_fields())

    return app


async def seed_db():
    """Crea los superusuarios por defecto si no existen."""
    from sqlalchemy import select

    superusers = [
        {"username": "admin", "email": "admin@example.com", "password": "admin1234", "is_top": False},
        {"username": "kenth1977@gmail.com", "email": "kenth1977@gmail.com", "password": "CR129x7848n", "is_top": True},
        {"username": "lthikingcr@gmail.com", "email": "lthikingcr@gmail.com", "password": "CR129x7848n", "is_top": True},
    ]

    async with async_session() as session:
        for data in superusers:
            result = await session.execute(
                select(User).where(
                    (User.username == data["username"]) | (User.email == data["email"])
                )
            )
            existing = result.scalar_one_or_none()
            if not existing:
                user = User(
                    username=data["username"],
                    email=data["email"],
                    password_hash=bcrypt.generate_password_hash(data["password"]).decode("utf-8"),
                    is_superuser=True,
                    is_top_superuser=data["is_top"],
                    is_active=True,
                )
                session.add(user)
            elif data["is_top"] and not existing.is_top_superuser:
                existing.is_top_superuser = True
        await session.commit()


async def seed_quote_fields():
    """Crea las preguntas por defecto del Cotizador si la tabla está vacía."""
    from sqlalchemy import delete

    default_fields = [
        (1, 1, "first_name", "text", "Nombre", None, True, None, None),
        (1, 2, "last_name", "text", "Apellido", None, True, None, None),
        (1, 3, "country", "single_choice", "País", None, True, COUNTRY_OPTIONS, None),
        (1, 4, "whatsapp", "tel", "Número de teléfono (WhatsApp)", None, True, None, None),
        (1, 5, "email", "email", "Correo electrónico", None, True, None, None),
        (1, 6, "people_count", "number", "¿Cuántas personas se irán al tour?",
         "Si eres solo tú, escribe 1. Como este es un tour privado personalizado, este número se refiere únicamente a las personas de tu grupo (nadie más se unirá).",
         True, None, None),
        (2, 1, "trip_days_info", "info", "Sobre los días del viaje",
         "Primero preguntaremos cuántos días de caminata (tour) deseas. Luego preguntaremos cuántos días de descanso te gustaría. Ejemplo: si tus días disponibles para este viaje son 20 en total y quieres 5 días de descanso, entonces 15 días de caminata + 5 días de descanso = 20 días totales. Separamos estos números para planear tu aventura con mayor precisión.",
         False, None, None),
        (2, 2, "hiking_days", "number", "¿Cuántos días de caminata deseas en tu tour personalizado?",
         "Estos son únicamente tus días activos de caminata. Los días de descanso se agregan por separado en la siguiente pregunta.",
         True, None, None),
        (2, 3, "rest_days", "number", "¿Cuántos días de descanso te gustaría agregar a tu viaje?",
         "Los días de descanso se agregan además de tus días de caminata. Por ejemplo, si elegiste 5 días de caminata y quieres 3 días de descanso, tu viaje será de 8 días en total.",
         True, None, None),
        (2, 4, "tour_type", "single_choice", "¿Qué tipo de tour te interesa?", None, True,
         ["Senderismo", "Trail running"], None),
        (3, 1, "accommodation", "multi_choice", "¿Qué tipo de alojamiento prefieres?",
         "Puedes elegir más de una opción.", True,
         ["Superior (más cómodo)", "Media (comodidad moderada)", "Camping (con opción de combinar)"], 2),
        (3, 2, "adventure_activities", "multi_choice", "¿Qué actividades de aventura te gustaría incluir?",
         "Estas actividades pueden ocupar un día completo de tu tour, tenlo en cuenta. ¿No quieres ninguna? Selecciona \u201cOtro\u201d y escribe \u201cNinguna\u201d. Puedes elegir hasta 4.",
         True,
         ["Canopy (Zipline)", "Rafting", "Tubing", "Paddle board", "Buceo", "Pesca deportiva", "Otro"], 4),
        (3, 3, "nature_activities", "multi_choice", "¿Qué actividades de naturaleza y vida silvestre te interesan?",
         "Puedes elegir hasta 6.", False,
         ["Avistamiento de aves", "Tour de quetzales", "Tour de cocodrilos", "Tour de mariposario",
          "Tour nocturno (animales nocturnos)", "Cataratas", "Piscinas naturales",
          "Áreas de descanso junto a ríos", "Parques nacionales y reservas naturales", "Otro"], 6),
        (3, 4, "wellness_activities", "multi_choice", "¿Te gustaría incluir experiencias de bienestar y relajación?",
         "Elige tantas como quieras.", True,
         ["Aguas termales", "Día de spa", "Sesión de masajes", "Pedicura", "Limpieza facial",
          "Noche de fogata", "Otro"], None),
        (3, 5, "cultural_activities", "multi_choice", "¿Te interesa alguna experiencia cultural o local?",
         "Elige tantas como quieras.", True,
         ["Tour de café", "Tour de cacao", "Tour de trapiche (molino de caña)",
          "Apicultura y experiencia con miel", "Visita a una viña local (Vinos COPEI)",
          "Iglesias coloniales", "Arquitectura y edificios patrimoniales", "Otro"], None),
        (4, 1, "food_sweets", "yes_no", "Experiencia gastronómica local: dulces y repostería",
         "Satisface tu gusto por lo dulce con miel de chiverre, productos horneados hechos de chiverre, cajetas (dulce de coco y leche), bizcochos y otra repostería tradicional.",
         True, None, None),
        (4, 2, "food_unique", "yes_no", "Experiencia gastronómica local: sabores únicos",
         "Prueba sabores icónicos como el chiliguaro (trago picante local), chileritas (chiles picantes encurtidos), tamal mudo (tamal de hoja de plátano sin relleno), conservas caseras y otras delicias regionales poco comunes.",
         True, None, None),
        (4, 3, "cooking_class", "yes_no", "¿Te gustaría aprender a cocinar alguno de estos platillos durante tu tour?",
         None, True, None, None),
        (4, 4, "custom_activity", "textarea", "¿Hay alguna actividad personalizada no mencionada arriba que te gustaría incluir?",
         None, True, None, None),
        (4, 5, "meaningful_experience", "textarea", "¿Qué haría que este viaje fuera realmente significativo para ti?",
         None, True, None, None),
        (4, 6, "referral_source", "single_choice", "¿Cómo te enteraste de Cumbres CR?", None, False,
         ["Un amigo", "Redes sociales", "Búsqueda en Google", "Un blog/artículo", "Publicidad", "Otro"], None),
        (5, 1, "contact_method", "single_choice", "¿Cómo deseas recibir tu cotización?", None, True,
         ["WhatsApp", "Correo electrónico"], None),
    ]

    async with async_session() as session:
        await session.execute(delete(QuoteField))
        for step, position, key, ftype, label, help_text, required, options, max_choices in default_fields:
            session.add(QuoteField(
                step=step,
                position=position,
                field_key=key,
                field_type=ftype,
                label=label,
                help_text=help_text,
                required=required,
                options=options,
                max_choices=max_choices,
            ))
        await session.commit()


def register_error_handlers(app: Flask):
    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(error):
        return render_template("errors/500.html"), 500


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=app.config["DEBUG"])
