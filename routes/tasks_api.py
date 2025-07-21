from database.db import db

from flask import Blueprint, jsonify, request, send_file
from login_funcs import join_and_parse_group
from utils.tg_utils import send_message_to_user
import os
import random

tasks_bp = Blueprint("tasks_api", __name__)


@tasks_bp.route("/reports", methods=["GET"])
async def get_reports():
    all_reports = await db.get_all_reports()

    reports_data = []
    for report in all_reports:
        reports_data.append(
            {
                "id": report.id,
                "date": report.date,
                "worker_id": report.worker_id,
                "path": report.path,
                "type": report.type,
            }
        )

    return jsonify({"reports": reports_data})


@tasks_bp.route("/create-parse-task", methods=["POST"])
async def create_task_parse():
    task_data = request.json
    worker_id = task_data.get("worker_id")
    group_identifier = task_data.get("group_identifier")

    session_dir = "sessions"
    session_files = [f for f in os.listdir(session_dir) if f.endswith(".json")]
    selected = random.choice(session_files)
    session_name = selected.replace(".json", "").replace(".session", "")
    session_path = os.path.join(session_dir, session_name)
    json_path = os.path.join(session_dir, selected)

    result = await join_and_parse_group(
        group_username=group_identifier,
        session_path=session_path,
        json_path=json_path,
        message_limit=100,
        user_id=worker_id,
    )

    await send_message_to_user(
        user_id=worker_id,
        text=f"From group {group_identifier}.\n\nParsed: {result} users.",
    )

    return jsonify(
        {"task": True, "worker_id": worker_id, "group_identifier": group_identifier}
    )


@tasks_bp.route("/all-reports")
async def get_all_reportsss():
    all_reports = await db.get_all_reports()

    reports_data = []
    for report in all_reports:
        reports_data.append(
            {
                "id": report.id,
                "date": report.date,
                "worker_id": report.worker_id,
                "path": report.path,
                "type": report.type,
            }
        )

    return jsonify({"reports": reports_data})


@tasks_bp.route("/get_report", methods=["POST"])
async def get_task():
    task_data = request.json
    report_id = task_data.get("report_id")

    report = await db.get_report_by_id(report_id)

    data = {
        "id": report.id,
        "date": report.date,
        "worker_id": report.worker_id,
        "path": report.path,
        "type": report.type,
    }

    return jsonify(data)


@tasks_bp.route("/download-report", methods=["POST"])
async def download_report():
    data = request.json
    path = data.get("path")

    if not path or not os.path.exists(path):
        return jsonify({"error": "Invalid or missing path"}), 400

    return send_file(path, as_attachment=True)
