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

def update_sunrise_sunset(self, data):
    """Update sunrise/sunset times from API data."""
    if not hasattr(self, 'sunrise_label'):
        return
    
    # Check if API provides sunrise/sunset data
    sunrise_timestamp = data.get('sunrise')
    sunset_timestamp = data.get('sunset')
    
    if sunrise_timestamp and sunset_timestamp:
        from datetime import datetime
        
        sunrise = datetime.fromtimestamp(sunrise_timestamp)
        sunset = datetime.fromtimestamp(sunset_timestamp)
        
        self.sunrise_label.config(text=f"Sunrise: {sunrise.strftime('%I:%M %p')}")
        self.sunset_label.config(text=f"Sunset: {sunset.strftime('%I:%M %p')}")
        
        # Calculate day length
        day_length = sunset - sunrise
        hours = day_length.seconds // 3600
        minutes = (day_length.seconds % 3600) // 60
        self.day_length_label.config(text=f"Day length: {hours}h {minutes}m")
    else:
        # Fallback to default values
        self.sunrise_label.config(text="Sunrise: 6:45 AM")
        self.sunset_label.config(text="Sunset: 7:32 PM")
        self.day_length_label.config(text="Day length: 12h 47m")