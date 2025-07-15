import asyncio
import json
import os
import re
from pyrogram import Client, raw


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


# if __name__ == "__main__":
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
