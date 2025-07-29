import asyncio
from flask import Flask
from routes import register_blueprints
from database.db import db
from login_funcs import run_commenting_loop

from threading import Thread

app = Flask(__name__, template_folder="frontend", static_folder="frontend/static")
app.secret_key = "super_secret_value_123"
register_blueprints(app)


def run_flask():
    app.run(host="0.0.0.0", port=5555, debug=False, use_reloader=False)


async def main():
    await db.init_models()

    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    await run_commenting_loop()


if __name__ == "__main__":
    asyncio.run(main())
