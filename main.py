import asyncio
from flask import Flask
from routes import register_blueprints
from database.db import db

app = Flask(__name__, template_folder="frontend", static_folder="frontend/static")
app.secret_key = "super_secret_value_123"
register_blueprints(app)


async def main():
    await db.init_models()
    app.run(host="0.0.0.0", port=5555, debug=True)


if __name__ == "__main__":
    asyncio.run(main())
