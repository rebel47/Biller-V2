import os
from dotenv import load_dotenv
from datetime import datetime, timezone

# Load environment variables
load_dotenv()

# API configurations
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Debug: Check if API key is loaded (only show length for security)
if GOOGLE_API_KEY:
    print(f"Google API Key loaded: Yes")
    print(f"API Key length: {len(GOOGLE_API_KEY)} characters")
else:
    print("Google API Key loaded: No")

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

# Firebase Admin SDK Service Account
# For Streamlit Cloud, this should be the JSON content as a string
# For local development, this can be a file path
FIREBASE_ADMIN_KEY_PATH = os.getenv("FIREBASE_ADMIN_KEY_PATH", "firebase-admin-key.json")

# Alternative way to handle Firebase service account (more explicit)
FIREBASE_SERVICE_ACCOUNT_KEY = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY")

# If FIREBASE_SERVICE_ACCOUNT_KEY is provided, use it; otherwise use FIREBASE_ADMIN_KEY_PATH
if FIREBASE_SERVICE_ACCOUNT_KEY:
    FIREBASE_ADMIN_KEY_PATH = FIREBASE_SERVICE_ACCOUNT_KEY

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

# Debug: Print configuration status (without sensitive data)
print("=== Configuration Status ===")
print(f"Google API Key: {'✓' if GOOGLE_API_KEY else '✗'}")
print(f"Firebase Config loaded: {'✓' if all(FIREBASE_CONFIG.values()) else '✗'}")
print(f"Firebase Admin Key: {'✓' if FIREBASE_ADMIN_KEY_PATH else '✗'}")
print(f"Firebase Admin Key type: {'JSON content' if FIREBASE_ADMIN_KEY_PATH and FIREBASE_ADMIN_KEY_PATH.strip().startswith('{') else 'File path'}")
print("=============================")