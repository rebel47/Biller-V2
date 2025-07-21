import streamlit as st
import time
import uuid
from database import FirebaseHandler
from ui_components import render_header, create_success_message, create_info_card

def init_register_session_state():
    """Initialize session state for register page"""
    if "register_form_key" not in st.session_state:
        st.session_state.register_form_key = str(uuid.uuid4())

def main():
    """Registration page"""
    # Initialize session state
    init_register_session_state()
    
    render_header("Biller", "Create Your Account")
    
    # Center the registration form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 📝 Join Biller Today!")
        
        # Use session state form key to avoid conflicts
        with st.form(st.session_state.register_form_key, clear_on_submit=True):
            username = st.text_input("👤 Username", placeholder="Choose a unique username")
            email = st.text_input("📧 Email", placeholder="Enter your email address")
            name = st.text_input("🏷️ Full Name", placeholder="Enter your full name")
            password = st.text_input("🔒 Password", type="password", placeholder="Create a strong password")
            confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm your password")
            
            col_register, col_login = st.columns([2, 1])
            
            with col_register:
                register_button = st.form_submit_button("Create Account", type="primary", use_container_width=True)
            
            with col_login:
                login_button = st.form_submit_button("Have Account?", use_container_width=True)
            
            if register_button:
                handle_registration(username, email, name, password, confirm_password)
            
            # Handle login button click
            if login_button:
                st.session_state.current_page = "auth"
                st.session_state.register_form_key = str(uuid.uuid4())  # Generate new form key
                st.rerun()

    # Add benefits section
    st.markdown("---")
    st.markdown("### 🌟 Why Choose Biller?")
    
    col1, col2, col3 = st.columns(3)
    
    benefits = [
        ("💰", "Save Money", "Track every expense and identify spending patterns to save more money each month."),
        ("⏰", "Save Time", "AI-powered receipt scanning eliminates manual data entry and saves hours of work."),
        ("📈", "Grow Wealth", "Smart analytics help you make better financial decisions and build wealth over time.")
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
                create_success_message("🎉 Account created successfully! Please sign in to continue.")
                
                # Clear form key and redirect to login
                if "register_form_key" in st.session_state:
                    del st.session_state["register_form_key"]
                
                time.sleep(2)
                st.session_state.current_page = "auth"
                st.rerun()
            else:
                st.error("❌ Registration failed. Username or email may already exist.")
                
    except Exception as e:
        st.error(f"❌ Registration error: {str(e)}")

# Run the registration page
main()