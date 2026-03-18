import os
from flask import Flask
import threading
import bot  # your bot.py

app = Flask(__name__)

@app.route("/")
def home():
    return "Telegram Business Agent is running!"

if __name__ == "__main__":
    # Start the bot in a background thread
    threading.Thread(target=bot.app.run_polling, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
