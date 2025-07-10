import asyncio
import json
import os
from pyrogram import Client
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


async def main():
    print(
        await check_session_with_config(
            "pyro_funcs/178166173", "pyro_funcs/178166173.json"
        )
    )


# if __name__ == "__main__":
#     print(os.listdir("pyro_funcs/"))
#     asyncio.run(main())
