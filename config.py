import os
import streamlit as st
from dotenv import load_dotenv
from datetime import datetime, timezone

# Load environment variables for local development
load_dotenv()

def get_env_or_secret(key, default=None):
    """Get value from environment variables or Streamlit secrets"""
    # Try Streamlit secrets first (for cloud deployment)
    if hasattr(st, 'secrets') and key in st.secrets:
        return st.secrets[key]
    # Fallback to environment variables (for local development)
    return os.getenv(key, default)

# API configurations
GOOGLE_API_KEY = get_env_or_secret("GOOGLE_API_KEY")

# Firebase configurations - these will be handled directly in database.py
# We're not defining FIREBASE_CONFIG here anymore to avoid issues

# Firebase Admin SDK Service Account - this will be handled in database.py
# We're not defining FIREBASE_ADMIN_KEY_PATH here anymore

# Gemini Model configurations
GEMINI_MODEL = "gemini-1.5-flash"
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

# Debug: Print configuration status (without sensitive data)
print("=== Configuration Status ===")
print(f"Google API Key: {'✓' if GOOGLE_API_KEY else '✗'}")
print(f"Using Streamlit Secrets: {'✓' if hasattr(st, 'secrets') else '✗'}")
print("Firebase config will be handled in database.py")
print("=============================")