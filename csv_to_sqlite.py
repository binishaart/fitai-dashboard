import csv
from database import get_connection

conn = get_connection()
cur = conn.cursor()

with open("workout_history.csv", "r") as f:
    reader = csv.DictReader(f)

    for row in reader:
        cur.execute("""
        INSERT INTO workout_history
        (date, exercise, reps, recommendation)
        VALUES (?, ?, ?, ?)
        """, (
            row["Date"],
            row["Exercise"],
            row["Reps"],
            row["Recommendation"]
        ))

conn.commit()
conn.close()

print("CSV imported")