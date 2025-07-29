import os

from database.db import db

from flask import Blueprint, jsonify, request
from login_funcs import try_random_session_join_channel

links_bp = Blueprint("links", __name__)


@links_bp.route("/links", methods=["GET"])
async def get_links():
    all_links = await db.get_all_channel_links()

    links_data = []
    for link in all_links:
        links_data.append(
            {
                "id": link.id,
                "link": link.link,
                "spam_text": link.spam_text,
                "link_name": link.link_name,
                "active": link.active,
            }
        )

    return jsonify({"links": links_data})


@links_bp.route("/delete-link/<int:link_id>", methods=["POST"])
async def delete_link():
    link_id = request.form.get("link_id", type=int)
    link_info = await db.get_channel_link_by_id(link_id)

    if not link_info:
        return jsonify({"error": "Link not found"}), 404

    await db.delete_channel_link_by_id(link_id)

    return jsonify({"success": True})


@links_bp.route("/add-link", methods=["POST"])
async def add_link():
    link = request.form.get("link")
    link_name = request.form.get("link_name", "")
    spam_text = request.form.get("spam_text")

    if not link or not spam_text:
        return jsonify({"error": "Link and spam text are required"}), 400

    await db.add_channel_link(link, spam_text, link_name)

    return jsonify({"message": "Link added successfully"})


@links_bp.route("/get-link", methods=["POST"])
async def get_link():
    link_id = request.form.get("link_id", type=int)
    link_info = await db.get_channel_link_by_id(link_id)

    if not link_info:
        return jsonify({"error": "Link not found"}), 404

    return jsonify(
        {
            "id": link_info.id,
            "link": link_info.link,
            "spam_text": link_info.spam_text,
            "link_name": link_info.link_name,
            "active": link_info.active,
        }
    )


@links_bp.route("/check-link", methods=["POST"])
async def check_link():
    link = request.form.get("link")

    if not link:
        return jsonify({"error": "Link is required"}), 400

    is_exists = await try_random_session_join_channel(link)

    return jsonify({"exists": is_exists})


@links_bp.route("/upload-file", methods=["POST"])
async def upload_file():
    file = request.files.get("file")
    link_id = request.form.get("link_id", type=int)
    link_info = await db.get_channel_link_by_id(link_id)

    try:
        os.remove(link_info.spam_text)
    except Exception as e:
        print(f"Ошибка при удалении файла: {e}")

    if not file or not file.filename.endswith(".txt") or not link_id:
        return jsonify({"success": False, "error": "Invalid file or link ID"}), 400

    save_path = os.path.join("database", file.filename)
    try:
        file.save(save_path)
        await db.update_channel_link_text(link_id, save_path)
        return jsonify({"success": True})
    except Exception as e:
        print(f"Ошибка при сохранении файла или обновлении текста: {e}")
        return jsonify({"success": False}), 500


@links_bp.route("/update-status", methods=["POST"])
async def update_status():
    link_id = request.form.get("link_id", type=int)
    status = request.form.get("status", type=str)

    if not link_id:
        return jsonify({"error": "Link ID is required"}), 400

    if status == "True":
        await db.update_channel_link_status(link_id, True)
        return jsonify({"success": True})
    elif status == "False":
        await db.update_channel_link_status(link_id, False)
        return jsonify({"success": True})

    return jsonify({"success": True})
