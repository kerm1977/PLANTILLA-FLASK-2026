"""Ruta del panel de administración."""
from __future__ import annotations
import json
import os
from datetime import datetime

from flask import Response, current_app, flash, redirect, render_template, request, session, url_for
from sqlalchemy import func, select

from blueprints.main import main_bp, superuser_required
from blueprints.main_config import *  # noqa: F401, F403
from blueprints.main_noticumbres import load_noticumbres, save_noticumbres
from i18n import sync_translations, translation_status
from models import QuoteField, User, async_session


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
            cfg["content"] = request.form.get("privacy_content", "").strip()
            save_privacy_policy(cfg)
            flash("Política de privacidad actualizada", "success")
            return redirect(url_for("main.dashboard") + "?section=privacyPolicy")

        if "save_terms_conditions" in request.form:
            cfg = load_terms_conditions()
            cfg["content"] = request.form.get("terms_content", "").strip()
            save_terms_conditions(cfg)
            flash("Términos y condiciones actualizados", "success")
            return redirect(url_for("main.dashboard") + "?section=termsConditions")

        if "save_noticumbres_config" in request.form:
            data = load_noticumbres()
            data.setdefault("config", {})
            data["config"]["update_time"] = request.form.get("noticumbres_update_time", "").strip()
            try:
                data["config"]["max_posts"] = int(request.form.get("noticumbres_max_posts", "0") or "0")
            except ValueError:
                data["config"]["max_posts"] = 0
            save_noticumbres(data)
            flash("Configuración de noticias actualizada", "success")
            return redirect(url_for("main.dashboard") + "?section=noticumbresAdmin")


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
        noticumbres_config=load_noticumbres(),
    )

