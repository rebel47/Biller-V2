 
import streamlit as st
from datetime import datetime
from PIL import Image
import os

from utils.storage import load_user_profile, save_food_log_entry, load_food_logs
from utils.food_analysis import analyze_food_image, display_food_analysis_results, get_meal_suggestions, display_meal_suggestions

def track_food_page():
    """Food tracking page"""
    st.title("🍽️ Track Food")
    
    # Check if user profile exists
    user_profile = load_user_profile(st.session_state.user_id)
    if not user_profile:
        st.warning("Please set up your profile first!")
        return
    
    # Display daily calorie goal
    calorie_goal = user_profile.get("calorie_goal", 2000)
    
    # Get today's date
    today = datetime.now().date().strftime("%Y-%m-%d")
    
    # Load today's food logs
    today_logs = load_food_logs(st.session_state.user_id, today)
    
    # Calculate daily totals
    total_calories = sum(entry.get("calories", 0) for entry in today_logs)
    total_protein = sum(entry.get("protein", 0) for entry in today_logs)
    total_carbs = sum(entry.get("carbs", 0) for entry in today_logs)
    total_fat = sum(entry.get("fat", 0) for entry in today_logs)
    
    # Calculate remaining calories
    remaining_calories = calorie_goal - total_calories
    
    # Display daily progress
    st.markdown("""
    <div class="custom-card">
        <h3>Today's Progress</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Calculate percentage of goal
        percentage = min(100, (total_calories / calorie_goal) * 100)
        
        # Display progress bar
        st.progress(percentage / 100)
        
        # Display calories and remaining
        st.markdown(
            f"""
            <div style="display:flex; justify-content:space-between; margin-top:0.5rem;">
                <div>
                    <span style="font-size:1.5rem; font-weight:bold;">{total_calories}</span>
                    <span style="color:#666;"> / {calorie_goal} cal</span>
                </div>
                <div style="text-align:right;">
                    <span style="font-weight:bold;">{remaining_calories}</span>
                    <span style="color:#666;"> cal remaining</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        # Display macronutrient progress
        st.markdown(
            f"""
            <div style="text-align:center;">
                <div style="font-size:0.9rem;">
                    <span style="font-weight:bold;">{total_protein}g</span> protein
                </div>
                <div style="font-size:0.9rem;">
                    <span style="font-weight:bold;">{total_carbs}g</span> carbs
                </div>
                <div style="font-size:0.9rem;">
                    <span style="font-weight:bold;">{total_fat}g</span> fat
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Create tabs for different tracking methods
    tabs = st.tabs(["Photo Analysis", "Quick Add", "Meal History"])
    
    # Tab 1: Photo Analysis
    with tabs[0]:
        st.markdown("""
        <div class="custom-card">
            <h3>Analyze Food Photo</h3>
            <p>Upload a photo of your meal for automatic nutrition analysis.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Image upload
        uploaded_file = st.file_uploader("Choose an image of your meal", type=["jpg", "jpeg", "png"])
        
        col1, col2 = st.columns(2)
        
        # Add meal name and time
        with col1:
            meal_name = st.text_input("Meal Name", placeholder="Breakfast, Lunch, Dinner, Snack...")
            meal_time = st.time_input("Meal Time", datetime.now().time())
        
        with col2:
            meal_date = st.date_input("Date", datetime.now().date())
            manual_calories = st.number_input("Manual Calorie Override (optional)", min_value=0, value=0)
        
        # Process image when submitted
        if st.button("Analyze Food", use_container_width=True):
            if uploaded_file:
                # Display uploaded image
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Meal", use_container_width=True)
                
                with st.spinner("Analyzing your food... This may take a moment."):
                    # Analyze image
                    analysis_result = analyze_food_image(image)
                    
                    # Display results
                    processed_data = display_food_analysis_results(
                        analysis_result, 
                        user_profile, 
                        manual_calories
                    )
                    
                    if processed_data:
                        # Prepare log entry
                        log_entry = {
                            "date": meal_date.strftime("%Y-%m-%d"),
                            "time": meal_time.strftime("%H:%M"),
                            "meal_name": meal_name if meal_name else "Unnamed Meal",
                            "calories": processed_data.get("calories", 0),
                            "protein": processed_data.get("protein", 0),
                            "carbs": processed_data.get("carbs", 0),
                            "fat": processed_data.get("fat", 0),
                            "food_items": processed_data.get("food_items", []),
                            "health_suggestions": processed_data.get("health_suggestions", [])
                        }
                        
                        # Save button
                        if st.button("Save to Food Log", use_container_width=True):
                            if save_food_log_entry(st.session_state.user_id, log_entry):
                                st.success("Meal logged successfully!")
                                st.rerun()
            else:
                st.warning("Please upload an image or enter manual calories.")
    
    # Tab 2: Quick Add
    with tabs[1]:
        st.markdown("""
        <div class="custom-card">
            <h3>Quick Add</h3>
            <p>Manually add a meal or snack with known nutritional information.</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("quick_add_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                quick_meal_name = st.text_input("Meal Name", placeholder="Breakfast, Lunch, Dinner, Snack...", key="quick_meal_name")
                quick_meal_time = st.time_input("Meal Time", datetime.now().time(), key="quick_meal_time")
                quick_meal_date = st.date_input("Date", datetime.now().date(), key="quick_meal_date")
            
            with col2:
                quick_calories = st.number_input("Calories", min_value=0, key="quick_calories")
                quick_protein = st.number_input("Protein (g)", min_value=0, value=0, key="quick_protein")
                quick_carbs = st.number_input("Carbs (g)", min_value=0, value=0, key="quick_carbs")
                quick_fat = st.number_input("Fat (g)", min_value=0, value=0, key="quick_fat")
            
            # Food items (optional)
            st.text_area("Food Items (one per line)", key="quick_food_items", placeholder="E.g. Chicken breast\nBrown rice\nBroccoli")
            
            quick_add_submit = st.form_submit_button("Add to Food Log", use_container_width=True)
        
        if quick_add_submit:
            # Process food items
            food_items = []
            if st.session_state.quick_food_items:
                food_items = [item.strip() for item in st.session_state.quick_food_items.split("\n") if item.strip()]
            
            # Prepare log entry
            log_entry = {
                "date": quick_meal_date.strftime("%Y-%m-%d"),
                "time": quick_meal_time.strftime("%H:%M"),
                "meal_name": quick_meal_name if quick_meal_name else "Unnamed Meal",
                "calories": quick_calories,
                "protein": quick_protein,
                "carbs": quick_carbs,
                "fat": quick_fat,
                "food_items": food_items,
                "health_suggestions": []
            }
            
            if save_food_log_entry(st.session_state.user_id, log_entry):
                st.success("Meal logged successfully!")
                st.rerun()
    
    # Tab 3: Meal History
    with tabs[2]:
        st.markdown("""
        <div class="custom-card">
            <h3>Today's Meals</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if today_logs:
            # Sort logs by time
            sorted_logs = sorted(today_logs, key=lambda x: x.get("time", "00:00"))
            
            for log in sorted_logs:
                # Create an expander for each meal
                with st.expander(f"{log.get('meal_name')} - {log.get('time')} ({log.get('calories')} cal)"):
                    col1, col2 = st.columns([3, 2])
                    
                    with col1:
                        st.markdown("<h4>Food Items</h4>", unsafe_allow_html=True)
                        
                        if log.get("food_items"):
                            for item in log.get("food_items"):
                                st.markdown(f"• {item}")
                        else:
                            st.markdown("No food items recorded")
                        
                        if log.get("health_suggestions"):
                            st.markdown("<h4>Health Suggestions</h4>", unsafe_allow_html=True)
                            for suggestion in log.get("health_suggestions"):
                                st.markdown(f"• {suggestion}")
                    
                    with col2:
                        st.markdown("<h4>Nutrition</h4>", unsafe_allow_html=True)
                        st.markdown(
                            f"""
                            <div style="text-align:center;">
                                <div style="font-size:1.8rem; font-weight:bold; margin-bottom:0.5rem;">
                                    {log.get('calories')} cal
                                </div>
                                <div style="display:flex; justify-content:space-between; margin:1rem 0;">
                                    <div style="text-align:center; width:33%;">
                                        <div style="font-weight:bold;">{log.get('protein', 0)}g</div>
                                        <div style="font-size:0.8rem;">Protein</div>
                                    </div>
                                    <div style="text-align:center; width:33%;">
                                        <div style="font-weight:bold;">{log.get('carbs', 0)}g</div>
                                        <div style="font-size:0.8rem;">Carbs</div>
                                    </div>
                                    <div style="text-align:center; width:33%;">
                                        <div style="font-weight:bold;">{log.get('fat', 0)}g</div>
                                        <div style="font-size:0.8rem;">Fat</div>
                                    </div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    
                    # Delete button
                    if st.button("Delete Entry", key=f"delete_{log.get('entry_id', '')}"):
                        # Import delete function here to avoid circular import
                        from utils.storage import delete_food_log_entry
                        
                        if delete_food_log_entry(st.session_state.user_id, log.get("entry_id", "")):
                            st.success("Entry deleted successfully!")
                            st.rerun()
        else:
            st.info("No meals logged for today. Start tracking your food intake!")
    
    # Meal suggestions based on remaining calories
    if remaining_calories > 100:
        st.markdown("""
        <div class="custom-card">
            <h3>What to Eat Next?</h3>
            <p>Based on your goals and what you've eaten today, here are some suggestions:</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Daily intake summary for the suggestions
        daily_intake = {
            "calories": total_calories,
            "protein": total_protein,
            "carbs": total_carbs,
            "fat": total_fat
        }
        
        # Get and display meal suggestions
        suggestions = get_meal_suggestions(user_profile, daily_intake, remaining_calories)
        display_meal_suggestions(suggestions)