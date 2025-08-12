import os
import json
import asyncio
from pyrogram import Client


def _normalize_channel_id(channel_id):
    if isinstance(channel_id, int):
        return (
            channel_id
            if str(channel_id).startswith("-100")
            else int(f"-100{channel_id}")
        )
    if isinstance(channel_id, str):
        s = channel_id.strip()
        if s.startswith("-100") and s[4:].isdigit():
            return int(s)
        if s.isdigit():
            return int(f"-100{s}")
        return s
    return channel_id


async def comment_last_post(
    channel_id, session_path: str, json_path: str, text: str
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

        chan = _normalize_channel_id(channel_id)

        async with client:
            try:
                await client.join_chat(chan)
            except Exception:
                pass

            chat = await client.get_chat(chan)

            async for m in client.get_chat_history(chat.id, limit=1):
                last_post = m
                break
            else:
                return False

            linked = getattr(chat, "linked_chat", None)
            if not linked:
                return False

            try:
                await client.join_chat(linked.id)
            except Exception:
                pass

            await asyncio.sleep(2)

            await client.send_message(
                chat_id=linked.id, text=text, message_thread_id=last_post.id
            )
            return True
    except Exception as e:
        print("comment_last_post error:", e)
        return False


async def main():
    channel_id = -1002378196415
    session_path = "sessions/126143775"
    json_path = "sessions/126143775.json"
    text = "Your comment text here"

    success = await comment_last_post(channel_id, session_path, json_path, text)
    if success:
        print("Comment posted successfully.")
    else:
        print("Failed to post comment.")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
