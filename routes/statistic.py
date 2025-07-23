from flask import Blueprint, render_template, request

from datetime import datetime

statistic_bp = Blueprint("statistic", __name__)


@statistic_bp.route("/statistic")
async def open_statistic():
    statistics = [
        {
            "id": 1,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "type": "Рассылка",
            "target_type": "Сессия",
        },
        {
            "id": 2,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "type": "Парсинг",
            "target_type": "Задача",
        },
    ]
    return render_template("statistic.html", statistics=statistics)
