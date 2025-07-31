import asyncio
import os
import json
from pyrogram import Client
from pyrogram import raw
from pyrogram.raw.types import (
    InputPrivacyKeyStatusTimestamp,
    InputPrivacyKeyPhoneNumber,
    InputPrivacyKeyProfilePhoto,
    InputPrivacyKeyForwards,
    InputPrivacyKeyPhoneCall,
    InputPrivacyKeyVoiceMessages,
    InputPrivacyKeyChatInvite,
)
from pyrogram.raw.functions.account import GetPrivacy


async def get_privacy_settings(session_path: str, json_path: str) -> dict:
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
            keys_map = {
                "phone_number": InputPrivacyKeyPhoneNumber(),
                "last_seen": InputPrivacyKeyStatusTimestamp(),
                "profile_photo": InputPrivacyKeyProfilePhoto(),
                "message_forwards": InputPrivacyKeyForwards(),
                "calls": InputPrivacyKeyPhoneCall(),
                "voice_messages": InputPrivacyKeyVoiceMessages(),
                "chat_invites": InputPrivacyKeyChatInvite(),
            }

            result = {}

            for name, key in keys_map.items():
                try:
                    privacy_rules = await client.invoke(GetPrivacy(key=key))
                    rules = privacy_rules.rules

                    # Проверяем тип правила - используем правильные типы из ответа API
                    is_public = any(
                        isinstance(r, raw.types.PrivacyValueAllowAll) for r in rules
                    )
                    is_restricted = any(
                        isinstance(
                            r,
                            (
                                raw.types.PrivacyValueDisallowAll,
                                raw.types.PrivacyValueDisallowUsers,
                                raw.types.PrivacyValueDisallowChatParticipants,
                            ),
                        )
                        for r in rules
                    )

                    # Если есть AllowAll и нет ограничений - публичный
                    result[name] = is_public and not is_restricted

                except Exception as e:
                    print(f"Ошибка при получении {name}: {e}")
                    result[name] = None  # Не удалось получить

            return result

    except Exception as e:
        print("Ошибка при получении настроек конфиденциальности:", e)
        return {}


async def main():
    session_path = "sessions/130256930"
    json_path = "sessions/130256930.json"

    privacy_settings = await get_privacy_settings(session_path, json_path)
    print("Privacy Settings:", privacy_settings)


if __name__ == "__main__":
    asyncio.run(main())
