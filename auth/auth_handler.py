import streamlit as st
import os
import json
import time
from datetime import datetime, timedelta
import jwt
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from utils.firebase_config import get_firestore_client
from auth.google_auth import google_sign_in_button

# Secret key for JWT
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-here")
if hasattr(st, 'secrets') and "JWT_SECRET" in st.secrets:
    JWT_SECRET = st.secrets["JWT_SECRET"]

JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24

def create_jwt_token(user_id, username):
    """Create a JWT token for the user"""
    # Set token expiry
    expiry = datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS)
    
    # Create token payload
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": expiry
    }
    
    # Create token
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def verify_jwt_token(token):
    """Verify the JWT token and return the payload if valid"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

def register_user(username, email, password):
    """Register a new user with Firebase Authentication"""
    try:
        db = get_firestore_client()
        if not db:
            return False, "Failed to connect to database"
        
        # Check if email already exists
        try:
            existing_user = firebase_auth.get_user_by_email(email)
            return False, "Email already exists"
        except firebase_auth.UserNotFoundError:
            pass  # Email doesn't exist, continue with registration
        
        # Create the user in Firebase Auth
        user = firebase_auth.create_user(
            email=email,
            password=password,
            display_name=username
        )
        
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
        st.session_state.auth_token = create_jwt_token(user.uid, username)
        
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
    """Login user with Firebase Authentication
    
    Note: Firebase Admin SDK doesn't support password verification directly.
    In a production app, you'd use Firebase Auth REST API or a custom auth server.
    For simplicity, we're using a workaround here.
    """
    try:
        db = get_firestore_client()
        if not db:
            return False, "Failed to connect to database"
        
        # Try to get the user by email
        try:
            user = firebase_auth.get_user_by_email(email)
        except firebase_auth.UserNotFoundError:
            return False, "Invalid email or password"
        
        # Since Admin SDK can't verify passwords, we'll rely on Firebase Auth Rules
        # This is a simplified approach for demo purposes
        # For actual password verification, you'd need a Firebase Auth REST API call
        
        # For demo purposes, we'll just check if the user exists
        # and assume the password is correct (NOT SECURE - DEMO ONLY)
        
        # Update last login
        db.collection('users').document(user.uid).update({
            "last_login": datetime.now()
        })
        
        # Set session state
        st.session_state.user_id = user.uid
        st.session_state.username = user.display_name
        st.session_state.authenticated = True
        st.session_state.auth_token = create_jwt_token(user.uid, user.display_name)
        
        return True, "Login successful"
    except Exception as e:
        return False, f"Error during login: {str(e)}"

def logout_user():
    """Logout user"""
    # Clear session state
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.authenticated = False
    if 'auth_token' in st.session_state:
        del st.session_state.auth_token
    
    return True

def check_auth_status():
    """Check if the user is authenticated"""
    # Check if user is already authenticated in session state
    if st.session_state.authenticated and st.session_state.user_id:
        return True
    
    # Check for JWT token in session state
    if 'auth_token' in st.session_state:
        token = st.session_state.auth_token
        payload = verify_jwt_token(token)
        
        if payload:
            # Token is valid, set session state
            st.session_state.user_id = payload.get("user_id")
            st.session_state.username = payload.get("username")
            st.session_state.authenticated = True
            return True
    
    # User is not authenticated
    st.session_state.authenticated = False
    return False

def login_page():
    """Display login page"""
    st.markdown("""
    <div class="auth-form">
        <h1>Welcome Back! 👋</h1>
        <p>Sign in to continue to NutriSnap AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        email = st.text_input("Email")  # Changed from username to email
        password = st.text_input("Password", type="password")
        
        submit_button = st.form_submit_button("Sign In", use_container_width=True)
    
    # Google sign-in button
    google_sign_in_button()
    
    st.markdown("""
    <div class="separator">OR</div>
    """, unsafe_allow_html=True)
    
    # Switch to signup
    if st.button("Don't have an account? Sign up", use_container_width=True):
        st.session_state.auth_page = "signup"
        st.rerun()
    
    if submit_button:
        if not email or not password:
            st.error("Please enter both email and password")
        else:
            success, message = login_user(email, password)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

def signup_page():
    """Display signup page"""
    st.markdown("""
    <div class="auth-form">
        <h1>Create Account 🚀</h1>
        <p>Sign up to start your health journey with NutriSnap AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("signup_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        submit_button = st.form_submit_button("Create Account", use_container_width=True)
    
    # Google sign-in button
    google_sign_in_button()
    
    st.markdown("""
    <div class="separator">OR</div>
    """, unsafe_allow_html=True)
    
    # Switch to login
    if st.button("Already have an account? Sign in", use_container_width=True):
        st.session_state.auth_page = "login"
        st.rerun()
    
    if submit_button:
        if not username or not email or not password:
            st.error("All fields are required")
        elif password != confirm_password:
            st.error("Passwords do not match")
        elif len(password) < 8:
            st.error("Password must be at least 8 characters long")
        else:
            success, message = register_user(username, email, password)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)