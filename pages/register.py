import streamlit as st
import time
from database import FirebaseHandler
from ui_components import render_header, create_success_message, create_info_card

def main():
    """Registration page"""
    render_header("Biller", "Create Your Account")
    
    # Center the registration form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 📝 Join Biller Today!")
        
        with st.form("register_form", clear_on_submit=True):
            username = st.text_input(
                "👤 Username", 
                placeholder="Choose a unique username",
                key="register_username_input"
            )
            email = st.text_input(
                "📧 Email", 
                placeholder="Enter your email address",
                key="register_email_input"
            )
            name = st.text_input(
                "🏷️ Full Name", 
                placeholder="Enter your full name",
                key="register_name_input"
            )
            password = st.text_input(
                "🔒 Password", 
                type="password", 
                placeholder="Create a strong password",
                key="register_password_input"
            )
            confirm_password = st.text_input(
                "🔒 Confirm Password", 
                type="password", 
                placeholder="Confirm your password",
                key="register_confirm_password_input"
            )
            
            submit_button = st.form_submit_button("Create Account", type="primary", use_container_width=True)
            
            if submit_button:
                handle_registration(username, email, name, password, confirm_password)

    # Add benefits section
    st.markdown("---")
    st.markdown("**Already have an account?** Use the **Login** tab above.")
    st.markdown("### 🌟 Why Choose Biller?")
    
    col1, col2, col3 = st.columns(3)
    
    benefits = [
        ("💰", "Save Money", "Track every expense and identify spending patterns."),
        ("⏰", "Save Time", "AI-powered receipt scanning eliminates manual data entry."),
        ("📈", "Grow Wealth", "Smart analytics help you make better financial decisions.")
    ]
    
    for i, (icon, title, desc) in enumerate(benefits):
        with [col1, col2, col3][i]:
            create_info_card(title, desc, icon)

def handle_registration(username, email, name, password, confirm_password):
    """Handle user registration with Firebase"""
    # Validation
    if not all([username, email, name, password, confirm_password]):
        st.error("❌ All fields are required!")
        return
    
    if password != confirm_password:
        st.error("❌ Passwords do not match!")
        return
    
    if len(password) < 6:
        st.error("❌ Password must be at least 6 characters!")
        return
    
    if len(username) < 3:
        st.error("❌ Username must be at least 3 characters!")
        return
    
    if "@" not in email:
        st.error("❌ Please enter a valid email address!")
        return
    
    try:
        with st.spinner("Creating your account..."):
            db = FirebaseHandler()
            if db.create_user(username, email, name, password):
                create_success_message("🎉 Account created! Use the Login tab to sign in.")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Registration failed. Username or email may already exist.")
                
    except Exception as e:
        st.error(f"❌ Registration error: {str(e)}")