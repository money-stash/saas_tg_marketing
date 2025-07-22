import os
import re
import csv
import json
import random
import asyncio
from datetime import datetime
from pyrogram import Client, raw
from pyrogram.errors import SessionRevoked

from utils.logger import logger
from database.db import db


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


async def change_username(session_path: str, json_path: str, new_username: str) -> bool:
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
            try:
                result = await client.set_username(new_username)
                return result
            except Exception as e:
                print("Ошибка при смене username:", e)
                return False
    except:
        pass


async def change_first_name(
    session_path: str, json_path: str, new_first_name: str
) -> bool:
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
            try:
                await client.update_profile(first_name=new_first_name)
                return True
            except Exception as e:
                print("Ошибка при обновлении имени:", e)
                return False
    except Exception as e:
        print("Ошибка при изменении имени:", e)


async def change_last_name(
    session_path: str, json_path: str, new_last_name: str
) -> bool:
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
            try:
                await client.update_profile(last_name=new_last_name)
                return True
            except Exception as e:
                print("Ошибка при обновлении фамилии:", e)
                return False
    except Exception as e:
        print("Ошибка при изменении фамилии:", e)


async def set_privacy_all_closed(session_path: str, json_path: str) -> bool:
    try:
        with open(json_path, "r") as f:
            cfg = json.load(f)

        client = Client(
            name=os.path.basename(session_path),
            workdir=os.path.dirname(session_path),
            api_id=cfg["app_id"],
            api_hash=cfg["app_hash"],
        )

        async with client:
            try:
                closelist = [raw.types.InputPrivacyValueAllowContacts()]
                disallow = [raw.types.InputPrivacyValueDisallowAll()]
                priv = raw.functions.account.SetPrivacy

                tasks = [
                    priv(
                        key=raw.types.InputPrivacyKeyStatusTimestamp(), rules=closelist
                    ),
                    priv(key=raw.types.InputPrivacyKeyPhoneNumber(), rules=closelist),
                    priv(key=raw.types.InputPrivacyKeyProfilePhoto(), rules=closelist),
                    priv(key=raw.types.InputPrivacyKeyForwards(), rules=disallow),
                    priv(key=raw.types.InputPrivacyKeyPhoneCall(), rules=closelist),
                    priv(key=raw.types.InputPrivacyKeyAddedByPhone(), rules=closelist),
                    priv(key=raw.types.InputPrivacyKeyChatInvite(), rules=disallow),
                    priv(key=raw.types.InputPrivacyKeyVoiceMessages(), rules=closelist),
                    priv(key=raw.types.InputPrivacyKeyPhoneP2P(), rules=closelist),
                ]
                for t in tasks:
                    await client.invoke(t)
                return True
            except Exception as e:
                print("Ошибка закрытия приватности:", e)
                return False
    except Exception as e:
        print("Ошибка при изменении приватности:", e)


async def set_privacy_all_open(session_path: str, json_path: str) -> bool:
    try:
        with open(json_path, "r") as f:
            cfg = json.load(f)

        client = Client(
            name=os.path.basename(session_path),
            workdir=os.path.dirname(session_path),
            api_id=cfg["app_id"],
            api_hash=cfg["app_hash"],
        )

        async with client:
            try:
                openlist = [raw.types.InputPrivacyValueAllowAll()]
                priv = raw.functions.account.SetPrivacy

                keys = [
                    raw.types.InputPrivacyKeyStatusTimestamp(),
                    raw.types.InputPrivacyKeyPhoneNumber(),
                    raw.types.InputPrivacyKeyProfilePhoto(),
                    raw.types.InputPrivacyKeyForwards(),
                    raw.types.InputPrivacyKeyPhoneCall(),
                    raw.types.InputPrivacyKeyAddedByPhone(),
                    raw.types.InputPrivacyKeyChatInvite(),
                    raw.types.InputPrivacyKeyVoiceMessages(),
                    raw.types.InputPrivacyKeyPhoneP2P(),
                ]
                for key in keys:
                    await client.invoke(priv(key=key, rules=openlist))
                return True
            except Exception as e:
                print("Ошибка открытия приватности:", e)
                return False
    except Exception as e:
        print("Ошибка при изменении приватности:", e)


async def update_profile_photo(
    session_path: str, json_path: str, photo_path: str = "images/avatar.jpg"
) -> bool:
    try:
        with open(json_path, "r") as f:
            cfg = json.load(f)

        client = Client(
            name=os.path.basename(session_path),
            workdir=os.path.dirname(session_path),
            api_id=cfg["app_id"],
            api_hash=cfg["app_hash"],
        )

        async with client:
            try:
                result = await client.set_profile_photo(photo=photo_path)
                return result

            except Exception as e:
                print("Ошибка при обновлении фото профиля:", e)
                return False

    except Exception as e:
        print("Ошибка при обновлении фото профиля:", e)
        pass


async def download_profile_photo(
    session_path: str, json_path: str, images_dir: str = "images"
) -> bool:
    try:
        os.makedirs(images_dir, exist_ok=True)

        with open(json_path, "r") as f:
            cfg = json.load(f)

        client = Client(
            name=os.path.basename(session_path),
            workdir=os.path.dirname(session_path),
            api_id=cfg["app_id"],
            api_hash=cfg["app_hash"],
        )

        async with client:
            async for photo in client.get_chat_photos("me", limit=1):
                session_name = os.path.basename(session_path)
                dest = f"frontend/static/{images_dir}/{session_name}.jpg"

                await client.download_media(photo, file_name=dest)

                return True
            return False
    except Exception as e:
        print("Ошибка при скачивании фото профиля:", e)
        pass


