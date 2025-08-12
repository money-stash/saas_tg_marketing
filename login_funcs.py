import os
import re
import csv
import json
import random
import aiofiles
import asyncio
from datetime import datetime

from pyrogram import Client, raw
from pyrogram.errors import SessionRevoked
from pyrogram.raw.functions.messages import ImportChatInvite
from pyrogram.raw.types import (
    InputPrivacyKeyStatusTimestamp,
    InputPrivacyKeyPhoneNumber,
    InputPrivacyKeyProfilePhoto,
    InputPrivacyKeyForwards,
    InputPrivacyKeyPhoneCall,
    InputPrivacyKeyVoiceMessages,
    InputPrivacyKeyChatInvite,
)

from pyrogram.errors import ChatWriteForbidden, UserNotParticipant, FloodWait
from pyrogram.raw.functions.account import GetPrivacy

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

        if new_username.strip().lower() == "none":
            new_username = None

        async with client:
            try:
                result = await client.set_username(new_username)
                return result
            except Exception as e:
                print("Ошибка при смене username:", e)
                return False
    except Exception as e:
        print("Ошибка при открытии или обработке файла:", e)
        return False


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


async def change_bio(session_path: str, json_path: str, new_bio: str) -> bool:
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
                await client.update_profile(bio=new_bio)
                return True
            except Exception as e:
                print("Ошибка при обновлении био:", e)
                return False
    except Exception as e:
        print("Ошибка при изменении био:", e)


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
                chat = await client.get_chat(user.id)
                bio = chat.bio or ""
            except:
                bio = ""

            keys_map = {
                "phone_number": InputPrivacyKeyPhoneNumber(),
                "last_seen": InputPrivacyKeyStatusTimestamp(),
                "profile_photo": InputPrivacyKeyProfilePhoto(),
                "message_forwards": InputPrivacyKeyForwards(),
                "calls": InputPrivacyKeyPhoneCall(),
                "voice_messages": InputPrivacyKeyVoiceMessages(),
                "chat_invites": InputPrivacyKeyChatInvite(),
            }

            result = {
                "first_name": user.first_name or "",
                "last_name": user.last_name or "",
                "username": user.username or False,
                "bio": bio,
            }

            for field, key in keys_map.items():
                try:
                    privacy_rules = await client.invoke(GetPrivacy(key=key))
                    rules = privacy_rules.rules

                    # Используем правильные типы из ответа API
                    result[field] = any(
                        isinstance(r, raw.types.PrivacyValueAllowAll) for r in rules
                    )
                except Exception as e:
                    print(f"Ошибка при получении {field}: {e}")
                    result[field] = False

            return result

    except Exception as e:
        print("Ошибка при получении информации о сессии:", e)
        return {}


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


