from database.db import db

from flask import Blueprint, render_template, request, redirect, url_for

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
