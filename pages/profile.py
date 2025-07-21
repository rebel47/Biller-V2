import streamlit as st
import time
from database import FirebaseHandler
from ui_components import render_header, create_success_message
from utils import check_authentication

# Check authentication
check_authentication()

def profile_page():
    """User profile management"""
    render_header("👤 Profile", "Manage your account settings")
    
    user_data = st.session_state.get("user_data", {})
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Profile card with proper HTML rendering
        profile_stats_html = render_profile_stats()
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(240, 147, 251, 0.1) 100%);
            padding: 2rem;
            border-radius: 16px;
            text-align: center;
            border: 1px solid rgba(102, 126, 234, 0.2);
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        ">
            <div style="
                width: 80px;
                height: 80px;
                border-radius: 50%;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 1.5rem auto;
                font-size: 2rem;
                color: white;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            ">👤</div>
            <h2 style="margin: 0; color: #1a202c; font-weight: 700;">{user_data.get('name', 'User')}</h2>
            <p style="color: #718096; margin: 0.5rem 0; font-weight: 500;">@{st.session_state.get('username', '')}</p>
            <p style="color: #718096; margin: 0; font-size: 0.9rem;">{user_data.get('email', '')}</p>
            
            <div style="margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid rgba(102, 126, 234, 0.2);">
                <h4 style="margin: 0 0 1rem 0; color: #667eea;">Account Stats</h4>
                {profile_stats_html}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Profile editing form
        st.markdown("### ✏️ Edit Profile")
        
        # FIX: Use unique form key to avoid conflicts
        with st.form("profile_edit_form", clear_on_submit=False):
            st.markdown("#### 📝 Personal Information")
            
            col_name, col_email = st.columns(2)
            
            with col_name:
                new_name = st.text_input(
                    "👤 Full Name", 
                    value=user_data.get('name', ''),
                    placeholder="Enter your full name"
                )
            
            with col_email:
                new_email = st.text_input(
                    "📧 Email", 
                    value=user_data.get('email', ''),
                    placeholder="Enter your email"
                )
            
            st.markdown("#### 🔒 Security")
            new_password = st.text_input(
                "🔑 New Password (leave blank to keep current)", 
                type="password",
                placeholder="Enter new password"
            )
            
            if new_password:
                confirm_password = st.text_input(
                    "🔑 Confirm New Password", 
                    type="password",
                    placeholder="Confirm new password"
                )
            else:
                confirm_password = ""
            
            col_update, col_cancel = st.columns([2, 1])
            
            with col_update:
                update_button = st.form_submit_button("💾 Update Profile", type="primary", use_container_width=True)
            
            with col_cancel:
                if st.form_submit_button("🔄 Reset", use_container_width=True):
                    st.rerun()
            
            if update_button:
                update_profile(new_name, new_email, new_password, confirm_password)

def render_profile_stats():
    """Render profile statistics as HTML string"""
    try:
        username = st.session_state["username"]
        db = FirebaseHandler()
        bills_df = db.get_bills(username)
        
        if not bills_df.empty:
            total_bills = len(bills_df)
            total_spent = bills_df['amount'].sum()
            
            return f"""
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.75rem;">
                <span style="color: #718096;">Total Bills:</span>
                <span style="color: #1a202c; font-weight: 600;">{total_bills}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.75rem;">
                <span style="color: #718096;">Total Spent:</span>
                <span style="color: #1a202c; font-weight: 600;">€{total_spent:.2f}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="color: #718096;">Avg per Bill:</span>
                <span style="color: #1a202c; font-weight: 600;">€{(total_spent/total_bills):.2f}</span>
            </div>
            """
        else:
            return """
            <div style="text-align: center; color: #718096;">
                <p style="margin: 0; font-size: 0.9rem;">No spending data yet</p>
                <p style="margin: 0.25rem 0 0 0; font-size: 0.8rem;">Start adding bills!</p>
            </div>
            """
    except Exception as e:
        return '<p style="color: #718096; margin: 0;">Stats loading...</p>'

def update_profile(name, email, password, confirm_password):
    """Update user profile"""
    # Validation
    if not name or not email:
        st.error("❌ Name and email are required!")
        return
    
    if "@" not in email:
        st.error("❌ Please enter a valid email address!")
        return
    
    if password and password != confirm_password:
        st.error("❌ Passwords do not match!")
        return
    
    if password and len(password) < 6:
        st.error("❌ Password must be at least 6 characters!")
        return
    
    try:
        username = st.session_state["username"]
        db = FirebaseHandler()
        
        with st.spinner("Updating your profile..."):
            if db.update_user(username, name, email, password if password else None):
                # Update session data
                st.session_state["user_data"]["name"] = name
                st.session_state["user_data"]["email"] = email
                
                create_success_message("✅ Profile updated successfully!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Failed to update profile. Please try again.")
                
    except Exception as e:
        st.error(f"❌ Error updating profile: {str(e)}")

# Account actions section
st.markdown("---")
st.markdown("### ⚙️ Account Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 View Analytics", use_container_width=True):
        st.switch_page("pages/analytics.py")

with col2:
    if st.button("📸 Upload Bill", use_container_width=True):
        st.switch_page("pages/upload.py")

with col3:
    if st.button("🏠 Dashboard", use_container_width=True):
        st.switch_page("pages/dashboard.py")

# Run the profile page
profile_page()