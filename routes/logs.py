from flask import Blueprint, render_template

from database.db import db


logs_bp = Blueprint("logs", __name__)


@logs_bp.route("/logs")
async def open_logs():
    all_reports = await db.get_all_reports()

    reports_data = []
    for report in all_reports:
        reports_data.append(
            {
                "id": report.id,
                "date": report.date,
                "worker_id": report.worker_id,
                "path": report.path,
                "target_type": report.type,
            }
        )

    return render_template("logs.html", reports=reports_data)
