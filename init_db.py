from database import get_connection

conn = get_connection()
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS workout_history(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    exercise TEXT,
    reps INTEGER,
    recommendation TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS mood_log(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    sentiment TEXT,
    score REAL
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS iot_session_log(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    heart_rate INTEGER,
    resistance_kg INTEGER,
    equipment_temp_c REAL,
    rest_seconds INTEGER,
    overall_score INTEGER
)
""")

conn.commit()
conn.close()

print("Database created successfully")