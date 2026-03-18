import sqlite3
import os

DB_FILE = "founderOS.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS company (
        key TEXT PRIMARY KEY,
        value TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timeframe TEXT,
        goal TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS task_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task TEXT,
        report TEXT,
        outcome TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS lessons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS scratchpad (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        note TEXT
    )""")

    conn.commit()
    conn.close()

def insert(table, **kwargs):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    keys = ", ".join(kwargs.keys())
    placeholders = ", ".join(["?"] * len(kwargs))
    values = list(kwargs.values())
    c.execute(f"INSERT INTO {table} ({keys}) VALUES ({placeholders})", values)
    conn.commit()
    conn.close()

def fetch_all(table):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(f"SELECT * FROM {table}")
    rows = c.fetchall()
    conn.close()
    return rows

def load_full_context():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    context = {}
    for table in ["company", "goals", "task_log", "lessons", "scratchpad"]:
        c.execute(f"SELECT * FROM {table}")
        context[table] = c.fetchall()
    conn.close()
    return context

init_db()
