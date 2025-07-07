import streamlit as st
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

# Initialize Firebase
def get_firestore_client():
    """Get the Firestore client"""
    try:
        # Check if Firebase is already initialized
        if firebase_admin._apps:
            return firestore.client()
        
        # Initialize Firebase
        if hasattr(st, 'secrets') and 'firebase' in st.secrets:
            # Use the secrets dict from Streamlit
            cred_dict = st.secrets['firebase']
            cred = credentials.Certificate(cred_dict)
        else:
            # Check for a service account file
            service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT', 'firebase-key.json')
            if os.path.exists(service_account_path):
                cred = credentials.Certificate(service_account_path)
            else:
                st.error("Firebase credentials not found. Please set up your Firebase credentials.")
                return None
        
        # Initialize the app
        firebase_admin.initialize_app(cred)
        return firestore.client()
    except Exception as e:
        st.error(f"Error initializing Firebase: {e}")
        return None

# Convert Firestore document to dict
def document_to_dict(doc):
    """Convert a Firestore document to a dict"""
    if not doc.exists:
        return None
    
    doc_dict = doc.to_dict()
    doc_dict['id'] = doc.id
    return doc_dict

# Format timestamp fields for JSON serialization
def format_timestamp_fields(data):
    """Format any timestamp fields for JSON serialization"""
    if isinstance(data, dict):
        for key, value in list(data.items()):
            if hasattr(value, 'timestamp'):  # Check if it's a Firestore timestamp
                data[key] = value.isoformat() if hasattr(value, 'isoformat') else str(value)
            elif isinstance(value, dict) or isinstance(value, list):
                data[key] = format_timestamp_fields(value)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            data[i] = format_timestamp_fields(item)
    return data

# User Profile Operations
def save_user_profile(user_id, profile_data):
    """Save user profile data to Firestore"""
    try:
        db = get_firestore_client()
        if not db:
            return False
        
        # Check if we need to load existing profile first (for merging)
        existing_profile = load_user_profile(user_id)
        
        # Create a new profile data dict
        updated_profile = {}
        
        # If there's an existing profile, start with that
        if existing_profile:
            updated_profile.update(existing_profile)
        
        # Update with new profile data
        updated_profile.update(profile_data)
        
        # Add last updated timestamp
        updated_profile["last_updated"] = firestore.SERVER_TIMESTAMP
        
        # Save to Firestore
        db.collection('profiles').document(user_id).set(updated_profile)
        
        # Also save a copy in the users collection for easier access
        db.collection('users').document(user_id).set({
            "has_profile": True,
            "last_profile_update": firestore.SERVER_TIMESTAMP
        }, merge=True)
        
        return True
    except Exception as e:
        st.error(f"Error saving profile: {e}")
        return False

def load_user_profile(user_id):
    """Load user profile data from Firestore"""
    try:
        db = get_firestore_client()
        if not db:
            return None
        
        # Get from Firestore
        doc = db.collection('profiles').document(user_id).get()
        
        if not doc.exists:
            # Try to load from legacy file storage first
            legacy_profile = _load_legacy_profile(user_id)
            if legacy_profile:
                # Migrate to Firebase
                save_user_profile(user_id, legacy_profile)
                return legacy_profile
            return None
        
        profile = doc.to_dict()
        
        # Format timestamp fields for JSON serialization
        profile = format_timestamp_fields(profile)
        
        return profile
    except Exception as e:
        st.error(f"Error loading profile: {e}")
        
        # Fallback to legacy storage if Firebase fails
        return _load_legacy_profile(user_id)

def _load_legacy_profile(user_id):
    """Try to load profile from legacy file storage as fallback"""
    try:
        # Check different possible locations
        potential_paths = [
            f"user_profile.json",  # Original location
            f"data/profiles/{user_id}_profile.json"  # New location
        ]
        
        for path in potential_paths:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    return json.load(f)
        
        return None
    except Exception:
        return None

