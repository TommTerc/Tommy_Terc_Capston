import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
API_KEY = os.getenv('OPENWEATHER_API_KEY')

def get_coordinates(city):
    """Get latitude and longitude for a city using Geocoding API"""
    geocoding_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
    
    try:
        response = requests.get(geocoding_url)
        response.raise_for_status()
        data = response.json()
        
        if data:
            location = data[0]
            # Extract state if available (usually in 'state' field for US locations)
            state = location.get('state', '')
            return location['lat'], location['lon'], location['name'], location['country'], state
        return None, None, None, None, None
        
    except Exception as e:
        print(f"Error getting coordinates: {e}")
        return None, None, None, None, None

def fetch_weather_data(city):
    """Fetch comprehensive weather data using One Call API 3.0"""
    # First get coordinates including state
    lat, lon, city_name, country, state = get_coordinates(city)
    
    if not lat or not lon:
        print(f"Could not find coordinates for {city}")
        return None
    
    # Use One Call API 3.0
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={API_KEY}&units=imperial"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        raw_data = response.json()
        current = raw_data['current']
        daily = raw_data['daily'][0]  # Today's daily data
        
        # Extract comprehensive weather data
        data = {
            'city': city_name,
            'state': state,  # Add this line
            'country': country,
            'lat': lat,
            'lon': lon,
            'temperature': round(current['temp']),
            'temp_max': round(daily['temp']['max']),
            'temp_min': round(daily['temp']['min']),
            'feels_like': round(current['feels_like']),
            'description': current['weather'][0]['description'],
            'humidity': current['humidity'],
            'pressure': current['pressure'],
            'wind_speed': current.get('wind_speed', 0),
            'wind_deg': current.get('wind_deg', 0),
            'visibility': current.get('visibility', 0) / 1000,  # Convert to km
            'uvi': current.get('uvi', 0),
            'clouds': current.get('clouds', 0),
            'dew_point': round(current.get('dew_point', 0)),
            'sunrise': current.get('sunrise'),
            'sunset': current.get('sunset'),
            
            # Weather alerts (if any)
            'alerts': raw_data.get('alerts', []),
            
            # Wind data formatted
            'wind': {
                'speed': current.get('wind_speed', 0),
                'deg': current.get('wind_deg', 0),
                'gust': current.get('wind_gust', 0)
            }
        }
        
        # Add precipitation data if available
        if 'rain' in current:
            data['precipitation'] = current['rain'].get('1h', 0)
        elif 'snow' in current:
            data['precipitation'] = current['snow'].get('1h', 0)
        else:
            data['precipitation'] = 0
            
        return data
        
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response: {response.text}")
        return None
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None

def fetch_5day_forecast(city):
    """Fetch 5-day forecast using One Call API 3.0 daily data"""
    # First get coordinates
    lat, lon, city_name, country, state = get_coordinates(city)
    
    if not lat or not lon:
        return []
    
    # Use One Call API 3.0
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={API_KEY}&units=imperial"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        raw_data = response.json()
        daily_data = raw_data['daily'][1:6]  # Skip today, get next 5 days
        
        forecast = []
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        
        for i, day_data in enumerate(daily_data):
            # Calculate day name
            future_date = datetime.now() + timedelta(days=i+1)
            day_name = days[future_date.weekday()]
            
            # Weather icon mapping
            weather_main = day_data['weather'][0]['main'].lower()
            if 'cloud' in weather_main:
                icon = "☁️"
            elif 'rain' in weather_main:
                icon = "🌧️"
            elif 'clear' in weather_main:
                icon = "☀️"
            elif 'snow' in weather_main:
                icon = "❄️"
            elif 'thunder' in weather_main:
                icon = "⛈️"
            else:
                icon = "🌤️"
            
            forecast.append({
                'day': day_name,
                'high': round(day_data['temp']['max']),
                'low': round(day_data['temp']['min']),
                'icon': icon,
                'description': day_data['weather'][0]['description']
            })
        
        return forecast
        
    except Exception as e:
        print(f"Error fetching forecast: {e}")
        return []

def get_weather_alerts(lat, lon):
    """Get weather alerts for specific coordinates"""
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={API_KEY}&units=imperial"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        raw_data = response.json()
        alerts = raw_data.get('alerts', [])
        
        formatted_alerts = []
        for alert in alerts:
            formatted_alerts.append({
                'event': alert.get('event', 'Weather Alert'),
                'description': alert.get('description', 'No description available'),
                'start': alert.get('start'),
                'end': alert.get('end'),
                'sender_name': alert.get('sender_name', 'Weather Service')
            })
        
        return formatted_alerts
        
    except Exception as e:
        print(f"Error fetching weather alerts: {e}")
        return []