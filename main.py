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
        st.Page(auth.login_page, title="Login", icon="🔑"),
        st.Page(register.register_page, title="Register", icon="📝"),
    ]
    
    pg = st.navigation(auth_pages)
    pg.run()
    
else:
    # Authenticated - show main app pages
    app_pages = [
        st.Page(dashboard.dashboard_page, title="Dashboard", icon="🏠"),
        st.Page(upload.upload_page, title="Upload Bill", icon="📸"),
        st.Page(bills.bills_page, title="My Bills", icon="📋"),
        st.Page(analytics.analytics_page, title="Analytics", icon="📊"),
        st.Page(profile.profile_page, title="Profile", icon="👤"),
    ]
    
    # Add logout functionality in sidebar
    with st.sidebar:
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            logout_user()
    
    pg = st.navigation(app_pages)
    pg.run()