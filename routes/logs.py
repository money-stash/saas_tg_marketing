from flask import Blueprint, render_template

logs_bp = Blueprint("logs", __name__)


@logs_bp.route("/logs")
async def open_logs():
    return render_template("logs.html")
