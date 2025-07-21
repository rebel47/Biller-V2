import re
import streamlit as st
import pandas as pd
from datetime import datetime
import time
from database import FirebaseHandler
from image_utils import ImageProcessor
from bill_processor import BillProcessor
from ui_components import render_header, create_success_message
from config import SUPPORTED_IMAGE_TYPES, EXPENSE_CATEGORIES

# --- Session state init -------------------------------------------------------
if "receipt_items" not in st.session_state:
    st.session_state.receipt_items = None          # list[dict] or None
if "receipt_date" not in st.session_state:
    st.session_state.receipt_date = datetime.now().date()

# Check authentication
if not st.session_state.get("authentication_status"):
    # Update this to whatever navigation helper you actually use
    st.switch_page("pages/auth.py")

def parse_ai_items(raw_items):
    """Convert AI free-form lines into structured dicts."""
    parsed = []
    if not raw_items:
        return parsed

    for it in raw_items:
        # If already dict-like
        if isinstance(it, dict):
            name = it.get("item") or it.get("description") or it.get("name") or ""
            amt_raw = it.get("amount") or it.get("price") or 0
            cat = it.get("category") or ""
        else:
            # assume string like '- Tomatenketchup: €1.29 (Category: grocery)'
            s = str(it).strip()
            m = re.search(r'^\s*[-*]?\s*(.+?):\s*€?\s*([\d.,]+).*?(?:Category:\s*([^)]+))?', s, re.I)
            if m:
                name = m.group(1).strip()
                amt_raw = m.group(2)
                cat = (m.group(3) or "").strip()
            else:
                name, amt_raw, cat = s, 0, ""

        # clean amount
        amt = 0.0
        try:
            amt = float(str(amt_raw).replace("€", "").replace(",", "."))
        except Exception:
            pass

        # normalize category
        cat_norm = match_category(cat)

        parsed.append({"item": name, "amount": amt, "category": cat_norm})
    return parsed

def match_category(cat):
    """Return best‑match category from EXPENSE_CATEGORIES; fallback to first."""
    if not cat:
        return EXPENSE_CATEGORIES[0]
    cat_lower = cat.lower()
    # simple contains match
    for c in EXPENSE_CATEGORIES:
        if cat_lower in c.lower() or c.lower() in cat_lower:
            return c
    return EXPENSE_CATEGORIES[0]  # fallback

def main():
    render_header("📸 Upload Bill", "Scan receipts or add expenses manually")
    tab1, tab2 = st.tabs(["📷 Scan Receipt", "✍️ Manual Entry"])
    with tab1:
        show_receipt_upload()
    with tab2:
        show_manual_entry()

def show_receipt_upload():
    st.markdown("### 📸 Upload Receipt Image")
    st.markdown("Upload a photo of your receipt and let AI extract the information automatically.")

    uploaded_file = st.file_uploader(
        "Choose a receipt image (PNG, JPG, JPEG, HEIC)",
        type=SUPPORTED_IMAGE_TYPES,
        help="Upload a clear photo of your receipt for best AI processing results"
    )

    if uploaded_file:
        if st.button("🔍 Process with AI", use_container_width=True, type="primary", key="process_ai"):
            run_ai_processing(uploaded_file)

    if st.session_state.receipt_items is not None and len(st.session_state.receipt_items) > 0:
        show_extracted_items_editor(uploaded_file)  # Image shown only here


def show_extracted_items_editor(uploaded_file=None):
    st.markdown("### 📝 Extracted Items")
    st.markdown("Review and edit before saving:")

    col1, col2 = st.columns([1, 2])
    with col1:
        if uploaded_file:
            st.image(uploaded_file, caption="Receipt Preview", width=300)  # Fixed width

    with col2:
        items_df = pd.DataFrame(st.session_state.receipt_items)
        edited_df = st.data_editor(
            items_df,
            key="receipt_editor",
            column_config={
                "item": st.column_config.TextColumn("Item Description"),
                "amount": st.column_config.NumberColumn("Amount (€)", min_value=0, format="€%.2f", step=0.01),
                "category": st.column_config.SelectboxColumn("Category", options=EXPENSE_CATEGORIES)
            },
            hide_index=True,
            use_container_width=True
        )

        col_a, col_b = st.columns([1, 1])
        with col_a:
            selected_date = st.date_input("📅 Date", value=st.session_state.receipt_date, key="receipt_date_input")
        with col_b:
            total_amount = edited_df["amount"].sum(numeric_only=True)
            st.metric("💰 Total Amount", f"€{total_amount:.2f}")

        if st.button("💾 Save All Items", type="primary", use_container_width=True, key="save_receipt_items"):
            save_success = save_items_simple(edited_df, selected_date)
            if save_success:
                st.success("🎉 All items saved successfully!")
                st.balloons()
                st.session_state.receipt_items = None
                time.sleep(1)
                st.rerun()


