import sys
import os

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Keep existing imports below:
import tkinter as tk
from tkinter import font, messagebox
import sys
import os
from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta

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
from features.weather_alert import check_weather_alerts, add_alert_rule, init_alerts_db
from features.team_feature import CitySuggestionApp


# Mock data import for testing purposes
# Set USE_MOCK to True to use mock data instead of real API calls
USE_MOCK = False
if USE_MOCK:
    from data.mock_weather import get_mock_weather_data

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tommy's Weather App")
        self.root.geometry("1400x900")  # Larger window
        self.root.resizable(True, True)
        self.root.configure(bg="#6db3f2")

        # BETTER grid configuration
        self.root.grid_rowconfigure(0, weight=0)  # Search bar
        self.root.grid_rowconfigure(1, weight=3)  # Main weather - MORE space
        self.root.grid_rowconfigure(2, weight=0)  # Temperature
        self.root.grid_rowconfigure(3, weight=0)  # Conditions  
        self.root.grid_rowconfigure(4, weight=1)  # Forecast
        
        self.root.grid_columnconfigure(0, weight=2)  # Main content
        self.root.grid_columnconfigure(1, weight=2)  # Main content
        self.root.grid_columnconfigure(2, weight=1)  # Right frame

        # Initialize the alerts database
        init_alerts_db()
        
        # Initialize variables
        self.city_var = tk.StringVar()
        self.current_city_data = None

        # UPDATED - Larger, better fonts
        self.large_font = font.Font(family="Helvetica", size=72, weight="bold")  # Temperature
        self.city_font = font.Font(family="Helvetica", size=32, weight="bold")   # City
        self.medium_font = font.Font(family="Helvetica", size=24)                # Description
        self.small_font = font.Font(family="Helvetica", size=18, weight="bold")  # Other elements
        self.country_font = font.Font(family="Helvetica", size=20)               # Country

        # Initialize dark mode state
        self.dark_mode = False
        
        # Define color schemes
        self.light_colors = {
            'bg': "#6db3f2",
            'search_bg': "#375874",
            'card_bg': "#2c2c2c",
            'text': "white",
            'search_text': "white"
        }
        
        self.dark_colors = {
            'bg': "#0d1117",           # Very dark background
            'search_bg': "#21262d",    # Darker search bar
            'card_bg': "#161b22",      # Dark card background
            'card_border': "#30363d",  # Card borders
            'text': "#f0f6fc",         # Light text
            'search_text': "#f0f6fc",  # Light search text
            'secondary_text': "#8b949e" # Gray text
        }

        # --- Search bar and buttons ---
        search_frame = tk.Frame(self.root, bg="#375874")
        search_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=10, pady=(10, 0))  # Changed columnspan to 3
        search_frame.grid_columnconfigure(0, weight=0)
        search_frame.grid_columnconfigure(1, weight=0)
        search_frame.grid_columnconfigure(2, weight=0)
        search_frame.grid_columnconfigure(3, weight=0)
        search_frame.grid_columnconfigure(4, weight=0)  # Dark mode button
        search_frame.grid_columnconfigure(5, weight=1)  # Clock spacing

        self.city_entry = tk.Entry(search_frame, textvariable=self.city_var, font=self.medium_font, width=18)
        self.city_entry.grid(row=0, column=0, padx=10, pady=10)

        # Get Weather button (existing)
        self.get_weather_btn = tk.Button(search_frame, text="Get Weather", font=self.small_font, command=self.get_weather)
        self.get_weather_btn.grid(row=0, column=1, padx=5, pady=10)

        # Favorites button (existing)
        self.favorites_btn = tk.Button(search_frame, text="⭐ Favorites", font=self.small_font, command=self.show_favorites_menu)
        self.favorites_btn.grid(row=0, column=2, padx=5, pady=10)

        # Dark Mode toggle (existing)
        self.dark_mode_btn = tk.Button(search_frame, text="🌙", font=self.small_font, command=self.toggle_dark_mode)
        self.dark_mode_btn.grid(row=0, column=3, padx=5, pady=10)

        # DIGITAL CLOCK (moved to column 4)
        self.clock_label = tk.Label(search_frame, text="", font=("Helvetica", 16, "bold"), bg="#375874", fg="white")
        self.clock_label.grid(row=0, column=5, sticky="e", padx=(20, 10), pady=10)

        # Suggest Cities button
        self.suggest_cities_btn = tk.Button(search_frame, text="🏙️ Suggest Cities", font=self.small_font, 
                                            command=self.show_city_recommendations)
        self.suggest_cities_btn.grid(row=0, column=4, padx=5, pady=10)

        # Store reference to search frame for theme updates
        self.search_frame = search_frame

        self.city_entry.bind('<Return>', lambda event: self.get_weather())

        # Start the clock
        self.update_clock()

        self.create_main_weather_display()
        self.create_temperature_section()
        self.create_conditions_section()
        self.create_forecast_section()
        self.right_frame_utilities()  

    def create_main_weather_display(self):
        self.main_frame = tk.Frame(self.root, bg="#6db3f2")
        self.main_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=20, pady=20)
        
        # Configure main frame for proper centering
        self.main_frame.grid_rowconfigure(0, weight=0)
        self.main_frame.grid_rowconfigure(1, weight=1)  # Icon gets more space
        self.main_frame.grid_rowconfigure(2, weight=0)
        self.main_frame.grid_rowconfigure(3, weight=0)
        self.main_frame.grid_rowconfigure(4, weight=0)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # ENLARGED City label
        self.city_label = tk.Label(self.main_frame, text="", font=("Helvetica", 32, "bold"), bg="#6db3f2", fg="white")
        self.city_label.grid(row=0, column=0, pady=(20, 10), sticky="ew")

        # ENLARGED Weather icon
        self.icon_label = tk.Label(self.main_frame, text="☁️", font=("Helvetica", 80), bg="#6db3f2")
        self.icon_label.grid(row=1, column=0, pady=(10, 15), sticky="ew")

        # ENLARGED Temperature
        self.temp_label = tk.Label(self.main_frame, text="", font=("Helvetica", 72, "bold"), bg="#6db3f2", fg="white")
        self.temp_label.grid(row=2, column=0, pady=(0, 10), sticky="ew")

        # ENLARGED Description
        self.desc_label = tk.Label(self.main_frame, text="", font=("Helvetica", 24), bg="#6db3f2", fg="white")
        self.desc_label.grid(row=3, column=0, pady=(0, 10), sticky="ew")

        # ENLARGED Country
        self.country_label = tk.Label(self.main_frame, text="", font=("Helvetica", 20), bg="#6db3f2", fg="white")
        self.country_label.grid(row=4, column=0, pady=(0, 20), sticky="ew")

    def create_temperature_section(self):
        self.temp_frame = tk.Frame(self.root, bg="#6db3f2")
        self.temp_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=80, pady=15)
        self.temp_frame.grid_columnconfigure(0, weight=1)
        self.temp_frame.grid_columnconfigure(1, weight=1)

        # ENLARGED High/Low labels
        self.high_label = tk.Label(self.temp_frame, text="H: 91°F", font=("Helvetica", 22, "bold"), bg="#6db3f2", fg="white")
        self.high_label.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        
        self.low_label = tk.Label(self.temp_frame, text="L: 73°F", font=("Helvetica", 22, "bold"), bg="#6db3f2", fg="white")
        self.low_label.grid(row=0, column=1, padx=20, pady=10, sticky="ew")

    def create_conditions_section(self):
        self.conditions_frame = tk.Frame(self.root, bg="#6db3f2")
        self.conditions_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=80, pady=15)
        self.conditions_frame.grid_columnconfigure(0, weight=1)
        self.conditions_frame.grid_columnconfigure(1, weight=1)

        # ENLARGED Humidity and wind labels
        self.humidity_label = tk.Label(self.conditions_frame, text="Humidity: 55%", font=("Helvetica", 20), bg="#6db3f2", fg="white")
        self.humidity_label.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        
        self.wind_label = tk.Label(self.conditions_frame, text="Wind: 7 mph", font=("Helvetica", 20), bg="#6db3f2", fg="white")
        self.wind_label.grid(row=0, column=1, padx=20, pady=10, sticky="ew")

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
        card_font = font.Font(family="Helvetica", size=16, weight="bold")
        temp_font = font.Font(family="Helvetica", size=14, weight="bold")
        
        # BETTER SIZED forecast cards
        frame = tk.Frame(parent, bg="#4a90e2", bd=2, relief="solid", highlightbackground="black", highlightthickness=1)
        frame.grid(row=0, column=day_offset, padx=8, pady=8, sticky="nsew")
        
        # Configure internal grid
        frame.grid_rowconfigure(0, weight=0)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_rowconfigure(2, weight=0)
        frame.grid_columnconfigure(0, weight=1)
        
        # Use grid instead of pack for better control
        day_label = tk.Label(frame, text="", font=card_font, bg="#4a90e2", fg="white")
        day_label.grid(row=0, column=0, pady=(12,5), sticky="ew")
        
        icon_label = tk.Label(frame, text="", font=("Helvetica", 44), bg="#4a90e2")
        icon_label.grid(row=1, column=0, pady=8, sticky="nsew")
        
        temp_label = tk.Label(frame, text="", font=temp_font, bg="#4a90e2", fg="white")
        temp_label.grid(row=2, column=0, pady=(5,12), sticky="ew")
        
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

        # UPDATE RIGHT FRAME CARDS WITH API DATA
        self.update_right_frame_cards(data)

        # Check for weather alerts and update the card
        self.update_weather_alerts(data)

        # Update moon phase
        self.update_moon_phase()

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
        favorites_window.geometry("400x500")
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

    def right_frame_utilities(self):
        # Create right frame that spans alongside the main content
        self.right_frame = tk.Frame(self.root, bg="#6db3f2")
        self.right_frame.grid(row=1, column=2, rowspan=4, sticky="nsew", padx=10, pady=10)

        # Configure right frame grid weights for proper scaling
        for i in range(4):  # 4 rows
            self.right_frame.grid_rowconfigure(i, weight=1)
        for j in range(2):  # 2 columns
            self.right_frame.grid_columnconfigure(j, weight=1)

        card_padx = 10
        card_pady = 10

        # Row 0
        self.alerts_frame = tk.Frame(self.right_frame, bg="#2c2c2c", relief="solid", bd=1)
        self.alerts_frame.grid(row=0, column=0, sticky="nsew", padx=card_padx, pady=card_pady)

        tk.Label(self.alerts_frame, text="⚠️ WEATHER ALERTS", font=("Helvetica", 10), bg="#2c2c2c", fg="gray").grid(row=0, column=0, sticky="w", padx=10, pady=(8, 2))
        self.alert_title_label = tk.Label(self.alerts_frame, text="Heat Advisory & 1 More", font=("Helvetica", 16, "bold"), bg="#2c2c2c", fg="white")
        self.alert_title_label.grid(row=1, column=0, sticky="w", padx=15, pady=(5, 0))
        
        self.alert_desc_label = tk.Label(self.alerts_frame, text="Heat Advisory. These conditions are expected by\n11:00 AM (EDT), Friday, July 25. Additional alert: Air\nQuality Alert.", 
                                        font=("Helvetica", 9), bg="#2c2c2c", fg="white", justify="left", wraplength=250)
        self.alert_desc_label.grid(row=2, column=0, sticky="w", padx=12, pady=(5, 0))
        
        tk.Label(self.alerts_frame, text="National Weather Service", font=("Helvetica", 8), bg="#2c2c2c", fg="gray").grid(row=3, column=0, sticky="w", padx=10, pady=(5, 8))

        # SUNRISE/SUNSET CARD (Second position - under weather alerts)
        self.sunrise_sunset_frame = tk.Frame(self.right_frame, bg="#2c2c2c", relief="solid", bd=1)
        self.sunrise_sunset_frame.grid(row=0, column=1, sticky="nsew", padx=card_padx, pady=card_pady)
        self.sunrise_sunset_frame.grid_columnconfigure(0, weight=1)

        tk.Label(self.sunrise_sunset_frame, text="🌅 SUNRISE & SUNSET", font=("Helvetica", 10), bg="#2c2c2c", fg="gray").grid(row=0, column=0, sticky="w", padx=10, pady=(8, 0))

        # Sunrise label
        self.sunrise_label = tk.Label(self.sunrise_sunset_frame, text="Sunrise: 6:45 AM", font=("Helvetica", 14, "bold"), bg="#2c2c2c", fg="white")
        self.sunrise_label.grid(row=1, column=0, sticky="w", padx=10, pady=(5, 2))

        # Sunset label  
        self.sunset_label = tk.Label(self.sunrise_sunset_frame, text="Sunset: 7:32 PM", font=("Helvetica", 14, "bold"), bg="#2c2c2c", fg="white")
        self.sunset_label.grid(row=2, column=0, sticky="w", padx=10, pady=(2, 5))

        # Day length info
        self.day_length_label = tk.Label(self.sunrise_sunset_frame, text="Day length: 12h 47m", font=("Helvetica", 10), bg="#2c2c2c", fg="gray")
        self.day_length_label.grid(row=3, column=0, sticky="w", padx=10, pady=(0, 8))

        # Precipitation card (moved to third position)  
        self.precip_frame = tk.Frame(self.right_frame, bg="#2c2c2c", relief="solid", bd=1)
        self.precip_frame.grid(row=1, column=0, sticky="nsew", padx=card_padx, pady=card_pady)
        self.precip_frame.grid_columnconfigure(0, weight=1)
        
        tk.Label(self.precip_frame, text="💧 PRECIPITATION", font=("Helvetica", 10), bg="#2c2c2c", fg="gray").grid(row=0, column=0, sticky="w", padx=10, pady=(8, 0))
        self.precip_label = tk.Label(self.precip_frame, text='0"', font=("Helvetica", 32, "bold"), bg="#2c2c2c", fg="white")
        self.precip_label.grid(row=1, column=0, sticky="w", padx=10)
        tk.Label(self.precip_frame, text="Today", font=("Helvetica", 12), bg="#2c2c2c", fg="white").grid(row=2, column=0, sticky="w", padx=10)
        self.precip_next_label = tk.Label(self.precip_frame, text="Next expected is .6\" Sun.", font=("Helvetica", 11), bg="#2c2c2c", fg="white")
        self.precip_next_label.grid(row=3, column=0, sticky="w", padx=10, pady=(0, 8))

        # Feels like card
        self.feels_frame = tk.Frame(self.right_frame, bg="#2c2c2c", relief="solid", bd=1)
        self.feels_frame.grid(row=1, column=1, sticky="nsew", padx=card_padx, pady=card_pady)
        self.feels_frame.grid_columnconfigure(0, weight=1)
        
        tk.Label(self.feels_frame, text="🌡️ FEELS LIKE", font=("Helvetica", 10), bg="#2c2c2c", fg="gray").grid(row=0, column=0, sticky="w", padx=10, pady=(8, 0))
        self.feels_like_label = tk.Label(self.feels_frame, text="74°", font=("Helvetica", 32, "bold"), bg="#2c2c2c", fg="white")
        self.feels_like_label.grid(row=1, column=0, sticky="w", padx=10)
        tk.Label(self.feels_frame, text="Wind is making it feel cooler.", font=("Helvetica", 11), bg="#2c2c2c", fg="white").grid(row=2, column=0, sticky="w", padx=10, pady=(0, 8))

        # Pressure card
        self.pressure_frame = tk.Frame(self.right_frame, bg="#2c2c2c", relief="solid", bd=1)
        self.pressure_frame.grid(row=2, column=0, sticky="nsew", padx=card_padx, pady=card_pady)
        self.pressure_frame.grid_columnconfigure(0, weight=1)
        
        tk.Label(self.pressure_frame, text="🔘 PRESSURE", font=("Helvetica", 10), bg="#2c2c2c", fg="gray").grid(row=0, column=0, sticky="w", padx=10, pady=(8, 0))
        
        self.pressure_label = tk.Label(self.pressure_frame, text="29.98\ninHg", font=("Helvetica", 18, "bold"), bg="#2c2c2c", fg="white", justify="center")
        self.pressure_label.grid(row=1, column=0, padx=10, pady=5)
        
        tk.Label(self.pressure_frame, text="Low                    High", font=("Helvetica", 10), bg="#2c2c2c", fg="white").grid(row=2, column=0, padx=10, pady=(0, 8))

        # Averages card
        self.averages_frame = tk.Frame(self.right_frame, bg="#2c2c2c", relief="solid", bd=1)
        self.averages_frame.grid(row=3, column=0, sticky="nsew", padx=card_padx, pady=card_pady)
        self.averages_frame.grid_columnconfigure(0, weight=1)
        
        tk.Label(self.averages_frame, text="📊 AVERAGES", font=("Helvetica", 10), bg="#2c2c2c", fg="gray").grid(row=0, column=0, sticky="w", padx=10, pady=(8, 0))
        self.avg_temp_label = tk.Label(self.averages_frame, text="+14°", font=("Helvetica", 32, "bold"), bg="#2c2c2c", fg="white")
        self.avg_temp_label.grid(row=1, column=0, sticky="w", padx=10)
        tk.Label(self.averages_frame, text="above average daily high", font=("Helvetica", 11), bg="#2c2c2c", fg="white").grid(row=2, column=0, sticky="w", padx=10)
        
        # Today/Average comparison
        comparison_frame = tk.Frame(self.averages_frame, bg="#2c2c2c")
        comparison_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(5, 0))
        comparison_frame.grid_columnconfigure(0, weight=1)
        comparison_frame.grid_columnconfigure(1, weight=1)
        
        tk.Label(comparison_frame, text="Today", font=("Helvetica", 10), bg="#2c2c2c", fg="gray").grid(row=0, column=0, sticky="w")
        self.today_high_label = tk.Label(comparison_frame, text="H:96°", font=("Helvetica", 10), bg="#2c2c2c", fg="white")
        self.today_high_label.grid(row=0, column=1, sticky="e")
        
        tk.Label(comparison_frame, text="Average", font=("Helvetica", 10), bg="#2c2c2c", fg="gray").grid(row=1, column=0, sticky="w", pady=(0, 8))
        self.avg_high_label = tk.Label(comparison_frame, text="H:82°", font=("Helvetica", 10), bg="#2c2c2c", fg="white")
        self.avg_high_label.grid(row=1, column=1, sticky="e", pady=(0, 8))

        # Moon phase card (move to row 4, column 1)
        self.moon_frame = tk.Frame(self.right_frame, bg="#2c2c2c", relief="solid", bd=1)
        self.moon_frame.grid(row=3, column=1, sticky="nsew", padx=card_padx, pady=card_pady)
        self.moon_frame.grid_columnconfigure(0, weight=1)

        tk.Label(self.moon_frame, text="🌙 MOON PHASE", font=("Helvetica", 10), bg="#2c2c2c", fg="gray").grid(row=0, column=0, sticky="w", padx=10, pady=(8, 0))

        # Large moon emoji
        self.moon_phase_label = tk.Label(self.moon_frame, text="🌕", font=("Helvetica", 32), bg="#2c2c2c", fg="white")
        self.moon_phase_label.grid(row=1, column=0, padx=10, pady=(5, 0))

        # Moon phase name
        self.moon_name_label = tk.Label(self.moon_frame, text="Full Moon", font=("Helvetica", 14, "bold"), bg="#2c2c2c", fg="white")
        self.moon_name_label.grid(row=2, column=0, padx=10, pady=(0, 2))

        # Illumination percentage
        self.moon_illumination_label = tk.Label(self.moon_frame, text="100% illuminated", font=("Helvetica", 10), bg="#2c2c2c", fg="white")
        self.moon_illumination_label.grid(row=3, column=0, padx=10, pady=(0, 2))

        # Next full moon
        self.moon_next_label = tk.Label(self.moon_frame, text="Next full moon: In 29 days", font=("Helvetica", 9), bg="#2c2c2c", fg="gray")
        self.moon_next_label.grid(row=4, column=0, padx=10, pady=(0, 8))

        # UV INDEX CARD (NEW - Add in row 3, column 1)
        self.uv_frame = tk.Frame(self.right_frame, bg="#2c2c2c", relief="solid", bd=1)
        self.uv_frame.grid(row=2, column=1, sticky="nsew", padx=card_padx, pady=card_pady)
        self.uv_frame.grid_columnconfigure(0, weight=1)

        tk.Label(self.uv_frame, text="☀️ UV INDEX", font=("Helvetica", 10), bg="#2c2c2c", fg="gray").grid(row=0, column=0, sticky="w", padx=10, pady=(8, 0))
        
        # UV Index value (large display)
        self.uv_index_label = tk.Label(self.uv_frame, text="8", font=("Helvetica", 32, "bold"), bg="#2c2c2c", fg="white")
        self.uv_index_label.grid(row=1, column=0, padx=10, pady=(5, 0))
        
        # UV level description
        self.uv_level_label = tk.Label(self.uv_frame, text="Very High", font=("Helvetica", 14, "bold"), bg="#2c2c2c", fg="white")
        self.uv_level_label.grid(row=2, column=0, padx=10, pady=(0, 2))
        
        # UV advice
        self.uv_advice_label = tk.Label(self.uv_frame, text="Use sunscreen, wear protective\nclothing and sunglasses.", 
                                       font=("Helvetica", 9), bg="#2c2c2c", fg="white", justify="left")
        self.uv_advice_label.grid(row=3, column=0, padx=10, pady=(0, 8))

        # Bind moon phase update to the weather data fetch
        self.original_display_weather = self.display_weather
        def display_weather_with_moon(data):
            self.original_display_weather(data)
            self.update_moon_phase()  # Update moon phase after weather data is displayed
        self.display_weather = display_weather_with_moon

    def update_moon_phase(self):
        """Update the moon phase card with current moon data."""
        try:
            from features.moon_phase import get_moon_data, get_next_full_moon
            
            moon_data = get_moon_data()
            next_full = get_next_full_moon()
            
            # Update moon phase labels
            if hasattr(self, 'moon_phase_label'):
                self.moon_phase_label.config(text=moon_data['emoji'])
                self.moon_name_label.config(text=moon_data['phase_name'])
                self.moon_illumination_label.config(text=f"{moon_data['illumination']}% illuminated")
                
                # Format next full moon date
                days_until_full = (next_full - datetime.now()).days
                if days_until_full == 0:
                    next_full_text = "Today"
                elif days_until_full == 1:
                    next_full_text = "Tomorrow"
                else:
                    next_full_text = f"In {days_until_full} days"
                
                self.moon_next_label.config(text=f"Next full moon: {next_full_text}")
            
        except ImportError:
            # Fallback if moon_phase module has issues
            if hasattr(self, 'moon_phase_label'):
                self.moon_phase_label.config(text="🌙")
                self.moon_name_label.config(text="Moon Phase")
                self.moon_illumination_label.config(text="-- % illuminated")
                self.moon_next_label.config(text="Next full moon: --")

    def add_custom_alert(self, city, country, alert_type, threshold_value, condition=">="):
        """Add a custom weather alert rule."""
        success = add_alert_rule(city, country, alert_type, threshold_value, condition)
        if success:
            messagebox.showinfo("Alert Added", f"Alert rule added for {city}: {alert_type} {condition} {threshold_value}")
        else:
            messagebox.showerror("Error", "Failed to add alert rule.")

    def update_weather_alerts(self, data):
        """Update the weather alerts card with actual alert data from One Call API."""
        if not hasattr(self, 'alert_title_label'):
            return
        
        # Get alerts from the API data
        api_alerts = data.get('alerts', [])
        
        # Also check your custom alert rules
        custom_alerts = check_weather_alerts(data)
        
        # Combine both types of alerts
        all_alerts = api_alerts + custom_alerts
        
        if all_alerts and len(all_alerts) > 0:
            # Display the first (most important) alert
            first_alert = all_alerts[0]
            
            # Handle API alerts vs custom alerts differently
            if 'event' in first_alert:  # API alert
                title = first_alert.get('event', 'Weather Alert')
                description = first_alert.get('description', 'No details available')
            else:  # Custom alert
                title = first_alert.get('alert_type', 'Weather Alert').replace('_', ' ').title()
                description = first_alert.get('message', 'No details available')
            
            # Update alert title - show count if multiple alerts
            if len(all_alerts) > 1:
                title = f"{title} & {len(all_alerts) - 1} More"
            
            self.alert_title_label.config(text=title, fg="#ff8800")  # Orange for alerts
            
            # Truncate description if too long for display
            if len(description) > 150:
                display_message = description[:150] + "..."
            else:
                display_message = description
            
            self.alert_desc_label.config(text=display_message)
                
        else:
            # No alerts - show default message
            self.alert_title_label.config(text="No Active Alerts", fg="white")
            self.alert_desc_label.config(text="No weather alerts in effect for this area.")

    def update_right_frame_cards(self, data):
        """Update all right frame cards with One Call API data."""
        try:
            print(f"Updating right frame cards with data keys: {list(data.keys())}")  # Debug
            
            # Update Feels Like temperature
            feels_like = data.get('feels_like', data.get('temperature', 0))
            if hasattr(self, 'feels_like_label'):
                self.feels_like_label.config(text=f"{int(feels_like)}°")
                print(f"Updated feels like: {feels_like}")  # Debug
            
            # Update Pressure
            pressure = data.get('pressure', 0)
            if hasattr(self, 'pressure_label') and pressure:
                # Convert hPa to inHg (1 hPa = 0.02953 inHg)
                pressure_inhg = pressure * 0.02953
                self.pressure_label.config(text=f"{pressure_inhg:.2f}\ninHg")
                print(f"Updated pressure: {pressure} hPa -> {pressure_inhg:.2f} inHg")  # Debug
            
            # Update Precipitation
            precipitation = data.get('precipitation', 0)
            if hasattr(self, 'precip_label'):
                self.precip_label.config(text=f'{precipitation:.1f}"')
                print(f"Updated precipitation: {precipitation}")  # Debug
            
            # Update Sunrise/Sunset if available
            if hasattr(self, 'sunrise_label') and data.get('sunrise'):
                sunrise_time = datetime.fromtimestamp(data['sunrise']).strftime('%I:%M %p')
                sunset_time = datetime.fromtimestamp(data['sunset']).strftime('%I:%M %p')
                
                self.sunrise_label.config(text=f"Sunrise: {sunrise_time}")
                self.sunset_label.config(text=f"Sunset: {sunset_time}")
                
                # Calculate day length
                sunrise_dt = datetime.fromtimestamp(data['sunrise'])
                sunset_dt = datetime.fromtimestamp(data['sunset'])
                day_length = sunset_dt - sunrise_dt
                hours = day_length.seconds // 3600
                minutes = (day_length.seconds % 3600) // 60
                self.day_length_label.config(text=f"Day length: {hours}h {minutes}m")
                
                print(f"Updated sunrise/sunset: {sunrise_time} / {sunset_time}")  # Debug
            
            # Update averages (using current temp for now)
            current_temp = data.get('temperature', 0)
            temp_max = data.get('temp_max', current_temp)
            if hasattr(self, 'today_high_label'):
                self.today_high_label.config(text=f"H:{int(temp_max)}°")
                print(f"Updated today high: {temp_max}")  # Debug
    
        except Exception as e:
            print(f"Error updating right frame cards: {e}")
            import traceback
            traceback.print_exc()
    
    def update_clock(self):
        """Update the digital clock display."""
        try:
            # Get current time
            now = datetime.now()
            
            # Format time as HH:MM:SS AM/PM
            time_string = now.strftime("%I:%M:%S %p")
            
            # Format date as Day, Month DD, YYYY
            date_string = now.strftime("%A, %B %d, %Y")
            
            # Update clock label with time and date
            clock_text = f"{time_string}\n{date_string}"
            self.clock_label.config(text=clock_text)
            
            # Schedule next update in 1000ms (1 second)
            self.root.after(1000, self.update_clock)
            
        except Exception as e:
            print(f"Error updating clock: {e}")
            # Try again in 1 second even if there's an error
            self.root.after(1000, self.update_clock)

    def get_timezone_time(self, timezone_offset=None):
        """Get time for a specific timezone (for future enhancement)."""
        if timezone_offset is not None:
            # Convert timezone offset from seconds to hours
            offset_hours = timezone_offset / 3600
            utc_time = datetime.utcnow()
            local_time = utc_time + timedelta(hours=offset_hours)
            return local_time
        else:
            return datetime.now()

    def toggle_dark_mode(self):
        """Toggle between light and dark mode."""
        self.dark_mode = not self.dark_mode
        
        if self.dark_mode:
            # Switch to dark mode
            colors = self.dark_colors
            self.dark_mode_btn.config(text="☀️")  # Sun icon for switching back to light
        else:
            # Switch to light mode
            colors = self.light_colors
            self.dark_mode_btn.config(text="🌙")  # Moon icon for switching to dark
        
        # Update all UI elements
        self.apply_theme(colors)

    def apply_theme(self, colors):
        """Apply the selected color theme to all UI elements."""
        try:
            # Update root window
            self.root.configure(bg=colors['bg'])
            
            # Update search frame
            self.search_frame.configure(bg=colors['search_bg'])
            self.clock_label.configure(bg=colors['search_bg'], fg=colors['search_text'])
            
            # Update main weather display
            if hasattr(self, 'main_frame'):
                self.main_frame.configure(bg=colors['bg'])
                self.city_label.configure(bg=colors['bg'], fg=colors['text'])
                self.icon_label.configure(bg=colors['bg'])
                self.temp_label.configure(bg=colors['bg'], fg=colors['text'])
                self.desc_label.configure(bg=colors['bg'], fg=colors['text'])
                self.country_label.configure(bg=colors['bg'], fg=colors['text'])
            
            # Update temperature section
            if hasattr(self, 'temp_frame'):
                self.temp_frame.configure(bg=colors['bg'])
                self.high_label.configure(bg=colors['bg'], fg=colors['text'])
                self.low_label.configure(bg=colors['bg'], fg=colors['text'])
            
            # Update conditions section
            if hasattr(self, 'conditions_frame'):
                self.conditions_frame.configure(bg=colors['bg'])
                self.humidity_label.configure(bg=colors['bg'], fg=colors['text'])
                self.wind_label.configure(bg=colors['bg'], fg=colors['text'])
            
            # Update forecast section
            if hasattr(self, 'forecast_frame'):
                self.forecast_frame.configure(bg=colors['bg'])
            
            # Update right frame
            if hasattr(self, 'right_frame'):
                self.right_frame.configure(bg=colors['bg'])
            
            # Update all right frame cards
            self.update_right_frame_theme(colors)
            
        except Exception as e:
            print(f"Error applying theme: {e}")

    def update_right_frame_theme(self, colors):
        """Update the theme for all right frame cards."""
        try:
            # List of all card frames and their labels
            card_elements = [
                # Weather alerts card
                ('alerts_frame', [
                    'alert_title_label', 'alert_desc_label'
                ]),
                # Sunrise/sunset card
                ('sunrise_sunset_frame', [
                    'sunrise_label', 'sunset_label', 'day_length_label'
                ]),
                # Precipitation card
                ('precip_frame', [
                    'precip_label', 'precip_next_label'
                ]),
                # Feels like card
                ('feels_frame', [
                    'feels_like_label'
                ]),
                # Pressure card
                ('pressure_frame', [
                    'pressure_label'
                ]),
                # Averages card
                ('averages_frame', [
                    'avg_temp_label', 'today_high_label', 'avg_high_label'
                ]),
                # Moon phase card
                ('moon_frame', [
                    'moon_phase_label', 'moon_name_label', 'moon_illumination_label', 'moon_next_label'
                ]),
                # UV index card
                ('uv_frame', [
                    'uv_index_label', 'uv_level_label', 'uv_advice_label'
                ])
            ]
            
            # Update each card
            for frame_name, label_names in card_elements:
                if hasattr(self, frame_name):
                    frame = getattr(self, frame_name)
                    frame.configure(bg=colors['card_bg'])
                    
                    # Update all child widgets in the frame
                    for widget in frame.winfo_children():
                        if isinstance(widget, tk.Label):
                            if widget.cget('fg') in ['white', 'gray', '#ff8800']:
                                widget.configure(bg=colors['card_bg'])

            # ADD FORECAST CARDS THEME UPDATE - MOVED INSIDE TRY BLOCK
            if hasattr(self, 'forecast_cards'):
                for card in self.forecast_cards:
                    day_label, icon_label, temp_label = card
                    card_frame = day_label.master
                    
                    # Update forecast card colors based on theme
                    if self.dark_mode:
                        card_frame.configure(bg=colors['card_bg'])
                    else:
                        card_frame.configure(bg="#4a90e2")  # Original blue
                    
                    # Update all labels in forecast card
                    current_bg = card_frame.cget('bg')
                    day_label.configure(bg=current_bg)
                    icon_label.configure(bg=current_bg)
                    temp_label.configure(bg=current_bg)
        except Exception as e:
            print(f"Error updating right frame theme: {e}")
    
    def show_city_recommendations(self):
        """Show the city recommendation feature."""
        app = CitySuggestionApp(self.root)
        app.show_preference_dialog()
#
# Run the app if this file is executed directly
if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()
