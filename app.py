from flask import Flask, render_template, request, redirect, url_for, flash, abort, sessions
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from textblob import TextBlob 
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "thesis_secret_key"
DB_NAME = "omdb_movies.db"

# --- LOGIN CONFIGURATION ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user_data = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if user_data:
        return User(user_data['id'], user_data['username'], user_data['password_hash'])
    return None

def get_db_connection():
    if not os.path.exists(DB_NAME):
        return None
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# --- ANALYSIS HELPER FUNCTION ---
def analyze_movie(movie):
    """
    Analyzes sentiment and rating.
    """
    try:
        rating = float(movie['imdb_rating']) if movie['imdb_rating'] != 'N/A' else 0.0
    except:
        rating = 0.0
        
    if rating > 6.5:
        verdict = "Excellent"
        color = "green"
    else:
        verdict = "Bad"
        color = "red"

    # Ensures TextBlob always gets a string, even if the plot is missing in the DB
    plot_text = movie['plot'] if movie['plot'] else "No plot available."
    blob = TextBlob(plot_text)
    
    sentiment_score = blob.sentiment.polarity 
    
    if sentiment_score > 0.1:
        sentiment = "Positive Story"
    elif sentiment_score < -0.1:
        sentiment = "Negative/Dark Story"
    else:
        sentiment = "Neutral"
    return {
        "verdict": verdict,
        "color": color,
        "sentiment": sentiment,
        "score": round(sentiment_score, 2)
    }

# --- ROUTES ---

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    conn = get_db_connection()
    # Get the search query and remove leading/trailing spaces
    query = request.args.get('query', '').strip()
    
    if query:
        # Using LOWER() makes the search case-insensitive
        movies = conn.execute(
            "SELECT * FROM movies WHERE LOWER(title) LIKE LOWER(?)", 
            ('%' + query + '%',)
        ).fetchall()
    else:
        movies = conn.execute('SELECT * FROM movies').fetchall()
    
    conn.close()
    
    analyzed_movies = []
    for m in movies:
        analysis = analyze_movie(m)
        # Merge the database row with the sentiment analysis
        analyzed_movies.append({**dict(m), **analysis})

    return render_template('index.html', movies=analyzed_movies, name=current_user.username)

# Notice the <imdb_id> added to the route
@app.route('/movie/<imdb_id>') 
@login_required
def movie_details(imdb_id):
    conn = get_db_connection()
    
    try:
        # 1. Get the Main Movie
        movie = conn.execute(
            'SELECT * FROM movies WHERE imdb_id = ?', 
            (imdb_id,)
        ).fetchone()
        
        if not movie:
            # Using Flask's abort is generally cleaner for 404s
            abort(404, description="Movie not found") 

        # 2. IMPROVED RECOMMENDATION LOGIC
        if movie['genre'] and movie['genre'].strip() != 'N/A':
            main_genre = movie['genre'].split(',')[0].strip()
        else:
            main_genre = ""

        recommendations = conn.execute(
            '''SELECT * FROM movies 
               WHERE genre LIKE ? AND imdb_id != ? 
               ORDER BY RANDOM() LIMIT 3''', 
            ('%' + main_genre + '%', imdb_id)
        ).fetchall()

        # 3. Analyze the main movie
        analysis = analyze_movie(movie)
        
    finally:
        # This ensures the connection ALWAYS closes, even if analyze_movie crashes
        conn.close() 

    return render_template(
        'movie_details.html', 
        movie=movie, 
        analysis=analysis, 
        recommendations=recommendations
    )

# --- LOGIN/REGISTER ROUTES ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_pw = generate_password_hash(password)
        try:
            conn = get_db_connection()
            conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed_pw))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except:
            flash('Username taken!', 'error')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password_hash'], password):
            login_user(User(user['id'], user['username'], user['password_hash']))
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)