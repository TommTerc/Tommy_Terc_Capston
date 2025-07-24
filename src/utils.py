def format_temperature(temp_kelvin):
    """Convert temperature from Kelvin to Celsius."""
    # Subtract 273.15 from Kelvin to get Celsius, round to 2 decimal places
    return round(temp_kelvin - 273.15, 2)

def format_humidity(humidity):
    """Format humidity percentage."""
    # Return humidity value as a string with a percent sign
    return f"{humidity}%"

def validate_city_name(city_name):
    """Check if the city name is valid (non-empty)."""
    # Remove leading/trailing whitespace and check if the result is empty
    if not city_name.strip():
        # Raise an error if the city name is empty after stripping
        raise ValueError("City name cannot be empty.")
    # Return the cleaned city name
    return city_name.strip()

def format_wind_direction(degrees):
    """Convert wind direction from degrees to compass direction."""
    if degrees is None:
        return "N/A"
    
    # Define compass directions (16 points)
    directions = [
        "N", "NNE", "NE", "ENE",
        "E", "ESE", "SE", "SSE", 
        "S", "SSW", "SW", "WSW",
        "W", "WNW", "NW", "NNW"
    ]
    
    # Calculate index (each direction covers 22.5 degrees)
    index = round(degrees / 22.5) % 16
    return directions[index]

def format_wind_speed(speed_ms):
    """Convert wind speed from m/s to mph and format."""
    # Convert m/s to mph: multiply by 2.237
    speed_mph = speed_ms * 2.237
    return f"{speed_mph:.1f} mph"

def format_wind_info(wind_data):
    """Format complete wind information with speed and direction."""
    if not wind_data:
        return "Wind: N/A"
    
    speed = wind_data.get('speed', 0)
    direction_deg = wind_data.get('deg')
    
    # Format wind speed
    if speed == 0:
        return "Wind: Calm"
    
    # Format with direction if available
    if direction_deg is not None:
        direction = format_wind_direction(direction_deg)
        speed_formatted = format_wind_speed(speed)
        return f"Wind: {speed_formatted} {direction}"
    else:
        speed_formatted = format_wind_speed(speed)
        return f"Wind: {speed_formatted}"

def format_pressure(pressure_hpa):
    """Format atmospheric pressure."""
    if pressure_hpa is None:
        return "Pressure: N/A"
    
    # Convert hPa to inches of mercury
    pressure_inhg = pressure_hpa * 0.02953
    return f"Pressure: {pressure_hpa} hPa ({pressure_inhg:.2f} inHg)"

def format_visibility(visibility_m):
    """Format visibility distance."""
    if visibility_m is None:
        return "Visibility: N/A"
    
    # Convert meters to miles
    visibility_miles = visibility_m * 0.000621371
    return f"Visibility: {visibility_miles:.1f} mi"