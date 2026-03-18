import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from orchestrator import run_deliberation, run_daily_memo, run_research, handle_pushback
from database import fetch_all, insert
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

app = ApplicationBuilder().token(TOKEN).build()

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
        rows = fetch