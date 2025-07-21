import streamlit as st
import time
import uuid
from database import FirebaseHandler
from ui_components import render_header, create_success_message, create_info_card
from utils import save_session

def init_auth_session_state():
    """Initialize session state for auth page"""
    if "auth_form_key" not in st.session_state:
        st.session_state.auth_form_key = str(uuid.uuid4())

def main():
    """Login page"""
    # Initialize session state
    init_auth_session_state()
    
    render_header("Biller", "Snap, Track, Save!")
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔑 Welcome Back!")
        
        # Use session state form key to avoid conflicts
        with st.form(st.session_state.auth_form_key, clear_on_submit=False):
            email = st.text_input("📧 Email", placeholder="Enter your email")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            remember_me = st.checkbox("🔐 Remember me for 7 days")
            
            col_login, col_register = st.columns([2, 1])
            
            with col_login:
                login_button = st.form_submit_button("Sign In", use_container_width=True)
            
            with col_register:
                register_button = st.form_submit_button("Need Account?", use_container_width=True)
            
            if login_button and email and password:
                handle_login(email, password, remember_me)
            
            # Handle registration button click
            if register_button:
                st.session_state.current_page = "register"
                st.session_state.auth_form_key = str(uuid.uuid4())  # Generate new form key
                st.rerun()

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
                # Set default page to dashboard
                st.session_state["current_page"] = "dashboard"
                
                # Clear auth form key since we're logging in
                if "auth_form_key" in st.session_state:
                    del st.session_state["auth_form_key"]
                
                # Save session if remember me is checked
                if remember_me:
                    save_session(user_data.get("username"), user_data, True)
                
                create_success_message("Login successful! Welcome back!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Invalid email or password")
                
    except Exception as e:
        st.error(f"❌ Login failed: {str(e)}")

# Check if already logged in
if st.session_state.get("authentication_status"):
    # User is logged in, redirect to dashboard using rerun
    st.rerun()
else:
    main()