import os
import random
import pandas as pd
import tkinter as tk
from tkinter import messagebox
import requests
import tempfile
import zipfile

class CitySuggestionApp:
    def __init__(self, parent):
        """Initialize the CitySuggestionApp."""
        self.parent = parent
        self.preference_var = tk.StringVar()
        self.repo_url = "https://github.com/SNoeCode/group_8_weather_capstone/archive/refs/heads/main.zip"
        
    def download_csv_files(self):
        """Download CSV files from the remote repository."""
        try:
            # Create a temporary directory
            temp_dir = tempfile.mkdtemp()
            
            # Download the repository zip file
            response = requests.get(self.repo_url, stream=True)
            response.raise_for_status()
            
            zip_path = os.path.join(temp_dir, "repo.zip")
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        
            # Extract the zip file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
        
            # Find CSV files in the extracted directory
            csv_files = []
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith('.csv'):
                        csv_files.append(os.path.join(root, file))
        
            return csv_files  # Return ALL CSV files, not just first 3
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download repository: {e}")
            return []

    def pick_random_csv_files(self, count=3):
        """Pick random CSV files from the downloaded repository."""
        try:
            csv_files = self.download_csv_files()
            if not csv_files:
                raise FileNotFoundError("No CSV files found in the repository.")
            
            # Pick random files (up to the specified count)
            selected_files = random.sample(csv_files, min(count, len(csv_files)))
            return selected_files
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to pick random CSV files: {e}")
            return []

    def load_combined_city_data(self):
        """Load and combine city data from 3 random CSV files."""
        try:
            # Show loading message
            loading_dialog = self.show_loading_dialog()
            self.parent.update()
            
            # Get 3 random CSV files
            csv_files = self.pick_random_csv_files(3)
            if not csv_files:
                loading_dialog.destroy()
                return None

            combined_data = pd.DataFrame()
            
            for file_path in csv_files:
                try:
                    # Load each CSV file
                    data = pd.read_csv(file_path)
                    
                    # Try to identify temperature and city columns
                    temp_cols = [col for col in data.columns if any(word in col.lower() for word in ['temp', 'temperature', 'high', 'low'])]
                    city_cols = [col for col in data.columns if any(word in col.lower() for word in ['city', 'location', 'place', 'name'])]
                    
                    if temp_cols and city_cols:
                        # Create standardized DataFrame
                        standardized_data = pd.DataFrame({
                            'city': data[city_cols[0]],
                            'temperature': pd.to_numeric(data[temp_cols[0]], errors='coerce')
                        })
                        
                        # Add source file info
                        standardized_data['source'] = os.path.basename(file_path)
                        
                        # Append to combined data
                        combined_data = pd.concat([combined_data, standardized_data], ignore_index=True)
                        
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")
                    continue
            
            loading_dialog.destroy()
            
            # Remove duplicates and NaN values
            combined_data = combined_data.dropna().drop_duplicates(subset=['city'])
            
            return combined_data if not combined_data.empty else None
            
        except Exception as e:
            if 'loading_dialog' in locals():
                loading_dialog.destroy()
            messagebox.showerror("Error", f"Failed to load city data: {e}")
            return None

    def show_loading_dialog(self):
        """Show a loading dialog while processing data."""
        loading_dialog = tk.Toplevel(self.parent)
        loading_dialog.title("Loading...")
        loading_dialog.geometry("350x220")
        loading_dialog.configure(bg="#2c3e50")
        loading_dialog.resizable(False, False)
        
        # Center the dialog
        loading_dialog.transient(self.parent)
        loading_dialog.grab_set()
        
        tk.Label(loading_dialog, text="🔄 Downloading and analyzing weather data...", 
                 font=("Helvetica", 12, "bold"), bg="#2c3e50", fg="white").pack(expand=True)
        
        return loading_dialog

    def suggest_cities_by_preference(self, preference):
        """Suggest cities based on weather preference (hot, cool, cold)."""
        city_data = self.load_combined_city_data()
        if city_data is None or city_data.empty:
            messagebox.showwarning("Warning", "No city data available for suggestions.")
            return []

        # Define temperature ranges for preferences (in Fahrenheit)
        temp_ranges = {
            "cold": (-20, 50),    # Cold weather: below 50°F
            "cool": (50, 75),     # Cool weather: 50-75°F
            "hot": (75, 120)      # Hot weather: above 75°F
        }

        if preference not in temp_ranges:
            messagebox.showerror("Error", "Invalid preference. Choose 'hot', 'cool', or 'cold'.")
            return []

        # Filter cities based on preference
        min_temp, max_temp = temp_ranges[preference]
        filtered_cities = city_data[
            (city_data["temperature"] >= min_temp) & 
            (city_data["temperature"] <= max_temp)
        ]

        if filtered_cities.empty:
            messagebox.showinfo("Info", f"No cities found for {preference} weather preference.\nTry a different preference!")
            return pd.DataFrame()

        # Sort cities by relevance (closest to the middle of the range)
        mid_temp = (min_temp + max_temp) / 2
        filtered_cities = filtered_cities.copy()
        filtered_cities["relevance"] = abs(filtered_cities["temperature"] - mid_temp)
        sorted_cities = filtered_cities.sort_values(by="relevance").head(3)

        return sorted_cities

    def show_preference_dialog(self):
        """Show dialog to get user's weather preference."""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Weather Preference")
        dialog.geometry("450x500")
        dialog.configure(bg="#34495e")
        dialog.resizable(False, False)

        # Center the dialog
        dialog.transient(self.parent)
        dialog.grab_set()

        # Title
        title_label = tk.Label(dialog, text="What's Your Weather Preference?", 
                              font=("Helvetica", 20, "bold"), bg="#34495e", fg="white")
        title_label.pack(pady=20)

        subtitle_label = tk.Label(dialog, text="We'll analyze weather data from multiple sources\nto find the perfect cities for you!", 
                                  font=("Helvetica", 12), bg="#34495e", fg="#ecf0f1", justify="center")
        subtitle_label.pack(pady=(0, 30))

        # Preference options with better styling
        preferences = [
            ("cold", "❄️ Cold Weather", "I enjoy cooler temperatures (below 50°F)", "#3498db"),
            ("cool", "🌤️ Cool Weather", "I prefer mild temperatures (50-75°F)", "#2ecc71"),
            ("hot", "🌞 Hot Weather", "I love warm temperatures (above 75°F)", "#e74c3c")
        ]

        # Create radio buttons with better contrast
        for value, title, description, color in preferences:
            frame = tk.Frame(dialog, bg=color, relief="raised", bd=2)
            frame.pack(pady=8, padx=30, fill="x")

            radio = tk.Radiobutton(frame, text=title, variable=self.preference_var, value=value,
                                  font=("Helvetica", 14, "bold"), bg=color, fg="white",
                                  selectcolor="#2c3e50", activebackground=color, 
                                  activeforeground="white", indicatoron=True)
            radio.pack(anchor="w", padx=15, pady=(10, 5))

            desc_label = tk.Label(frame, text=description, font=("Helvetica", 10),
                                 bg=color, fg="white")
            desc_label.pack(anchor="w", padx=35, pady=(0, 10))

        # Set default selection
        self.preference_var.set("cool")

        # Buttons frame
        button_frame = tk.Frame(dialog, bg="#34495e")
        button_frame.pack(pady=40)

        # Custom button function
        def create_custom_button(parent, text, bg_color, fg_color, command):
            """Create a custom button using Frame and Label."""
            button_frame = tk.Frame(parent, bg=bg_color, relief="raised", bd=3, cursor="hand2")
            
            button_label = tk.Label(button_frame, text=text, font=("Helvetica", 14, "bold"),
                                   bg=bg_color, fg=fg_color, padx=20, pady=10)
            button_label.pack()
            
            # Bind click events
            def on_click(event):
                command()
            
            def on_enter(event):
                button_frame.config(relief="solid")
            
            def on_leave(event):
                button_frame.config(relief="raised")
            
            button_frame.bind("<Button-1>", on_click)
            button_label.bind("<Button-1>", on_click)
            button_frame.bind("<Enter>", on_enter)
            button_frame.bind("<Leave>", on_leave)
            button_label.bind("<Enter>", on_enter)
            button_label.bind("<Leave>", on_leave)
            
            return button_frame

        # Use the custom button function
        def suggest_cities():
            preference = self.preference_var.get()
            dialog.destroy()
            suggested_cities = self.suggest_cities_by_preference(preference)
            self.show_results(suggested_cities, preference)

        suggest_btn = create_custom_button(button_frame, "Suggest Cities", "#27ae60", "white", suggest_cities)
        suggest_btn.pack(side=tk.LEFT, padx=10)

        cancel_btn = create_custom_button(button_frame, "Cancel", "#e74c3c", "white", dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=10)

    def show_results(self, cities, preference):
        """Display the suggested cities in a dialog."""
        result_dialog = tk.Toplevel(self.parent)
        result_dialog.title("City Suggestions")
        result_dialog.geometry("550x500")
        result_dialog.configure(bg="#2c3e50")
        result_dialog.resizable(False, False)

        # Center the dialog
        result_dialog.transient(self.parent)
        result_dialog.grab_set()

        # Title
        title_label = tk.Label(result_dialog, text=f"🏙️ Top Cities for {preference.title()} Weather", 
                               font=("Helvetica", 18, "bold"), bg="#2c3e50", fg="white")
        title_label.pack(pady=20)

        # Custom button function (same as in show_preference_dialog)
        def create_custom_button(parent, text, bg_color, fg_color, command):
            """Create a custom button using Frame and Label."""
            button_frame = tk.Frame(parent, bg=bg_color, relief="raised", bd=3, cursor="hand2")
            
            button_label = tk.Label(button_frame, text=text, font=("Helvetica", 14, "bold"),
                                   bg=bg_color, fg=fg_color, padx=20, pady=10)
            button_label.pack()
            
            # Bind click events
            def on_click(event):
                command()
            
            def on_enter(event):
                button_frame.config(relief="solid")
            
            def on_leave(event):
                button_frame.config(relief="raised")
            
            button_frame.bind("<Button-1>", on_click)
            button_label.bind("<Button-1>", on_click)
            button_frame.bind("<Enter>", on_enter)
            button_frame.bind("<Leave>", on_leave)
            button_label.bind("<Enter>", on_enter)
            button_label.bind("<Leave>", on_leave)
            
            return button_frame

        if cities is None or cities.empty:
            # No results found
            no_data_frame = tk.Frame(result_dialog, bg="#e74c3c", relief="raised", bd=3)
            no_data_frame.pack(pady=30, padx=30, fill="x")
            
            no_data_label = tk.Label(no_data_frame, text="❌ No cities found matching your preference", 
                                     font=("Helvetica", 14, "bold"), bg="#e74c3c", fg="white")
            no_data_label.pack(pady=20)
            
            suggestion_label = tk.Label(no_data_frame, text="Try selecting a different weather preference!", 
                                       font=("Helvetica", 12), bg="#e74c3c", fg="white")
            suggestion_label.pack(pady=(0, 20))
            
            # Retry button - UPDATED TO USE CUSTOM BUTTON
            retry_btn = create_custom_button(result_dialog, "Try Again", "#3498db", "white", 
                                           lambda: (result_dialog.destroy(), self.show_preference_dialog()))
            retry_btn.pack(pady=10)
        else:
            # Display cities with better formatting
            for i, (_, city) in enumerate(cities.iterrows(), 1):
                city_frame = tk.Frame(result_dialog, bg="#34495e", relief="raised", bd=3)
                city_frame.pack(pady=10, padx=30, fill="x")

                # City rank and name
                city_label = tk.Label(city_frame, text=f"#{i} 📍 {city['city']}", 
                                      font=("Helvetica", 16, "bold"), bg="#34495e", fg="white")
                city_label.pack(pady=(15, 5))

                # Temperature with color coding
                temp_color = "#e74c3c" if preference == "hot" else "#3498db" if preference == "cold" else "#2ecc71"
                temp_label = tk.Label(city_frame, text=f"🌡️ Temperature: {city['temperature']:.1f}°F", 
                                      font=("Helvetica", 14, "bold"), bg="#34495e", fg=temp_color)
                temp_label.pack(pady=5)

                # Source information
                source_label = tk.Label(city_frame, text=f"📊 Data Source: {city['source']}", 
                                        font=("Helvetica", 10), bg="#34495e", fg="#bdc3c7")
                source_label.pack(pady=(0, 15))

        # Close button - UPDATED TO USE CUSTOM BUTTON
        close_btn = create_custom_button(result_dialog, "Close", "#95a5a6", "white", result_dialog.destroy)
        close_btn.pack(pady=30)