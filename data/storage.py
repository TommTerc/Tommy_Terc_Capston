import sqlite3
import json
import csv
import os
from datetime import datetime

# Name of the SQLite database file
DB_NAME = 'weather_data.db'
# Name of the CSV file
CSV_FILE = 'weather_data.csv'

# Initializes the database and creates the weather table if it doesn't exist
def init_db():
    # Connect to the SQLite database (creates file if it doesn't exist)
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Create the weather table with columns for city, country, temperature, and description
    c.execute('''
        CREATE TABLE IF NOT EXISTS weather (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            country TEXT,
            temperature REAL,
            description TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Saves weather data to both SQLite database and CSV file
def save_weather_data(data):
    try:
        # Save to SQLite database (existing functionality)
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.execute('''
            INSERT INTO weather (city, country, temperature, description, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (data['city'], data['country'], data['temperature'], data['description'], timestamp))
        conn.commit()
        conn.close()
        
        # Also save to CSV file (new functionality)
        save_to_csv(data)
        
    except sqlite3.Error as e:
        print(f"Error saving weather data: {e}")

# Save weather data to CSV file
def save_to_csv(data):
    try:
        file_exists = os.path.exists(CSV_FILE)
        
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['timestamp', 'city', 'country', 'temperature', 'description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header if file is new
            if not file_exists:
                writer.writeheader()
            
            # Write data row
            writer.writerow({
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'city': data['city'],
                'country': data['country'],
                'temperature': data['temperature'],
                'description': data['description']
            })
            
    except Exception as e:
        print(f"Error saving to CSV: {e}")

# Loads the most recently saved weather data from the database
def load_weather_data():
    try:
        # Connect to the database
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        # Select the most recent weather entry
        c.execute('SELECT city, country, temperature, description FROM weather ORDER BY id DESC LIMIT 1')
        row = c.fetchone()
        conn.close()
        # If data exists, return it as a dictionary
        if row:
            return {
                'city': row[0],
                'country': row[1],
                'temperature': row[2],
                'description': row[3]
            }
        # If no data, return None
        return None
    except sqlite3.Error as e:
        # Print an error message if loading fails
        print(f"Error loading weather data: {e}")
        return None

# Initialize the database when the module is imported
init_db()