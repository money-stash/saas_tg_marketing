from flask import Blueprint, render_template

tokens_bp = Blueprint("tokens", __name__)


@tokens_bp.route("/tokens")
def open_tokens():
    return render_template("tokens.html")
