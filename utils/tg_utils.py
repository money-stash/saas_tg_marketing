import aiohttp
from config import BOT_TOKEN


async def send_message_to_user(user_id: int, text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": user_id, "text": text}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            return await response.json()
