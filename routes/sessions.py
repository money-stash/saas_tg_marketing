import os

from flask import Blueprint, render_template, request, redirect, url_for, jsonify

from database.db import db
from config import UPLOAD_FOLDER
from pyro_funcs.checker import check_session_with_config
from login_funcs import (
    get_session_info,
    set_privacy_all_open,
    update_profile_photo,
    change_first_name,
    change_last_name,
    change_username,
)

sessions_bp = Blueprint("sessions", __name__)


@sessions_bp.route("/sessions")
async def open_sessions():
    all_sessions = await db.get_all_sessions()

    return render_template("sessions.html", all_sessions=all_sessions)


@sessions_bp.route("/get-all-sessions")
async def get_all_sessions():
    all_sessions = await db.get_all_sessions()

    sessions_data = []
    for session in all_sessions:
        sessions_data.append(
            {
                "id": session.id,
                "account_id": session.account_id,
                "is_valid": session.is_valid,
                "date": session.date,
            }
        )

    return jsonify({"sessions": sessions_data})


@sessions_bp.route("/get-session-by-id/<int:session_id>")
async def get_session_by_id(session_id):
    session_info = await db.get_session_by_id(int(session_id))

    session_path = session_info.path
    json_path = session_path + ".json"

    session_pyro_info = await get_session_info(session_path, json_path)

    if not session_info:
        return jsonify({"error": "Session not found"}), 404

    session_data = {
        "id": session_info.id,
        "account_id": session_info.account_id,
        "is_valid": session_info.is_valid,
        "date": session_info.date,
        "first_name": session_pyro_info.get("first_name", ""),
        "last_name": session_pyro_info.get("last_name", ""),
        "username": session_pyro_info.get("username", ""),
        "is_private": session_pyro_info.get("is_private", False),
    }

    return jsonify({"session": session_data})


@sessions_bp.route("/upload-session", methods=["POST"])
async def upload_session():
    files = request.files.getlist("session_files")
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    session_file = None
    json_file = None

    for file in files:
        if file and file.filename.endswith(".session"):
            session_file = file
        elif file and file.filename.endswith(".json"):
            json_file = file

    if not session_file or not json_file:
        return redirect(url_for("sessions.open_sessions", success=0))

    session_file.save(os.path.join(UPLOAD_FOLDER, session_file.filename))
    json_file.save(os.path.join(UPLOAD_FOLDER, json_file.filename))

    session_path = os.path.join(UPLOAD_FOLDER, session_file.filename).rsplit(".", 1)[0]
    json_path = os.path.join(UPLOAD_FOLDER, json_file.filename)

    is_valid = await check_session_with_config(session_path, json_path)
    if is_valid:
        parametr = 1
        await db.add_session(
            account_id=is_valid,
            path=session_path,
        )
    else:
        parametr = 0

    if parametr == 0:
        try:
            os.remove(f"{session_path}.session")
            os.remove(f"{json_path}.json")
        except:
            pass

    return redirect(url_for("sessions.open_sessions", success=parametr))


@sessions_bp.route("/upload-session-from-bot", methods=["POST"])
async def upload_session_from_bot():
    files = request.files.getlist("session_files")
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    session_file = None
    json_file = None

    for file in files:
        if file and file.filename.endswith(".session"):
            session_file = file
        elif file and file.filename.endswith(".json"):
            json_file = file

    if not session_file or not json_file:
        return redirect(url_for("sessions.open_sessions", success=0))

    session_file.save(os.path.join(UPLOAD_FOLDER, session_file.filename))
    json_file.save(os.path.join(UPLOAD_FOLDER, json_file.filename))

    session_path = os.path.join(UPLOAD_FOLDER, session_file.filename).rsplit(".", 1)[0]
    json_path = os.path.join(UPLOAD_FOLDER, json_file.filename)

    is_valid = await check_session_with_config(session_path, json_path)

    if is_valid:
        parametr = 1
        await db.add_session(
            account_id=is_valid,
            path=session_path,
        )
    else:
        parametr = 0

    if parametr == 0:
        try:
            os.remove(f"{session_path}.session")
            os.remove(f"{json_path}.json")
        except:
            pass

    if parametr == 1:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})


@sessions_bp.route("/delete-session", methods=["POST"])
async def delete_session():
    session_id = request.form.get("session_id")
    session_info = await db.get_session_by_id(session_id)

    session_path = session_info.path
    json_path = session_path + ".json"

    try:
        os.remove(session_path + ".session")
        os.remove(json_path)
    except:
        pass

    if session_id:
        await db.delete_session(int(session_id))

    return redirect(url_for("sessions.open_sessions"))


@sessions_bp.route("/open-privacy", methods=["POST"])
async def open_privacy():
    session_id = request.form.get("session_id")

    session_info = await db.get_session_by_id(session_id)
    session_path = session_info.path
    json_path = session_path + ".json"

    is_changed = await set_privacy_all_open(session_path, json_path)

    return jsonify({"success": is_changed})


@sessions_bp.route("/change-name", methods=["POST"])
async def change_name_func():
    session_id = request.form.get("session_id")
    new_first_name = request.form.get("first_name")

    session_info = await db.get_session_by_id(session_id)
    session_path = session_info.path
    json_path = session_path + ".json"

    is_changed = await change_first_name(session_path, json_path, new_first_name)

    return jsonify({"success": is_changed})


@sessions_bp.route("/change-surname", methods=["POST"])
async def change_surname_func():
    session_id = request.form.get("session_id")
    new_surname = request.form.get("surname")

    session_info = await db.get_session_by_id(session_id)
    session_path = session_info.path
    json_path = session_path + ".json"

    is_changed = await change_last_name(session_path, json_path, new_surname)

    return jsonify({"success": is_changed})


@sessions_bp.route("/change-username", methods=["POST"])
async def change_username_func():
    session_id = request.form.get("session_id")
    new_username = request.form.get("username")

    session_info = await db.get_session_by_id(session_id)
    session_path = session_info.path
    json_path = session_path + ".json"

    is_changed = await change_username(session_path, json_path, new_username)

    return jsonify({"success": is_changed})


@sessions_bp.route("/upload-avatar-api/<session_id>", methods=["POST"])
async def upload_avatar_api(session_id):
    try:
        avatar_file = request.files.get("avatar")
        if not avatar_file:
            return jsonify({"success": False, "error": "Файл не получен"}), 400

        session_record = await db.get_session_by_id(session_id)
        session_path = session_record.path
        json_path = session_path + ".json"

        filename = f"{session_path.split('/')[-1]}.jpg"
        save_path = os.path.join("frontend", "static", "images", filename)
        avatar_file.save(save_path)

        session_info = await get_session_info(session_path, json_path)

        info = {
            "first_name": session_info.get("first_name", "Иван"),
            "last_name": session_info.get("last_name", "Иванов"),
            "username": session_info.get("username", "ivanovv"),
            "is_private": session_info.get("is_private"),
        }

        answer = await update_profile_photo(session_path, json_path, save_path)

        if answer:
            return jsonify(
                {
                    "success": True,
                    "session_id": session_id,
                    "first_name": info["first_name"],
                    "last_name": info["last_name"],
                    "username": info["username"],
                    "is_private": info["is_private"],
                }
            )
        else:
            return (
                jsonify({"success": False, "error": "Не удалось обновить аватар"}),
                500,
            )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
