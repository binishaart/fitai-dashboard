import sqlite3
import os

DB_NAME = "fitai.db"

def get_connection(base_path=None):
    """Returns a SQLite connection to fitai.db"""
    if base_path:
        db_path = os.path.join(base_path, DB_NAME)
    else:
        db_path = DB_NAME
    conn = sqlite3.connect(db_path)
    return conn

def init_db(base_path=None):
    """Creates all tables if they don't exist."""
    conn = get_connection(base_path)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS mood_log (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            date      TEXT    NOT NULL,
            sentiment TEXT    NOT NULL,
            score     REAL    NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS workout_history (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            date           TEXT,
            exercise       TEXT,
            reps           INTEGER,
            recommendation TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS iot_session_log (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp       TEXT,
            heart_rate      INTEGER,
            resistance_kg   REAL,
            equipment_temp  REAL,
            rest_seconds    INTEGER,
            reps            INTEGER,
            overall_score   INTEGER
        )
    """)

    conn.commit()
    conn.close()