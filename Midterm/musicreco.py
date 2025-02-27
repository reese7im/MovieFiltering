import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import pandas as pd
import requests
from io import BytesIO
import webbrowser
import threading
import os

# Define the database path
db_path = 'C:/Users/Therese/PycharmProjects/MidtermLab/Midterm/create_favorites_table/favorite.db'

# Load the movie dataset into a DataFrame (use the correct path to your dataset)
movies_df = pd.read_csv('C:/Users/Therese/PycharmProjects/MidtermLab/Midterm/Datasets/movie_data.csv')

# Function to establish a connection to SQLite
def get_db_connection():
    return sqlite3.connect(db_path)

# Function to create the favorites table (in case it doesn't exist yet)
def create_favorites_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_title TEXT NOT NULL,
            year INTEGER,
            rating REAL,
            imdb_link TEXT NOT NULL,
            genres TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Function to open IMDb link in the browser
def open_imdb_link(url):
    webbrowser.open(url)

# Function to fetch the movie poster from OMDB API in a separate thread
def fetch_movie_poster(imdb_id, label):
    try:
        omdb_url = f"http://www.omdbapi.com/?i={imdb_id}&apikey=10dfed77"
        response = requests.get(omdb_url)
        movie_data = response.json()

        if 'Poster' in movie_data and movie_data['Poster'] != 'N/A':
            poster_url = movie_data['Poster']
            poster_response = requests.get(poster_url)
            img_data = BytesIO(poster_response.content)
            img = Image.open(img_data)
            img = img.resize((100, 150))  # Resize the image
            label.image = ImageTk.PhotoImage(img)  # Keep reference
            label.config(image=label.image)
    except Exception as e:
        print(f"Error loading image for IMDb ID {imdb_id}: {e}")

