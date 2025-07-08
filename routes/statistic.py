from flask import Blueprint, render_template

statistic_bp = Blueprint("statistic", __name__)


@statistic_bp.route("/statistic")
def open_statistic():
    return render_template("statistic.html")
