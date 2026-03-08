import sqlite3

DB_NAME = "omdb_movies.db"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Create the Users table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )
''')

conn.commit()
conn.close()
print("✅ Users table added successfully!")