# Python Weather App

This project is a simple weather application that fetches current weather data from an API and displays it using a Tkinter GUI. It also implements file-based data storage for saving and loading weather information.

## Project Structure

```
python-weather-app
├── src
│   ├── main.py          # Entry point of the application
│   ├── gui.py           # Tkinter GUI components
│   ├── weather_api.py   # API interaction for fetching weather data
│   ├── storage.py       # File-based data storage functions
│   └── utils.py         # Utility functions for the application
├── requirements.txt     # Project dependencies
└── README.md            # Project documentation
```

## Setup Instructions

1. Clone the repository or download the project files.
2. Navigate to the project directory.
3. Install the required dependencies using pip:

   ```
   pip install -r requirements.txt
   ```

## Usage Guidelines

1. Run the application by executing the `main.py` file:

   ```
   python src/main.py
   ```

2. Enter the location for which you want to fetch the weather data in the GUI.
3. Click the "Get Weather" button to retrieve and display the current weather information.

## Weather API

This application uses a weather API to fetch current weather data. Make sure to sign up for an API key if required and update the `weather_api.py` file with your API key.

## Error Handling

The application includes error handling for API requests and file operations to ensure a smooth user experience. If an error occurs, appropriate messages will be displayed in the GUI.

## Contributing

Contributions are welcome! Feel free to submit a pull request or open an issue for any suggestions or improvements.# capstone
