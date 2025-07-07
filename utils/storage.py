 
import os
import json
from datetime import datetime

# Define data directory paths
DATA_DIR = "data"
USER_DATA_DIR = os.path.join(DATA_DIR, "users")
FOOD_LOG_DIR = os.path.join(DATA_DIR, "food_logs")
PROFILE_DIR = os.path.join(DATA_DIR, "profiles")

def create_data_folders():
    """Create necessary data folders if they don't exist"""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(USER_DATA_DIR, exist_ok=True)
    os.makedirs(FOOD_LOG_DIR, exist_ok=True)
    os.makedirs(PROFILE_DIR, exist_ok=True)

def get_user_data_path(filename):
    """Get the path for a user data file"""
    return os.path.join(USER_DATA_DIR, filename)

def get_profile_path(user_id):
    """Get the path for a user profile file"""
    return os.path.join(PROFILE_DIR, f"{user_id}_profile.json")

def get_food_log_path(user_id, date=None):
    """Get the path for a food log file
    
    If date is provided, returns the path for that specific date.
    Otherwise, returns the path for all food logs.
    """
    if date:
        return os.path.join(FOOD_LOG_DIR, f"{user_id}_{date}.json")
    return os.path.join(FOOD_LOG_DIR, f"{user_id}_logs.json")

def save_user_profile(user_id, profile_data):
    """Save user profile data to JSON file"""
    try:
        profile_path = get_profile_path(user_id)
        
        # Add last updated timestamp
        profile_data["last_updated"] = datetime.now().isoformat()
        
        with open(profile_path, 'w') as f:
            json.dump(profile_data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving profile: {e}")
        return False

def load_user_profile(user_id):
    """Load user profile data from JSON file"""
    try:
        profile_path = get_profile_path(user_id)
        
        if os.path.exists(profile_path):
            with open(profile_path, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"Error loading profile: {e}")
        return None

def save_food_log_entry(user_id, food_log_data):
    """Save food log entry to JSON file"""
    try:
        # Get the date from the food log data
        date = food_log_data.get("date")
        
        if not date:
            # Use current date if not provided
            date = datetime.now().strftime("%Y-%m-%d")
            food_log_data["date"] = date
        
        # Get file path for all logs
        log_path = get_food_log_path(user_id)
        
        # Load existing logs
        logs = []
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                logs = json.load(f)
        
        # Add entry ID if not present
        if "entry_id" not in food_log_data:
            food_log_data["entry_id"] = str(int(datetime.now().timestamp() * 1000))
        
        # Add timestamp if not present
        if "timestamp" not in food_log_data:
            food_log_data["timestamp"] = datetime.now().isoformat()
        
        # Add new entry
        logs.append(food_log_data)
        
        # Save updated logs
        with open(log_path, 'w') as f:
            json.dump(logs, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving food log: {e}")
        return False

def load_food_logs(user_id, date=None, start_date=None, end_date=None):
    """Load food log data for a user
    
    If date is provided, returns entries for that specific date.
    If start_date and end_date are provided, returns entries within that range.
    Otherwise, returns all entries.
    """
    try:
        # Get file path for all logs
        log_path = get_food_log_path(user_id)
        
        # Check if log file exists
        if not os.path.exists(log_path):
            return []
        
        # Load all logs
        with open(log_path, 'r') as f:
            logs = json.load(f)
        
        # Filter by date if provided
        if date:
            return [entry for entry in logs if entry.get("date") == date]
        
        # Filter by date range if provided
        if start_date and end_date:
            return [
                entry for entry in logs 
                if start_date <= entry.get("date", "") <= end_date
            ]
        
        # Return all logs
        return logs
    except Exception as e:
        print(f"Error loading food logs: {e}")
        return []

def delete_food_log_entry(user_id, entry_id):
    """Delete a food log entry"""
    try:
        # Get file path for all logs
        log_path = get_food_log_path(user_id)
        
        # Check if log file exists
        if not os.path.exists(log_path):
            return False
        
        # Load all logs
        with open(log_path, 'r') as f:
            logs = json.load(f)
        
        # Find and remove the entry
        logs = [entry for entry in logs if entry.get("entry_id") != entry_id]
        
        # Save updated logs
        with open(log_path, 'w') as f:
            json.dump(logs, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error deleting food log entry: {e}")
        return False

def update_food_log_entry(user_id, entry_id, updated_data):
    """Update a food log entry"""
    try:
        # Get file path for all logs
        log_path = get_food_log_path(user_id)
        
        # Check if log file exists
        if not os.path.exists(log_path):
            return False
        
        # Load all logs
        with open(log_path, 'r') as f:
            logs = json.load(f)
        
        # Find and update the entry
        for i, entry in enumerate(logs):
            if entry.get("entry_id") == entry_id:
                # Update entry with new data
                logs[i] = {**entry, **updated_data}
                break
        else:
            # Entry not found
            return False
        
        # Save updated logs
        with open(log_path, 'w') as f:
            json.dump(logs, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error updating food log entry: {e}")
        return False