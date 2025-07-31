from database.db import db

from flask import Blueprint, render_template, request, redirect, url_for, jsonify

workers_bp = Blueprint("workers", __name__)


@workers_bp.route("/workers")
async def open_workers():
    all_users = await db.get_users()
    return render_template("workers.html", all_users=all_users)


@workers_bp.route("/block-user", methods=["POST"])
async def block_user():
    user_id = request.form.get("user_id")
    if user_id:
        await db.block_user(int(user_id))
    return redirect(url_for("workers.open_workers"))


@workers_bp.route("/unblock-user", methods=["POST"])
async def unblock_user():
    user_id = request.form.get("user_id")
    if user_id:
        await db.unblock_user(int(user_id))
    return redirect(url_for("workers.open_workers"))


@workers_bp.route("/list_workers_bot")
async def list_workers_bot():
    all_users = await db.get_users()
    workers_data = []

    for user in all_users:
        workers_data.append(
            {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "user_id": user.user_id,
                "date": user.date,
            }
        )

    return jsonify({"workers": workers_data})


@workers_bp.route("/ban_user_bot", methods=["POST"])
async def ban_user_bot():
    task_data = request.json
    username = task_data.get("username")

    await db.block_user_by_username(username.replace("@", ""))

    return jsonify({"status": "ok"})
