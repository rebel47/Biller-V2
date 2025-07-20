import streamlit as st
import pandas as pd
from datetime import datetime
import time
from database import FirebaseHandler
from image_utils import ImageProcessor
from bill_processor import BillProcessor
from ui_components import render_header, create_success_message
from config import SUPPORTED_IMAGE_TYPES, EXPENSE_CATEGORIES

# Check authentication
if not st.session_state.get("authentication_status"):
    st.switch_page("pages/auth.py")

def main():
    """Upload and manual entry page"""
    render_header("📸 Upload Bill", "Scan receipts or add expenses manually")
    
    # Create tabs for different input methods
    tab1, tab2 = st.tabs(["📷 Scan Receipt", "✍️ Manual Entry"])
    
    with tab1:
        show_receipt_upload()
    
    with tab2:
        show_manual_entry()

def show_receipt_upload():
    """Receipt upload with AI processing"""
    st.markdown("### 📸 Upload Receipt Image")
    st.markdown("Upload a photo of your receipt and let AI extract the information automatically.")
    
    uploaded_file = st.file_uploader(
        "Choose a receipt image (PNG, JPG, JPEG, HEIC)",
        type=SUPPORTED_IMAGE_TYPES,
        help="Upload a clear photo of your receipt for best AI processing results"
    )
    
    if uploaded_file:
        try:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.image(uploaded_file, caption="Uploaded Receipt", use_container_width=True)
            
            with col2:
                st.markdown("**Receipt Details:**")
                st.write(f"📄 **Filename:** {uploaded_file.name}")
                st.write(f"💾 **Size:** {round(uploaded_file.size/1024, 1)} KB")
                st.write(f"🎯 **Type:** {uploaded_file.type}")
                
                if st.button("🔍 Process with AI", use_container_width=True, type="primary"):
                    process_receipt(uploaded_file)
                    
        except Exception as e:
            st.error(f"Error displaying image: {str(e)}")

def process_receipt(uploaded_file):
    """Process receipt with AI"""
    try:
        with st.spinner("🤖 AI is analyzing your receipt..."):
            image_processor = ImageProcessor()
            bill_processor = BillProcessor()
            
            image_data, mime_type = image_processor.setup_input_image(uploaded_file)
            result = bill_processor.process_with_gemini(image_data, mime_type)
            
            if result and result['items']:
                st.success("✅ Receipt processed successfully!")
                
                # Show extracted items
                st.markdown("### 📝 Extracted Items")
                st.markdown("Review and edit the extracted information before saving:")
                
                items_df = pd.DataFrame(result['items'])
                
                # Allow editing with unique key
                edited_df = st.data_editor(
                    items_df,
                    column_config={
                        "item": st.column_config.TextColumn("Item Description"),
                        "amount": st.column_config.NumberColumn(
                            "Amount (€)",
                            min_value=0,
                            format="€%.2f",
                            step=0.01
                        ),
                        "category": st.column_config.SelectboxColumn(
                            "Category",
                            options=EXPENSE_CATEGORIES
                        )
                    },
                    hide_index=True,
                    use_container_width=True,
                    key=f"items_editor_{uploaded_file.name}_{int(time.time())}"  # Unique key
                )
                
                # Date input
                col1, col2 = st.columns([1, 1])
                with col1:
                    default_date = (datetime.strptime(result['date'], '%Y-%m-%d').date() 
                                   if result['date'] else datetime.now().date())
                    selected_date = st.date_input("📅 Date", value=default_date)
                
                with col2:
                    total_amount = edited_df['amount'].sum()
                    st.metric("💰 Total Amount", f"€{total_amount:.2f}")
                
                # Save button with unique key
                save_key = f"save_items_{uploaded_file.name}_{int(time.time())}"
                if st.button("💾 Save All Items", type="primary", use_container_width=True, key=save_key):
                    if save_processed_items(edited_df, selected_date):
                        # Clear the uploaded file state by rerunning
                        st.rerun()
            else:
                st.warning("⚠️ Could not extract items from the receipt. Please try manual entry.")
                st.info("💡 **Tips for better results:**\n- Ensure the receipt is clearly visible\n- Good lighting helps\n- Make sure text is readable")
                
    except Exception as e:
        st.error(f"❌ Error processing receipt: {str(e)}")
        st.info("Please try uploading a different image or use manual entry.")

def save_processed_items(items_df, date):
    """Save processed items to database"""
    try:
        username = st.session_state["username"]
        db = FirebaseHandler()
        saved_count = 0
        total_items = len(items_df)
        
        # Progress bar for saving
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, (_, row) in enumerate(items_df.iterrows()):
            status_text.text(f"Saving item {i+1} of {total_items}: {row['item'][:30]}...")
            
            if db.save_bill(
                username=username,
                date=date,
                category=row['category'],
                amount=row['amount'],
                description=row['item']
            ):
                saved_count += 1
            
            # Update progress
            progress_bar.progress((i + 1) / total_items)
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        if saved_count == total_items:
            create_success_message(f"🎉 Successfully saved all {saved_count} items!")
            st.balloons()  # Celebration animation
            time.sleep(2)
            return True
        else:
            st.warning(f"⚠️ Saved {saved_count} out of {total_items} items")
            return False
            
    except Exception as e:
        st.error(f"❌ Error saving items: {str(e)}")
        return False

@st.fragment
def show_manual_entry():
    """Manual entry form"""
    st.markdown("### ✍️ Add Expense Manually")
    st.markdown("Enter your expense details manually if you don't have a receipt or prefer manual entry.")
    
    with st.form("manual_entry", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            date = st.date_input("📅 Date", value=datetime.now().date(), help="When did you make this purchase?")
            category = st.selectbox("🏷️ Category", options=EXPENSE_CATEGORIES, help="Select the most appropriate category")
        
        with col2:
            amount = st.number_input("💰 Amount (€)", min_value=0.0, step=0.01, format="%.2f", help="Enter the total amount spent")
            description = st.text_input("📝 Description", placeholder="What did you buy?", help="Brief description of the purchase")
        
        submitted = st.form_submit_button("💾 Save Entry", type="primary", use_container_width=True)
        
        if submitted:
            if amount > 0 and description.strip():
                try:
                    db = FirebaseHandler()
                    if db.save_bill(
                        username=st.session_state["username"],
                        date=date,
                        category=category,
                        amount=amount,
                        description=description.strip()
                    ):
                        create_success_message("✅ Entry saved successfully!")
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Failed to save entry. Please try again.")
                except Exception as e:
                    st.error(f"❌ Error saving entry: {str(e)}")
            else:
                if amount <= 0:
                    st.error("❌ Please enter an amount greater than 0")
                if not description.strip():
                    st.error("❌ Please enter a description")

# Run the upload page
main()