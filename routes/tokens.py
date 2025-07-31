from database.db import db

from flask import request, redirect, url_for, Blueprint, render_template, jsonify

tokens_bp = Blueprint("tokens", __name__)


@tokens_bp.route("/tokens")
async def open_tokens():
    all_tokens = await db.get_all_tokens()

    return render_template("tokens.html", tokens=all_tokens)


@tokens_bp.route("/delete-token", methods=["POST"])
async def delete_token():
    token_id = request.form.get("token_id")

    if token_id:
        await db.delete_token(int(token_id))

    return redirect(url_for("tokens.open_tokens"))


@tokens_bp.route("/create-token", methods=["POST"])
async def create_token():
    token_key = request.form.get("token_key")

    if token_key:
        await db.create_token(name=token_key)

    return redirect(url_for("tokens.open_tokens"))


@tokens_bp.route("/create_token_bot", methods=["POST"])
async def create_token_bot():
    task_data = request.json
    token_name = task_data.get("token_name")

    if token_name:
        new_token = await db.create_token(name=token_name)

        return jsonify({"token": new_token}), 200
