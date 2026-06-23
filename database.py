import sqlite3

DB_NAME = "fitai.db"

def get_connection():
    return sqlite3.connect(DB_NAME)