async def try_random_session_join_channel(
    channel_link: str, sessions_dir: str = "sessions"
) -> tuple[bool, str | None]:
    try:
        print("Поиск доступных сессий...")
        all_sessions = [
            f
            for f in os.listdir(sessions_dir)
            if not f.endswith(".json") and os.path.isfile(os.path.join(sessions_dir, f))
        ]

        if not all_sessions:
            print("Сессии не найдены.")
            return False, None

        selected = random.choice(all_sessions)
        session_id = os.path.splitext(selected)[0]
        print(f"Выбрана сессия: {session_id}")
        session_path = os.path.join(sessions_dir, session_id)
        json_path = os.path.join(sessions_dir, session_id + ".json")

        if not os.path.exists(json_path):
            print(f"JSON-файл не найден для: {selected}")
            return False, None

        with open(json_path, "r") as f:
            config = json.load(f)

        client = Client(
            name=os.path.basename(session_path),
            workdir=os.path.dirname(session_path),
            api_id=config["app_id"],
            api_hash=config["app_hash"],
        )

        print(f"Попытка подписки на канал: {channel_link}")
        async with client:
            # Определяем тип ссылки и обрабатываем соответственно
            is_invite_link = False
            join_target = channel_link

            if "t.me/+" in channel_link:
                # Это ссылка-приглашение
                is_invite_link = True
                join_target = channel_link
            elif "t.me/" in channel_link:
                # Это обычная ссылка с username
                join_target = channel_link.split("t.me/")[-1]
                if join_target.startswith("@"):
                    join_target = join_target[1:]  # Убираем @ если есть
            else:
                # Передан просто username (возможно с @)
                if join_target.startswith("@"):
                    join_target = join_target[1:]  # Убираем @ если есть

            try:
                if is_invite_link:
                    # Для ссылок-приглашений используем join_chat с полной ссылкой
                    chat = await client.join_chat(join_target)
                else:
                    # Для username используем join_chat с очищенным именем
                    chat = await client.join_chat(join_target)

            except Exception as e:
                if "CHANNELS_TOO_MUCH" in str(e):
                    print("Слишком много каналов, пытаемся покинуть несколько...")
                    dialogs = []
                    async for dialog in client.get_dialogs():
                        dialogs.append(dialog)

                    # Покидаем первые 5 каналов/чатов
                    for dialog in dialogs[:5]:
                        try:
                            await client.leave_chat(dialog.chat.id)
                            print(f"Покинул чат: {dialog.chat.title or dialog.chat.id}")
                            await asyncio.sleep(random.uniform(1, 3))
                        except Exception as leave_e:
                            print(f"Не удалось покинуть чат: {leave_e}")

                    # Повторная попытка подписки
                    try:
                        if is_invite_link:
                            chat = await client.join_chat(join_target)
                        else:
                            chat = await client.join_chat(join_target)
                    except Exception as retry_e:
                        print(f"Ошибка повторной попытки подписки: {retry_e}")
                        return False, None

                elif "USERNAME_INVALID" in str(e):
                    print(f"Неверный username или недоступная ссылка: {join_target}")
                    return False, None
                elif "INVITE_HASH_EXPIRED" in str(e):
                    print("Ссылка-приглашение истекла")
                    return False, None
                elif "USER_ALREADY_PARTICIPANT" in str(e):
                    print("Пользователь уже участник канала")
                    # Получаем информацию о канале для возврата названия
                    try:
                        if is_invite_link:
                            # Для invite links нужно как-то получить информацию о канале
                            # Попробуем через get_chat, но это может не сработать
                            return True, "Канал (уже участник)"
                        else:
                            chat = await client.get_chat(join_target)
                            return True, chat.title or chat.first_name or str(chat.id)
                    except:
                        return True, "Канал (уже участник)"
                else:
                    print(f"Ошибка при подписке случайной сессией: {e}")
                    return False, None

            print(f"Успешно подписались на канал: {chat.title}")
            return True, chat.title

    except Exception as e:
        print(f"Общая ошибка при подписке случайной сессией: {e}")
        return False, None


