def get_mock_weather_data(city):
    return {
        'city': 'Washington Heights',
        'country': 'US',
        'temperature': 87,
        'description': 'mostly cloudy',
        'forecast': [
            {'day': 'Thu', 'icon': '☁️', 'high': 85, 'low': 73},
            {'day': 'Fri', 'icon': '🌧️', 'high': 83, 'low': 72},
            {'day': 'Sat', 'icon': '☀️', 'high': 88, 'low': 74},
            {'day': 'Sun', 'icon': '⛅', 'high': 86, 'low': 73},
            {'day': 'Mon', 'icon': '☁️', 'high': 84, 'low': 72},
        ]
    }