import sqlite3
import json
from datetime import datetime, timedelta
from enum import Enum

# Database name for weather alerts
ALERTS_DB = 'weather_alerts.db'

class AlertType(Enum):
    """Types of weather alerts available."""
    TEMPERATURE_HIGH = "temperature_high"
    TEMPERATURE_LOW = "temperature_low"
    RAIN = "rain"
    SNOW = "snow"
    STORM = "storm"
    WIND_SPEED = "wind_speed"
    HUMIDITY = "humidity"

class AlertSeverity(Enum):
    """Severity levels for alerts."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

def init_alerts_db():
    """Initialize the alerts database and create necessary tables."""
    conn = sqlite3.connect(ALERTS_DB)
    c = conn.cursor()
    
    # Create alerts configuration table
    c.execute('''
        CREATE TABLE IF NOT EXISTS alert_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            country TEXT,
            alert_type TEXT NOT NULL,
            threshold_value REAL,
            condition TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_date TEXT,
            last_triggered TEXT
        )
    ''')
    
    # Create alerts history table
    c.execute('''
        CREATE TABLE IF NOT EXISTS alert_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            alert_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            message TEXT NOT NULL,
            triggered_date TEXT,
            weather_data TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def add_alert_rule(city, country, alert_type, threshold_value, condition=">="):
    """Add a new weather alert rule."""
    try:
        conn = sqlite3.connect(ALERTS_DB)
        c = conn.cursor()
        created_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Insert new alert rule
        c.execute('''
            INSERT INTO alert_rules (city, country, alert_type, threshold_value, condition, created_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (city, country, alert_type.value, threshold_value, condition, created_date))
        
        conn.commit()
        print(f"Alert rule added for {city}: {alert_type.value} {condition} {threshold_value}")
        return True
        
    except sqlite3.Error as e:
        print(f"Error adding alert rule: {e}")
        return False
    finally:
        conn.close()

def remove_alert_rule(rule_id):
    """Remove an alert rule by ID."""
    try:
        conn = sqlite3.connect(ALERTS_DB)
        c = conn.cursor()
        
        c.execute('DELETE FROM alert_rules WHERE id = ?', (rule_id,))
        
        if c.rowcount > 0:
            conn.commit()
            print(f"Alert rule {rule_id} removed successfully")
            return True
        else:
            print(f"Alert rule {rule_id} not found")
            return False
            
    except sqlite3.Error as e:
        print(f"Error removing alert rule: {e}")
        return False
    finally:
        conn.close()

def get_alert_rules(city=None):
    """Get all alert rules, optionally filtered by city."""
    try:
        conn = sqlite3.connect(ALERTS_DB)
        c = conn.cursor()
        
        if city:
            c.execute('SELECT * FROM alert_rules WHERE city = ? AND is_active = 1', (city,))
        else:
            c.execute('SELECT * FROM alert_rules WHERE is_active = 1')
        
        rules = c.fetchall()
        
        # Convert to list of dictionaries
        return [
            {
                'id': row[0],
                'city': row[1],
                'country': row[2],
                'alert_type': row[3],
                'threshold_value': row[4],
                'condition': row[5],
                'is_active': row[6],
                'created_date': row[7],
                'last_triggered': row[8]
            }
            for row in rules
        ]
        
    except sqlite3.Error as e:
        print(f"Error getting alert rules: {e}")
        return []
    finally:
        conn.close()

def check_weather_alerts(weather_data):
    """Check current weather data against all active alert rules."""
    city = weather_data.get('city')
    if not city:
        return []
    
    # Get all active rules for this city
    rules = get_alert_rules(city)
    triggered_alerts = []
    
    for rule in rules:
        alert_triggered = False
        alert_message = ""
        severity = AlertSeverity.LOW
        
        # Check temperature alerts
        if rule['alert_type'] == AlertType.TEMPERATURE_HIGH.value:
            temp = weather_data.get('temperature', 0)
            if _check_condition(temp, rule['threshold_value'], rule['condition']):
                alert_triggered = True
                severity = _get_temperature_severity(temp, rule['threshold_value'], True)
                alert_message = f"High temperature alert: {temp}°F (threshold: {rule['threshold_value']}°F)"
        
        elif rule['alert_type'] == AlertType.TEMPERATURE_LOW.value:
            temp = weather_data.get('temperature', 0)
            if _check_condition(temp, rule['threshold_value'], rule['condition']):
                alert_triggered = True
                severity = _get_temperature_severity(temp, rule['threshold_value'], False)
                alert_message = f"Low temperature alert: {temp}°F (threshold: {rule['threshold_value']}°F)"
        
        # Check weather condition alerts
        elif rule['alert_type'] == AlertType.RAIN.value:
            description = weather_data.get('description', '').lower()
            if 'rain' in description:
                alert_triggered = True
                severity = AlertSeverity.MEDIUM
                alert_message = f"Rain alert: {description.title()}"
        
        elif rule['alert_type'] == AlertType.SNOW.value:
            description = weather_data.get('description', '').lower()
            if 'snow' in description:
                alert_triggered = True
                severity = AlertSeverity.HIGH
                alert_message = f"Snow alert: {description.title()}"
        
        elif rule['alert_type'] == AlertType.STORM.value:
            description = weather_data.get('description', '').lower()
            if 'storm' in description or 'thunder' in description:
                alert_triggered = True
                severity = AlertSeverity.CRITICAL
                alert_message = f"Storm alert: {description.title()}"
        
        # If alert was triggered, record it
        if alert_triggered:
            alert_data = {
                'rule_id': rule['id'],
                'city': city,
                'alert_type': rule['alert_type'],
                'severity': severity,
                'message': alert_message,
                'weather_data': weather_data
            }
            triggered_alerts.append(alert_data)
            
            # Save to alert history
            _save_alert_to_history(alert_data)
            
            # Update last triggered time for the rule
            _update_rule_last_triggered(rule['id'])
    
    return triggered_alerts

def _check_condition(value, threshold, condition):
    """Check if value meets the condition against threshold."""
    if condition == ">=":
        return value >= threshold
    elif condition == "<=":
        return value <= threshold
    elif condition == ">":
        return value > threshold
    elif condition == "<":
        return value < threshold
    elif condition == "==":
        return value == threshold
    return False

def _get_temperature_severity(temp, threshold, is_high_alert):
    """Determine severity based on how far temperature is from threshold."""
    diff = abs(temp - threshold)
    
    if diff <= 5:
        return AlertSeverity.LOW
    elif diff <= 10:
        return AlertSeverity.MEDIUM
    elif diff <= 20:
        return AlertSeverity.HIGH
    else:
        return AlertSeverity.CRITICAL

def _save_alert_to_history(alert_data):
    """Save triggered alert to history table."""
    try:
        conn = sqlite3.connect(ALERTS_DB)
        c = conn.cursor()
        triggered_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        c.execute('''
            INSERT INTO alert_history (city, alert_type, severity, message, triggered_date, weather_data)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            alert_data['city'],
            alert_data['alert_type'],
            alert_data['severity'].value,
            alert_data['message'],
            triggered_date,
            json.dumps(alert_data['weather_data'])
        ))
        
        conn.commit()
        
    except sqlite3.Error as e:
        print(f"Error saving alert to history: {e}")
    finally:
        conn.close()

def _update_rule_last_triggered(rule_id):
    """Update the last triggered time for an alert rule."""
    try:
        conn = sqlite3.connect(ALERTS_DB)
        c = conn.cursor()
        last_triggered = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        c.execute('UPDATE alert_rules SET last_triggered = ? WHERE id = ?', (last_triggered, rule_id))
        conn.commit()
        
    except sqlite3.Error as e:
        print(f"Error updating rule last triggered: {e}")
    finally:
        conn.close()

def get_alert_history(city=None, limit=50):
    """Get alert history, optionally filtered by city."""
    try:
        conn = sqlite3.connect(ALERTS_DB)
        c = conn.cursor()
        
        if city:
            c.execute('''
                SELECT * FROM alert_history 
                WHERE city = ? 
                ORDER BY triggered_date DESC 
                LIMIT ?
            ''', (city, limit))
        else:
            c.execute('''
                SELECT * FROM alert_history 
                ORDER BY triggered_date DESC 
                LIMIT ?
            ''', (limit,))
        
        history = c.fetchall()
        
        return [
            {
                'id': row[0],
                'city': row[1],
                'alert_type': row[2],
                'severity': row[3],
                'message': row[4],
                'triggered_date': row[5],
                'weather_data': json.loads(row[6]) if row[6] else None
            }
            for row in history
        ]
        
    except sqlite3.Error as e:
        print(f"Error getting alert history: {e}")
        return []
    finally:
        conn.close()

def clear_old_alerts(days_old=30):
    """Clear alert history older than specified days."""
    try:
        conn = sqlite3.connect(ALERTS_DB)
        c = conn.cursor()
        cutoff_date = (datetime.now() - timedelta(days=days_old)).strftime('%Y-%m-%d %H:%M:%S')
        
        c.execute('DELETE FROM alert_history WHERE triggered_date < ?', (cutoff_date,))
        deleted_count = c.rowcount
        conn.commit()
        
        print(f"Cleared {deleted_count} old alert records")
        return deleted_count
        
    except sqlite3.Error as e:
        print(f"Error clearing old alerts: {e}")
        return 0
    finally:
        conn.close()

# Initialize the alerts database when this module is imported
init_alerts_db()

# Example usage and testing
if __name__ == "__main__":
    print("Testing weather alerts...")
    
    # Add some example alert rules
    add_alert_rule("New York", "US", AlertType.TEMPERATURE_HIGH, 90.0, ">=")
    add_alert_rule("New York", "US", AlertType.TEMPERATURE_LOW, 32.0, "<=")
    add_alert_rule("Miami", "US", AlertType.RAIN, 0, ">=")
    add_alert_rule("Chicago", "US", AlertType.STORM, 0, ">=")
    
    # Test with sample weather data
    sample_weather = {
        'city': 'New York',
        'country': 'US',
        'temperature': 95.5,
        'description': 'Clear sky'
    }
    
    # Check for alerts
    alerts = check_weather_alerts(sample_weather)
    print(f"Triggered alerts: {len(alerts)}")
    for alert in alerts:
        print(f"- {alert['message']} (Severity: {alert['severity'].value})")
    
    # Show alert rules
    rules = get_alert_rules("New York")
    print(f"\nAlert rules for New York: {len(rules)}")
    for rule in rules:
        print(f"- {rule['alert_type']}: {rule['condition']} {rule['threshold_value']}")