async def run_commenting_loop(sessions_dir: str = "sessions"):
    while True:
        try:
            all_links = await db.get_all_channel_links()
            all_sessions = [
                f
                for f in os.listdir(sessions_dir)
                if not f.endswith(".json")
                and os.path.isfile(os.path.join(sessions_dir, f))
            ]

            for link in all_links:
                if not link.active or link.spam_text == "False":
                    continue

                if not os.path.exists(link.spam_text):
                    print(f"Файл {link.spam_text} не найден для link_id={link.id}")
                    continue

                async with aiofiles.open(link.spam_text, "r", encoding="utf-8") as f:
                    lines = await f.readlines()
                    spam_lines = [line.strip() for line in lines if line.strip()]
                    if not spam_lines:
                        print(f"Файл spam_text пустой для link_id={link.id}")
                        continue

                for session_file in all_sessions:
                    session_id = os.path.splitext(session_file)[0]
                    session_path = os.path.join(sessions_dir, session_id)
                    json_path = os.path.join(sessions_dir, session_id + ".json")

                    if not os.path.exists(json_path):
                        print(f"JSON-файл не найден для: {session_id}")
                        continue

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
                                is_invite = "/+" in link.link or "t.me/+" in link.link
                                print(f"Попытка подписки на канал: {link.link}")

                                if is_invite:
                                    invite_hash = link.link.split("+")[-1]
                                    try:
                                        await client.invoke(
                                            ImportChatInvite(hash=invite_hash)
                                        )
                                        print(
                                            f"Успешно попписались на канал: {link.link}"
                                        )
                                    except Exception as e:
                                        if "USER_ALREADY_PARTICIPANT" in str(e):
                                            print(
                                                f"Уже подписаны на канал: {link.link}"
                                            )
                                        elif "CHANNELS_TOO_MUCH" in str(e):
                                            print(
                                                "Слишком много каналов, пытаемся покинуть несколько.."
                                            )
                                            dialogs = [
                                                d async for d in client.get_dialogs()
                                            ]
                                            to_leave = dialogs[: random.randint(3, 5)]
                                            for d in to_leave:
                                                try:
                                                    title = getattr(
                                                        d.chat, "title", "unknown"
                                                    )
                                                    await client.leave_chat(d.chat.id)
                                                    print(f"Покинул чат: {title}")
                                                    await asyncio.sleep(
                                                        random.uniform(1, 2)
                                                    )
                                                except Exception as leave_e:
                                                    print(
                                                        f"Не удалось покинуть чат: {leave_e}"
                                                    )
                                            try:
                                                await client.invoke(
                                                    ImportChatInvite(hash=invite_hash)
                                                )
                                                print(
                                                    f"Успешно попписались на канал: {link.link}"
                                                )
                                            except Exception as retry_e:
                                                if "USER_ALREADY_PARTICIPANT" in str(
                                                    retry_e
                                                ):
                                                    print(
                                                        f"Уже подписаны на канал: {link.link}"
                                                    )
                                                else:
                                                    print(
                                                        f"Повторная ошибка при подписке на канал {link.link}: {retry_e}"
                                                    )
                                                    continue
                                        else:
                                            print(
                                                f"Ошибка при подписке на канал {link.link}: {e}"
                                            )
                                            continue
                                    chat = await client.get_chat(link.link)
                                else:
                                    try:
                                        await client.join_chat(link.link)
                                        print(
                                            f"Успешно попписались на канал: {link.link}"
                                        )
                                    except Exception as e:
                                        if "CHANNELS_TOO_MUCH" in str(e):
                                            print(
                                                "Слишком много каналов, пытаемся покинуть несколько.."
                                            )
                                            dialogs = [
                                                d async for d in client.get_dialogs()
                                            ]
                                            to_leave = dialogs[: random.randint(3, 5)]
                                            for d in to_leave:
                                                try:
                                                    title = getattr(
                                                        d.chat, "title", "unknown"
                                                    )
                                                    await client.leave_chat(d.chat.id)
                                                    print(f"Покинул чат: {title}")
                                                    await asyncio.sleep(
                                                        random.uniform(1, 2)
                                                    )
                                                except Exception as leave_e:
                                                    print(
                                                        f"Не удалось покинуть чат: {leave_e}"
                                                    )
                                            try:
                                                await client.join_chat(link.link)
                                                print(
                                                    f"Успешно попписались на канал: {link.link}"
                                                )
                                            except Exception as retry_e:
                                                print(
                                                    f"Повторная ошибка при подписке на канал {link.link}: {retry_e}"
                                                )
                                                continue
                                        elif "USER_ALREADY_PARTICIPANT" in str(e):
                                            print(
                                                f"Уже подписаны на канал: {link.link}"
                                            )
                                        else:
                                            print(f"Ошибка при подписке на канал: {e}")
                                            continue
                                    chat = await client.get_chat(link.link)

                                if not chat.linked_chat:
                                    print(
                                        f"У канала {link.link} нет обсуждаемой группы"
                                    )
                                    continue

                                try:
                                    history = [
                                        m
                                        async for m in client.get_chat_history(
                                            chat.id, limit=1
                                        )
                                    ]
                                    if not history:
                                        print(f"В канале {link.link} нет постов")
                                        continue
                                    last_post = history[0]
                                except Exception as e:
                                    print(
                                        f"Не удалось получить последний пост канала {link.link}: {e}"
                                    )
                                    continue

                                try:
                                    discussion_msg = (
                                        await client.get_discussion_message(
                                            chat.id, last_post.id
                                        )
                                    )
                                except Exception as e:
                                    print(
                                        f"Не удалось получить тред для поста {last_post.id} канала {link.link}: {e}"
                                    )
                                    continue

                                comment = random.choice(spam_lines)

                                try:
                                    await discussion_msg.reply(comment)
                                    print(
                                        f"Сессия {session_id} оставила комментарий к последнему посту {last_post.id} в канале {link.link}"
                                    )
                                except (ChatWriteForbidden, UserNotParticipant) as e:
                                    try:
                                        await client.join_chat(discussion_msg.chat.id)
                                        await asyncio.sleep(random.uniform(1.5, 3.0))
                                        await discussion_msg.reply(comment)
                                        print(
                                            f"Сессия {session_id} оставила комментарий после подписки на обсуждаемую группу {discussion_msg.chat.id}"
                                        )
                                    except Exception as e2:
                                        print(
                                            f"Не удалось оставить комментарий после подписки: {e2}"
                                        )
                                except FloodWait as fw:
                                    print(
                                        f"FloodWait {fw.value}s на сессии {session_id}"
                                    )
                                    await asyncio.sleep(fw.value + 1)
                                except Exception as e:
                                    if "USER_NOT_PARTICIPANT" in str(
                                        e
                                    ) or "CHAT_WRITE_FORBIDDEN" in str(e):
                                        try:
                                            await client.join_chat(
                                                discussion_msg.chat.id
                                            )
                                            await asyncio.sleep(
                                                random.uniform(1.5, 3.0)
                                            )
                                            await discussion_msg.reply(comment)
                                            print(
                                                f"Сессия {session_id} оставила комментарий после подписки на обсуждаемую группу {discussion_msg.chat.id}"
                                            )
                                        except Exception as e2:
                                            print(
                                                f"Не удалось оставить комментарий после подписки: {e2}"
                                            )
                                    else:
                                        print(f"Ошибка при отправке комментария: {e}")

                            except Exception as e:
                                print(
                                    f"Ошибка при работе с каналом {link.link} через сессию {session_id}: {e}"
                                )

                        print(f"Сессия {session_id} закрыта после отправки комментария")

                        session_delay = random.uniform(30, 90)
                        print(
                            f"Задержка {session_delay:.1f} сек перед следующей сессией..."
                        )
                        await asyncio.sleep(session_delay)

                    except Exception as e:
                        print(f"Ошибка запуска клиента для сессии {session_id}: {e}")
                        await asyncio.sleep(random.uniform(10, 30))

            sleep_minutes = random.randint(5, 15)
            print(f"Цикл завершён. Сон {sleep_minutes} минут...")
            await asyncio.sleep(sleep_minutes * 60)

        except Exception as e:
            print(f"Ошибка в основном цикле run_commenting_loop: {e}")
            await asyncio.sleep(60)


