import requests
from datetime import datetime
import os

def get_sunrise_sunset(lat, lon):
    """
    Get sunrise and sunset times for given coordinates
    """
    try:
        # Using sunrise-sunset.org API (free, no key required)
        url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&formatted=0"
        response = requests.get(url)
        data = response.json()
        
        if data['status'] == 'OK':
            sunrise = datetime.fromisoformat(data['results']['sunrise'].replace('Z', '+00:00'))
            sunset = datetime.fromisoformat(data['results']['sunset'].replace('Z', '+00:00'))
            
            return {
                'sunrise': sunrise,
                'sunset': sunset,
                'day_length': data['results']['day_length']
            }
    except Exception as e:
        print(f"Error fetching sunrise/sunset: {e}")
        return None

def format_sun_times(sun_data):
    """
    Format sunrise/sunset data for display
    """
    if not sun_data:
        return "Sunrise: --:--", "Sunset: --:--"
    
    sunrise = sun_data['sunrise'].strftime("%-I:%M %p")
    sunset = sun_data['sunset'].strftime("%-I:%M %p")
    
    return f"Sunrise: {sunrise}", f"Sunset: {sunset}"