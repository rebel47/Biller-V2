import streamlit as st
import firebase_admin
from firebase_admin import auth as firebase_auth
from datetime import datetime, timedelta
from utils.firebase_config import get_firestore_client

def register_user(username, email, password):
    """Register a new user with Firebase Authentication"""
    try:
        # Create the user in Firebase Auth
        user = firebase_auth.create_user(
            email=email,
            password=password,
            display_name=username
        )
        
        # Get Firestore client
        db = get_firestore_client()
        if not db:
            return False, "Failed to connect to database"
        
        # Save additional user data to Firestore
        user_data = {
            "user_id": user.uid,
            "username": username,
            "email": email,
            "auth_provider": "email",
            "created_at": datetime.now(),
            "last_login": datetime.now()
        }
        
        db.collection('users').document(user.uid).set(user_data)
        
        # Set session state
        st.session_state.user_id = user.uid
        st.session_state.username = username
        st.session_state.authenticated = True
        
        return True, "Registration successful"
    except firebase_admin.exceptions.FirebaseError as e:
        error_message = str(e)
        if "EMAIL_EXISTS" in error_message:
            return False, "Email already exists"
        elif "WEAK_PASSWORD" in error_message:
            return False, "Password is too weak"
        else:
            return False, f"Firebase Auth error: {error_message}"
    except Exception as e:
        return False, f"Error during registration: {str(e)}"

def login_user(email, password):
    """Login with Firebase Authentication (custom token approach for Streamlit)"""
    try:
        # NOTE: Since Firebase client-side auth isn't available in Streamlit,
        # we're using a workaround to authenticate users.
        # In a production app, you'd use Firebase Admin SDK to verify
        # credentials and create custom tokens.
        
        # Get the user by email
        users = firebase_auth.get_users_by_email([email])
        
        if not users.users:
            return False, "Invalid email or password"
        
        user = users.users[0]
        
        # In a real implementation, you'd verify the password
        # For now, we'll trust the email (NOT SECURE - DEMO ONLY)
        # In production, use Firebase Auth REST API or a custom auth server
        
        # Get Firestore client
        db = get_firestore_client()
        if not db:
            return False, "Failed to connect to database"
        
        # Update last login
        db.collection('users').document(user.uid).update({
            "last_login": datetime.now()
        })
        
        # Set session state
        st.session_state.user_id = user.uid
        st.session_state.username = user.display_name
        st.session_state.authenticated = True
        
        return True, "Login successful"
    except firebase_admin.exceptions.FirebaseError as e:
        return False, f"Firebase Auth error: {str(e)}"
    except Exception as e:
        return False, f"Error during login: {str(e)}"

def logout_user():
    """Logout user"""
    # Clear session state
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.authenticated = False
    return True

def check_auth_status():
    """Check if the user is authenticated"""
    # Check if user is already authenticated in session state
    if st.session_state.authenticated and st.session_state.user_id:
        return True
    
    # User is not authenticated
    return False

def get_user_by_email(email):
    """Get user data by email"""
    try:
        # Get user from Firebase Auth
        users = firebase_auth.get_users_by_email([email])
        
        if not users.users:
            return None
        
        user = users.users[0]
        
        # Get additional user data from Firestore
        db = get_firestore_client()
        if not db:
            return None
        
        doc = db.collection('users').document(user.uid).get()
        
        if not doc.exists:
            return {
                "user_id": user.uid,
                "username": user.display_name,
                "email": user.email,
                "auth_provider": "email"
            }
        
        user_data = doc.to_dict()
        return user_data
    except Exception:
        return None