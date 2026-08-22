"""Rutas y utilidades de Noticumbres."""
from __future__ import annotations

import json
import os
import re
import uuid
from datetime import datetime

from flask import (
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from blueprints.main import ALLOWED_IMAGE_EXT, main_bp, superuser_required
from models import User, async_session


def _noticumbres_path():
    return os.path.join(current_app.root_path, "noticumbres.json")


def load_noticumbres():
    path = _noticumbres_path()
    default = {"config": {}, "posts": []}
    if not os.path.exists(path):
        return default
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        default.update(data)
    except Exception:
        pass
    return default


def save_noticumbres(data):
    with open(_noticumbres_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


@main_bp.route("/noticumbres")
async def blog():
    data = load_noticumbres()
    return render_template(
        "noticumbres.html",
        posts=data.get("posts", []),
    )


@main_bp.route("/panel/noticumbres", methods=["GET", "POST"])
@superuser_required
async def noticumbres_admin():
    if request.method == "POST":
        title = request.form.get("noticumbres_title", "").strip()
        summary = request.form.get("noticumbres_summary", "").strip()
        content = request.form.get("noticumbres_content", "").strip()
        if not title:
            flash("El título es obligatorio", "warning")
            return redirect(url_for("main.noticumbres_admin"))
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "post"
        slug = f"{slug}-{int(datetime.now().timestamp())}"
        image = ""
        upload = request.files.get("noticumbres_image")
        if upload and upload.filename:
            ext = upload.filename.rsplit(".", 1)[-1].lower() if "." in upload.filename else ""
            if ext in ALLOWED_IMAGE_EXT:
                upload_dir = os.path.join(current_app.root_path, "static", "uploads", "noticumbres")
                os.makedirs(upload_dir, exist_ok=True)
                filename = f"{uuid.uuid4().hex}.{ext}"
                upload.save(os.path.join(upload_dir, filename))
                image = os.path.join("uploads", "noticumbres", filename).replace("\\", "/")
            else:
                flash("Formato de imagen no permitido", "warning")
        user_id = session.get("user_id")
        author = "Administrador"
        if user_id:
            async with async_session() as s:
                user = await s.get(User, user_id)
                if user:
                    author = " ".join(p for p in [user.first_name, user.first_last_name, user.second_last_name] if p) or user.username or user.email or "Administrador"

        data = load_noticumbres()
        posts = data.get("posts", [])
        now = datetime.now().isoformat(sep=" ", timespec="seconds")
        posts.insert(0, {
            "id": str(uuid.uuid4()),
            "title": title,
            "slug": slug,
            "summary": summary,
            "content": content,
            "author": author,
            "image": image,
            "published_at": now,
            "updated_at": now,
            "is_published": True,
        })
        data["posts"] = posts
        save_noticumbres(data)
        flash("Publicación de Noticumbres creada", "success")
        return redirect(url_for("main.noticumbres_admin"))
    return render_template(
        "panel/noticumbres.html",
        noticumbres=load_noticumbres(),
    )
