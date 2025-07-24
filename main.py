import tkinter as tk
from tkinter import messagebox
from src.gui import WeatherApp

from src.weather_api import fetch_weather_data
from data.storage import save_weather_data, load_weather_data

# Main entry point for the weather app
def main():
    # Create the main Tkinter window
    root = tk.Tk()
    root.title("Weather App")
    
    # Initialize the WeatherApp GUI
    app = WeatherApp(root)
    
    try:
        # Attempt to load previous weather data from storage
        previous_data = load_weather_data()
        if previous_data:
            # If data exists, update the display with it
            app.display_weather(previous_data)
    except Exception as e:
        # Show an error message if loading previous data fails
        messagebox.showerror("Error", f"Failed to load previous data: {e}")
    
    # Start the GUI main loop
    root.mainloop()

if __name__ == "__main__":
    main()