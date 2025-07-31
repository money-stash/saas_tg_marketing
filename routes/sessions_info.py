import os

from flask import Blueprint, render_template, request, redirect, url_for, flash

from database.db import db
from login_funcs import (
    get_session_info,
    update_profile_photo,
    change_username,
    change_first_name,
    change_last_name,
)

session_info_bp = Blueprint("session_info", __name__)


@session_info_bp.route("/session-info/<session_id>")
async def session_info(session_id):
    session_info = await db.get_session_by_id(session_id)
    session_path = session_info.path
    json_path = session_path + ".json"

    session_info = await get_session_info(session_path, json_path)

    info = {
        "first_name": session_info.get("first_name", "Иван"),
        "last_name": session_info.get("last_name", "Иванов"),
        "username": session_info.get("username", "ivanovv"),
        "is_private": session_info.get("is_private"),
    }
    return render_template(
        "session_info.html",
        session_id=session_path.split("/")[-1],
        session_has_avatar=True,
        first_name=info["first_name"],
        last_name=info["last_name"],
        username=info["username"],
        is_private=info["is_private"],
    )


@session_info_bp.route("/update-field/<session_id>/<field>", methods=["POST"])
async def update_field(session_id, field):
    try:
        value = request.form.get("value")

        session_path = f"sessions/{session_id}"
        print(session_path)

        session_info = await db.get_session_by_session_path(session_path)
        json_path = session_path + ".json"

        session_info = await get_session_info(session_path, json_path)

        info = {
            "first_name": session_info.get("first_name", "Иван"),
            "last_name": session_info.get("last_name", "Иванов"),
            "username": session_info.get("username", "ivanovv"),
            "is_private": session_info.get("is_private"),
        }

        print(f"Update field: {field}, session_id: {session_id}, value: {value}")

        if field == "first_name":
            await change_first_name(session_path, json_path, value)
            info["first_name"] = value
        elif field == "last_name":
            await change_last_name(session_path, json_path, value)
            info["last_name"] = value
        elif field == "username":
            await change_username(session_path, json_path, value)
            info["username"] = value

        return render_template(
            "session_info.html",
            session_id=session_path.split("/")[-1],
            session_has_avatar=True,
            first_name=info["first_name"],
            last_name=info["last_name"],
            username=info["username"],
            is_private=info["is_private"],
            updated_field=field,
            updated_value=value,
        )
    except Exception as e:
        flash(f"Error updating field: {e}", "error")
        return redirect(url_for("session_info.session_info", session_id=session_id))


@session_info_bp.route("/upload-avatar/<session_id>", methods=["POST"])
async def upload_avatar(session_id):
    try:
        avatar_file = request.files.get("avatar")
        if not avatar_file:
            flash("Файл не получен", "error")
            return redirect(url_for("session_info.session_info", session_id=session_id))

        filename = f"{session_id}.jpg"
        save_path = os.path.join("frontend", "static", "images", filename)
        avatar_file.save(save_path)

        session_path = f"sessions/{session_id}"
        session_record = await db.get_session_by_session_path(session_path)
        json_path = session_path + ".json"

        session_info = await get_session_info(session_path, json_path)

        info = {
            "first_name": session_info.get("first_name", "Иван"),
            "last_name": session_info.get("last_name", "Иванов"),
            "username": session_info.get("username", "ivanovv"),
            "is_private": session_info.get("is_private"),
        }

        await update_profile_photo(
            session_path, json_path, f"frontend/static/images/{filename}"
        )

        return render_template(
            "session_info.html",
            session_id=session_id,
            session_has_avatar=True,
            first_name=info["first_name"],
            last_name=info["last_name"],
            username=info["username"],
            is_private=info["is_private"],
        )
    except Exception as e:
        flash(f"Ошибка при загрузке аватарки: {e}", "error")

    return redirect(url_for("session_info.session_info", session_id=session_id))
