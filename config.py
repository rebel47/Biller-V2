import os
from dotenv import load_dotenv
from datetime import datetime, timezone
import streamlit as st

# Load environment variables
load_dotenv()

# API configurations
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Debug: Check if API key is loaded
print(f"Google API Key loaded: {'Yes' if GOOGLE_API_KEY else 'No'}")
if GOOGLE_API_KEY:
    print(f"API Key length: {len(GOOGLE_API_KEY)} characters")
    print(f"API Key starts with: {GOOGLE_API_KEY[:10]}...")

# # Firebase configurations
# FIREBASE_CONFIG = {
#     "apiKey": os.getenv("FIREBASE_API_KEY"),
#     "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
#     "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),
#     "projectId": os.getenv("FIREBASE_PROJECT_ID"),
#     "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
#     "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
#     "appId": os.getenv("FIREBASE_APP_ID")
# }

# # Firebase Admin SDK Service Account (for server-side operations)
# FIREBASE_ADMIN_KEY_PATH = os.getenv("FIREBASE_ADMIN_KEY_PATH", "firebase-admin-key.json")

# Firebase configurations (Client-side keys)
FIREBASE_CONFIG = {
    "apiKey": st.secrets.get("FIREBASE_API_KEY"),
    "authDomain": st.secrets.get("FIREBASE_AUTH_DOMAIN"),
    "databaseURL": st.secrets.get("FIREBASE_DATABASE_URL"),
    "projectId": st.secrets.get("FIREBASE_PROJECT_ID"),
    "storageBucket": st.secrets.get("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": st.secrets.get("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": st.secrets.get("FIREBASE_APP_ID"),
}

# Firebase Admin SDK (Server-side)
FIREBASE_ADMIN_KEY_PATH = st.secrets.get("FIREBASE_ADMIN_KEY_PATH", None)  # JSON content


# Gemini Model configurations
GEMINI_MODEL = "gemini-1.5-flash"  # Use stable model
GENERATION_CONFIG = {
    "temperature": 0.1,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 2048
}

# Image processing configurations
SUPPORTED_IMAGE_TYPES = ["jpg", "jpeg", "png", "heic"]

# Categories
EXPENSE_CATEGORIES = ["grocery", "utensil", "clothing", "miscellaneous"]

def get_current_utc_datetime():
    return datetime.now(timezone.utc)

# UI Theme Colors
THEME_COLORS = {
    "primary": "#667eea",
    "secondary": "#764ba2",
    "accent": "#f093fb",
    "background": "#f8fafc",
    "card": "#ffffff",
    "text": "#1a202c",
    "text_light": "#718096",
    "success": "#48bb78",
    "warning": "#ed8936",
    "error": "#f56565"
}