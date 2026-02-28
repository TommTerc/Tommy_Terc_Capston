import tkinter as tk
from tkinter import messagebox
from src.gui import WeatherApp

# Main entry point for the weather app
def main():
    # Create the main Tkinter window
    root = tk.Tk()
    root.title("Weather App")
    
    # Initialize the WeatherApp GUI
    # The WeatherApp initialization automatically loads the last city's weather
    # with forecast data through show_last_weather()
    app = WeatherApp(root)
    
    # Start the GUI main loop
    root.mainloop()

if __name__ == "__main__":
    main()