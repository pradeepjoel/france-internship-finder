import sqlite3
from pathlib import Path

DB_PATH = Path("data/jobs.sqlite")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    with conn() as c:
        c.execute("""
        CREATE TABLE IF NOT EXISTS bronze_raw (
            url TEXT PRIMARY KEY,
            source TEXT NOT NULL,
            html TEXT NOT NULL,
            fetched_at TEXT DEFAULT (datetime('now'))
        );
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS silver_jobs (
            url TEXT PRIMARY KEY,
            source TEXT NOT NULL,
            title TEXT,
            company TEXT,
            location TEXT,
            contract TEXT,
            description TEXT,
            parsed_at TEXT DEFAULT (datetime('now'))
        );
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS gold_jobs (
            url TEXT PRIMARY KEY,
            language TEXT,
            english_score INTEGER,
            contract_type TEXT,
            is_target INTEGER,
            computed_at TEXT DEFAULT (datetime('now'))
        );
        """)

        c.execute("CREATE INDEX IF NOT EXISTS idx_gold_score ON gold_jobs(english_score);")
        c.execute("CREATE INDEX IF NOT EXISTS idx_silver_loc ON silver_jobs(location);")
