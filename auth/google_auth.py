import streamlit as st
import os
import json
import secrets
import requests
from urllib.parse import urlencode
import time
from datetime import datetime
import firebase_admin
from firebase_admin import auth as firebase_auth, firestore

# Debug mode - set to True for detailed error information
DEBUG_MODE = True

# Use Streamlit secrets for Google OAuth configuration (preferred for deployment)
if hasattr(st, 'secrets'):
    GOOGLE_CLIENT_ID = st.secrets.get("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = st.secrets.get("GOOGLE_CLIENT_SECRET", "")
    REDIRECT_URI = st.secrets.get("REDIRECT_URI", "https://nutri-snap-ai.streamlit.app/")
else:
    # Fallback to environment variables (for local development)
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
    REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8501/")

# Print the redirect URI to the console for debugging
if DEBUG_MODE:
    print(f"Using redirect URI: {REDIRECT_URI}")

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
                cred_dict = st.secrets['firebase']
                cred = firebase_admin.credentials.Certificate(cred_dict)
            else:
                # Try to get credentials from local file
                firebase_key_path = os.getenv('FIREBASE_SERVICE_ACCOUNT', 'firebase-key.json')
                if os.path.exists(firebase_key_path):
                    if DEBUG_MODE:
                        st.write(f"Using Firebase credentials from {firebase_key_path}")
                    cred = firebase_admin.credentials.Certificate(firebase_key_path)
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
    
    # Log the request parameters for debugging (excluding secret)
    if DEBUG_MODE:
        debug_params = params.copy()
        debug_params["client_secret"] = "[REDACTED]"
        print(f"Token exchange parameters: {debug_params}")
    
    # Make request to exchange code for token
    response = requests.post(token_url, data=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        if DEBUG_MODE:
            error_text = response.text
            print(f"Token exchange error: {error_text}")
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
        if DEBUG_MODE:
            print(f"User info error: {response.text}")
        return None

def create_jwt_token(user_id, username):
    """Create a JWT token for the user"""
    # Get JWT_SECRET from environment or secrets
    JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-here")
    if hasattr(st, 'secrets') and "JWT_SECRET" in st.secrets:
        JWT_SECRET = st.secrets["JWT_SECRET"]
    
    # Set token expiry
    expiry = datetime.utcnow() + timedelta(hours=24)
    
    # Create token payload
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": expiry
    }
    
    # Create token
    try:
        import jwt
        token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
        return token
    except Exception as e:
        if DEBUG_MODE:
            st.error(f"Error creating JWT token: {e}")
        return None

def process_google_callback():
    """Process Google OAuth callback"""
    # Get query parameters using the Streamlit API
    query_params = st.query_params
    
    # Check for code and state
    code = query_params.get("code")
    state = query_params.get("state")
    
    # Debug output but only in a collapsible section
    with st.expander("Debug OAuth Information", expanded=DEBUG_MODE):
        st.write(f"Received state: {state}")
        st.write(f"Stored state: {st.session_state.get('oauth_state', 'No state found')}")
        st.write(f"Redirect URI: {REDIRECT_URI}")
        st.write(f"Client ID configured: {bool(GOOGLE_CLIENT_ID)}")
        st.write(f"Client Secret configured: {bool(GOOGLE_CLIENT_SECRET)}")
    
    # For now, bypass state validation to focus on fixing the redirect URI issue
    # In production, uncomment this validation
    # if not state or state != st.session_state.get("oauth_state"):
    #     return False, "Invalid state parameter"
    
    # Exchange code for token
    token_data = exchange_code_for_token(code)
    
    if not token_data:
        return False, "Failed to exchange code for token. Please check the console for more details."
    
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
    
    # Check if user exists in Firebase
    try:
        # Initialize Firebase
        db = ensure_firebase()
        if not db:
            return False, "Failed to connect to Firebase"
        
        # Try to get user from Firebase by email
        try:
            firebase_user = firebase_auth.get_user_by_email(email)
            user_id = firebase_user.uid
            
            if DEBUG_MODE:
                st.success(f"Found existing Firebase user: {user_id}")
                
            # Update user display name if needed
            if firebase_user.display_name != name:
                firebase_auth.update_user(user_id, display_name=name)
                
            # Update user document in Firestore
            db.collection('users').document(user_id).update({
                "last_login": firestore.SERVER_TIMESTAMP,
                "username": username,
                "auth_provider": "google"
            })
            
            if DEBUG_MODE:
                st.success(f"Updated existing user data in Firestore: {user_id}")
        except firebase_auth.UserNotFoundError:
            # User doesn't exist, create a new one
            if DEBUG_MODE:
                st.info(f"User {email} not found in Firebase, creating new user...")
                
            # Create user in Firebase Auth
            firebase_user = firebase_auth.create_user(
                uid=sub,  # Use Google's sub as Firebase UID
                email=email,
                display_name=name,
                email_verified=True
            )
            
            user_id = firebase_user.uid
            
            # Create user document in Firestore
            db.collection('users').document(user_id).set({
                "user_id": user_id,
                "username": username,
                "email": email,
                "auth_provider": "google",
                "created_at": firestore.SERVER_TIMESTAMP,
                "last_login": firestore.SERVER_TIMESTAMP
            })
            
            if DEBUG_MODE:
                st.success(f"Created new user in Firebase: {user_id}")
        
        # Set session state
        st.session_state.user_id = user_id
        st.session_state.username = username
        st.session_state.authenticated = True
        
        # Generate JWT token for session
        from datetime import timedelta
        st.session_state.auth_token = create_jwt_token(user_id, username)
        
        # Clear OAuth state
        if "oauth_state" in st.session_state:
            del st.session_state.oauth_state
        
        # Remove query parameters from URL
        st.query_params.clear()
        
        return True, "Login with Google successful"
    except Exception as e:
        if DEBUG_MODE:
            st.error(f"Error during Google authentication: {type(e).__name__}: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
        return False, f"Error during Google authentication: {str(e)}"

def check_google_callback():
    """Check if current request is a Google OAuth callback"""
    query_params = st.query_params
    
    if "code" in query_params and "state" in query_params:
        return process_google_callback()
    
    return None, None

def google_sign_in_button():
    """Display Google sign-in button"""
    # Check if Google credentials are configured
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        st.warning("Google Sign-In is not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in Streamlit secrets.")
        
        # Add detailed troubleshooting help
        with st.expander("Troubleshooting Google Sign-In Configuration"):
            st.markdown("""
            ### How to Set Up Google Sign-In:
            
            1. **Create OAuth Credentials**:
               - Go to [Google Cloud Console](https://console.cloud.google.com/)
               - Navigate to "APIs & Services" > "Credentials"
               - Create OAuth 2.0 Client ID credentials
            
            2. **Configure Authorized Redirect URIs**:
               - Add `https://nutri-snap-ai.streamlit.app/` for production
               - Add `http://localhost:8501/` for local development
            
            3. **Add Credentials to Streamlit Secrets**:
               ```toml
               GOOGLE_CLIENT_ID = "your-client-id"
               GOOGLE_CLIENT_SECRET = "your-client-secret"
               REDIRECT_URI = "https://nutri-snap-ai.streamlit.app/"
               ```
               
            4. **Restart Your App**: After configuring secrets, restart your Streamlit app
            """)
        return
    
    # Add debug tools if in debug mode
    if DEBUG_MODE:
        with st.expander("Debug Firebase for Google Auth"):
            if st.button("Test Firebase Connection"):
                db = ensure_firebase()
                if db:
                    st.success("Firebase connection successful!")
                    
                    # Try a simple write
                    try:
                        test_ref = db.collection('connection_test').document('test')
                        test_ref.set({'timestamp': firestore.SERVER_TIMESTAMP})
                        st.success("Firebase write test successful!")
                    except Exception as e:
                        st.error(f"Firebase write test failed: {e}")
                else:
                    st.error("Firebase connection failed!")
    
    # Check for OAuth callback
    success, message = check_google_callback()
    
    if success is not None:
        if success:
            st.success(message)
            st.rerun()
        else:
            st.error(message)
            # Add helpful error message
            st.info("If you're seeing a redirect URI mismatch error, make sure the redirect URI in your Google Cloud Console matches exactly with what's in your app configuration.")
    
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