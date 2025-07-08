from flask import Blueprint, render_template

sessions_bp = Blueprint("sessions", __name__)


@sessions_bp.route("/sessions")
def open_sessions():
    return render_template("sessions.html")
