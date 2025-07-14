import asyncio
import json
import os
import re
from pyrogram import Client
from pyrogram.enums import ChatType


async def get_full_phone_number(session_path: str, json_path: str) -> str | None:
    try:
        with open(json_path, "r") as f:
            config = json.load(f)

        client = Client(
            name=os.path.basename(session_path),
            workdir=os.path.dirname(session_path),
            api_id=config["app_id"],
            api_hash=config["app_hash"],
        )

        async with client:
            me = await client.get_me()
            return me.phone_number

    except Exception as ex:
        print("Ошибка при получении номера телефона:", ex)
        return None


async def get_login_code(session_path: str, json_path: str):
    try:
        with open(json_path, "r") as f:
            config = json.load(f)

        client = Client(
            name=os.path.basename(session_path),
            workdir=os.path.dirname(session_path),
            api_id=config["app_id"],
            api_hash=config["app_hash"],
        )

        async with client:
            chat_id = 777000
            message = await client.get_chat_history(chat_id, limit=1).__anext__()
            match = re.search(r"(?<!\d)(\d{5,6})(?!\d)", message.text or "")
            if match:
                return match.group(1)
            else:
                return False

    except Exception as ex:
        print("Ошибка:", ex)
        return False


# if __name__ == "__main__":
#     result = asyncio.run(
#         print_last_message_from_telegram(
#             "sessions/178166173", "sessions/178166173.json"
#         )
#     )
#     print(result)