# Food Log Operations
def save_food_log_entry(user_id, food_log_data):
    """Save food log entry to Firestore"""
    try:
        db = get_firestore_client()
        if not db:
            return False
        
        # Get the date from the food log data
        date = food_log_data.get("date")
        
        if not date:
            # Use current date if not provided
            date = datetime.now().strftime("%Y-%m-%d")
            food_log_data["date"] = date
        
        # Add timestamp if not present
        if "timestamp" not in food_log_data:
            food_log_data["timestamp"] = firestore.SERVER_TIMESTAMP
        
        # Add to Firestore
        db.collection('users').document(user_id).collection('food_logs').add(food_log_data)
        
        # Update user document to indicate they have food logs
        db.collection('users').document(user_id).set({
            "has_food_logs": True,
            "last_food_log": firestore.SERVER_TIMESTAMP
        }, merge=True)
        
        return True
    except Exception as e:
        st.error(f"Error saving food log: {e}")
        return False

def load_food_logs(user_id, date=None, start_date=None, end_date=None):
    """Load food log data for a user
    
    If date is provided, returns entries for that specific date.
    If start_date and end_date are provided, returns entries within that range.
    Otherwise, returns all entries.
    """
    try:
        db = get_firestore_client()
        if not db:
            return []
        
        # Get logs collection
        logs_ref = db.collection('users').document(user_id).collection('food_logs')
        
        # Apply filters
        if date:
            query = logs_ref.where("date", "==", date)
        elif start_date and end_date:
            query = logs_ref.where("date", ">=", start_date).where("date", "<=", end_date)
        else:
            query = logs_ref
        
        # Order by timestamp
        query = query.order_by("timestamp", direction=firestore.Query.ASCENDING)
        
        # Execute query
        docs = query.get()
        
        # Convert to list of dicts
        logs = []
        for doc in docs:
            log_data = doc.to_dict()
            log_data['entry_id'] = doc.id  # Add document ID as entry_id
            logs.append(log_data)
        
        # Format timestamp fields for JSON serialization
        logs = format_timestamp_fields(logs)
        
        # If no logs found, try legacy storage
        if not logs and date:
            legacy_logs = _load_legacy_food_logs(user_id, date)
            if legacy_logs:
                # Migrate legacy logs to Firebase
                for log in legacy_logs:
                    save_food_log_entry(user_id, log)
                return legacy_logs
        
        return logs
    except Exception as e:
        st.error(f"Error loading food logs: {e}")
        
        # Fallback to legacy storage if Firebase fails
        if date:
            return _load_legacy_food_logs(user_id, date)
        return []

def _load_legacy_food_logs(user_id, date=None):
    """Try to load food logs from legacy file storage as fallback"""
    try:
        # Check different possible locations
        potential_paths = [
            "food_log.json",  # Original location
            f"data/food_logs/{user_id}_logs.json"  # New location
        ]
        
        for path in potential_paths:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    all_logs = json.load(f)
                
                if date:
                    # Filter by date
                    return [log for log in all_logs if log.get("date") == date]
                return all_logs
        
        return []
    except Exception:
        return []

def delete_food_log_entry(user_id, entry_id):
    """Delete a food log entry"""
    try:
        db = get_firestore_client()
        if not db:
            return False
        
        # Delete from Firestore
        db.collection('users').document(user_id).collection('food_logs').document(entry_id).delete()
        return True
    except Exception as e:
        st.error(f"Error deleting food log entry: {e}")
        return False

def update_food_log_entry(user_id, entry_id, updated_data):
    """Update a food log entry"""
    try:
        db = get_firestore_client()
        if not db:
            return False
        
        # Update in Firestore
        updated_data["last_updated"] = firestore.SERVER_TIMESTAMP
        db.collection('users').document(user_id).collection('food_logs').document(entry_id).update(updated_data)
        return True
    except Exception as e:
        st.error(f"Error updating food log entry: {e}")
        return False

# For backward compatibility - maintain original function signatures
def create_data_folders():
    """Create necessary data folders if they don't exist (kept for backward compatibility)"""
    # No need to create folders with Firebase
    pass

def get_user_data_path(filename):
    """Get the path for a user data file (kept for backward compatibility)"""
    return None

def get_profile_path(user_id):
    """Get the path for a user profile file (kept for backward compatibility)"""
    return None

def get_food_log_path(user_id, date=None):
    """Get the path for a food log file (kept for backward compatibility)"""
    return None