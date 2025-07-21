import streamlit as st
import pandas as pd
from datetime import datetime
from utils import init_session_state, logout_user
from database import FirebaseHandler

# Configure the page
st.set_page_config(
    page_title="Biller -  Snap, Track, Save!",
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
        # Navigation section with styled buttons
        
        # Navigation buttons with icons
        if st.button("🏠 Dashboard", use_container_width=True):
            st.session_state.current_page = "dashboard"
            st.rerun()
        
        if st.button("📸 Upload Bill", use_container_width=True):
            st.session_state.current_page = "upload"
            st.rerun()
        
        if st.button("📋 My Bills", use_container_width=True):
            st.session_state.current_page = "bills"
            st.rerun()
        
        if st.button("📊 Analytics", use_container_width=True):
            st.session_state.current_page = "analytics"
            st.rerun()
        
        if st.button("👤 Profile", use_container_width=True):
            st.session_state.current_page = "profile"
            st.rerun()
        
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
                st.metric("💰 This Month", f"€{current_month_total:.2f}")
                st.metric("📄 Total Bills", str(total_bills))
            else:
                st.metric("💰 This Month", "€0.00")
                st.metric("📄 Total Bills", "0")
        except:
            st.write("📊 Stats loading...")
        
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            logout_user()
    
    # Initialize default page if not set
    if "current_page" not in st.session_state:
        st.session_state.current_page = "dashboard"
    
    # Handle page routing based on current_page
    if st.session_state.current_page == "dashboard":
        import pages.dashboard as dashboard_module
        dashboard_module.main()
    elif st.session_state.current_page == "upload":
        import pages.upload as upload_module  
        upload_module.main()
    elif st.session_state.current_page == "bills":
        import pages.bills as bills_module
        bills_module.main()
    elif st.session_state.current_page == "analytics":
        import pages.analytics as analytics_module
        analytics_module.main()
    elif st.session_state.current_page == "profile":
        import pages.profile as profile_module
        profile_module.profile_page()
    
else:
    # User is not authenticated - show login/register pages
    if "current_page" not in st.session_state:
        st.session_state.current_page = "auth"
    
    if st.session_state.current_page == "register":
        import pages.register as register_module
        register_module.main()
    else:
        import pages.auth as auth_module
        auth_module.main()