async def get_session_info(session_path: str, json_path: str) -> dict:
    try:
        with open(json_path, "r") as f:
            cfg = json.load(f)

        client = Client(
            name=os.path.basename(session_path),
            workdir=os.path.dirname(session_path),
            api_id=cfg["app_id"],
            api_hash=cfg["app_hash"],
        )

        async with client:
            user = await client.get_me()

            try:
                privacy = await client.invoke(
                    raw.functions.account.GetPrivacy(
                        key=raw.types.InputPrivacyKeyProfilePhoto()
                    )
                )

                rules = privacy.rules
                is_open = any(
                    isinstance(rule, raw.types.InputPrivacyValueAllowAll)
                    for rule in rules
                )
            except Exception:
                is_open = False
                rules = None

            return {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username if user.username else False,
                "is_private": not is_open if rules else False,
            }
    except Exception as e:
        print("Ошибка при получении информации о сессии:", e)


async def join_and_parse_group(
    group_username: str,
    session_path: str,
    json_path: str,
    message_limit: int,
    user_id: int,
):
    added_task = await db.add_task(task_type="parse", status=True, logs="text.txt")
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
            try:
                await client.join_chat(group_username)
            except Exception as e:
                print("Ошибка при вступлении в группу:", e)
            users = {}
            fetched = 0
            batch_size = 50
            offset_id = 0

            os.makedirs("work_reports", exist_ok=True)
            out_path = os.path.join(
                "work_reports", f"{random.randint(100000,1000000)}_group_users.csv"
            )
            f = open(out_path, "a", encoding="utf-8", newline="")
            writer = csv.writer(f)
            if os.stat(out_path).st_size == 0:
                writer.writerow(["user_id", "first_name", "last_name", "username"])

            try:
                while fetched < message_limit:
                    limit = min(batch_size, message_limit - fetched)
                    async for message in client.get_chat_history(
                        group_username, limit=limit, offset_id=offset_id
                    ):
                        offset_id = message.id
                        user = message.from_user
                        if user and user.id not in users:
                            users[user.id] = {
                                "id": user.id,
                                "first_name": user.first_name or "",
                                "last_name": user.last_name or "",
                                "username": user.username if user.username else "None",
                            }
                            writer.writerow(
                                [
                                    user.id,
                                    user.first_name or "",
                                    user.last_name or "",
                                    user.username or "None",
                                ]
                            )
                            f.flush()
                        fetched += 1
                    await asyncio.sleep(random.uniform(5.0, 20.0))
                    logger.info(
                        f"Parsed {fetched} messages, total unique users: {len(users)}"
                    )

                    await db.delete_task(added_task)

            except SessionRevoked:
                await db.delete_task(added_task)
                logger.error("Сессия недействительна / отозвана")
                return 0

            except:
                await db.delete_task(added_task)

            finally:
                f.close()

            await db.add_report(
                date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                worker_id=user_id,
                path=out_path,
                type_="parse",
            )

            return len(users)

    except Exception as e:
        print("Ошибка:", e)
        return False


async def send_message_from_session(session_path, json_path, username, text) -> bool:
    try:
        with open(json_path) as f:
            cfg = json.load(f)

        client = Client(
            name=os.path.basename(session_path),
            workdir=os.path.dirname(session_path),
            api_id=cfg["app_id"],
            api_hash=cfg["app_hash"],
        )

        async with client:
            async for _ in client.get_dialogs(limit=200):
                pass

            await client.send_message(chat_id=username, text=text)
            return True

    except Exception as e:
        print("Ошибка при отправке сообщения:", e)
        return False


async def print_last_messages(
    session_path: str, json_path: str, messages_count: int = 5
):
    try:
        with open(json_path, "r") as f:
            cfg = json.load(f)

        client = Client(
            name=os.path.basename(session_path),
            workdir=os.path.dirname(session_path),
            api_id=cfg["app_id"],
            api_hash=cfg["app_hash"],
        )

        async with client:
            async for dialog in client.get_dialogs():
                title = (
                    getattr(dialog.chat, "title", None)
                    or getattr(dialog.chat, "first_name", None)
                    or str(dialog.chat.id)
                )
                print(f"\n--- Диалог: {title} ---")
                async for msg in client.get_chat_history(
                    dialog.chat.id, limit=messages_count
                ):
                    sender = msg.from_user.first_name if msg.from_user else "Unknown"
                    print(f"[{msg.date}] {sender}: {msg.text}")
    except Exception as e:
        print("Ошибка при получении сообщений:", e)


# if __name__ == "__main__":
#     result = asyncio.run(
#         print_last_messages(
#             session_path="sessions/179781882",
#             json_path="sessions/179781882.json",
#         )
#     )
#     print("Результат:", result)

#     # result = asyncio.run(
#     #     change_username("sessions/179279285", "sessions/179279285.json", "kilohilo13")
#     # )
#     # # result = asyncio.run(
#     # #     get_full_phone_number("sessions/179279285", "sessions/179279285.json")
#     # # )
#     # print(result)

#     # ok_photo = asyncio.run(
#     #     update_profile_photo("sessions/179279285", "sessions/179279285.json")
#     # )
#     # print("Фото обновлено:", ok_photo)

#     # ok1 = asyncio.run(
#     #     set_privacy_all_closed("sessions/179279285", "sessions/179279285.json")
#     # )
#     # print("Закрыта ли приватность:", ok1)

#     # ok2 = asyncio.run(
#     #     set_privacy_all_open("sessions/179279285", "sessions/179279285.json")
#     # )
#     # print("Открыта ли приватность:", ok2)

#     # result = asyncio.run(
#     #     download_profile_photo("sessions/179279285", "sessions/179279285.json")
#     # )
#     # print("Скачано:", result)

#     result = asyncio.run(
#         get_session_info("sessions/179278979", "sessions/179278979.json")
#     )
#     print("Скачано:", result)
