import asyncio
from flask import Flask
from routes import register_blueprints

from database.db import db


app = Flask(__name__, template_folder="frontend", static_folder="frontend/static")
register_blueprints(app)


async def main():
    await db.init_models()
    app.run(debug=True, port=5555)


if __name__ == "__main__":
    asyncio.run(main())
