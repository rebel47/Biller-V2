import streamlit as st
import time
from database import FirebaseHandler
from ui_components import render_header, create_success_message, create_info_card
from utils import save_session
from google_auth import GoogleAuthHandler

def main():
    """Login page"""
    render_header("Biller", "Snap, Track, Save!")
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔑 Welcome Back!")
        
        with st.form("login_form", clear_on_submit=False):  # FIXED: Kept existing unique form key
            email = st.text_input(
                "📧 Email", 
                placeholder="Enter your email",
                key="login_email_input"  # FIXED: Added unique key
            )
            password = st.text_input(
                "🔒 Password", 
                type="password", 
                placeholder="Enter your password",
                key="login_password_input"  # FIXED: Added unique key
            )
            remember_me = st.checkbox(
                "🔐 Remember me for 7 days",
                key="login_remember_checkbox"  # FIXED: Added unique key
            )
            
            col_login, col_register = st.columns([2, 1])
            
            with col_login:
                login_button = st.form_submit_button("Sign In", use_container_width=True)
            
            with col_register:
                register_clicked = st.form_submit_button("Need Account?", use_container_width=True)
                
            if register_clicked:
                st.session_state["show_register"] = True
                st.rerun()
            
            if login_button and email and password:
                handle_login(email, password, remember_me)

        # Google Sign In - moved below the form
        st.markdown("---")
        st.markdown("##### Or continue with")
        google_auth = GoogleAuthHandler()
        google_user_info = google_auth.render_google_login_button("Sign in with Google", "login")
        
        if google_user_info:
            handle_google_login(google_user_info)

    # Add feature highlights
    col1, col2, col3, col4 = st.columns(4)
    
    features = [
        ("🤖", "AI-Powered", "Automatic receipt scanning with AI"),
        ("📊", "Analytics", "Real-time insights and spending trends"),
        ("🔒", "Secure", "Firebase authentication and encryption"),
        ("📱", "New UI", "Clean, Modern and Intuitive interface")
    ]
    
    for i, (icon, title, desc) in enumerate(features):
        with [col1, col2, col3, col4][i]:
            create_info_card(title, desc, icon)

def handle_login(email, password, remember_me=False):
    """Handle user login with Firebase"""
    try:
        with st.spinner("Signing you in..."):
            db = FirebaseHandler()
            user_data = db.authenticate_user(email, password)
            
            if user_data:
                st.session_state["authentication_status"] = True
                st.session_state["username"] = user_data.get("username")
                st.session_state["user_data"] = user_data
                st.session_state["remember_me"] = remember_me
                
                # Save session if remember me is checked
                if remember_me:
                    save_session(user_data.get("username"), user_data, True)
                
                create_success_message("Login successful! Welcome back!")
                time.sleep(1)
                # Use rerun instead of switch_page to avoid navigation issues
                st.rerun()
            else:
                st.error("❌ Invalid email or password")
                
    except Exception as e:
        st.error(f"❌ Login failed: {str(e)}")

def handle_google_login(google_user_info):
    """Handle Google OAuth login"""
    try:
        with st.spinner("Signing you in with Google..."):
            db = FirebaseHandler()
            user_data = db.authenticate_google_user(google_user_info)
            
            if user_data:
                st.session_state["authentication_status"] = True
                st.session_state["username"] = user_data.get("username")
                st.session_state["user_data"] = user_data
                st.session_state["remember_me"] = True  # Google login auto-remembers
                
                # Save session
                save_session(user_data.get("username"), user_data, True)
                
                create_success_message(f"Welcome back, {user_data.get('name', 'User')}!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Google authentication failed")
                
    except Exception as e:
        st.error(f"❌ Google login failed: {str(e)}")