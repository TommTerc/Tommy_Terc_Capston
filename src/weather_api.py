import os
import requests
from dotenv import load_dotenv
from collections import defaultdict
from datetime import datetime

# Load environment variables from the .env file (for API key)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

# Retrieve the OpenWeatherMap API key from environment variables
API_KEY = os.getenv('OPENWEATHER_API_KEY')

# Define the base URLs for current weather and forecast endpoints
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'
FORECAST_URL = 'https://api.openweathermap.org/data/2.5/forecast'

def fetch_weather_data(city):
    """
    Fetch current weather data for a given city from OpenWeatherMap API.
    Returns a dictionary with temperature, description, city, and country.
    """
    try:
        # Make a GET request to the current weather endpoint with city and API key
        response = requests.get(BASE_URL, params={'q': city, 'appid': API_KEY, 'units': 'imperial'})
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        
        # Extract weather information including actual min/max temps
        weather_info = {
            'temperature': round(data['main']['temp']),
            'description': data['weather'][0]['description'],
            'city': data['name'],
            'country': data['sys']['country'],
            'humidity': data['main'].get('humidity'),
            'wind': data.get('wind', {}),
            # Get actual min/max from API response
            'temp_max': round(data['main'].get('temp_max', data['main']['temp'])),
            'temp_min': round(data['main'].get('temp_min', data['main']['temp'])),
            'feels_like': round(data['main'].get('feels_like', data['main']['temp']))
        }
        
        print(f"API Response - temp_max: {data['main'].get('temp_max')}, temp_min: {data['main'].get('temp_min')}")  # Debug
        
        return weather_info
        
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None

def fetch_forecast(lat, lon):
    """
    Fetch the 5-day/3-hour forecast data for given latitude and longitude.
    Returns the full JSON response from the API.
    """
    try:
        params = {
            'lat': lat,
            'lon': lon,
            'appid': API_KEY,
            'units': 'imperial'
        }
        # Make a GET request to the forecast endpoint with coordinates and API key
        response = requests.get(FORECAST_URL, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        # Handle errors during the API call
        print(f"Error fetching forecast: {e}")
        return None

def fetch_5day_forecast(city):
    """
    Fetch and process the 5-day forecast for a city.
    Returns a list of dictionaries, each representing a day's forecast.
    """
    try:
        # Make a GET request to the forecast endpoint with city and API key
        response = requests.get(FORECAST_URL, params={'q': city, 'appid': API_KEY, 'units': 'imperial'})
        response.raise_for_status()
        data = response.json()
        # Group forecast entries by day
        days = defaultdict(list)
        for entry in data['list']:
            dt = datetime.fromtimestamp(entry['dt'])
            days[dt.date()].append(entry)
        forecast = []
        for i, (day, entries) in enumerate(days.items()):
            # Pick the entry closest to 12:00 for each day
            target = min(entries, key=lambda e: abs(datetime.fromtimestamp(e['dt']).hour - 12))
            weather = target['weather'][0]
            forecast.append({
                'day': day.strftime('%a'),
                'icon': get_icon_from_description(weather['description']),
                'high': int(target['main']['temp_max']),
                'low': int(target['main']['temp_min'])
            })
            # Only keep 5 days
            if len(forecast) == 5:
                break
        return forecast
    except Exception as e:
        # Handle errors during the API call or processing
        print(f"Error fetching 5-day forecast: {e}")
        return []

def get_icon_from_description(desc):
    """
    Map a weather description string to a weather emoji/icon.
    """
    desc = desc.lower()
    if "cloud" in desc:
        return "☁️"
    elif "rain" in desc:
        return "🌧️"
    elif "clear" in desc:
        return "☀️"
    elif "snow" in desc:
        return "❄️"
    elif "storm" in desc:
        return "⛈️"
    elif "fog" in desc or "mist" in desc:
        return "🌫️"
    else:
        return "🌡️"