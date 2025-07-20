import os
from dotenv import load_dotenv
from datetime import datetime, timezone

# Load environment variables
load_dotenv()

# API configurations
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Firebase configurations
FIREBASE_CONFIG = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID")
}

# Firebase Admin SDK Service Account (for server-side operations)
FIREBASE_ADMIN_KEY_PATH = os.getenv("FIREBASE_ADMIN_KEY_PATH", "firebase-admin-key.json")

# Gemini Model configurations
GEMINI_MODEL = "gemini-2.0-flash"
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