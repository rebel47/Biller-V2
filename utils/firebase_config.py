import os
import json
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, auth
from datetime import datetime

# Initialize Firebase (if not already initialized)
def initialize_firebase():
    """Initialize Firebase if not already initialized"""
    if not firebase_admin._apps:
        # Check if running on Streamlit Cloud (using secrets)
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
                raise FileNotFoundError(
                    "Firebase credentials not found. Either create a 'firebase-key.json' file "
                    "or set up Streamlit secrets with Firebase credentials."
                )
        
        # Initialize the app
        firebase_admin.initialize_app(cred)
    
    return firestore.client()

# Get Firestore client
def get_firestore_client():
    """Get the Firestore client"""
    try:
        db = initialize_firebase()
        return db
    except Exception as e:
        st.error(f"Error initializing Firebase: {e}")
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
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, dict) or isinstance(value, list):
                data[key] = format_timestamp_fields(value)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            data[i] = format_timestamp_fields(item)
    return data