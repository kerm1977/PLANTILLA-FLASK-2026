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






async def handle_home_media(request):
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

    return redirect(url_for('main.dashboard'))
