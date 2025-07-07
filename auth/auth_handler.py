import streamlit as st
import os
from auth.auth_utils import (
    get_password_hash, 
    verify_password, 
    create_jwt_token, 
    verify_jwt_token, 
    get_user_by_username, 
    get_user_by_email, 
    get_user_by_id, 
    save_user_to_db, 
    update_last_login
)
from auth.google_auth import google_sign_in_button

def check_auth_status():
    """Check if the user is authenticated"""
    # Check if user is already authenticated in session state
    if st.session_state.authenticated and st.session_state.user_id:
        return True
    
    # Check for JWT token in cookies
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

def login_user(username, password):
    """Login user with username and password"""
    # Get user data
    user = get_user_by_username(username)
    
    if not user:
        return False, "Invalid username or password"
    
    # Check if user is using email authentication
    if user.get("auth_provider") != "email":
        return False, f"Please use {user.get('auth_provider')} to login"
    
    # Verify password
    if not verify_password(user.get("password", ""), password):
        return False, "Invalid username or password"
    
    # Update last login
    update_last_login(user.get("user_id"))
    
    # Create JWT token
    token = create_jwt_token(user.get("user_id"), user.get("username"))
    
    # Set session state
    st.session_state.user_id = user.get("user_id")
    st.session_state.username = user.get("username")
    st.session_state.authenticated = True
    st.session_state.auth_token = token
    
    return True, "Login successful"

def register_user(username, email, password, confirm_password):
    """Register a new user"""
    # Validate inputs
    if not username or not email or not password:
        return False, "All fields are required"
    
    if password != confirm_password:
        return False, "Passwords do not match"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    # Check if username or email already exists
    if get_user_by_username(username):
        return False, "Username already exists"
    
    if get_user_by_email(email):
        return False, "Email already exists"
    
    # Hash password
    password_hash = get_password_hash(password)
    
    # Save user to database
    success, result = save_user_to_db(username, email, password_hash)
    
    if not success:
        return False, result
    
    # Create JWT token
    token = create_jwt_token(result, username)
    
    # Set session state
    st.session_state.user_id = result
    st.session_state.username = username
    st.session_state.authenticated = True
    st.session_state.auth_token = token
    
    return True, "Registration successful"

def logout_user():
    """Logout user"""
    # Clear session state
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.authenticated = False
    if 'auth_token' in st.session_state:
        del st.session_state.auth_token
    
    return True

def login_page():
    """Display login page"""
    st.markdown("""
    <div class="auth-form">
        <h1>Welcome Back! 👋</h1>
        <p>Sign in to continue to NutriSnap AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Username")
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
        if not username or not password:
            st.error("Please enter both username and password")
        else:
            success, message = login_user(username, password)
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
        success, message = register_user(username, email, password, confirm_password)
        if success:
            st.success(message)
            st.rerun()
        else:
            st.error(message)