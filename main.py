import streamlit as st
from utils import init_session_state, logout_user
from ui_components import apply_custom_css

# Configure the page
st.set_page_config(
    page_title="Biller - Smart Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
apply_custom_css()

# Initialize session state
init_session_state()

# Import page modules
from pages import auth, register, dashboard, upload, bills, analytics, profile

# Check authentication status
if not st.session_state.get("authentication_status"):
    # Not authenticated - show auth pages
    auth_pages = [
        st.Page(auth.main, title="Login", icon="🔑", url_path="login"),
        st.Page(register.main, title="Register", icon="📝", url_path="register"),
    ]
    
    pg = st.navigation(auth_pages)
    pg.run()
    
else:
    # Authenticated - show main app pages
    app_pages = [
        st.Page(dashboard.main, title="Dashboard", icon="🏠", url_path="dashboard"),
        st.Page(upload.main, title="Upload Bill", icon="📸", url_path="upload"),
        st.Page(bills.main, title="My Bills", icon="📋", url_path="bills"),
        st.Page(analytics.main, title="Analytics", icon="📊", url_path="analytics"),
        st.Page(profile.main, title="Profile", icon="👤", url_path="profile"),
    ]
    
    # Add logout functionality in sidebar
    with st.sidebar:
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            logout_user()
    
    pg = st.navigation(app_pages)
    pg.run()