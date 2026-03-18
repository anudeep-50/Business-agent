import os
import threading
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

    # Run the Telegram bot (manages its own asyncio loop internally)
    app.run_polling()
