from database.db import db

from flask import Blueprint, render_template

workers_bp = Blueprint("workers", __name__)


@workers_bp.route("/workers")
async def open_workers():
    all_users = await db.get_users()
    return render_template("workers.html", all_users=all_users)
