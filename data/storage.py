import sqlite3
import json
import csv
import os
from datetime import datetime

# Name of the SQLite database file
DB_NAME = 'weather_data.db'
# Name of the CSV file
CSV_FILE = 'weather_data.csv'  # This will create the new format

# Initializes the database and creates the weather table if it doesn't exist
def init_db():
    """Initialize database and ensure schema is up to date."""
    # Connect to the SQLite database (creates file if it doesn't exist)
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Get existing columns
    c.execute("PRAGMA table_info(weather)")
    existing_columns = [column[1] for column in c.fetchall()]
    
    # Create the weather table if it doesn't exist
    if not existing_columns:
        print("Creating new weather database table")
        c.execute('''
            CREATE TABLE IF NOT EXISTS weather (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT,
                state TEXT DEFAULT "",
                country TEXT,
                temperature REAL,
                feels_like REAL DEFAULT 0,
                humidity INTEGER,
                precipitation REAL DEFAULT 0,
                pressure REAL,
                wind_speed REAL DEFAULT 0,
                wind_direction INTEGER DEFAULT 0,
                visibility REAL DEFAULT 0,
                sunrise TEXT DEFAULT "",
                sunset TEXT DEFAULT "",
                description TEXT,
                timestamp TEXT
            )
        ''')
    else:
        # Check for missing columns and add them
        required_columns = {
            'state': 'TEXT DEFAULT ""',
            'feels_like': 'REAL DEFAULT 0',
            'precipitation': 'REAL DEFAULT 0',
            'wind_speed': 'REAL DEFAULT 0',
            'wind_direction': 'INTEGER DEFAULT 0',
            'visibility': 'REAL DEFAULT 0',
            'sunrise': 'TEXT DEFAULT ""',
            'sunset': 'TEXT DEFAULT ""',
            'description': 'TEXT'
        }
        
        for column, data_type in required_columns.items():
            if column not in existing_columns:
                print(f"Adding missing column: {column}")
                c.execute(f'ALTER TABLE weather ADD COLUMN {column} {data_type}')
    
    conn.commit()
    conn.close()
    print("Database initialization complete")

# Saves weather data to both SQLite database and CSV file
def save_weather_data(data):
    try:
        # Save to SQLite database (updated for new fields)
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        timestamp = datetime.now().strftime('%m-%d-%y %H:%M:%S')
        
        # Extract all data fields with defaults
        city = data.get('city', '')
        state = data.get('state', '')  # You may need to add state to your API response
        country = data.get('country', '')
        temperature = data.get('temperature', 0)
        feels_like = data.get('feels_like', 0)
        humidity = data.get('humidity', 0)
        precipitation = data.get('precipitation', 0)
        pressure = data.get('pressure', 0)
        wind_speed = data.get('wind_speed', data.get('wind', {}).get('speed', 0))
        wind_direction = data.get('wind_deg', data.get('wind', {}).get('deg', 0))
        visibility = data.get('visibility', 0)
        
        # Format sunrise/sunset times
        sunrise = ''
        sunset = ''
        if data.get('sunrise'):
            sunrise = datetime.fromtimestamp(data['sunrise']).strftime('%H:%M:%S')
        if data.get('sunset'):
            sunset = datetime.fromtimestamp(data['sunset']).strftime('%H:%M:%S')
        
        description = data.get('description', '')
        
        c.execute('''
            INSERT INTO weather (city, state, country, temperature, feels_like, humidity, 
                               precipitation, pressure, wind_speed, wind_direction, visibility,
                               sunrise, sunset, description, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (city, state, country, temperature, feels_like, humidity, precipitation,
              pressure, wind_speed, wind_direction, visibility, sunrise, sunset, description, timestamp))
        conn.commit()
        conn.close()
        
        # Also save to CSV file
        save_to_csv(data)
        
    except sqlite3.Error as e:
        print(f"Error saving weather data: {e}")

# Save weather data to CSV file with your specified format
def save_to_csv(data):
    try:
        file_exists = os.path.exists(CSV_FILE)
        
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as csvfile:
            # Define fieldnames to match your exact format
            fieldnames = [
                'current time (mm-dd-yy hh:mm:ss)', 'City ', 'State', 'Country', 'Temperature', 
                'Feels Like', 'Humidity', 'Precipitation', 'Pressure', 
                'Wind Speed', 'Wind Direction', 'Visibility', 'Sunrise', 'Sunset'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header if file is new
            if not file_exists:
                writer.writeheader()
            
            # Format current time as mm-dd-yy hh:mm:ss
            current_time = datetime.now().strftime('%m-%d-%y %H:%M:%S')
            
            # Extract wind data
            wind_data = data.get('wind', {})
            wind_speed = data.get('wind_speed', wind_data.get('speed', 0))
            wind_direction = data.get('wind_deg', wind_data.get('deg', 0))
            
            # Format sunrise/sunset times
            sunrise = ''
            sunset = ''
            if data.get('sunrise'):
                sunrise = datetime.fromtimestamp(data['sunrise']).strftime('%H:%M:%S')
            if data.get('sunset'):
                sunset = datetime.fromtimestamp(data['sunset']).strftime('%H:%M:%S')
            
            # Write data row with exact field names
            writer.writerow({
                'current time (mm-dd-yy hh:mm:ss)': current_time,
                'City ': data.get('city', ''),
                'State': data.get('state', ''),
                'Country': data.get('country', ''),
                'Temperature': data.get('temperature', 0),
                'Feels Like': data.get('feels_like', 0),
                'Humidity': data.get('humidity', 0),
                'Precipitation': data.get('precipitation', 0),
                'Pressure': data.get('pressure', 0),
                'Wind Speed': wind_speed,
                'Wind Direction': wind_direction,
                'Visibility': data.get('visibility', 0),
                'Sunrise': sunrise,
                'Sunset': sunset
            })
            
    except Exception as e:
        print(f"Error saving to CSV: {e}")

# Loads the most recently saved weather data from the database
def load_weather_data():
    try:
        # Connect to the database
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        # Select the most recent weather entry with all fields
        c.execute('''SELECT city, state, country, temperature, feels_like, humidity, 
                            precipitation, pressure, wind_speed, wind_direction, visibility,
                            sunrise, sunset, description 
                     FROM weather ORDER BY id DESC LIMIT 1''')
        row = c.fetchone()
        conn.close()
        # If data exists, return it as a dictionary
        if row:
            return {
                'city': row[0],
                'state': row[1],
                'country': row[2],
                'temperature': row[3],
                'feels_like': row[4],
                'humidity': row[5],
                'precipitation': row[6],
                'pressure': row[7],
                'wind_speed': row[8],
                'wind_direction': row[9],
                'visibility': row[10],
                'sunrise': row[11],
                'sunset': row[12],
                'description': row[13],
                # Reconstruct wind data for compatibility
                'wind': {
                    'speed': row[8],
                    'deg': row[9]
                }
            }
        # If no data, return None
        return None
    except sqlite3.Error as e:
        # Print an error message if loading fails
        print(f"Error loading weather data: {e}")
        return None

# Function to get state from coordinates (optional enhancement)
def get_state_from_coords(lat, lon):
    """
    This function could be enhanced to determine state from coordinates
    For now, returns empty string - you could integrate with a geocoding service
    """
    return ""

# Initialize the database when the module is imported
init_db()