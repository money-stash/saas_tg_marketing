import os

from flask import Blueprint, render_template, request, redirect, url_for, jsonify

from database.db import db
from config import UPLOAD_FOLDER
from pyro_funcs.checker import check_session_with_config

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

    if not session_info:
        return jsonify({"error": "Session not found"}), 404

    session_data = {
        "id": session_info.id,
        "account_id": session_info.account_id,
        "is_valid": session_info.is_valid,
        "path": session_info.path,
        "date": session_info.date,
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
