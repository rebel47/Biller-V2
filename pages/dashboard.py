import streamlit as st
import pandas as pd
from datetime import datetime
from database import FirebaseHandler
from ui_components import render_header, render_metric_card

def main():
    """Main function for dashboard page"""
    dashboard_page()

def dashboard_page():
    """Dashboard page with overview and quick actions"""
    render_header("📊 Dashboard", "Your expense overview at a glance")
    
    # Quick stats
    render_quick_stats()
    
    # Recent activity
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 📋 Recent Bills")
        render_recent_bills()
    
    with col2:
        st.markdown("### ⚡ Quick Info")
        render_quick_info()

@st.fragment
def render_quick_stats():
    """Render quick statistics cards"""
    try:
        username = st.session_state["username"]
        db = FirebaseHandler()
        bills_df = db.get_bills(username)
        
        if not bills_df.empty:
            # Calculate statistics
            current_month = datetime.now().strftime('%Y-%m')
            bills_df['date'] = pd.to_datetime(bills_df['date'])
            bills_df['month'] = bills_df['date'].dt.strftime('%Y-%m')
            
            current_month_bills = bills_df[bills_df['month'] == current_month]
            current_month_total = current_month_bills['amount'].sum()
            total_bills = len(bills_df)
            total_amount = bills_df['amount'].sum()
            avg_bill = bills_df['amount'].mean()
            
            # Render metric cards
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                render_metric_card("This Month", f"€{current_month_total:.2f}", "💰")
            
            with col2:
                render_metric_card("Total Bills", str(total_bills), "📄")
            
            with col3:
                render_metric_card("Total Spent", f"€{total_amount:.2f}", "💸")
            
            with col4:
                render_metric_card("Average Bill", f"€{avg_bill:.2f}", "📊")
        else:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                render_metric_card("This Month", "€0.00", "💰")
            with col2:
                render_metric_card("Total Bills", "0", "📄")
            with col3:
                render_metric_card("Total Spent", "€0.00", "💸")
            with col4:
                render_metric_card("Average Bill", "€0.00", "📊")
                
    except Exception as e:
        st.error(f"Error loading statistics: {str(e)}")

@st.fragment
def render_recent_bills():
    """Show recent bills in a modern format"""
    try:
        username = st.session_state["username"]
        db = FirebaseHandler()
        bills_df = db.get_bills(username)
        
        if not bills_df.empty:
            # Show last 5 bills
            recent_bills = bills_df.head(5)
            
            for _, bill in recent_bills.iterrows():
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                    
                    with col1:
                        st.write(f"**{bill['description'][:30]}{'...' if len(bill['description']) > 30 else ''}**")
                    
                    with col2:
                        st.write(f"€{bill['amount']:.2f}")
                    
                    with col3:
                        st.write(bill['category'].title())
                    
                    with col4:
                        st.write(bill['date'])
                    
                    st.markdown("---")
        else:
            st.info("📋 No bills yet. Upload your first receipt to get started!")
            
    except Exception as e:
        st.error(f"Error loading recent bills: {str(e)}")

def render_quick_info():
    """Show quick information and tips"""
    st.markdown("""
    ### 💡 Quick Tips
    
    🎯 **Upload receipts** regularly to track all expenses
    
    📊 **Check analytics** to identify spending patterns
    
    💰 **Set monthly goals** to manage your budget
    
    🏷️ **Use categories** to organize your expenses
    """)
    
    # Show user info
    user_data = st.session_state.get("user_data", {})
    st.markdown("---")
    st.markdown("### 👤 Account Info")
    st.write(f"**Name:** {user_data.get('name', 'User')}")
    st.write(f"**Email:** {user_data.get('email', 'Not set')}")