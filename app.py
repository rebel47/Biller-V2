import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv

# IMPORTANT: This CSS must be applied before any other Streamlit commands
hide_streamlit_nav = """
<style>
/* Hide the default Streamlit navigation - comprehensive targeting */
[data-testid="stSidebarNav"],
.css-1d391kg,
.css-1k0ckh2,
section[data-testid="stSidebar"] > div:first-child > div:first-child,
section[data-testid="stSidebar"] ul,
section[data-testid="stSidebar"] a,
.st-emotion-cache-6qob1r,
.st-emotion-cache-ue6h4q,
.st-emotion-cache-1cypcdb,
.css-17lntkn,
.css-1oe6wy4 {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    width: 0 !important;
    position: absolute !important;
    top: -9999px !important;
    left: -9999px !important;
    opacity: 0 !important;
    pointer-events: none !important;
}

/* Force container to be empty */
section[data-testid="stSidebar"] > div:first-child > div:nth-child(1)::before {
    content: "";
    display: block;
    clear: both;
}
</style>
"""

# Apply the hiding CSS immediately
st.markdown(hide_streamlit_nav, unsafe_allow_html=True)

# Import modules
from auth.auth_handler import check_auth_status, login_page, signup_page, logout_user
from pages.profile import profile_page
from pages.track_food import track_food_page
from pages.daily_summary import daily_summary_page
from pages.progress import progress_page
from utils.storage import create_data_folders

# Load environment variables
load_dotenv()

# Ensure data directories exist
create_data_folders()

