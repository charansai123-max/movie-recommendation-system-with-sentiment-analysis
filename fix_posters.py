import sqlite3

DB_NAME = "omdb_movies.db"

def fix_database_posters():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 1. Check if 'poster' column exists, if not, you'll need to add it
    try:
        cursor.execute("SELECT poster FROM movies LIMIT 1")
    except sqlite3.OperationalError:
        print("Error: The 'poster' column does not exist in your database!")
        conn.close()
        return

    # 2. Update any 'N/A' or empty strings to a working placeholder
    placeholder = "https://images.unsplash.com/photo-1485846234645-a62644f84728?q=80&w=2059&auto=format&fit=crop"
    
    cursor.execute("""
        UPDATE movies 
        SET poster = ? 
        WHERE poster IS NULL OR poster = 'N/A' OR poster = ''
    """, (placeholder,))

    print(f"Updated {cursor.rowcount} movies with placeholder posters.")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    fix_database_posters()