import asyncio
import json
import os
from pyrogram import Client
import pyrogram
from pyrogram.errors import RPCError


async def check_session_with_config(session_path: str, json_path: str):
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
            # Проверяем через get_me()
            me = await client.get_me()
            if not me:
                print("SESSION IS DEAD")
                return False
            return me.id

    except RPCError as e:
        print("RPC error:", e)
        return False
    except Exception as ex:
        print("Error:", ex)
        return False


async def print_session_info(session_path: str, json_path: str):
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
            print(f"Имя: {me.first_name}")
            print(f"Фамилия: {me.last_name if me.last_name else 'Нет'}")
            print(f"Юзернейм: @{me.username if me.username else 'Нет'}")

            # Аватарка
            photos = await client.get_profile_photos("me", limit=1)
            if photos.total_count > 0:
                photo = photos.photos[0]
                file_path = await client.download_media(
                    photo, file_name=f"{me.id}_avatar.jpg"
                )
                print(f"Аватарка скачана: {file_path}")

            else:
                print("Аватарка отсутствует")
                # Параметры конфиденциальности
                privacy_settings = await client.invoke(
                    pyrogram.raw.functions.account.GetPrivacy(
                        key=pyrogram.raw.types.InputPrivacyKeyStatusTimestamp()
                    )
                )
                print("Параметры конфиденциальности:")
                print(privacy_settings)

    except Exception as ex:
        print("Ошибка:", ex)


async def main():
    print(
        await check_session_with_config(
            "pyro_funcs/178166173", "pyro_funcs/178166173.json"
        )
    )


# if __name__ == "__main__":
#     print(os.listdir("pyro_funcs/"))
#     asyncio.run(main())
