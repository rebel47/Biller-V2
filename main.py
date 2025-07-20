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
from ui_components import apply_custom_css
apply_custom_css()

# Initialize session state
init_session_state()

# Check authentication status and handle navigation
if st.session_state.get("authentication_status"):
    # User is authenticated - show the main app
    
    # Add sidebar for authenticated users
    with st.sidebar:
        # User profile section
        user_data = st.session_state.get("user_data", {})
        username = st.session_state.get("username", "")
        
        st.markdown(f"""
        <div style="text-align: center; padding: 1.5rem; background: rgba(255,255,255,0.05); border-radius: 12px; margin-bottom: 1.5rem; border: 1px solid rgba(255,255,255,0.1);">
            <div style="width: 60px; height: 60px; border-radius: 50%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem auto; font-size: 1.5rem; color: white;">👤</div>
            <h3 style="color: #e2e8f0; font-weight: 600; margin: 0; font-size: 1.1rem;">{user_data.get('name', 'User')}</h3>
            <p style="color: #a0aec0; margin: 0.25rem 0 0 0; font-size: 0.9rem;">@{username}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick stats in sidebar
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
                
                st.metric("This Month", f"€{current_month_total:.2f}")
                st.metric("Total Bills", str(total_bills))
            else:
                st.metric("This Month", "€0.00")
                st.metric("Total Bills", "0")
        except:
            st.write("📊 Stats loading...")
        
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