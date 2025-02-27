📌 User Manual: How to Download & Run the Movie Filtering Application
This guide will help users **download, set up, and run** the **Movie Filtering and Favorites Application** on their local system.

---

🔹 Step 1: Download the Project
You can download the project from GitHub

💾 Option 1: Clone from GitHub (Recommended)
If the project is on GitHub, open Terminal

```sh
[git clone https://github.com/yourusername/yourrepository.git
cd yourrepository](https://github.com/reese7im/MovieFiltering/edit/main/
```

💾 Option 2: Download as a ZIP
1. Go to the GitHub repository (or shared folder).
2. Click Download ZIP
3. Extract the ZIP file to your preferred location.

---

🔹 Step 2: Install Required Dependencies
Before running the application, install the required Python libraries:

```sh
pip install sqlite3 pandas requests pillow tk
```

🔹 `sqlite3` → Manages the favorites database.  
🔹 `pandas` → Reads and processes movie data.  
🔹 `requests` → Fetches movie poster images.  
🔹 `pillow` → Handles image processing.  
🔹 `tk` → Builds the graphical user interface.

---

🔹 Step 3: Set Up the Database
The application uses SQLite to store favorite movies.  
Make sure the database file is in the correct location:

📂 Database Path:  
`C:/Users////Midterm/create_favorites_table/favorite.db`

If the file doesn’t exist, the application will create it automatically.

---

🔹 Step 4: Using the Application
🎬 Filtering Movies
- Select genres (e.g., Action, Comedy).
- Enter a release year (e.g., 2002).
- Set a minimum IMDb rating (e.g., 7,9,8).
- Click "Filter Movies" to display matching movies.

⭐ Adding to Favorites
- Click "Add to Favorites" under a movie.
- The movie will be saved to the favorites database.

📌 Viewing Favorites
- Click "My Favorites" to view saved movies.

🔗 Viewing IMDb Details
- Click "View on IMDb" to open the movie’s IMDb page.

---
🎯 Done!
You can now filter, save, and view movies using the application! 🚀  