# Function to create a star rating system
def create_star_rating(rating):
    stars = int(rating // 2)  # Convert IMDb rating out of 10 to a star rating out of 5
    return "★" * stars + "☆" * (5 - stars)

# Function to display movies in the scrollable frame
def display_movies(movies):
    for widget in movie_list_frame.winfo_children():
        widget.destroy()  # Clear the frame before displaying new results

    if not movies.empty:
        for index, row in movies.iterrows():
            frame = tk.Frame(movie_list_frame, bg='#f0f0f0', pady=10, padx=5, bd=1, relief='solid')
            frame.pack(fill='x', pady=5, padx=5)

            # Label for poster
            poster_label = tk.Label(frame, cursor="hand2")
            poster_label.grid(row=0, column=0, rowspan=3, padx=10, pady=5)
            imdb_id = extract_imdb_id(row['movie_imdb_link'])
            threading.Thread(target=fetch_movie_poster, args=(imdb_id, poster_label), daemon=True).start()

            # Bind click event to open IMDb link
            poster_label.bind("<Button-1>", lambda e, link=row['movie_imdb_link']: open_imdb_link(link))

            # Display movie title
            title_label = tk.Label(frame, text=row['movie_title'], font=('Helvetica', 14, 'bold'), anchor='w',
                                   bg='#f0f0f0')
            title_label.grid(row=0, column=1, sticky='w')

            # Display year and IMDb rating
            year_text = f"Year: {int(row['title_year'])}" if pd.notna(row['title_year']) else "Year: N/A"
            rating_text = f"Rating: {row['imdb_score']}/10"
            year_label = tk.Label(frame, text=f"{year_text} | {rating_text}", font=('Helvetica', 12), bg='#f0f0f0')
            year_label.grid(row=1, column=1, sticky='w')

            # Display star rating
            star_rating = create_star_rating(row['imdb_score'])
            rating_label = tk.Label(frame, text=star_rating, font=('Helvetica', 12), bg='#f0f0f0')
            rating_label.grid(row=1, column=2, sticky='w', padx=10)

            # Add to favorites button
            add_fav_button = tk.Button(
                frame,
                text="Add to Favorites",
                command=lambda r=row: add_to_favorites(r),
                bg='#f94449',
                fg='white',
                font=('Helvetica', 10, 'bold')
            )
            add_fav_button.grid(row=2, column=1, padx=5, pady=5, sticky='w')

            # View IMDb Button
            view_imdb_button = tk.Button(
                frame,
                text="View on IMDb",
                command=lambda link=row['movie_imdb_link']: open_imdb_link(link),
                bg='#0073e6',
                fg='white',
                font=('Helvetica', 10, 'bold')
            )
            view_imdb_button.grid(row=2, column=2, padx=5, pady=5, sticky='w')

    else:
        tk.Label(movie_list_frame, text="No movies found with the given criteria.", font=('Helvetica', 12),
                 bg='#f0f0f0').pack(pady=20)

# Function to extract IMDb ID from the link
def extract_imdb_id(imdb_link):
    try:
        parts = imdb_link.strip().split('/')
        for part in parts:
            if part.startswith('tt') and part[2:].isdigit():
                return part
        print(f"Could not extract IMDb ID from link: {imdb_link}")
        return ""
    except Exception as e:
        print(f"Error extracting IMDb ID from link {imdb_link}: {e}")
        return ""

# Function to add a movie to favorites in the SQLite database
def add_to_favorites(movie):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the movie already exists in the database
        cursor.execute("SELECT COUNT(*) FROM favorites WHERE movie_title = ?", (movie['movie_title'],))
        exists = cursor.fetchone()[0]

        if exists == 0:
            # Insert the movie into the database
            cursor.execute(
                "INSERT INTO favorites (movie_title, year, rating, imdb_link, genres) VALUES (?, ?, ?, ?, ?)",
                (movie['movie_title'], movie['title_year'], movie['imdb_score'], movie['movie_imdb_link'], movie['genres'])
            )
            conn.commit()
            messagebox.showinfo("Success", f"'{movie['movie_title']}' has been added to your favorites!")
        else:
            messagebox.showinfo("Info", f"'{movie['movie_title']}' is already in favorites.")

    except Exception as e:
        print(f"Error adding to favorites: {e}")
    finally:
        if conn:
            conn.close()

# Function to load user favorites from the SQLite database
def load_favorites():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT movie_title, year, rating, imdb_link, genres FROM favorites")
        favorites = cursor.fetchall()

        favorites_dict = {title: {'year': year, 'rating': rating, 'imdb_link': imdb_link, 'genres': genres} for
                          title, year, rating, imdb_link, genres in favorites}

        return favorites_dict

    except Exception as e:
        print(f"Error loading favorites: {e}")
        return {}
    finally:
        if conn:
            conn.close()

# Function to display favorites
def display_favorites():
    favorites = load_favorites()

    # Create a new window for favorites
    fav_window = tk.Toplevel(root)
    fav_window.title("Favorites")
    fav_window.geometry("800x600")
    fav_window.configure(bg='#FF7F7F')

    # Create a canvas and a scrollbar for the favorites display
    fav_canvas = tk.Canvas(fav_window, bg='#f0f0f0')
    fav_canvas.pack(side='left', fill='both', expand=True)

    fav_scrollbar = ttk.Scrollbar(fav_window, orient="vertical", command=fav_canvas.yview)
    fav_scrollbar.pack(side='right', fill='y')
    fav_canvas.configure(yscrollcommand=fav_scrollbar.set)

    fav_list_frame = tk.Frame(fav_canvas, bg='#f0f0f0')
    fav_canvas.create_window((0, 0), window=fav_list_frame, anchor='nw')

    fav_list_frame.bind("<Configure>", lambda e: fav_canvas.configure(scrollregion=fav_canvas.bbox("all")))

    if favorites:
        for title, info in favorites.items():
            frame = tk.Frame(fav_list_frame, bg='#f0f0f0', pady=10, padx=5, bd=1, relief='solid')
            frame.pack(fill='x', pady=5, padx=5)

            # Movie Title
            title_label = tk.Label(frame, text=title, font=('Helvetica', 14, 'bold'), bg='#f0f0f0')
            title_label.grid(row=0, column=0, sticky='w', padx=10)

            # Year, Genres, and Rating
            year_text = f"Year: {int(info['year'])}" if info['year'] is not None else "Year: N/A"
            rating_text = f"Rating: {info['rating']}/10"
            genres_text = f"Genres: {info['genres']}"
            year_label = tk.Label(frame, text=f"{year_text} | {rating_text} | {genres_text}", font=('Helvetica', 12), bg='#f0f0f0')
            year_label.grid(row=1, column=0, sticky='w', padx=10)

            # View IMDb Button
            imdb_button = tk.Button(
                frame,
                text="View on IMDb",
                command=lambda link=info['imdb_link']: open_imdb_link(link),
                bg='#0073e6',
                fg='white',
                font=('Helvetica', 10, 'bold')
            )
            imdb_button.grid(row=0, column=1, rowspan=2, padx=10, pady=5)

    else:
        tk.Label(fav_list_frame, text="No favorites found.", font=('Helvetica', 12), bg='#f0f0f0').pack(pady=20)

# Function to filter movies based on user inputs (year, rating, genres)
def filter_movies():
    selected_genres = [genre for genre, var in genre_var.items() if var.get()]
    year = year_entry.get().strip()
    rating = rating_entry.get().strip()

    filtered_movies = movies_df

    # Filter by selected genres
    if selected_genres:
        filtered_movies = filtered_movies[filtered_movies['genres'].apply(lambda x: any(genre in x for genre in selected_genres))]

    # Filter by year
    if year:
        filtered_movies = filtered_movies[filtered_movies['title_year'] == int(year)]

    # Filter by rating
    if rating:
        filtered_movies = filtered_movies[filtered_movies['imdb_score'] >= float(rating)]

    # Display the filtered movies
    display_movies(filtered_movies)

# Function to show the top ten most popular movies with ratings from 10 to 7
def display_top_movies():
    top_movies = movies_df[movies_df['imdb_score'] >= 7]
    top_movies = top_movies.sort_values(by='imdb_score', ascending=False).head(10)
    display_movies(top_movies)

# Define the list of genre options
genre_options = ['Action', 'Comedy', 'Drama', 'Fantasy', 'Horror', 'Romance', 'Sci-Fi', 'Thriller']

# Set up the main application window
def setup_main_interface():
    global root, year_entry, rating_entry, genre_var, movie_list_frame, movie_canvas

    root = tk.Tk()
    root.title("Movie Filter")
    root.geometry("1200x700")
    root.configure(bg='#FF7F7F')

    font_style = ('Helvetica', 12)

    # Configure grid weights for resizing
    root.grid_rowconfigure(2, weight=1)
    root.grid_columnconfigure(5, weight=1)

    # Genre checkboxes
    genre_var = {genre: tk.BooleanVar() for genre in genre_options}
    tk.Label(root, text="Select Genres:", bg='#FF7F7F', font=font_style).grid(row=0, column=0, padx=10, pady=10,
                                                                              sticky='e')

    for i, genre in enumerate(genre_options):
        tk.Checkbutton(root, text=genre, variable=genre_var[genre], bg='#FF7F7F').grid(row=0, column=i + 1, padx=5,
                                                                                       pady=5, sticky='w')

    # Year input
    tk.Label(root, text="Release Year:", bg='#FF7F7F', font=font_style).grid(row=1, column=0, padx=10, pady=10,
                                                                             sticky='e')
    year_entry = tk.Entry(root, font=font_style)
    year_entry.grid(row=1, column=1, padx=10, pady=10, sticky='w')

    # IMDb rating input
    tk.Label(root, text="Minimum IMDb Rating (0-10):", bg='#FF7F7F', font=font_style).grid(row=1, column=2, padx=10,
                                                                                           pady=10, sticky='e')
    rating_entry = tk.Entry(root, font=font_style)
    rating_entry.grid(row=1, column=3, padx=10, pady=10, sticky='w')

    # Filter button
    filter_button = tk.Button(
        root,
        text="Filter Movies",
        command=filter_movies,
        bg='#f94449',
        fg='white',
        font=font_style
    )
    filter_button.grid(row=1, column=4, padx=10, pady=10)

    # Show favorites button
    show_favorites_button = tk.Button(
        root,
        text="My Favorites",
        command=display_favorites,
        bg='#f94449',
        fg='white',
        font=font_style
    )
    show_favorites_button.grid(row=1, column=5, padx=2, pady=10)

    # Create a canvas and a scrollbar for the movie display
    movie_canvas = tk.Canvas(root, bg='#f28080')
    movie_canvas.grid(row=2, column=0, columnspan=6, pady=10, sticky='nsew')

    # Add scrollbar to the canvas
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=movie_canvas.yview)
    scrollbar.grid(row=2, column=6, sticky='ns', pady=10)
    movie_canvas.configure(yscrollcommand=scrollbar.set)

    # Create a frame inside the canvas to hold the movie widgets
    global movie_list_frame
    movie_list_frame = tk.Frame(movie_canvas, bg='#f28080')
    movie_canvas.create_window((0, 0), window=movie_list_frame, anchor='nw')

    # Update scroll region after adding widgets
    movie_list_frame.bind("<Configure>", lambda e: movie_canvas.configure(scrollregion=movie_canvas.bbox("all")))

    # Display top movies on startup
    display_top_movies()

    root.mainloop()

# Run the application
if __name__ == "__main__":
    # Ensure that the table is created before running the app
    create_favorites_table()
    setup_main_interface()

