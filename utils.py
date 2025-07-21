import streamlit as st
import json
from datetime import datetime, timedelta
from base64 import b64encode, b64decode

def save_session(username, user_data, remember_me=False):
    """Save session data for persistence"""
    if remember_me:
        # Create a simple session token
        session_data = {
            "username": username,
            "user_data": user_data,
            "timestamp": datetime.now().isoformat(),
            "expires": (datetime.now() + timedelta(days=7)).isoformat()
        }
        
        # Encode and save to session state (in production, use proper secure storage)
        session_token = b64encode(json.dumps(session_data).encode()).decode()
        st.session_state["saved_session"] = session_token

def load_saved_session():
    """Load saved session if valid"""
    if "saved_session" in st.session_state and st.session_state["saved_session"]:
        try:
            session_data = json.loads(b64decode(st.session_state["saved_session"]).decode())
            expires = datetime.fromisoformat(session_data["expires"])
            
            if datetime.now() < expires:
                st.session_state["authentication_status"] = True
                st.session_state["username"] = session_data["username"]
                st.session_state["user_data"] = session_data["user_data"]
                # FIX: Set default page to dashboard when loading saved session
                if "current_page" not in st.session_state:
                    st.session_state["current_page"] = "dashboard"
            else:
                # Session expired
                del st.session_state["saved_session"]
        except:
            # Invalid session data
            if "saved_session" in st.session_state:
                del st.session_state["saved_session"]

def clear_saved_session():
    """Clear saved session data"""
    if "saved_session" in st.session_state:
        del st.session_state["saved_session"]

def logout_user():
    """Handle user logout - SIMPLE VERSION"""
    # Clear authentication session state
    st.session_state["authentication_status"] = False
    st.session_state["username"] = None
    st.session_state["user_data"] = None
    st.session_state["remember_me"] = False
    st.session_state["current_page"] = "auth"  # FIX: Reset to auth page
    
    # Clear any saved session
    if "saved_session" in st.session_state:
        del st.session_state["saved_session"]
    
    # Clear upload-related state
    if "processed_items" in st.session_state:
        del st.session_state["processed_items"]
    if "uploaded_file_id" in st.session_state:
        del st.session_state["uploaded_file_id"]
    if "save_success" in st.session_state:
        del st.session_state["save_success"]
    if "receipt_items" in st.session_state:
        del st.session_state["receipt_items"]
    if "receipt_date" in st.session_state:
        del st.session_state["receipt_date"]
    
    # Use rerun to refresh the app state
    st.rerun()

def check_authentication():
    """Check if user is authenticated, redirect if not"""
    if not st.session_state.get("authentication_status"):
        st.switch_page("pages/auth.py")
    return True

def init_session_state():
    """Initialize session state variables"""
    defaults = {
        "authentication_status": False,
        "username": None,
        "user_data": None,
        "remember_me": False,
        "force_logout": False,
        "current_page": "auth"  # FIX: Default to auth page initially
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    # Check for saved session
    if not st.session_state.get("force_logout"):
        load_saved_session()
        # FIX: If user is authenticated but no current_page set, default to dashboard
        if (st.session_state.get("authentication_status") and 
            st.session_state.get("current_page") == "auth"):
            st.session_state["current_page"] = "dashboard"
    else:
        # Reset force logout flag
        st.session_state["force_logout"] = False