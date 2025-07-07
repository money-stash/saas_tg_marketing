import asyncio
from database.db import db


async def main():
    await db.init_models()


if __name__ == "__main__":
    asyncio.run(main())
