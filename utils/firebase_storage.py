import streamlit as st
from datetime import datetime
from utils.firebase_config import get_firestore_client, document_to_dict, format_timestamp_fields

# User Profile Operations
def save_user_profile(user_id, profile_data):
    """Save user profile data to Firestore"""
    try:
        db = get_firestore_client()
        if not db:
            return False
        
        # Add last updated timestamp
        profile_data["last_updated"] = datetime.now()
        
        # Save to Firestore
        db.collection('profiles').document(user_id).set(profile_data, merge=True)
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
        profile = document_to_dict(doc)
        
        # Format timestamp fields for JSON serialization
        if profile:
            profile = format_timestamp_fields(profile)
        
        return profile
    except Exception as e:
        st.error(f"Error loading profile: {e}")
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
            food_log_data["timestamp"] = datetime.now()
        
        # Add to Firestore
        db.collection('users').document(user_id).collection('food_logs').add(food_log_data)
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
        query = query.order_by("timestamp", direction="asc")
        
        # Execute query
        docs = query.get()
        
        # Convert to list of dicts
        logs = [document_to_dict(doc) for doc in docs]
        
        # Format timestamp fields for JSON serialization
        logs = format_timestamp_fields(logs)
        
        return logs
    except Exception as e:
        st.error(f"Error loading food logs: {e}")
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
        db.collection('users').document(user_id).collection('food_logs').document(entry_id).update(updated_data)
        return True
    except Exception as e:
        st.error(f"Error updating food log entry: {e}")
        return False