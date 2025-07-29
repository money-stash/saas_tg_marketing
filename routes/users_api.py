import os

from database.db import db

from flask import Blueprint, jsonify, request

users_bp = Blueprint("users", __name__)


@users_bp.route("/users")
async def get_users():
    all_users = await db.get_users()

    users_data = []
    for user in all_users:
        users_data.append(
            {
                "id": user.id,
                "username": user.username,
                "status": user.status,
                "role": user.status,
                "key_id": user.key_id,
                "user_id": user.user_id,
            }
        )

    return jsonify({"users": users_data})


@users_bp.route("/add-user", methods=["POST"])
async def add_user():
    user_id = request.form.get("user_id")
    username = request.form.get("username")
    key = request.form.get("key")

    await db.create_worker(username, user_id=user_id)
    await db.bind_user_to_token(user_id, username, key)

    return jsonify({"status": "ok"})


@users_bp.route("/update-user-login", methods=["POST"])
async def update_add_user():
    user_id = request.form.get("user_id")
    username = request.form.get("username")
    key = request.form.get("key")

    await db.bind_user_to_token(user_id, username, key)

    return jsonify({"status": "ok"})


@users_bp.route("/get_key_info", methods=["POST"])
async def get_key_info():
    key = request.form.get("key")
    key_info = await db.get_token_by_key(key)

    if key_info:
        key_data = {
            "id": key_info.id,
            "key": key_info.key,
            "name": key_info.name,
            "user_id": key_info.user_id,
        }

        return jsonify({"key_info": key_data})
    else:
        return jsonify({"key_info": False})
