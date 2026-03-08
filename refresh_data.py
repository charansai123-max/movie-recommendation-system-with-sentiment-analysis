import sqlite3
import requests
import os

# --- CONFIGURATION ---
API_KEY = "b20f9215"  # Replace with your actual OMDb API key
DB_NAME = "omdb_movies.db"
MOVIE_QUERIES = ["Sarrainodu", "Pushpa: The Rise", "Pushpa 2: The Rule", "Baahubali: The Beginning", "Baahubali 2: The Conclusion", "RRR", "K.G.F: Chapter 1", "K.G.F: Chapter 2", "Vikram", "Kaithi", "Jailer", "Master", "Hit", "HIT: The Second Case", "HIT: The Third Case", "Salaar: Part 1 – Ceasefire", "Saaho", "Pathaan", "Committee Kurrollu", "Rangasthalam", "Jai Lava Kusa", "Ala Vaikunthapurramuloo", "Aravinda Sametha Veera Raghava", "Sarileru Neekevvaru", "Waltair Veerayya", "Srimanthudu", "Maharshi"]

def setup_database():
    # Remove old DB to ensure a clean start with the correct columns
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print("Old database removed.")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create Movies Table with the 'poster' column included
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            imdb_id TEXT UNIQUE,
            title TEXT,
            year TEXT,
            genre TEXT,
            director TEXT,
            plot TEXT,
            imdb_rating TEXT,
            poster TEXT
        )
    ''')
    
    # Create Users Table (for your login system)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT
        )
    ''')
    
    conn.commit()
    return conn

def fetch_and_save(conn):
    cursor = conn.cursor()
    for query in MOVIE_QUERIES:
        print(f"Searching for: {query}...")
        search_url = f"http://www.omdbapi.com/?s={query}&apikey={API_KEY}"
        r = requests.get(search_url).json()
        
        if r.get('Response') == 'True':
            for item in r['Search']:
                # Get Full Details for each movie to get the Plot and Rating
                detail_url = f"http://www.omdbapi.com/?i={item['imdbID']}&apikey={API_KEY}"
                m = requests.get(detail_url).json()
                
                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO movies 
                        (imdb_id, title, year, genre, director, plot, imdb_rating, poster)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        m['imdbID'], m['Title'], m['Year'], m['Genre'], 
                        m['Director'], m['Plot'], m['imdbRating'], m['Poster']
                    ))
                except Exception as e:
                    print(f"Error saving {m['Title']}: {e}")
    
    conn.commit()
    print("Data Refresh Complete!")

if __name__ == "__main__":
    connection = setup_database()
    fetch_and_save(connection)
    connection.close()