import firebase_admin
from firebase_admin import credentials, firestore, auth
from google.cloud.firestore_v1.base_query import FieldFilter
import pandas as pd
from datetime import datetime
import hashlib
import pyrebase
import streamlit as st
import json
import os

class FirebaseHandler:
    def __init__(self):
        # Initialize Firebase Admin SDK (for server-side operations)
        if not firebase_admin._apps:
            try:
                # Try to get Firebase credentials from multiple sources
                service_account_info = self._get_firebase_credentials()
                
                if service_account_info:
                    cred = credentials.Certificate(service_account_info)
                    firebase_admin.initialize_app(cred)
                    print("Firebase Admin SDK initialized successfully")
                else:
                    raise ValueError("No valid Firebase credentials found")
                
            except Exception as e:
                error_msg = f"Failed to initialize Firebase Admin: {e}"
                print(error_msg)
                st.error(error_msg)
                raise e
        
        self.db = firestore.client()
        
        # Initialize Pyrebase for client-side authentication
        firebase_config = self._get_firebase_config()
        self.firebase = pyrebase.initialize_app(firebase_config)
        self.auth = self.firebase.auth()

    def _get_firebase_credentials(self):
        """Try multiple ways to get Firebase credentials"""
        
        # Method 1: Try direct JSON content from environment variable
        firebase_key_json = os.getenv("FIREBASE_ADMIN_KEY_PATH")
        if firebase_key_json and firebase_key_json.strip().startswith('{'):
            try:
                return json.loads(firebase_key_json)
            except json.JSONDecodeError:
                print("Failed to parse FIREBASE_ADMIN_KEY_PATH as JSON")
        
        # Method 2: Try Streamlit secrets (for Streamlit Cloud)
        if hasattr(st, 'secrets'):
            try:
                # Try to get the full JSON from secrets
                if "FIREBASE_ADMIN_KEY_PATH" in st.secrets:
                    firebase_key = st.secrets["FIREBASE_ADMIN_KEY_PATH"]
                    if isinstance(firebase_key, str) and firebase_key.strip().startswith('{'):
                        return json.loads(firebase_key)
                
                # Try to build from individual components in secrets
                if all(key in st.secrets for key in ["FIREBASE_PROJECT_ID", "FIREBASE_PRIVATE_KEY", "FIREBASE_CLIENT_EMAIL"]):
                    return {
                        "type": "service_account",
                        "project_id": st.secrets["FIREBASE_PROJECT_ID"],
                        "private_key_id": st.secrets.get("FIREBASE_PRIVATE_KEY_ID", ""),
                        "private_key": st.secrets["FIREBASE_PRIVATE_KEY"].replace('\\n', '\n'),
                        "client_email": st.secrets["FIREBASE_CLIENT_EMAIL"],
                        "client_id": st.secrets.get("FIREBASE_CLIENT_ID", ""),
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                        "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{st.secrets['FIREBASE_CLIENT_EMAIL'].replace('@', '%40')}",
                        "universe_domain": "googleapis.com"
                    }
            except Exception as e:
                print(f"Failed to get credentials from Streamlit secrets: {e}")
        
        # Method 3: Try individual environment variables
        if all(os.getenv(key) for key in ["FIREBASE_PROJECT_ID", "FIREBASE_PRIVATE_KEY", "FIREBASE_CLIENT_EMAIL"]):
            return {
                "type": "service_account",
                "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID", ""),
                "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace('\\n', '\n'),
                "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                "client_id": os.getenv("FIREBASE_CLIENT_ID", ""),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{os.getenv('FIREBASE_CLIENT_EMAIL', '').replace('@', '%40')}",
                "universe_domain": "googleapis.com"
            }
        
        # Method 4: Try local file (for development)
        firebase_key_path = os.getenv("FIREBASE_ADMIN_KEY_PATH", "firebase-admin-key.json")
        if os.path.isfile(firebase_key_path):
            with open(firebase_key_path, 'r') as f:
                return json.load(f)
        
        return None

    def _get_firebase_config(self):
        """Get Firebase web config from environment variables or Streamlit secrets"""
        
        # Try Streamlit secrets first (for cloud deployment)
        if hasattr(st, 'secrets'):
            try:
                return {
                    "apiKey": st.secrets.get("FIREBASE_API_KEY"),
                    "authDomain": st.secrets.get("FIREBASE_AUTH_DOMAIN"),
                    "databaseURL": st.secrets.get("FIREBASE_DATABASE_URL"),
                    "projectId": st.secrets.get("FIREBASE_PROJECT_ID"),
                    "storageBucket": st.secrets.get("FIREBASE_STORAGE_BUCKET"),
                    "messagingSenderId": st.secrets.get("FIREBASE_MESSAGING_SENDER_ID"),
                    "appId": st.secrets.get("FIREBASE_APP_ID")
                }
            except:
                pass
        
        # Fallback to environment variables
        return {
            "apiKey": os.getenv("FIREBASE_API_KEY"),
            "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
            "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),
            "projectId": os.getenv("FIREBASE_PROJECT_ID"),
            "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
            "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
            "appId": os.getenv("FIREBASE_APP_ID")
        }

    def serialize_datetime(self, obj):
        """Convert Firestore datetime objects to serializable format"""
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        return obj

    def serialize_user_data(self, user_data):
        """Serialize user data for session storage"""
        if not user_data:
            return user_data
        
        serialized = {}
        for key, value in user_data.items():
            if hasattr(value, 'isoformat'):  # datetime object
                serialized[key] = value.isoformat()
            else:
                serialized[key] = value
        return serialized

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def create_user(self, username, email, name, password):
        try:
            # Use Pyrebase client SDK to create user (compatible with login)
            user = self.auth.create_user_with_email_and_password(email, password)
            
            # Store additional user data in Firestore using the username as document ID
            user_data = {
                "username": username,
                "email": email,
                "name": name,
                "firebase_uid": user['localId'],  # Store the Firebase UID for reference
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            self.db.collection('users').document(username).set(user_data)
            return True
            
        except Exception as e:
            print(f"Error creating user: {e}")
            # Handle specific Firebase errors
            error_message = str(e)
            if "EMAIL_EXISTS" in error_message:
                raise Exception("This email is already registered. Please use a different email.")
            elif "WEAK_PASSWORD" in error_message:
                raise Exception("Password is too weak. Please use a stronger password.")
            elif "INVALID_EMAIL" in error_message:
                raise Exception("Please enter a valid email address.")
            else:
                raise Exception(f"Registration failed: {error_message}")

    def authenticate_user(self, email, password):
        try:
            # Sign in user with email and password using Pyrebase
            user = self.auth.sign_in_with_email_and_password(email, password)
            
            # Get user data from Firestore using the email to find username
            user_data = self.get_user_by_email(email)
            if user_data:
                user_data['uid'] = user['localId']
                user_data['token'] = user.get('idToken', '')
                
                # Serialize datetime objects for session storage
                serialized_user_data = self.serialize_user_data(user_data)
                return serialized_user_data
            else:
                # If no user data found in Firestore, create minimal data
                print(f"User found in Auth but not in Firestore: {email}")
                return {
                    "username": email.split('@')[0],  # Use email prefix as username
                    "email": email,
                    "name": email.split('@')[0],
                    "uid": user['localId'],
                    "token": user.get('idToken', '')
                }
            
        except Exception as e:
            print(f"Authentication error: {e}")
            error_message = str(e)
            
            # Handle specific Firebase auth errors
            if "INVALID_PASSWORD" in error_message or "INVALID_LOGIN_CREDENTIALS" in error_message:
                return None  # Invalid credentials
            elif "EMAIL_NOT_FOUND" in error_message:
                return None  # Email not registered
            elif "TOO_MANY_ATTEMPTS_TRY_LATER" in error_message:
                raise Exception("Too many failed login attempts. Please try again later.")
            elif "USER_DISABLED" in error_message:
                raise Exception("This account has been disabled.")
            elif "INVALID_EMAIL" in error_message:
                raise Exception("Please enter a valid email address.")
            else:
                print(f"Unexpected auth error: {error_message}")
                return None

    def get_user_by_username(self, username):
        try:
            user_doc = self.db.collection('users').document(username).get()
            if user_doc.exists:
                return self.serialize_user_data(user_doc.to_dict())
            return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None

    def get_user_by_email(self, email):
        try:
            users_ref = self.db.collection('users')
            query = users_ref.where(filter=FieldFilter('email', '==', email)).limit(1)
            docs = query.stream()
            
            for doc in docs:
                user_data = doc.to_dict()
                user_data['username'] = doc.id
                return self.serialize_user_data(user_data)
            return None
            
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None

    def authenticate_google_user(self, google_user_info):
        """Authenticate or create user using Google OAuth data"""
        try:
            email = google_user_info.get('email')
            google_id = google_user_info.get('google_id')
            
            if not email or not google_id:
                raise Exception("Invalid Google user data")
            
            # Check if user already exists by email
            existing_user = self.get_user_by_email(email)
            
            if existing_user:
                # Update existing user with Google ID if not already set
                if not existing_user.get('google_id'):
                    self.update_user_google_id(existing_user['username'], google_id)
                    existing_user['google_id'] = google_id
                
                # Add authentication info
                existing_user['auth_method'] = 'google'
                existing_user['uid'] = google_id
                return self.serialize_user_data(existing_user)
            else:
                # Create new user from Google data
                username = self.generate_username_from_email(email)
                name = google_user_info.get('name', google_user_info.get('given_name', email.split('@')[0]))
                
                user_data = {
                    "username": username,
                    "email": email,
                    "name": name,
                    "google_id": google_id,
                    "profile_picture": google_user_info.get('picture', ''),
                    "verified_email": google_user_info.get('verified_email', False),
                    "auth_method": "google",
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }
                
                # Save to Firestore
                self.db.collection('users').document(username).set(user_data)
                
                # Add authentication info for return
                user_data['uid'] = google_id
                return self.serialize_user_data(user_data)
                
        except Exception as e:
            print(f"Google authentication error: {e}")
            raise Exception(f"Google authentication failed: {str(e)}")

    def generate_username_from_email(self, email):
        """Generate a unique username from email"""
        base_username = email.split('@')[0].lower()
        username = base_username
        counter = 1
        
        # Check if username exists and generate unique one
        while self.get_user_by_username(username):
            username = f"{base_username}{counter}"
            counter += 1
            
        return username

    def update_user_google_id(self, username, google_id):
        """Update existing user with Google ID"""
        try:
            user_ref = self.db.collection('users').document(username)
            user_ref.update({
                'google_id': google_id,
                'updated_at': datetime.now()
            })
            return True
        except Exception as e:
            print(f"Error updating user Google ID: {e}")
            return False

    def save_bill(self, username, date, category, amount, description):
        try:
            # Convert date to string if it's a datetime object
            if isinstance(date, datetime):
                date_str = date.strftime('%Y-%m-%d')
            elif hasattr(date, 'strftime'):
                date_str = date.strftime('%Y-%m-%d')
            else:
                date_str = str(date)
            
            bill_data = {
                "username": username,
                "date": date_str,
                "category": category,
                "amount": float(amount),
                "description": description or "",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            # Add bill to Firestore
            doc_ref = self.db.collection('bills').add(bill_data)
            #print(f"Bill saved with ID: {doc_ref[1].id}")
            return True
            
        except Exception as e:
            print(f"Error saving bill: {e}")
            return False

    def get_bills(self, username):
        try:
            # Use simpler query to avoid index requirements initially
            bills_ref = self.db.collection('bills')
            query = bills_ref.where(filter=FieldFilter('username', '==', username))
            docs = query.stream()
            
            bills = []
            for doc in docs:
                bill_data = doc.to_dict()
                bill_data['id'] = doc.id
                bills.append(bill_data)
            
            if bills:
                df = pd.DataFrame(bills)
                # Sort by date in Python instead of Firestore to avoid index requirement
                if 'date' in df.columns:
                    df['date'] = df['date'].astype(str)
                    df = df.sort_values('date', ascending=False)
                return df
            
            return pd.DataFrame()
            
        except Exception as e:
            print(f"Error getting bills: {e}")
            return pd.DataFrame()

    def delete_bill(self, bill_id):
        try:
            self.db.collection('bills').document(bill_id).delete()
            return True
        except Exception as e:
            print(f"Error deleting bill: {e}")
            return False

    def get_monthly_summary(self, username):
        try:
            bills_ref = self.db.collection('bills')
            query = bills_ref.where(filter=FieldFilter('username', '==', username))
            docs = query.stream()
            
            bills = []
            for doc in docs:
                bill_data = doc.to_dict()
                bills.append(bill_data)
            
            if bills:
                df = pd.DataFrame(bills)
                df['date'] = pd.to_datetime(df['date'])
                df['month'] = df['date'].dt.strftime('%Y-%m')
                monthly_summary = df.groupby('month')['amount'].sum().reset_index()
                monthly_summary.columns = ['month', 'total_amount']
                return monthly_summary
            
            return pd.DataFrame()
            
        except Exception as e:
            print(f"Error getting monthly summary: {e}")
            return pd.DataFrame()

    def get_category_summary(self, username):
        try:
            bills_ref = self.db.collection('bills')
            query = bills_ref.where(filter=FieldFilter('username', '==', username))
            docs = query.stream()
            
            bills = []
            for doc in docs:
                bill_data = doc.to_dict()
                bills.append(bill_data)
            
            if bills:
                df = pd.DataFrame(bills)
                category_summary = df.groupby('category')['amount'].sum().reset_index()
                category_summary.columns = ['category', 'total_amount']
                return category_summary
            
            return pd.DataFrame()
            
        except Exception as e:
            print(f"Error getting category summary: {e}")
            return pd.DataFrame()

    def update_user(self, username, name, email, password=None):
        try:
            update_data = {
                "name": name,
                "email": email,
                "updated_at": datetime.now()
            }
            
            # Update Firestore document
            self.db.collection('users').document(username).update(update_data)
            
            # Note: Password updates with Pyrebase client SDK are more complex
            # For now, we'll just update the profile information
            # Password changes would typically require re-authentication
            if password:
                print("Password update requested but requires re-authentication")
                # In a production app, you'd implement password change with re-auth
            
            return True
            
        except Exception as e:
            print(f"Error updating user: {e}")
            return False