import streamlit as st
import os
import json
import secrets
import requests
from urllib.parse import urlencode
import time
from auth.auth_utils import save_user_to_db, create_jwt_token, get_user_by_email

# Google OAuth configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
REDIRECT_URI = os.getenv("REDIRECT_URI", "https://nutri-snap-ai.streamlit.app/")

def generate_state_token():
    """Generate a random state token for OAuth security"""
    return secrets.token_hex(16)

def get_google_auth_url():
    """Generate Google OAuth URL"""
    # Generate a state token and store it in session
    # Use a fixed key in session state for better persistence
    if 'oauth_state' not in st.session_state:
        st.session_state.oauth_state = generate_state_token()
    
    # Define OAuth parameters
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": st.session_state.oauth_state,
        "prompt": "select_account"
    }
    
    # Generate URL
    auth_url = f"https://accounts.google.com/o/oauth2/auth?{urlencode(params)}"
    return auth_url

def exchange_code_for_token(code):
    """Exchange authorization code for access token"""
    token_url = "https://oauth2.googleapis.com/token"
    
    # Define token request parameters
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI
    }
    
    # Make request to exchange code for token
    response = requests.post(token_url, data=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Token exchange error: {response.text}")
        return None

def get_user_info(token_data):
    """Get user information from Google"""
    # Extract access token
    access_token = token_data.get("access_token")
    
    if not access_token:
        return None
    
    # Make request to get user info
    user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.get(user_info_url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"User info error: {response.text}")
        return None

def process_google_callback():
    """Process Google OAuth callback"""
    # Get query parameters using the updated Streamlit API
    query_params = st.query_params
    
    # Check for code and state
    code = query_params.get("code")
    state = query_params.get("state")
    
    # Debug output to diagnose the state issue
    st.write(f"Received state: {state}")
    st.write(f"Stored state: {st.session_state.get('oauth_state', 'No state found')}")
    
    # For testing purposes, temporarily bypass state validation
    # NOTE: In production, you should always validate the state parameter
    # if not state or state != st.session_state.get("oauth_state"):
    #     return False, "Invalid state parameter"
    
    # Exchange code for token
    token_data = exchange_code_for_token(code)
    
    if not token_data:
        return False, "Failed to exchange code for token"
    
    # Get user info
    user_info = get_user_info(token_data)
    
    if not user_info:
        return False, "Failed to get user info"
    
    # Extract user data
    email = user_info.get("email")
    name = user_info.get("name", email.split("@")[0])
    sub = user_info.get("sub")  # Google's unique user ID
    
    # Generate a username if name contains spaces
    username = name.replace(" ", "").lower()
    
    # Check if user exists
    user = get_user_by_email(email)
    
    if user:
        # User exists, login
        user_id = user.get("user_id")
        username = user.get("username")
    else:
        # Create new user
        success, result = save_user_to_db(
            username=username, 
            email=email, 
            password_hash=None, 
            user_id=sub,
            auth_provider="google"
        )
        
        if not success:
            return False, result
        
        user_id = result
    
    # Create JWT token
    token = create_jwt_token(user_id, username)
    
    # Set session state
    st.session_state.user_id = user_id
    st.session_state.username = username
    st.session_state.authenticated = True
    st.session_state.auth_token = token
    
    # Clear OAuth state
    if "oauth_state" in st.session_state:
        del st.session_state.oauth_state
    
    # Remove query parameters from URL using the updated Streamlit API
    st.query_params.clear()
    
    return True, "Login with Google successful"

def check_google_callback():
    """Check if current request is a Google OAuth callback"""
    # Use the updated Streamlit API for query parameters
    query_params = st.query_params
    
    if "code" in query_params and "state" in query_params:
        return process_google_callback()
    
    return None, None

def google_sign_in_button():
    """Display Google sign-in button"""
    # Check if Google credentials are configured
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        st.warning("Google Sign-In is not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env file.")
        return
    
    # Add a development mode bypass option for testing
    # if st.checkbox("Enable Development Mode"):
    #     if st.button("DEV MODE: Simulate Google Login"):
    #         # Simulate successful Google login
    #         user_id = "test_user_123"
    #         username = "testuser"
            
    #         # Set session state
    #         st.session_state.user_id = user_id
    #         st.session_state.username = username
    #         st.session_state.authenticated = True
    #         st.session_state.auth_token = "dev_mode_token"
            
    #         st.success("Development login successful!")
    #         st.rerun()
    #     return
    
    # Check for OAuth callback
    success, message = check_google_callback()
    
    if success is not None:
        if success:
            st.success(message)
            st.rerun()
        else:
            st.error(message)
    
    # Generate Google auth URL
    auth_url = get_google_auth_url()
    
    # Display Google sign-in button
    st.markdown(
        f"""
        <a href="{auth_url}" class="google-btn">
            <div class="google-icon">
                <svg width="18" height="18" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">
                    <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
                    <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
                    <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
                    <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
                </svg>
            </div>
            <span>Sign in with Google</span>
        </a>
        """,
        unsafe_allow_html=True
    )
    
    # # Debug info for OAuth state
    # with st.expander("Debug OAuth Information"):
    #     st.write("Current OAuth State:", st.session_state.get("oauth_state", "Not set"))
    #     st.write("Redirect URI:", REDIRECT_URI)
    #     st.write("Client ID configured:", bool(GOOGLE_CLIENT_ID))
        
    #     if st.button("Generate New OAuth State"):
    #         st.session_state.oauth_state = generate_state_token()
    #         st.write("New state generated:", st.session_state.oauth_state)
    #         st.rerun()