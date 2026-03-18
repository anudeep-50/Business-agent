import os
import asyncio
import threading
from flask import Flask
from bot import app  # your ApplicationBuilder().token(...).build()

flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Telegram Business Agent is running!"

async def main():
    # Run the Telegram bot in the main asyncio loop
    await app.run_polling()

if __name__ == "__main__":
    # Run Flask in a background thread
    threading.Thread(
        target=lambda: flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000))),
        daemon=True
    ).start()

    # Run the bot
    asyncio.run(main())
