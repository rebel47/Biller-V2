import os
import json
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Initialize Firebase (if not already initialized)
def initialize_firebase():
    """Initialize Firebase if not already initialized"""
    try:
        # Check if we already have an initialized app
        firebase_app = None
        
        # Get the default app if it exists
        try:
            firebase_app = firebase_admin.get_app()
        except ValueError:
            # No default app exists, so create one
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
                    print("Firebase credentials not found. Please set up Firebase credentials.")
                    return None
            
            firebase_app = firebase_admin.initialize_app(cred)
        
        # Get Firestore client
        return firestore.client(app=firebase_app)
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        return None

# Get Firestore client
def get_firestore_client():
    """Get the Firestore client"""
    try:
        db = initialize_firebase()
        return db
    except Exception as e:
        print(f"Error getting Firestore client: {e}")
        return None

# Convert a Firestore document to a dict
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
            if hasattr(value, "timestamp"):  # Check if it's a Firestore timestamp
                data[key] = value.isoformat() if hasattr(value, 'isoformat') else str(value)
            elif isinstance(value, dict) or isinstance(value, list):
                data[key] = format_timestamp_fields(value)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            data[i] = format_timestamp_fields(item)
    return data