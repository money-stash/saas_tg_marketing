from flask import Flask, render_template
import asyncio
from database.db import db

app = Flask(__name__, template_folder="frontend", static_folder="frontend/static")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/workers")
def open_workers():
    return render_template("workers.html")


@app.route("/tokens")
def open_tokens():
    return render_template("tokens.html")


@app.route("/sessions")
def open_sessions():
    return render_template("sessions.html")


@app.route("/newsletter")
def open_newsletter():
    return render_template("newsletter.html")


async def main():
    await db.init_models()
    app.run(debug=True)


if __name__ == "__main__":
    asyncio.run(main())