def run_ai_processing(uploaded_file):
    """Run the AI and stash results in session_state."""
    try:
        with st.spinner("🤖 AI is analyzing your receipt..."):
            image_processor = ImageProcessor()
            bill_processor = BillProcessor()

            image_data, mime_type = image_processor.setup_input_image(uploaded_file)
            result = bill_processor.process_with_gemini(image_data, mime_type)

        # Debug display
        #st.write("**Raw AI result:**")
        #st.json(result)

        raw_items = result.get("items", [])
        st.session_state.receipt_items = parse_ai_items(raw_items)

        # Parse date
        rec_date = datetime.now().date()
        if result.get("date"):
            try:
                rec_date = datetime.strptime(result["date"], "%Y-%m-%d").date()
            except Exception:
                pass
        st.session_state.receipt_date = rec_date

        st.success("✅ Receipt processed! Scroll down to review and save.")
    except Exception as e:
        st.error(f"❌ Error processing receipt: {e}")
        st.session_state.receipt_items = None

def show_extracted_items_editor(uploaded_file=None):
    st.markdown("### 📝 Extracted Items")
    st.markdown("Review and edit before saving:")

    col1, col2 = st.columns([1.2, 2])  # Image left, editor right
    with col1:
        if uploaded_file:
            st.image(uploaded_file, caption="Receipt Preview", width=300)  # Fixed width

    with col2:
        items_df = pd.DataFrame(st.session_state.receipt_items)
        edited_df = st.data_editor(
            items_df,
            key="receipt_editor",
            column_config={
                "item": st.column_config.TextColumn("Item Description"),
                "amount": st.column_config.NumberColumn(
                    "Amount (€)", min_value=0, format="€%.2f", step=0.01
                ),
                "category": st.column_config.SelectboxColumn("Category", options=EXPENSE_CATEGORIES)
            },
            hide_index=True,
            use_container_width=True
        )

        col_a, col_b = st.columns([1, 1])
        with col_a:
            selected_date = st.date_input("📅 Date", value=st.session_state.receipt_date, key="receipt_date_input")
        with col_b:
            total_amount = edited_df["amount"].sum(numeric_only=True)
            st.metric("💰 Total Amount", f"€{total_amount:.2f}")

        if st.button("💾 Save All Items", type="primary", use_container_width=True, key="save_receipt_items"):
            save_success = save_items_simple(edited_df, selected_date)
            if save_success:
                st.success("🎉 All items saved successfully!")
                st.balloons()
                st.session_state.receipt_items = None
                time.sleep(1)
                st.rerun()


def save_items_simple(items_df, date):
    """Save rows to Firebase."""
    try:
        username = st.session_state.get("username")
        if not username:
            st.error("❌ User not logged in.")
            return False

        db = FirebaseHandler()
        saved_count = 0

        for _, row in items_df.iterrows():
            item = str(row.get("item", "")).strip()
            # safe amount
            try:
                amt = float(row.get("amount", 0) or 0)
            except Exception:
                amt = 0.0
            cat = row.get("category") or EXPENSE_CATEGORIES[0]

            ok = db.save_bill(
                username=username,
                date=date,
                category=cat,
                amount=amt,
                description=item
            )
            if ok:
                saved_count += 1

        if saved_count == len(items_df):
            return True
        else:
            st.warning(f"Only saved {saved_count} of {len(items_df)} items.")
            return False

    except Exception as e:
        st.error(f"❌ Error saving items: {e}")
        return False

# --- Manual entry (unchanged except small safety tweaks) ----------------------
def show_manual_entry():
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
                        username=st.session_state.get("username"),
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
                    st.error(f"❌ Error saving entry: {e}")
            else:
                if amount <= 0:
                    st.error("❌ Please enter an amount greater than 0")
                if not description.strip():
                    st.error("❌ Please enter a description")

# Run page
main()