# Set page configuration
st.set_page_config(
    page_title="NutriSnap AI",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS for modern UI
def apply_custom_css():
    st.markdown("""
    <style>
        /* Modern color scheme */
        :root {
            --primary-color: #4CAF50;
            --secondary-color: #2E7D32;
            --background-color: #f8f9fa;
            --text-color: #212121;
            --light-gray: #f1f3f5;
            --card-border-radius: 10px;
            --card-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        /* Main container styling */
        .main {
            background-color: var(--background-color);
            color: var(--text-color);
            padding: 1rem;
        }
        
        /* Header styling */
        h1, h2, h3 {
            font-family: 'Helvetica Neue', sans-serif;
            font-weight: 600;
            color: var(--text-color);
        }
        
        /* Card styling for containers */
        .stCard {
            border-radius: var(--card-border-radius);
            box-shadow: var(--card-shadow);
            padding: 1.5rem;
            margin-bottom: 1rem;
            background-color: white;
        }
        
        /* Button styling */
        .stButton>button {
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.3s;
            border: none;
            background-color: #f8f9fa;
            color: #333;
        }
        
        .stButton>button:hover {
            background-color: #e9ecef;
            color: #000;
        }
        
        /* Active button styling */
        .active-nav-button button {
            background-color: var(--primary-color) !important;
            color: white !important;
        }
        
        /* Input fields */
        .stTextInput>div>div>input, .stNumberInput>div>div>input {
            border-radius: 5px;
            border: 1px solid #e0e0e0;
            padding: 0.5rem;
        }
        
        /* Sidebar styling */
        .sidebar .sidebar-content {
            background-color: white;
        }
        
        /* Progress bars */
        .stProgress>div>div>div {
            background-color: var(--primary-color);
        }
        
        /* Custom card class */
        .custom-card {
            background-color: white;
            border-radius: var(--card-border-radius);
            box-shadow: var(--card-shadow);
            padding: 1.5rem;
            margin-bottom: 1rem;
        }
        
        /* Auth form styling */
        .auth-form {
            max-width: 500px;
            margin: 0 auto;
            padding: 2rem;
            background-color: white;
            border-radius: var(--card-border-radius);
            box-shadow: var(--card-shadow);
        }
        
        /* Logo and branding */
        .logo-container {
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .logo-text {
            font-family: 'Helvetica Neue', sans-serif;
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--primary-color);
            margin-left: 0.5rem;
        }
        
        /* Google button */
        .google-btn {
            background-color: white;
            color: #757575;
            border: 1px solid #ddd;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            cursor: pointer;
            margin: 1rem 0;
            width: 100%;
            transition: background-color 0.3s;
        }
        
        .google-btn:hover {
            background-color: #f5f5f5;
        }
        
        .google-icon {
            margin-right: 0.5rem;
        }
        
        /* Separator for auth options */
        .separator {
            display: flex;
            align-items: center;
            text-align: center;
            margin: 1rem 0;
        }
        
        .separator::before, .separator::after {
            content: '';
            flex: 1;
            border-bottom: 1px solid #eee;
        }
        
        .separator::before {
            margin-right: 0.5rem;
        }
        
        .separator::after {
            margin-left: 0.5rem;
        }
        
        /* User avatar in sidebar */
        .user-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background-color: var(--primary-color);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            margin-right: 0.5rem;
        }
        
        .user-info {
            display: flex;
            align-items: center;
            padding: 1rem;
            border-bottom: 1px solid #eee;
            margin-bottom: 1rem;
        }
        
        /* Hide streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Simple navigation styles */
        .nav-button {
            margin-bottom: 8px;
        }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state for authentication
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'auth_page' not in st.session_state:
    st.session_state.auth_page = "login"
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Profile Setup"

# Apply custom CSS
apply_custom_css()

# Check authentication status
is_authenticated = check_auth_status()

# App Navigation
def main():
    # Sidebar
    with st.sidebar:
        # Clear the top of the sidebar (belt and suspenders approach)
        st.markdown('<div style="height: 5px"></div>', unsafe_allow_html=True)
        
        # Logo and app name
        st.markdown(
            """
            <div class="logo-container">
                <div>🥗</div>
                <div class="logo-text">NutriSnap AI</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # User info if authenticated
        if is_authenticated:
            st.markdown(
                f"""
                <div class="user-info">
                    <div class="user-avatar">{st.session_state.username[0].upper()}</div>
                    <div>{st.session_state.username}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Simple Navigation using buttons
            st.markdown("### Navigate")
            
            # Profile Setup button
            profile_active = st.session_state.current_page == "Profile Setup"
            profile_div = st.empty()
            if profile_active:
                profile_div.markdown('<div class="active-nav-button">', unsafe_allow_html=True)
            else:
                profile_div.markdown('<div>', unsafe_allow_html=True)
            if st.button("👤 Profile Setup", key="nav_profile", use_container_width=True):
                st.session_state.current_page = "Profile Setup"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Track Food button
            track_active = st.session_state.current_page == "Track Food"
            track_div = st.empty()
            if track_active:
                track_div.markdown('<div class="active-nav-button">', unsafe_allow_html=True)
            else:
                track_div.markdown('<div>', unsafe_allow_html=True)
            if st.button("🍽️ Track Food", key="nav_track", use_container_width=True):
                st.session_state.current_page = "Track Food"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Daily Summary button
            summary_active = st.session_state.current_page == "Daily Summary"
            summary_div = st.empty()
            if summary_active:
                summary_div.markdown('<div class="active-nav-button">', unsafe_allow_html=True)
            else:
                summary_div.markdown('<div>', unsafe_allow_html=True)
            if st.button("📊 Daily Summary", key="nav_summary", use_container_width=True):
                st.session_state.current_page = "Daily Summary"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Progress button
            progress_active = st.session_state.current_page == "Progress"
            progress_div = st.empty()
            if progress_active:
                progress_div.markdown('<div class="active-nav-button">', unsafe_allow_html=True)
            else:
                progress_div.markdown('<div>', unsafe_allow_html=True)
            if st.button("📈 Progress", key="nav_progress", use_container_width=True):
                st.session_state.current_page = "Progress"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Add some space before logout
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Logout button
            if st.button("Logout", use_container_width=True):
                logout_user()
                st.rerun()
        else:
            st.info("Please log in to access the app")
    
    # Main content
    if not is_authenticated:
        # Show login or signup page
        if st.session_state.auth_page == "login":
            login_page()
        else:
            signup_page()
    else:
        # Show app pages based on navigation selection
        current_page = st.session_state.current_page
        
        if current_page == "Profile Setup":
            profile_page()
        elif current_page == "Track Food":
            track_food_page()
        elif current_page == "Daily Summary":
            daily_summary_page()
        elif current_page == "Progress":
            progress_page()

# Run the app
if __name__ == "__main__":
    main()