# Tommy's Weather App 🌤️

A comprehensive Python weather application built with Tkinter that provides real-time weather data, forecasts, and intelligent city suggestions based on weather preferences.

## 🚀 Setup Instructions

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repository-url>
   cd python-weather-app
   ```

2. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   Or install manually:
   ```bash
   pip install requests pandas python-dotenv pillow
   ```

3. **Set up your API key:**
   - Create a `.env` file in the root directory
   - Add your OpenWeatherMap API key:
     ```
     OPENWEATHER_API_KEY=your_api_key_here
     ```
   - Get a free API key from [OpenWeatherMap](https://openweathermap.org/api)

4. **Run the application:**
   ```bash
   python src/gui.py
   ```

## 📱 Usage Guide

### Main Interface
The app features a clean navigation bar with quick-access buttons:
- **Search Bar**: Enter any city name and press Enter or click "Get Weather"
- **⭐ Favorites**: View and manage your saved favorite cities
- **➕ Add to Favorites**: Save the current city to your favorites list
- **🌙 Dark Mode**: Toggle between light and dark themes
- **🏙️ Suggest Cities**: Get AI-powered city recommendations
- **🕐 Live Clock**: Real-time clock display in the top-right corner

### Basic Weather Search
1. Enter a city name in the search bar
2. Click "Get Weather" or press Enter
3. View current weather conditions, temperature, and 5-day forecast

### Advanced Features

#### ⭐ Favorites System
- **Add to Favorites**: Click "➕ Add to Favorites" to save the current city
- **View Favorites**: Click "⭐ Favorites" to see your saved cities
- **Quick Load**: Select any favorite city to instantly load its weather
- **Persistent Storage**: Favorites are saved locally using SQLite database

#### 🏙️ Intelligent City Suggestions
- Click "🏙️ Suggest Cities" for personalized recommendations
- Choose your weather preference:
  - **Cold**: Below 50°F for cooler climates
  - **Cool**: 50-75°F for moderate temperatures  
  - **Hot**: Above 75°F for warmer weather
- Get 3 curated city suggestions based on real weather data

#### 🌙 Dynamic Theme System
- Toggle between light and dark modes with the "🌙" button
- Automatic color adaptation across all interface elements
- Improved visibility and accessibility

#### 🚨 Weather Alerts (Advanced)
- Set up custom notifications for specific weather conditions
- Monitor temperature, humidity, and other weather metrics
- Database-backed alert management system

## 🌟 Features Summary

### Core Weather Features
- **Real-time Weather Data**: Live conditions via OpenWeatherMap API
- **5-Day Forecast**: Extended predictions with daily breakdowns
- **Weather Icons**: Visual representation of current conditions
- **Detailed Metrics**: Temperature, humidity, pressure, wind speed, UV index
- **Sunrise/Sunset Times**: Precise astronomical data

### Custom UI Enhancements
- **🎨 Custom Navigation Bar**: 
  - Professionally styled buttons with hover effects
  - Color-coded functionality (Green=Action, Gold=Favorites, Blue=Info)
  - macOS-compatible custom styling

- **⭐ Advanced Favorites System**: 
  - One-click city saving with "Add to Favorites" button
  - SQLite database for persistent storage
  - Instant access to frequently checked locations

- **🏙️ Smart City Discovery**: 
  - AI-powered city recommendations based on weather preferences
  - Real-time weather data analysis from multiple sources
  - Temperature-based filtering and suggestions

- **🌙 Adaptive Theme System**: 
  - Seamless light/dark mode switching
  - Automatic UI element color adaptation
  - Enhanced user experience and accessibility

### Technical Features
- **Data Persistence**: SQLite databases for favorites and user preferences
- **Error Handling**: Comprehensive error management with user-friendly messages
- **Responsive Design**: Clean, modern interface that adapts to different screen sizes
- **Modular Architecture**: Feature-based code organization for maintainability

## 🗂️ Project Structure
```
python-weather-app/
├── src/
│   ├── gui.py              # Main application interface
│   ├── weather_api.py      # OpenWeatherMap API integration
│   └── utils.py            # Utility functions
├── features/
│   ├── favorite_cities.py  # Favorites management system
│   ├── weather_alert.py    # Weather alert functionality
│   ├── team_feature.py     # City suggestion engine
│   ├── moon_phase.py       # Lunar phase calculations
│   └── sunrise_sunset.py   # Solar time calculations
├── data/
│   ├── mock_weather.py     # Mock data for testing
│   └── weather_data.csv    # Historical weather data
├── favorites.db            # SQLite database (auto-created)
├── weather_alerts.db       # Alert storage (auto-created)
└── requirements.txt        # Python dependencies
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:
```
OPENWEATHER_API_KEY=your_api_key_here
USE_MOCK=False
```

### Customization Options
- **Button Colors**: Modify color schemes in `gui.py` `create_custom_nav_button()`
- **Temperature Ranges**: Adjust city suggestion criteria in `team_feature.py`
- **Theme Colors**: Update light/dark mode palettes in `gui.py`
- **Alert Conditions**: Customize weather alert triggers in `weather_alert.py`

## 🛠️ Troubleshooting

### Common Issues

1. **"API Key Error"**
   - Ensure your OpenWeatherMap API key is valid
   - Check that `.env` file exists in the root directory
   - Verify the key format: `OPENWEATHER_API_KEY=your_actual_key`

2. **"City Not Found"**
   - Check city name spelling
   - Try alternative names (e.g., "NYC" vs "New York")
   - Include country for disambiguation: "London, UK"

3. **Button Styling Issues (macOS)**
   - App uses custom button styling for macOS compatibility
   - Hover effects may vary based on system preferences

4. **Database Errors**
   - App will auto-create SQLite databases on first run
   - Ensure write permissions in the app directory

### Required Dependencies
```bash
pip install requests pandas python-dotenv pillow tkinter
```

## 💡 Tips for Best Experience

- **Keyboard Shortcuts**: Familiarize yourself with keyboard shortcuts for faster navigation:
  - `Ctrl + S`: Save current city to favorites
  - `Ctrl + F`: Open favorites list
  - `Ctrl + D`: Toggle dark mode
  - `Ctrl + R`: Refresh weather data

- **Explore Settings**: Customize the app to your liking in the settings menu:
  - Change temperature units between Celsius and Fahrenheit
  - Adjust update frequency for weather data
  - Manage alert settings and notification preferences

- **Use Mock Data**: Enable mock data in the `.env` file for testing and development:
  ```
  USE_MOCK=True
  ```
  This allows you to use the app without an active internet connection or valid API key.

- **Check Logs**: If you encounter issues, check the log file for detailed error messages:
  - Log file location: `python-weather-app/logs/app.log`
  - Common log messages:
    - `API Key Missing`: No API key found in environment variables
    - `City Not Found`: The searched city does not exist in the database
    - `Database Error`: Issues with reading or writing to the SQLite database

## 📝 License
This project is for educational purposes.
