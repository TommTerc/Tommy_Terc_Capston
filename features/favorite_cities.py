import sqlite3
import os

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