import os
import csv
import random
import asyncio
from datetime import datetime
from math import ceil
from flask import Blueprint, jsonify, request, send_file

from database.db import db

from login_funcs import join_and_parse_group, send_message_from_session
from utils.tg_utils import send_message_to_user

tasks_bp = Blueprint("tasks_api", __name__)


@tasks_bp.route("/reports", methods=["GET"])
async def get_reports():
    all_reports = await db.get_all_reports()

    reports_data = []
    for report in all_reports:
        count_with_username = 0
        if report.path and os.path.exists(report.path):
            try:
                with open(report.path, newline="", encoding="utf-8") as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        username = row.get("username", "").strip()
                        if username and username.lower() != "none":
                            count_with_username += 1
            except Exception as e:
                count_with_username = -1

        else:
            count_with_username = -1

        reports_data.append(
            {
                "id": report.id,
                "date": report.date,
                "worker_id": report.worker_id,
                "path": report.path,
                "type": report.type,
                "usernames_count": count_with_username,
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


@tasks_bp.route("/start-spam", methods=["POST"])
async def start_spam_func():
    data = request.json
    path = data.get("users_path")
    total_count = int(data.get("messages_count"))
    msg_text = data.get("msg_text")
    worker_id = data.get("worker_id")

    if not os.path.exists(path):
        return jsonify({"error": "Invalid users file path"}), 400

    all_sessions = await db.get_all_sessions()
    if not all_sessions:
        return jsonify({"error": "No sessions available"}), 400

    users = []
    with open(path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            username = row.get("username", "").strip()
            if username and username.lower() != "none":
                users.append(username)

    users = users[: min(total_count, len(users))]
    per_session = ceil(len(users) / len(all_sessions))

    os.makedirs("work_reports", exist_ok=True)
    report_filename = (
        f"work_reports/spam_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )
    with open(report_filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["username", "status"])

    user_index = 0

    for session in all_sessions:
        session_users = users[user_index : user_index + per_session]
        user_index += per_session

        for username in session_users:
            sesion_path = session.path
            success = await send_message_from_session(
                session_path=sesion_path,
                json_path=f"{sesion_path}.json",
                username=username,
                text=msg_text,
            )
            status = "success" if success else "fail"
            with open(report_filename, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([username, status])
            await asyncio.sleep(random.uniform(1.5, 3.5))

        await asyncio.sleep(random.uniform(2, 4))

    await send_message_to_user(
        user_id=worker_id,
        text=f"Отправил сообщения всем пользователям, можешь посмотреть отчёт!",
    )

    await db.add_report(
        date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        worker_id=worker_id,
        path=report_filename,
        type_="spam",
    )

    return jsonify({"status": "ok"})
