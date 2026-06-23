import csv
from database import get_connection

conn = get_connection()
cur = conn.cursor()

with open("mood_log.csv", "r") as f:
    reader = csv.DictReader(f)

    for row in reader:
        cur.execute("""
        INSERT INTO mood_log
        (date, sentiment, score)
        VALUES (?, ?, ?)
        """, (
            row["Date"],
            row["Sentiment"],
            float(row["Score"])
        ))

conn.commit()
conn.close()

print("Mood log imported successfully")