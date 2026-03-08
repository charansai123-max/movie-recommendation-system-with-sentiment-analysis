import sqlite3
import requests
import time

# --- CONFIGURATION ---
API_KEY = "b20f9215"  # Paste your key from email
DB_NAME = "omdb_movies.db"
SEARCH_KEYWORDS = ["Sarrainodu", "Pushpa: The Rise", "Pushpa 2: The Rule", "Baahubali: The Beginning", "Baahubali 2: The Conclusion", "RRR", "K.G.F: Chapter 1", "K.G.F: Chapter 2", "Vikram", "Kaithi", "Jailer", "Master", "Hit", "HIT: The Second Case", "HIT: The Third Case", "Salaar: Part 1 – Ceasefire", "Saaho", "Pathaan", "Committee Kurrollu", "Rangasthalam", "Jai Lava Kusa", "Ala Vaikunthapurramuloo", "Aravinda Sametha Veera Raghava", "Sarileru Neekevvaru", "Waltair Veerayya", "Srimanthudu", "Maharshi"]

def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # OMDb uses Capitalized Keys (Title, Year, etc.)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            imdb_id TEXT PRIMARY KEY,
            title TEXT,
            year TEXT,
            genre TEXT,
            director TEXT,
            plot TEXT,
            imdb_rating REAL
        )
    ''')
    conn.commit()
    return conn

def fetch_movie_details(imdb_id):
    """ Get full details for a specific movie ID """
    url = f"http://www.omdbapi.com/?apikey={API_KEY}&i={imdb_id}&plot=full"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Connection error: {e}")
    return None

def search_and_save(conn):
    cursor = conn.cursor()
    
    print(f"Starting search for keywords: {SEARCH_KEYWORDS}...")

    for keyword in SEARCH_KEYWORDS:
        # 1. Search for the keyword
        search_url = f"http://www.omdbapi.com/?apikey={API_KEY}&s={keyword}&type=movie"
        response = requests.get(search_url)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('Response') == 'True':
                search_results = data.get('Search', [])
                print(f"Found {len(search_results)} movies for '{keyword}'")
                
                # 2. Loop through results and get FULL details
                for item in search_results:
                    imdb_id = item.get('imdbID')
                    
                    # Check if we already have this movie to save API calls
                    cursor.execute("SELECT 1 FROM movies WHERE imdb_id = ?", (imdb_id,))
                    if cursor.fetchone():
                        print(f"  Skipping {item['Title']} (Already exists)")
                        continue

                    # Fetch full info
                    details = fetch_movie_details(imdb_id)
                    
                    if details and details.get('Response') == 'True':
                        cursor.execute('''
                            INSERT OR IGNORE INTO movies 
                            (imdb_id, title, year, genre, director, plot, imdb_rating)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            details.get('imdbID'),
                            details.get('Title'),
                            details.get('Year'),
                            details.get('Genre'),
                            details.get('Director'),
                            details.get('Plot'),
                            details.get('imdbRating'), # Note: might be "N/A"
                            details.get('Poster')
                        ))
                        print(f"  Saved: {details['Title']}")
                        conn.commit()
                        
                        # Sleep to be safe (Free tier limit)
                        time.sleep(0.5) 
            else:
                print(f"No results for '{keyword}'")
        else:
            print(f"Error searching for '{keyword}'")

if __name__ == "__main__":
    connection = setup_database()
    search_and_save(connection)
    connection.close()
    print("\nDatabase update complete. Check 'omdb_movies.db'")