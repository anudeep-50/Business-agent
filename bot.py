import os
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from orchestrator import run_deliberation, run_daily_memo, run_research, handle_pushback
from database import fetch_all, insert
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

app = ApplicationBuilder().token(TOKEN).build()

# --- Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "👋 Welcome to the Business Agent Bot!\n\n"
        "Here are the available commands:\n"
        "/deliberate - Run founders' deliberation\n"
        "/memo - Get today's task or log a report\n"
        "/research <topic> - Research a topic\n"
        "/problem <text> - Log a pushback/issue\n"
        "/lesson <text> - Store a lesson\n"
        "/status - Show company status\n"
    )
    await update.message.reply_text(message)

async def deliberate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = run_deliberation()
    await update.message.reply_text(f"Founders deliberated:\n{result}")

async def memo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        report = " ".join(context.args)
        insert("task_log", task="", report=report, outcome="")
        result = run_daily_memo()
        await update.message.reply_text(f"Next task:\n{result}")
    else:
        result = run_daily_memo()
        await update.message.reply_text(f"Today's task:\n{result}")

async def research(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = " ".join(context.args)
    result = run_research(topic)
    await update.message.reply_text(f"Research results:\n{result}")

async def problem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    result = handle_pushback(text)
    await update.message.reply_text(result)

async def lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    insert("lessons", text=text)
    await update.message.reply_text("Lesson stored.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tables = ["company", "goals", "task_log", "lessons", "scratchpad"]
    output = ""
    for t in tables:
        rows = fetch_all(t)
        output += f"{t}:\n{rows}\n\n"
    await update.message.reply_text(output)

# --- Register handlers ---
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("deliberate", deliberate))
app.add_handler(CommandHandler("memo", memo))
app.add_handler(CommandHandler("research", research))
app.add_handler(CommandHandler("problem", problem))
app.add_handler(CommandHandler("lesson", lesson))
app.add_handler(CommandHandler("status", status))

# --- Startup greeting only ---
if __name__ == "__main__":
    print("Starting Telegram bot...")

    # Send a greeting when the bot boots up
    bot = Bot(token=TOKEN)
    chat_id = int(os.getenv("TELEGRAM_CHAT_ID", "0"))  # set your chat ID in Render env vars
    if chat_id != 0:
        bot.send_message(
            chat_id=chat_id,
            text=(
                "👋 Hi, I’m online!\n"
                "Choose an option:\n"
                "/deliberate\n"
                "/memo\n"
                "/research <topic>\n"
                "/problem <text>\n"
                "/lesson <text>\n"
                "/status"
            )
        )

    # ⚠️ Removed app.run_polling() here
    # Polling is now only started in server.py
