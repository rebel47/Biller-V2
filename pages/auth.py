import streamlit as st
import time
from database import FirebaseHandler
from ui_components import render_header, create_success_message, create_info_card
from utils import save_session

def main():
    """Login page"""
    render_header("Biller", "Smart AI-Powered Expense Tracking")
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔑 Welcome Back!")
        
        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("📧 Email", placeholder="Enter your email")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            remember_me = st.checkbox("🔐 Remember me for 7 days")
            
            col_login, col_register = st.columns([2, 1])
            
            with col_login:
                login_button = st.form_submit_button("Sign In", use_container_width=True)
            
            with col_register:
                if st.form_submit_button("Need Account?", use_container_width=True):
                    st.switch_page("pages/register.py")
            
            if login_button and email and password:
                handle_login(email, password, remember_me)

    # Add feature highlights
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    features = [
        ("🤖", "AI-Powered", "Automatic receipt scanning with Google Gemini"),
        ("📊", "Smart Analytics", "Real-time insights and spending trends"),
        ("🔒", "Secure", "Firebase authentication and encryption"),
        ("📱", "Modern UI", "Clean, intuitive interface")
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
                st.switch_page("pages/dashboard.py")
            else:
                st.error("❌ Invalid email or password")
                
    except Exception as e:
        st.error(f"❌ Login failed: {str(e)}")

# Check if already logged in
if st.session_state.get("authentication_status"):
    st.switch_page("pages/dashboard.py")
else:
    main()