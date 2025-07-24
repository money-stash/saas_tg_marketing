from flask import Blueprint, render_template, request

from database.db import db
from datetime import datetime

statistic_bp = Blueprint("statistic", __name__)


@statistic_bp.route("/statistic")
async def open_statistic():
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

    return render_template("statistic.html", statistics=reports_data)