async def hide_profile_photo(session_path: str, json_path: str) -> bool:
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
            await client.invoke(
                raw.functions.account.SetPrivacy(
                    key=raw.types.InputPrivacyKeyProfilePhoto(),
                    rules=[raw.types.InputPrivacyValueDisallowAll()],
                )
            )
            return True
    except Exception as e:
        print("Ошибка при скрытии аватарки:", e)
        return False


async def open_profile_photo(session_path: str, json_path: str) -> bool:
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
            await client.invoke(
                raw.functions.account.SetPrivacy(
                    key=raw.types.InputPrivacyKeyProfilePhoto(),
                    rules=[raw.types.InputPrivacyValueAllowAll()],
                )
            )
            return True
    except Exception as e:
        print("Ошибка при открытии доступа к аватарке:", e)
        return False


async def set_privacy_closed(
    session_path: str, json_path: str, privacy_key_name: str
) -> bool:
    privacy_keys = {
        "phone_number": raw.types.InputPrivacyKeyPhoneNumber,
        "last_seen": raw.types.InputPrivacyKeyStatusTimestamp,
        "profile_photo": raw.types.InputPrivacyKeyProfilePhoto,
        "message_forwards": raw.types.InputPrivacyKeyForwards,
        "calls": raw.types.InputPrivacyKeyPhoneCall,
        "voice_messages": raw.types.InputPrivacyKeyVoiceMessages,
        "messages": raw.types.InputPrivacyKeyPhoneP2P,
        "chat_invites": raw.types.InputPrivacyKeyChatInvite,
    }

    if privacy_key_name not in privacy_keys:
        print(f"Недопустимый ключ конфиденциальности: {privacy_key_name}")
        return False

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
            key_instance = privacy_keys[privacy_key_name]()
            await client.invoke(
                raw.functions.account.SetPrivacy(
                    key=key_instance,
                    rules=[raw.types.InputPrivacyValueDisallowAll()],
                )
            )
            return True
    except Exception as e:
        print(f"Ошибка при закрытии параметра {privacy_key_name}:", e)
        return False


async def set_privacy_opened(
    session_path: str, json_path: str, privacy_key_name: str
) -> bool:
    privacy_keys = {
        "phone_number": raw.types.InputPrivacyKeyPhoneNumber,
        "last_seen": raw.types.InputPrivacyKeyStatusTimestamp,
        "profile_photo": raw.types.InputPrivacyKeyProfilePhoto,
        "message_forwards": raw.types.InputPrivacyKeyForwards,
        "calls": raw.types.InputPrivacyKeyPhoneCall,
        "voice_messages": raw.types.InputPrivacyKeyVoiceMessages,
        "messages": raw.types.InputPrivacyKeyPhoneP2P,
        "chat_invites": raw.types.InputPrivacyKeyChatInvite,
    }

    if privacy_key_name not in privacy_keys:
        print(f"Недопустимый ключ конфиденциальности: {privacy_key_name}")
        return False

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
            key_instance = privacy_keys[privacy_key_name]()
            await client.invoke(
                raw.functions.account.SetPrivacy(
                    key=key_instance,
                    rules=[raw.types.InputPrivacyValueAllowAll()],
                )
            )
            return True
    except Exception as e:
        print(f"Ошибка при открытии параметра {privacy_key_name}:", e)
        return False


async def main():
    await hide_profile_photo(
        session_path="sessions/130256930", json_path="sessions/130256930.json"
    )


# if __name__ == "__main__":
#     asyncio.run(main())
