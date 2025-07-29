import streamlit as st
import os
import requests
from urllib.parse import urlencode
import secrets

class GoogleAuthHandler:
    def __init__(self):
        self.client_id = self._get_google_client_id()
        self.client_secret = self._get_google_client_secret()
        self.redirect_uri = self._get_redirect_uri()
        
        if not self.client_id or not self.client_secret:
            # Silently disable Google OAuth if not configured
            pass
            
    def _get_google_client_id(self):
        """Get Google Client ID from environment or Streamlit secrets"""
        # Try environment variable first
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        if client_id:
            return client_id
            
        # Try Streamlit secrets
        if hasattr(st, 'secrets') and "GOOGLE_CLIENT_ID" in st.secrets:
            return st.secrets["GOOGLE_CLIENT_ID"]
            
        return None

    def _get_google_client_secret(self):
        """Get Google Client Secret from environment or Streamlit secrets"""
        # Try environment variable first
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        if client_secret:
            return client_secret
            
        # Try Streamlit secrets
        if hasattr(st, 'secrets') and "GOOGLE_CLIENT_SECRET" in st.secrets:
            return st.secrets["GOOGLE_CLIENT_SECRET"]
            
        return None

    def _get_redirect_uri(self):
        """Get redirect URI from environment or Streamlit secrets"""
        # Try environment variable first
        redirect_uri = os.getenv("REDIRECT_URI")
        if redirect_uri:
            return redirect_uri
            
        # Try Streamlit secrets
        if hasattr(st, 'secrets') and "REDIRECT_URI" in st.secrets:
            return st.secrets["REDIRECT_URI"]
            
        return "http://localhost:8501"
    
    def render_google_login_button(self, button_text="Continue with Google", key_suffix=""):
        """Render Google OAuth login button with real OAuth flow"""
        if not self.client_id or not self.client_secret:
            st.info("ℹ️ Google sign-in is currently unavailable. Please use email/password authentication.")
            return None

        # Check if we have an authorization code in the URL
        query_params = st.query_params
        if "code" in query_params:
            auth_code = query_params["code"]
            state_from_url = query_params.get("state", "")
            
            # Show loading while processing
            with st.spinner("Authenticating with Google..."):
                # Handle OAuth callback immediately
                user_info = self.handle_oauth_callback(auth_code, state_from_url)
            
            # Clear query params after processing
            if user_info:
                st.query_params.clear()
                return user_info
            else:
                st.query_params.clear()
                return None

        # Generate OAuth URL
        auth_url = self._generate_auth_url()
        
        # Custom Google button styling
        google_button_html = f"""
        <div style="display: flex; justify-content: center; margin: 10px 0;">
            <a href="{auth_url}" target="_self" style="text-decoration: none;">
                <div style="
                    display: flex;
                    align-items: center;
                    padding: 12px 24px;
                    border: 1px solid #dadce0;
                    border-radius: 6px;
                    background-color: white;
                    color: #3c4043;
                    font-family: 'Google Sans', Roboto, sans-serif;
                    font-size: 14px;
                    font-weight: 500;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    width: 280px;
                    justify-content: center;
                    box-shadow: 0 1px 2px 0 rgba(60,64,67,.30), 0 1px 3px 1px rgba(60,64,67,.15);
                " onmouseover="this.style.boxShadow='0 1px 3px 0 rgba(60,64,67,.30), 0 4px 8px 3px rgba(60,64,67,.15)'" 
                   onmouseout="this.style.boxShadow='0 1px 2px 0 rgba(60,64,67,.30), 0 1px 3px 1px rgba(60,64,67,.15)'">
                    <svg style="width: 18px; height: 18px; margin-right: 12px;" viewBox="0 0 24 24">
                        <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                        <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                        <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                        <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                    </svg>
                    {button_text}
                </div>
            </a>
        </div>
        """
        
        st.markdown(google_button_html, unsafe_allow_html=True)
        return None

    def _generate_auth_url(self):
        """Generate Google OAuth authorization URL"""
        # Generate a secure state parameter
        state = secrets.token_urlsafe(16)
        
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "scope": "openid email profile",
            "redirect_uri": self.redirect_uri,
            "state": state,
            "access_type": "offline",
            "prompt": "select_account"
        }
        
        auth_url = f"https://accounts.google.com/o/oauth2/auth?{urlencode(params)}"
        return auth_url

    def handle_oauth_callback(self, auth_code, state_from_url=""):
        """Handle OAuth callback and get user info"""
        try:
            # Exchange authorization code for access token
            token_data = self._exchange_code_for_token(auth_code)
            
            if not token_data:
                st.error("Authentication failed. Please try again.")
                return None

            # Get user info from Google
            user_info = self._get_user_info_from_token(token_data["access_token"])
            
            return user_info
            
        except Exception as e:
            st.error("Authentication failed. Please try again.")
            return None

    def _exchange_code_for_token(self, auth_code):
        """Exchange authorization code for access token"""
        try:
            token_url = "https://oauth2.googleapis.com/token"
            
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": auth_code,
                "grant_type": "authorization_code",
                "redirect_uri": self.redirect_uri
            }
            
            response = requests.post(token_url, data=data, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Authentication failed. Please try again.")
                return None
                
        except Exception as e:
            st.error("Authentication failed. Please try again.")
            return None

    def _get_user_info_from_token(self, access_token):
        """Get user information from Google using access token"""
        try:
            # Use Google's userinfo endpoint
            response = requests.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    "email": user_data.get("email"),
                    "name": user_data.get("name"),
                    "given_name": user_data.get("given_name"),
                    "family_name": user_data.get("family_name"),
                    "picture": user_data.get("picture"),
                    "google_id": user_data.get("id"),
                    "verified_email": user_data.get("verified_email", False)
                }
            else:
                st.error("Failed to retrieve user information. Please try again.")
                return None
                
        except Exception as e:
            st.error("Authentication failed. Please try again.")
            return None
