import streamlit as st
import pandas as pd
from datetime import datetime
from utils import init_session_state, logout_user
from database import FirebaseHandler

# Configure the page
st.set_page_config(
    page_title="Biller - Smart Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply modern CSS styling
from ui_components import apply_custom_css, render_sidebar_profile_card
apply_custom_css()

# Initialize session state
init_session_state()

# Check authentication status and handle navigation
if st.session_state.get("authentication_status"):
    # User is authenticated - show the main app
    
    # Add sidebar for authenticated users
    with st.sidebar:
        # User profile section with improved design
        user_data = st.session_state.get("user_data", {})
        username = st.session_state.get("username", "")
        
        # Render the beautiful profile card
        render_sidebar_profile_card(user_data, username)
        
        # Quick stats section
        st.markdown("### 📊 Quick Stats")
        
        try:
            db = FirebaseHandler()
            bills_df = db.get_bills(st.session_state["username"])
            
            if not bills_df.empty:
                current_month = datetime.now().strftime('%Y-%m')
                bills_df['date'] = pd.to_datetime(bills_df['date'])
                bills_df['month'] = bills_df['date'].dt.strftime('%Y-%m')
                
                current_month_total = bills_df[bills_df['month'] == current_month]['amount'].sum()
                total_bills = len(bills_df)
                
                # Use Streamlit's native metric components for better design
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("💰 This Month", f"€{current_month_total:.2f}")
                with col2:
                    st.metric("📄 Total Bills", str(total_bills))
            else:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("💰 This Month", "€0.00")
                with col2:
                    st.metric("📄 Total Bills", "0")
        except:
            st.write("📊 Stats loading...")
        
        # Navigation section with better styling
        st.markdown("---")
        st.markdown("### 🧭 Navigation")
        
        # Navigation buttons with icons
        if st.button("🏠 Dashboard", use_container_width=True):
            st.switch_page("pages/dashboard.py")
        
        if st.button("📸 Upload Bill", use_container_width=True):
            st.switch_page("pages/upload.py")
        
        if st.button("📋 My Bills", use_container_width=True):
            st.switch_page("pages/bills.py")
        
        if st.button("📊 Analytics", use_container_width=True):
            st.switch_page("pages/analytics.py")
        
        if st.button("👤 Profile", use_container_width=True):
            st.switch_page("pages/profile.py")
        
        # Logout button
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            logout_user()
    
    # Define pages for authenticated users
    dashboard_page = st.Page("pages/dashboard.py", title="Dashboard", icon="🏠", default=True)
    upload_page = st.Page("pages/upload.py", title="Upload Bill", icon="📸")
    bills_page = st.Page("pages/bills.py", title="My Bills", icon="📋")
    analytics_page = st.Page("pages/analytics.py", title="Analytics", icon="📊")
    profile_page = st.Page("pages/profile.py", title="Profile", icon="👤")
    
    # Authenticated user navigation
    pg = st.navigation([dashboard_page, upload_page, bills_page, analytics_page, profile_page])
    
else:
    # User is not authenticated - show login/register pages
    auth_page = st.Page("pages/auth.py", title="Login", icon="🔑", default=True)
    register_page = st.Page("pages/register.py", title="Register", icon="📝")
    
    # Unauthenticated user navigation
    pg = st.navigation([auth_page, register_page])

# Run the selected page
try:
    pg.run()
except Exception as e:
    st.error(f"Navigation error: {e}")
    # If there's a navigation error and user is not authenticated, force to auth page
    if not st.session_state.get("authentication_status"):
        st.switch_page("pages/auth.py")