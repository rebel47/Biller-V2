import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
from database import FirebaseHandler
from ui_components import render_header, create_success_message

def main():
    """Main function for bills page"""
    bills_page()

def bills_page():
    """Bills management page"""
    render_header("📋 My Bills", "Manage and review your expenses")
    
    try:
        username = st.session_state["username"]
        db = FirebaseHandler()
        bills_df = db.get_bills(username)
        
        if not bills_df.empty:
            # Add filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                categories = ['All'] + list(bills_df['category'].unique())
                selected_category = st.selectbox(
                    "🏷️ Filter by Category", 
                    categories, 
                    key="bills_category_filter"
                )
            
            with col2:
                date_range = st.selectbox(
                    "📅 Date Range",
                    ["All Time", "This Month", "Last 3 Months", "This Year"],
                    key="bills_date_filter"
                )
            
            with col3:
                search_term = st.text_input(
                    "🔍 Search", 
                    placeholder="Search descriptions...", 
                    key="bills_search_filter"
                )
            
            # Apply filters
            filtered_df = apply_filters(bills_df, selected_category, date_range, search_term)
            
            # Display bills
            if not filtered_df.empty:
                # Add delete column
                filtered_df['Delete'] = False
                
                # Format amount for display
                display_df = filtered_df.copy()
                display_df['amount'] = display_df['amount'].apply(lambda x: f"€{x:.2f}")
                
                # Show data editor
                edited_df = st.data_editor(
                    display_df,
                    column_config={
                        "Delete": st.column_config.CheckboxColumn("🗑️", default=False),
                        "date": "📅 Date",
                        "category": "🏷️ Category",
                        "amount": "💰 Amount",
                        "description": "📝 Description",
                        "id": None  # Hide ID
                    },
                    hide_index=True,
                    use_container_width=True,
                    key="bills_data_editor"
                )
                
                # Delete selected items
                if st.button(
                    "🗑️ Delete Selected", 
                    type="secondary", 
                    key="delete_selected_bills_btn"
                ):
                    delete_selected_bills(edited_df)
            else:
                st.info("No bills match your filters.")
        else:
            st.info("📋 No bills yet. Upload your first receipt to get started!")
            
    except Exception as e:
        st.error(f"Error loading bills: {str(e)}")

def apply_filters(df, category, date_range, search_term):
    """Apply filters to bills dataframe"""
    filtered_df = df.copy()
    
    # Category filter
    if category != 'All':
        filtered_df = filtered_df[filtered_df['category'] == category]
    
    # Date range filter
    if date_range != 'All Time':
        current_date = datetime.now()
        filtered_df['date'] = pd.to_datetime(filtered_df['date'])
        
        if date_range == 'This Month':
            start_date = current_date.replace(day=1)
            filtered_df = filtered_df[filtered_df['date'] >= start_date]
        elif date_range == 'Last 3 Months':
            start_date = current_date - timedelta(days=90)
            filtered_df = filtered_df[filtered_df['date'] >= start_date]
        elif date_range == 'This Year':
            start_date = current_date.replace(month=1, day=1)
            filtered_df = filtered_df[filtered_df['date'] >= start_date]
    
    # Search filter
    if search_term:
        filtered_df = filtered_df[
            filtered_df['description'].str.contains(search_term, case=False, na=False)
        ]
    
    return filtered_df

def delete_selected_bills(edited_df):
    """Delete selected bills"""
    try:
        items_to_delete = edited_df[edited_df['Delete']]['id'].tolist()
        
        if items_to_delete:
            db = FirebaseHandler()
            deleted_count = 0
            for bill_id in items_to_delete:
                if db.delete_bill(bill_id):
                    deleted_count += 1
            
            if deleted_count > 0:
                create_success_message(f"Deleted {deleted_count} items")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Failed to delete items")
        else:
            st.warning("No items selected for deletion")
            
    except Exception as e:
        st.error(f"Error deleting bills: {str(e)}")