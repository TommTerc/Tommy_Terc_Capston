import sqlite3
import os
import tkinter as tk

# Database name for favorite cities
FAVORITES_DB = 'favorites.db'

def init_favorites_db():
    """Initialize the favorites database and create the table if it doesn't exist."""
    conn = sqlite3.connect(FAVORITES_DB)
    c = conn.cursor()
    # Create the favorites table with city name and optional country
    c.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            country TEXT,
            added_date TEXT,
            UNIQUE(city, country)
        )
    ''')
    conn.commit()
    conn.close()

def add_favorite_city(city, country=None):
    """Add a city to favorites list."""
    try:
        conn = sqlite3.connect(FAVORITES_DB)
        c = conn.cursor()
        from datetime import datetime
        added_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Insert the favorite city (will ignore if already exists due to UNIQUE constraint)
        c.execute('''
            INSERT OR IGNORE INTO favorites (city, country, added_date)
            VALUES (?, ?, ?)
        ''', (city, country, added_date))
        
        if c.rowcount > 0:
            print(f"Added {city} to favorites!")
            conn.commit()
            return True
        else:
            print(f"{city} is already in favorites!")
            return False
            
    except sqlite3.Error as e:
        print(f"Error adding favorite city: {e}")
        return False
    finally:
        conn.close()

def remove_favorite_city(city, country=None):
    """Remove a city from favorites list."""
    try:
        conn = sqlite3.connect(FAVORITES_DB)
        c = conn.cursor()
        
        # Remove the favorite city
        c.execute('''
            DELETE FROM favorites 
            WHERE city = ? AND (country = ? OR (country IS NULL AND ? IS NULL))
        ''', (city, country, country))
        
        if c.rowcount > 0:
            print(f"Removed {city} from favorites!")
            conn.commit()
            return True
        else:
            print(f"{city} was not found in favorites!")
            return False
            
    except sqlite3.Error as e:
        print(f"Error removing favorite city: {e}")
        return False
    finally:
        conn.close()

def get_favorite_cities():
    """Get all favorite cities from the database."""
    try:
        conn = sqlite3.connect(FAVORITES_DB)
        c = conn.cursor()
        
        # Get all favorite cities ordered by when they were added
        c.execute('SELECT city, country, added_date FROM favorites ORDER BY added_date DESC')
        favorites = c.fetchall()
        
        # Return as list of dictionaries
        return [
            {
                'city': row[0],
                'country': row[1],
                'added_date': row[2]
            }
            for row in favorites
        ]
        
    except sqlite3.Error as e:
        print(f"Error getting favorite cities: {e}")
        return []
    finally:
        conn.close()

def is_favorite_city(city, country=None):
    """Check if a city is in the favorites list."""
    try:
        conn = sqlite3.connect(FAVORITES_DB)
        c = conn.cursor()
        
        # Check if the city exists in favorites
        c.execute('''
            SELECT COUNT(*) FROM favorites 
            WHERE city = ? AND (country = ? OR (country IS NULL AND ? IS NULL))
        ''', (city, country, country))
        
        count = c.fetchone()[0]
        return count > 0
        
    except sqlite3.Error as e:
        print(f"Error checking favorite city: {e}")
        return False
    finally:
        conn.close()

def clear_all_favorites():
    """Clear all favorite cities (use with caution!)."""
    try:
        conn = sqlite3.connect(FAVORITES_DB)
        c = conn.cursor()
        
        # Delete all favorites
        c.execute('DELETE FROM favorites')
        conn.commit()
        print("All favorite cities cleared!")
        return True
        
    except sqlite3.Error as e:
        print(f"Error clearing favorites: {e}")
        return False
    finally:
        conn.close()

def show_favorites_window(parent, callback=None):
    """Display favorite cities in a window with visible buttons."""
    # Create the window
    favorites_window = tk.Toplevel(parent)
    favorites_window.title("Favorite Cities")
    favorites_window.geometry("600x900")
    favorites_window.configure(bg="#6db3f2")  # Light blue background
    
    # Title label
    title_label = tk.Label(favorites_window, text="Favorite Cities", 
                          font=("Helvetica", 24, "bold"), bg="#6db3f2", fg="white")
    title_label.pack(pady=20)
    
    # Get favorite cities
    favorites = get_favorite_cities()
    
    # Create list frame with light background
    list_frame = tk.Frame(favorites_window, bg="#f0f0f0", bd=1, relief=tk.SUNKEN)  # Light background
    list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
    
    # Create scrollbar
    scrollbar = tk.Scrollbar(list_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Create listbox for cities
    city_listbox = tk.Listbox(list_frame, font=("Helvetica", 14), bg="#ffffff",
                             fg="#000000", selectbackground="#4a90e2", height=10)
    city_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Configure scrollbar
    scrollbar.config(command=city_listbox.yview)
    city_listbox.config(yscrollcommand=scrollbar.set)
    
    # Add cities to listbox
    for fav in favorites:
        city_text = f"{fav['city']}, {fav['country']}"
        city_listbox.insert(tk.END, city_text)
    
    # Button frame with clear background
    button_frame = tk.Frame(favorites_window, bg="#6db3f2")
    button_frame.pack(fill=tk.X, padx=20, pady=10)
    
    # Custom button function (same as in team_feature.py)
    def create_custom_button(parent, text, bg_color, fg_color, command):
        """Create a custom button using Frame and Label."""
        button_frame = tk.Frame(parent, bg=bg_color, relief="raised", bd=3, cursor="hand2")
        
        button_label = tk.Label(button_frame, text=text, font=("Helvetica", 12, "bold"),
                               bg=bg_color, fg=fg_color, padx=15, pady=8)
        button_label.pack()
        
        # Bind click events
        def on_click(event):
            command()
        
        def on_enter(event):
            button_frame.config(relief="solid")
        
        def on_leave(event):
            button_frame.config(relief="raised")
        
        button_frame.bind("<Button-1>", on_click)
        button_label.bind("<Button-1>", on_click)
        button_frame.bind("<Enter>", on_enter)
        button_frame.bind("<Leave>", on_leave)
        button_label.bind("<Enter>", on_enter)
        button_label.bind("<Leave>", on_leave)
        
        return button_frame
    
    # Load Weather function
    def load_city():
        selected = city_listbox.curselection()
        if selected:
            city_text = city_listbox.get(selected[0])
            city, country = city_text.split(", ")
            favorites_window.destroy()
            if callback:
                callback(city, country)
    
    # Load Weather Button - USING CUSTOM BUTTON
    load_button = create_custom_button(button_frame, "Load Weather", "#28a745", "white", load_city)
    load_button.pack(side=tk.LEFT, padx=5)
    
    # Close Button - USING CUSTOM BUTTON
    close_button = create_custom_button(button_frame, "Close", "#6c757d", "white", favorites_window.destroy)
    close_button.pack(side=tk.RIGHT, padx=5)

    # Force rendering of buttons immediately
    favorites_window.update_idletasks()

# Initialize the favorites database when this module is imported
init_favorites_db()

# Example usage functions for testing
if __name__ == "__main__":
    # Test the favorite cities functionality
    print("Testing favorite cities...")
    
    # Add some favorite cities
    add_favorite_city("New York", "US")
    add_favorite_city("London", "GB")
    add_favorite_city("Tokyo", "JP")
    
    # Get all favorites
    favorites = get_favorite_cities()
    print("Current favorites:")
    for fav in favorites:
        print(f"- {fav['city']}, {fav['country']} (added: {fav['added_date']})")
    
    # Check if a city is favorite
    print(f"Is New York a favorite? {is_favorite_city('New York', 'US')}")
    print(f"Is Paris a favorite? {is_favorite_city('Paris', 'FR')}")
    
    # Remove a favorite
    remove_favorite_city("London", "GB")
    
    # Show updated list
    favorites = get_favorite_cities()
    print("Updated favorites:")
    for fav in favorites:
        print(f"- {fav['city']}, {fav['country']}")