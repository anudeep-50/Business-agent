from flask import Flask
import bot  # this will start your Telegram bot

app = Flask(__name__)

@app.route("/")
def home():
    return "Telegram Business Agent is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
