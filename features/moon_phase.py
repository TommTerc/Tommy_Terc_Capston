import requests
from datetime import datetime
import math

def calculate_moon_phase(date=None):
    """
    Calculate the moon phase for a given date.
    Returns a value between 0 and 1, where:
    0 = New Moon
    0.25 = First Quarter
    0.5 = Full Moon
    0.75 = Last Quarter
    """
    if date is None:
        date = datetime.now()
    
    # Known new moon date: January 6, 2000, 18:14 UTC
    known_new_moon = datetime(2000, 1, 6, 18, 14)
    
    # Lunar cycle is approximately 29.53059 days
    lunar_cycle = 29.53059
    
    # Calculate days since known new moon
    days_since = (date - known_new_moon).total_seconds() / (24 * 3600)
    
    # Calculate moon phase (0 to 1)
    phase = (days_since % lunar_cycle) / lunar_cycle
    
    return phase

def get_moon_phase_name(phase):
    """
    Convert moon phase number to descriptive name.
    """
    if phase < 0.0625 or phase >= 0.9375:
        return "New Moon"
    elif phase < 0.1875:
        return "Waxing Crescent"
    elif phase < 0.3125:
        return "First Quarter"
    elif phase < 0.4375:
        return "Waxing Gibbous"
    elif phase < 0.5625:
        return "Full Moon"
    elif phase < 0.6875:
        return "Waning Gibbous"
    elif phase < 0.8125:
        return "Last Quarter"
    else:
        return "Waning Crescent"

def get_moon_phase_emoji(phase):
    """
    Convert moon phase number to emoji representation.
    """
    if phase < 0.0625 or phase >= 0.9375:
        return "🌑"  # New Moon
    elif phase < 0.1875:
        return "🌒"  # Waxing Crescent
    elif phase < 0.3125:
        return "🌓"  # First Quarter
    elif phase < 0.4375:
        return "🌔"  # Waxing Gibbous
    elif phase < 0.5625:
        return "🌕"  # Full Moon
    elif phase < 0.6875:
        return "🌖"  # Waning Gibbous
    elif phase < 0.8125:
        return "🌗"  # Last Quarter
    else:
        return "🌘"  # Waning Crescent

def get_moon_illumination(phase):
    """
    Calculate the percentage of moon illumination.
    """
    # Calculate illumination percentage
    if phase <= 0.5:
        illumination = phase * 2
    else:
        illumination = (1 - phase) * 2
    
    return int(illumination * 100)

def get_moon_data(date=None):
    """
    Get comprehensive moon phase data for a given date.
    """
    if date is None:
        date = datetime.now()
    
    phase = calculate_moon_phase(date)
    
    return {
        'phase': phase,
        'phase_name': get_moon_phase_name(phase),
        'emoji': get_moon_phase_emoji(phase),
        'illumination': get_moon_illumination(phase),
        'date': date.strftime('%Y-%m-%d')
    }

def get_next_full_moon(date=None):
    """
    Calculate the date of the next full moon.
    """
    if date is None:
        date = datetime.now()
    
    current_phase = calculate_moon_phase(date)
    
    # Days until next full moon
    if current_phase <= 0.5:
        days_until_full = (0.5 - current_phase) * 29.53059
    else:
        days_until_full = (1.0 - current_phase + 0.5) * 29.53059
    
    next_full_moon = date + datetime.timedelta(days=days_until_full)
    return next_full_moon

def get_next_new_moon(date=None):
    """
    Calculate the date of the next new moon.
    """
    if date is None:
        date = datetime.now()
    
    current_phase = calculate_moon_phase(date)
    
    # Days until next new moon
    if current_phase == 0:
        days_until_new = 29.53059
    else:
        days_until_new = (1.0 - current_phase) * 29.53059
    
    next_new_moon = date + datetime.timedelta(days=days_until_new)
    return next_new_moon

# Example usage and testing
if __name__ == "__main__":
    moon_data = get_moon_data()
    print(f"Current Moon Phase: {moon_data['phase_name']} {moon_data['emoji']}")
    print(f"Illumination: {moon_data['illumination']}%")
    print(f"Phase Value: {moon_data['phase']:.3f}")