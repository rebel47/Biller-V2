import streamlit as st
import os
import json
import time
from datetime import datetime, timedelta
import jwt
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth, firestore
from utils.firebase_config import get_firestore_client
from auth.google_auth import google_sign_in_button

# Secret key for JWT
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-here")
if hasattr(st, 'secrets') and "JWT_SECRET" in st.secrets:
    JWT_SECRET = st.secrets["JWT_SECRET"]

JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24

# Debug mode - set to True for detailed error information
DEBUG_MODE = True

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

def ensure_firebase():
    """Initialize Firebase and get Firestore client with detailed error information"""
    try:
        # Check if Firebase is already initialized
        app = None
        try:
            app = firebase_admin.get_app()
        except ValueError:
            # Firebase not initialized, try to initialize
            if DEBUG_MODE:
                st.write("Firebase not initialized, attempting to initialize...")
            
            # Try to get credentials from Streamlit secrets
            if hasattr(st, 'secrets') and 'firebase' in st.secrets:
                if DEBUG_MODE:
                    st.write("Using Firebase credentials from Streamlit secrets")
                # Get only the firebase section from secrets
                cred_dict = dict(st.secrets['firebase'])
                cred = credentials.Certificate(cred_dict)
            else:
                # Try to get credentials from local file
                firebase_key_path = os.getenv('FIREBASE_SERVICE_ACCOUNT', 'firebase-key.json')
                if os.path.exists(firebase_key_path):
                    if DEBUG_MODE:
                        st.write(f"Using Firebase credentials from {firebase_key_path}")
                    cred = credentials.Certificate(firebase_key_path)
                else:
                    if DEBUG_MODE:
                        st.error(f"Firebase credentials not found at {firebase_key_path}")
                    return None
            
            # Initialize Firebase
            app = firebase_admin.initialize_app(cred)        
        # Get Firestore client
        db = firestore.client(app=app)
        
        # Test the connection
        test_ref = db.collection('connection_test').document('test')
        test_ref.set({'timestamp': firestore.SERVER_TIMESTAMP})
        
        if DEBUG_MODE:
            st.success("Firebase connection established successfully")
        
        return db
    except Exception as e:
        if DEBUG_MODE:
            st.error(f"Firebase initialization error: {type(e).__name__}: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
        return None

def register_user(username, email, password):
    """Register a new user with Firebase Authentication"""
    try:
        # Get Firestore client with enhanced debugging
        db = ensure_firebase()
        if not db:
            return False, "Failed to connect to database. Check Firebase credentials."
        
        # Check if email already exists
        try:
            existing_user = firebase_auth.get_user_by_email(email)
            return False, "Email already exists"
        except firebase_auth.UserNotFoundError:
            pass  # Email doesn't exist, continue with registration
        except Exception as e:
            if DEBUG_MODE:
                st.error(f"Error checking existing user: {type(e).__name__}: {str(e)}")
            return False, f"Error checking user: {str(e)}"
        
        # Create the user in Firebase Auth
        try:
            user = firebase_auth.create_user(
                email=email,
                password=password,
                display_name=username
            )
            
            if DEBUG_MODE:
                st.success(f"Firebase Auth user created: {user.uid}")
        except Exception as e:
            if DEBUG_MODE:
                st.error(f"Error creating Firebase Auth user: {type(e).__name__}: {str(e)}")
            return False, f"Error creating user: {str(e)}"
        
        # Save additional user data to Firestore
        try:
            user_data = {
                "user_id": user.uid,
                "username": username,
                "email": email,
                "auth_provider": "email",
                "created_at": datetime.now(),
                "last_login": datetime.now()
            }
            
            db.collection('users').document(user.uid).set(user_data)
            
            if DEBUG_MODE:
                st.success(f"User data saved to Firestore: {user.uid}")
        except Exception as e:
            if DEBUG_MODE:
                st.error(f"Error saving user data to Firestore: {type(e).__name__}: {str(e)}")
            # User was created in Auth but not in Firestore, should still allow login
            st.warning("User created but profile data could not be saved. Some features may be limited.")
        
        # Set session state
        st.session_state.user_id = user.uid
        st.session_state.username = username
        st.session_state.authenticated = True
        st.session_state.auth_token = create_jwt_token(user.uid, username)
        
        return True, "Registration successful"
    except firebase_admin.exceptions.FirebaseError as e:
        error_message = str(e)
        if DEBUG_MODE:
            st.error(f"Firebase Error: {error_message}")
        
        if "EMAIL_EXISTS" in error_message:
            return False, "Email already exists"
        elif "WEAK_PASSWORD" in error_message:
            return False, "Password is too weak"
        else:
            return False, f"Firebase Auth error: {error_message}"
    except Exception as e:
        if DEBUG_MODE:
            st.error(f"Unexpected error: {type(e).__name__}: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
        
        return False, f"Error during registration: {str(e)}"

def login_user(email, password):
    """Login user with Firebase Authentication
    
    Note: Firebase Admin SDK doesn't support password verification directly.
    For simplicity, we're using a workaround here.
    """
    try:
        # Get Firestore client with enhanced debugging
        db = ensure_firebase()
        if not db:
            return False, "Failed to connect to database. Check Firebase credentials."
        
        # Try to get the user by email
        try:
            user = firebase_auth.get_user_by_email(email)
            
            if DEBUG_MODE:
                st.success(f"Found user: {user.uid} ({user.display_name})")
        except firebase_auth.UserNotFoundError:
            return False, "Invalid email or password"
        except Exception as e:
            if DEBUG_MODE:
                st.error(f"Error finding user: {type(e).__name__}: {str(e)}")
            return False, f"Error finding user: {str(e)}"
        
        # Since Admin SDK can't verify passwords, we'll rely on Firebase Auth Rules
        # This is a simplified approach for demo purposes
        # For actual password verification, you'd need a Firebase Auth REST API call
        
        # For demo purposes, we'll just check if the user exists
        # and assume the password is correct (NOT SECURE - DEMO ONLY)
        
        # Update last login
        try:
            db.collection('users').document(user.uid).update({
                "last_login": datetime.now()
            })
            
            if DEBUG_MODE:
                st.success(f"Updated last login for user: {user.uid}")
        except Exception as e:
            if DEBUG_MODE:
                st.error(f"Error updating last login: {type(e).__name__}: {str(e)}")
            # Non-critical error, continue with login
            st.warning("Login successful but user data could not be updated.")
        
        # Set session state
        st.session_state.user_id = user.uid
        st.session_state.username = user.display_name
        st.session_state.authenticated = True
        st.session_state.auth_token = create_jwt_token(user.uid, user.display_name)
        
        return True, "Login successful"
    except Exception as e:
        if DEBUG_MODE:
            st.error(f"Unexpected error during login: {type(e).__name__}: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
        
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
        email = st.text_input("Email")
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
                
                # In debug mode, provide more context on the failure
                if DEBUG_MODE:
                    st.info("Checking Firebase initialization status...")
                    
                    # Try to initialize Firebase and show the result
                    db = ensure_firebase()
                    if db:
                        st.success("Firebase connection test successful")
                        
                        # Test a simple write operation
                        try:
                            test_ref = db.collection('connection_test').document('test')
                            test_ref.set({'timestamp': firestore.SERVER_TIMESTAMP})
                            st.success("Firestore write test successful")
                        except Exception as e:
                            st.error(f"Firestore write test failed: {e}")
                    else:
                        st.error("Firebase connection test failed")