import sqlite3

def add_column():
    conn = sqlite3.connect("omdb_movies.db")
    cursor = conn.cursor()
    try:
        # Adds the 'poster' column to your existing 'movies' table
        cursor.execute("ALTER TABLE movies ADD COLUMN poster TEXT")
        print("Column 'poster' added successfully!")
    except sqlite3.OperationalError:
        print("Column 'poster' already exists.")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    add_column()