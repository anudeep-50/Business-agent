import os
import threading
import asyncio
from flask import Flask
from bot import app  # your ApplicationBuilder().token(...).build()

flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Telegram Business Agent is running!"

if __name__ == "__main__":
    # Run Flask in a background thread for Render health checks
    threading.Thread(
        target=lambda: flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000))),
        daemon=True
    ).start()

    # Explicitly create and set an event loop (needed for Python 3.14+)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Run the Telegram bot
    app.run_polling()
