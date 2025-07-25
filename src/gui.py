import tkinter as tk
from tkinter import font, messagebox
import sys
import os
from dotenv import load_dotenv
from tkinter import messagebox
import requests

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv('OPENWEATHER_API_KEY')
if not API_KEY:
    raise ValueError("OPENWEATHER_API_KEY not found in environment variables")

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.weather_api import fetch_weather_data, fetch_5day_forecast
from data.storage import load_weather_data, save_weather_data
from src.utils import format_wind_info, format_humidity
from features.favorite_cities import add_favorite_city, get_favorite_cities, is_favorite_city, remove_favorite_city

USE_MOCK = False
if USE_MOCK:
    from data.mock_weather import get_mock_weather_data

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tommy's Weather App")
        self.root.geometry("950x580")
        self.root.resizable(True, True)
        self.root.configure(bg="#6db3f2")


        #
        # Initialize variables
        self.city_var = tk.StringVar()
        self.current_city_data = None

        # Define fonts
        self.large_font = font.Font(family="Helvetica", size=44, weight="bold")
        self.medium_font = font.Font(family="Helvetica", size=18,)
        self.small_font = font.Font(family="Helvetica", size=16, weight="bold")

        # --- Search bar and buttons ---
        search_frame = tk.Frame(self.root, bg="#31618a")
        search_frame.grid(row=0, column=0, columnspan=2, sticky="e", padx=10, pady=(10, 0))
        search_frame.grid_columnconfigure(0, weight=0)
        search_frame.grid_columnconfigure(1, weight=0)
        search_frame.grid_columnconfigure(2, weight=0)

        self.city_entry = tk.Entry(search_frame, textvariable=self.city_var, font=self.medium_font, width=18)
        self.city_entry.grid(row=0, column=0, padx=10, pady=10)

        self.search_btn = tk.Button(search_frame, text="Get Weather", font=self.small_font, command=self.get_weather)
        self.search_btn.grid(row=0, column=1, padx=5, pady=10)

        self.favorite_btn = tk.Button(search_frame, text="🤍", font=self.small_font, command=self.toggle_favorite)
        self.favorite_btn.grid(row=0, column=2, padx=5, pady=10)

        self.city_entry.bind('<Return>', lambda event: self.get_weather())

        self.create_main_weather_display()
        self.create_temperature_section()
        self.create_conditions_section()
        self.create_forecast_section()

    def create_main_weather_display(self):
        main_frame = tk.Frame(self.root, bg="#6db3f2")
        main_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)  # Changed from row=0 to row=1
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

        # City label
        self.city_label = tk.Label(main_frame, text="", font=self.medium_font, bg="#6db3f2", fg="white")
        self.city_label.grid(row=0, column=0, columnspan=2, pady=(0, 5), sticky="ew")

        # Weather icon label (emoji placeholder)
        self.icon_label = tk.Label(main_frame, text="☁️", font=("Helvetica", 48), bg="#6db3f2")
        self.icon_label.grid(row=1, column=0, columnspan=2, pady=(0, 5), sticky="ew")

        # Temperature label
        self.temp_label = tk.Label(main_frame, text="", font=self.large_font, bg="#6db3f2", fg="white")
        self.temp_label.grid(row=2, column=0, columnspan=2, pady=(0, 5), sticky="ew")

        # Weather description label
        self.desc_label = tk.Label(main_frame, text="", font=self.medium_font, bg="#6db3f2", fg="white")
        self.desc_label.grid(row=3, column=0, columnspan=2, pady=(0, 5), sticky="ew")

        # Country label
        self.country_label = tk.Label(main_frame, text="", font=self.small_font, bg="#6db3f2", fg="white")
        self.country_label.grid(row=4, column=0, columnspan=2, pady=(0, 5), sticky="ew")

    def create_temperature_section(self):
        temp_frame = tk.Frame(self.root, bg="#6db3f2")  # Changed from "#4a90e2"
        temp_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=50, pady=10)
        temp_frame.grid_columnconfigure(0, weight=1)
        temp_frame.grid_columnconfigure(1, weight=1)

        # High/Low temperature labels
        self.high_label = tk.Label(temp_frame, text="H: 91°F", font=self.small_font, bg="#6db3f2", fg="white")  # Changed bg
        self.high_label.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        self.low_label = tk.Label(temp_frame, text="L: 73°F", font=self.small_font, bg="#6db3f2", fg="white")  # Changed bg
        self.low_label.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

    def create_conditions_section(self):
        conditions_frame = tk.Frame(self.root, bg="#6db3f2")  # Changed from "#31618a"
        conditions_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=50, pady=10)
        conditions_frame.grid_columnconfigure(0, weight=1)
        conditions_frame.grid_columnconfigure(1, weight=1)

        # Humidity and wind labels
        self.humidity_label = tk.Label(conditions_frame, text="Humidity: 55%", font=self.small_font, bg="#6db3f2", fg="white")  # Changed bg
        self.humidity_label.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        self.wind_label = tk.Label(conditions_frame, text="Wind: 7 mph", font=self.small_font, bg="#6db3f2", fg="white")  # Changed bg
        self.wind_label.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

    def create_forecast_section(self):
        self.forecast_frame = tk.Frame(self.root, bg="#6db3f2")
        self.forecast_frame.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=30, pady=10)  # Changed from row=3 to row=4
        for i in range(5):
            self.forecast_frame.grid_columnconfigure(i, weight=1)

        # Create and store forecast card widgets
        self.forecast_cards = []
        for i in range(5):
            card = self.create_forecast_card(self.forecast_frame, i)
            self.forecast_cards.append(card)

        # Load last weather data if available
        self.show_last_weather()

    def create_forecast_card(self, parent, day_offset):
        # Create a single forecast card (day, icon, temp) for the forecast row
        card_font = font.Font(family="Helvetica", size=16, weight="bold")
        temp_font = font.Font(family="Helvetica", size=14)
        
        # Add black border to the frame
        frame = tk.Frame(parent, bg="#4a90e2", bd=2, relief="solid", highlightbackground="black", highlightthickness=2)
        frame.grid(row=0, column=day_offset, padx=4, pady=2, sticky="nsew")
        
        day_label = tk.Label(frame, text="", font=card_font, bg="#4a90e2", fg="white")
        day_label.pack(pady=(2,0), fill="x")
        
        icon_label = tk.Label(frame, text="", font=("Helvetica", 28), bg="#4a90e2")
        icon_label.pack(fill="x")
        
        temp_label = tk.Label(frame, text="", font=temp_font, bg="#4a90e2", fg="white")
        temp_label.pack(pady=(0,2), fill="x")
        
        return day_label, icon_label, temp_label

    def get_weather(self):
        # Fetch weather and forecast for the entered city
        city = self.city_var.get()
        if not city:
            self.city_label.config(text="Enter a city name")
            return
            
        try:
            data = fetch_weather_data(city)
            if data:
                # Try to fetch forecast, but don't fail if it doesn't work
                try:
                    forecast = fetch_5day_forecast(city)
                    data['forecast'] = forecast if forecast else []
                except Exception as e:
                    print(f"Forecast unavailable: {e}")
                    data['forecast'] = []
                
                self.display_weather(data)
                save_weather_data(data)
            else:
                # Clear display if city not found or API error
                self.city_label.config(text="City not found or API error")
                self.temp_label.config(text="")
                self.desc_label.config(text="")
                self.country_label.config(text="")
                self.icon_label.config(text="")
        except Exception as e:
            print(f"Error fetching weather: {e}")
            self.city_label.config(text="Error fetching weather data")

    def display_weather(self, data):
        # Update main weather display with current data
        self.city_label.config(text=f"{data['city']}")
        self.temp_label.config(text=f"{data['temperature']}°F")
        self.desc_label.config(text=f"{data['description'].capitalize()}")
        self.country_label.config(text=f"{data['country']}")
        
        # Set icon based on weather description
        icon = "☀️"
        desc = data['description'].lower()
        if "cloud" in desc:
            icon = "☁️"
        elif "rain" in desc:
            icon = "🌧️"
        elif "clear" in desc:
            icon = "☀️"
        elif "snow" in desc:
            icon = "❄️"
        elif "storm" in desc or "thunder" in desc:
            icon = "⛈️"
        elif "mist" in desc or "fog" in desc:
            icon = "🌫️"
        self.icon_label.config(text=icon)
        
        # Use actual min/max temperatures from the API
        temp_max = data.get('temp_max', data.get('temperature', 75))
        temp_min = data.get('temp_min', data.get('temperature', 65))
        
        print(f"Display - High: {temp_max}, Low: {temp_min}")  # Debug
        
        # Display the actual high/low temperatures
        self.high_label.config(text=f"H: {int(temp_max)}°F")
        self.low_label.config(text=f"L: {int(temp_min)}°F")
        
        # Use the utility functions for real wind and humidity data
        wind_info = format_wind_info(data.get('wind', {}))
        self.wind_label.config(text=wind_info)
        
        humidity_value = data.get('humidity', 0)
        if humidity_value:
            humidity_info = format_humidity(humidity_value)
            self.humidity_label.config(text=f"Humidity: {humidity_info}")
        else:
            self.humidity_label.config(text="Humidity: N/A")

        # Update 5-day forecast cards with forecast data
        forecast = data.get('forecast', [])
        for i, card in enumerate(self.forecast_cards):
            if i < len(forecast) and forecast[i]:
                day = forecast[i]['day']
                icon = forecast[i]['icon']
                # Format temperature with Fahrenheit for forecast
                temp = f"{forecast[i]['high']}°F/{forecast[i]['low']}°F"
                card[0].config(text=day)
                card[1].config(text=icon)
                card[2].config(text=temp)
            else:
                # Clear card if no forecast data
                card[0].config(text="")
                card[1].config(text="")
                card[2].config(text="")

        # Store current city data for favorites
        self.current_city_data = data

        # Update favorite button at the end
        self.update_favorite_button()

    def show_last_weather(self):
        # Load and display the most recently saved weather data
        try:
            data = load_weather_data()
            if data:
                self.display_weather(data)
        except Exception as e:
            print(f"Error loading last weather data: {e}")

    def get_city_input(self):
        """Get the city name from the input field."""
        return self.city_var.get().strip()

    def toggle_favorite(self):
        """Toggle the current city as a favorite."""
        if not hasattr(self, 'current_city_data') or not self.current_city_data:
            messagebox.showwarning("No City", "Please search for a city first!")
            return
        
        city = self.current_city_data['city']
        country = self.current_city_data['country']
        
        if is_favorite_city(city, country):
            # Remove from favorites
            if remove_favorite_city(city, country):
                self.update_favorite_button()
                messagebox.showinfo("Favorite Removed", f"{city} removed from favorites!")
        else:
            # Add to favorites
            if add_favorite_city(city, country):
                self.update_favorite_button()
                messagebox.showinfo("Favorite Added", f"{city} added to favorites!")

    def update_favorite_button(self):
        """Update the favorite button based on current city."""
        if not hasattr(self, 'favorite_btn'):
            return
            
        if not hasattr(self, 'current_city_data') or not self.current_city_data:
            self.favorite_btn.config(text="🤍")
            return
        
        city = self.current_city_data['city']
        country = self.current_city_data['country']
        
        if is_favorite_city(city, country):
            self.favorite_btn.config(text="❤️")  # Filled heart
        else:
            self.favorite_btn.config(text="🤍")  # Empty heart

    def show_favorites_menu(self):
        """Show a dropdown menu with favorite cities."""
        favorites = get_favorite_cities()
        
        if not favorites:
            messagebox.showinfo("No Favorites", "No favorite cities saved yet!")
            return
        
        # Create a simple selection window
        favorites_window = tk.Toplevel(self.root)
        favorites_window.title("Favorite Cities")
        favorites_window.geometry("300x400")
        favorites_window.configure(bg="#6db3f2")
        
        tk.Label(favorites_window, text="Favorite Cities", font=self.medium_font, bg="#6db3f2", fg="white").pack(pady=10)
        
        # Create listbox for favorites
        listbox = tk.Listbox(favorites_window, font=self.small_font, height=15)
        listbox.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Add favorites to listbox
        for fav in favorites:
            listbox.insert(tk.END, f"{fav['city']}, {fav['country']}")
        
        def load_selected_city():
            """Load weather for the selected favorite city."""
            selection = listbox.curselection()
            if selection:
                selected_fav = favorites[selection[0]]
                # Set the city in the entry field
                self.city_var.set(selected_fav['city'])
                # Get weather for the selected city
                self.get_weather()
                # Close the favorites window
                favorites_window.destroy()
            else:
                messagebox.showwarning("No Selection", "Please select a city from the list!")
        
        # Create button frame
        button_frame = tk.Frame(favorites_window, bg="#6db3f2")
        button_frame.pack(pady=10)
        
        # Load button
        load_btn = tk.Button(button_frame, text="Load Weather", command=load_selected_city, font=self.small_font)
        load_btn.pack(side=tk.LEFT, padx=5)
        
        # Close button
        close_btn = tk.Button(button_frame, text="Close", command=favorites_window.destroy, font=self.small_font)
        close_btn.pack(side=tk.LEFT, padx=5)

# Run the app if this file is executed directly
if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()
