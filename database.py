import firebase_admin
from firebase_admin import credentials, firestore, auth
import pandas as pd
from datetime import datetime
import hashlib
import pyrebase
from config import FIREBASE_CONFIG, FIREBASE_ADMIN_KEY_PATH
import streamlit as st

class FirebaseHandler:
    def __init__(self):
        # Initialize Firebase Admin SDK (for server-side operations)
        if not firebase_admin._apps:
            try:
                cred = credentials.Certificate(FIREBASE_ADMIN_KEY_PATH)
                firebase_admin.initialize_app(cred)
            except Exception as e:
                st.error(f"Failed to initialize Firebase Admin: {e}")
        
        self.db = firestore.client()
        
        # Initialize Pyrebase for client-side authentication
        self.firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
        self.auth = self.firebase.auth()

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
            return False

    def authenticate_user(self, email, password):
        try:
            # Sign in user with email and password using Pyrebase
            user = self.auth.sign_in_with_email_and_password(email, password)
            
            # Get user data from Firestore using the email to find username
            user_data = self.get_user_by_email(email)
            if user_data:
                user_data['uid'] = user['localId']
                user_data['token'] = user.get('idToken', '')
                return user_data
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
            return user_doc.to_dict() if user_doc.exists else None
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
                return user_data
            return None
            
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None

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
            self.db.collection('bills').add(bill_data)
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