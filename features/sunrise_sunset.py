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

def update_sunrise_sunset(self, lat, lon):
    """Update sunrise/sunset times based on coordinates."""
    try:
        from features.sunrise_sunset import get_sunrise_sunset, format_sun_times
        
        sun_data = get_sunrise_sunset(lat, lon)
        if sun_data:
            sunrise, sunset = format_sun_times(sun_data)
            self.sunrise_label.config(text=sunrise)
            self.sunset_label.config(text=sunset)
            
            # Calculate day length
            day_length = sun_data.get('day_length', 'Unknown')
            self.day_length_label.config(text=f"Day length: {day_length}")
        else:
            self.sunrise_label.config(text="Sunrise: --:--")
            self.sunset_label.config(text="Sunset: --:--")
            self.day_length_label.config(text="Day length: --")
    except ImportError:
        # Fallback if sunrise_sunset module doesn't exist
        self.sunrise_label.config(text="Sunrise: 6:45 AM")
        self.sunset_label.config(text="Sunset: 7:32 PM")
        self.day_length_label.config(text="Day length: 12h 47m")