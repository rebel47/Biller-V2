 
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta

from utils.storage import load_user_profile, load_food_logs
from utils.food_analysis import get_meal_suggestions, display_meal_suggestions

def daily_summary_page():
    """Daily summary page"""
    st.title("📊 Daily Summary")
    
    # Check if user profile exists
    user_profile = load_user_profile(st.session_state.user_id)
    if not user_profile:
        st.warning("Please set up your profile first!")
        return
    
    # Select date
    selected_date = st.date_input("Select Date", datetime.now().date())
    date_str = selected_date.strftime("%Y-%m-%d")
    
    # Load food log for selected date
    daily_entries = load_food_logs(st.session_state.user_id, date_str)
    
    # Display summary header
    st.markdown("""
    <div class="custom-card">
        <h3>Daily Overview</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if daily_entries:
        # Calculate totals
        total_calories = sum(entry.get("calories", 0) for entry in daily_entries)
        total_protein = sum(entry.get("protein", 0) for entry in daily_entries)
        total_carbs = sum(entry.get("carbs", 0) for entry in daily_entries)
        total_fat = sum(entry.get("fat", 0) for entry in daily_entries)
        
        # Get daily goals
        calorie_goal = user_profile.get("calorie_goal", 2000)
        protein_goal = user_profile.get("protein_goal", 0)
        carbs_goal = user_profile.get("carbs_goal", 0)
        fat_goal = user_profile.get("fat_goal", 0)
        
        # Calculate remaining amounts
        remaining_calories = calorie_goal - total_calories
        remaining_protein = max(0, protein_goal - total_protein)
        remaining_carbs = max(0, carbs_goal - total_carbs)
        remaining_fat = max(0, fat_goal - total_fat)
        
        # Calculate percentages
        calorie_pct = min(100, (total_calories / calorie_goal) * 100)
        protein_pct = min(100, (total_protein / protein_goal) * 100) if protein_goal else 0
        carbs_pct = min(100, (total_carbs / carbs_goal) * 100) if carbs_goal else 0
        fat_pct = min(100, (total_fat / fat_goal) * 100) if fat_goal else 0
        
        # Display nutrition summary
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # Calories progress
            st.markdown("<h4>Calories</h4>", unsafe_allow_html=True)
            st.progress(calorie_pct / 100)
            
            col1a, col1b = st.columns(2)
            with col1a:
                st.markdown(
                    f"""
                    <div style="text-align:center;">
                        <div style="font-size:2rem; font-weight:bold;">{total_calories}</div>
                        <div style="font-size:0.9rem; color:#666;">consumed</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            with col1b:
                st.markdown(
                    f"""
                    <div style="text-align:center;">
                        <div style="font-size:2rem; font-weight:bold;">{calorie_goal}</div>
                        <div style="font-size:0.9rem; color:#666;">goal</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            # Display message based on calories
            if remaining_calories >= 0:
                st.markdown(
                    f"""
                    <div style="text-align:center; margin-top:0.5rem;">
                        <span style="font-weight:bold;">{remaining_calories}</span> calories remaining
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div style="text-align:center; margin-top:0.5rem; color:#ff4b4b;">
                        <span style="font-weight:bold;">{-remaining_calories}</span> calories over your goal
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        with col2:
            # Macros summary
            st.markdown("<h4>Macronutrients</h4>", unsafe_allow_html=True)
            
            # Create macros data
            macros_data = {
                "Nutrient": ["Protein", "Carbs", "Fat"],
                "Consumed": [total_protein, total_carbs, total_fat],
                "Goal": [protein_goal, carbs_goal, fat_goal],
                "Percent": [protein_pct, carbs_pct, fat_pct]
            }
            
            # Display macros as progress bars
            for i, nutrient in enumerate(macros_data["Nutrient"]):
                consumed = macros_data["Consumed"][i]
                goal = macros_data["Goal"][i]
                percent = macros_data["Percent"][i]
                
                st.markdown(
                    f"""
                    <div style="margin-bottom:0.5rem;">
                        <div style="display:flex; justify-content:space-between; margin-bottom:0.2rem;">
                            <div>{nutrient}</div>
                            <div>{consumed}g / {goal}g</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                st.progress(percent / 100)
        
        # Show macronutrient ratio
        st.markdown("<h4>Macronutrient Ratio</h4>", unsafe_allow_html=True)
        
        # Calculate calories from each macro
        protein_cals = total_protein * 4
        carbs_cals = total_carbs * 4
        fat_cals = total_fat * 9
        total_macro_cals = protein_cals + carbs_cals + fat_cals
        
        # Calculate percentages
        if total_macro_cals > 0:
            protein_ratio = (protein_cals / total_macro_cals) * 100
            carbs_ratio = (carbs_cals / total_macro_cals) * 100
            fat_ratio = (fat_cals / total_macro_cals) * 100
        else:
            protein_ratio = carbs_ratio = fat_ratio = 0
        
        # Create data for chart
        ratio_data = pd.DataFrame({
            'Macronutrient': ['Protein', 'Carbs', 'Fat'],
            'Calories': [protein_cals, carbs_cals, fat_cals],
            'Percentage': [protein_ratio, carbs_ratio, fat_ratio]
        })
        
        # Create donut chart
        base = alt.Chart(ratio_data).encode(
            theta=alt.Theta("Calories:Q", stack=True),
            color=alt.Color('Macronutrient:N', scale=alt.Scale(
                domain=['Protein', 'Carbs', 'Fat'],
                range=['#4CAF50', '#2196F3', '#FFC107']
            )),
            tooltip=['Macronutrient:N', 'Calories:Q', 'Percentage:Q']
        )
        
        pie = base.mark_arc(innerRadius=50, outerRadius=80)
        text = base.mark_text(radius=120, size=14).encode(text='Macronutrient:N')
        
        # Render chart
        st.altair_chart(pie + text, use_container_width=True)
        
        # Display meals throughout the day
        st.markdown("""
        <div class="custom-card">
            <h3>Meals Timeline</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Sort entries by time
        sorted_entries = sorted(daily_entries, key=lambda x: x.get("time", "00:00"))
        
        # Create timeline
        if sorted_entries:
            for i, entry in enumerate(sorted_entries):
                col1, col2, col3 = st.columns([1, 3, 2])
                
                with col1:
                    st.markdown(
                        f"""
                        <div style="text-align:center; padding-top:0.5rem;">
                            <div style="font-size:1.2rem; font-weight:bold;">{entry.get("time")}</div>
                            <div style="font-size:0.8rem; color:#666;">{entry.get("meal_name")}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                
                with col2:
                    food_items = entry.get("food_items", [])
                    food_items_str = ", ".join(food_items)
                    
                    st.markdown(
                        f"""
                        <div style="padding:0.5rem;">
                            <div style="font-weight:bold; margin-bottom:0.3rem;">Food Items:</div>
                            <div>{food_items_str if food_items else "No items recorded"}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                
                with col3:
                    # Calculate macro percentages for this meal
                    meal_protein = entry.get("protein", 0)
                    meal_carbs = entry.get("carbs", 0)
                    meal_fat = entry.get("fat", 0)
                    
                    meal_protein_cals = meal_protein * 4
                    meal_carbs_cals = meal_carbs * 4
                    meal_fat_cals = meal_fat * 9
                    meal_total_cals = meal_protein_cals + meal_carbs_cals + meal_fat_cals
                    
                    if meal_total_cals > 0:
                        meal_protein_pct = (meal_protein_cals / meal_total_cals) * 100
                        meal_carbs_pct = (meal_carbs_cals / meal_total_cals) * 100
                        meal_fat_pct = (meal_fat_cals / meal_total_cals) * 100
                    else:
                        meal_protein_pct = meal_carbs_pct = meal_fat_pct = 0
                    
                    st.markdown(
                        f"""
                        <div style="text-align:center; padding-top:0.5rem;">
                            <div style="font-size:1.5rem; font-weight:bold;">{entry.get("calories", 0)} cal</div>
                            <div style="font-size:0.8rem;">
                                P: {meal_protein}g ({meal_protein_pct:.0f}%) | 
                                C: {meal_carbs}g ({meal_carbs_pct:.0f}%) | 
                                F: {meal_fat}g ({meal_fat_pct:.0f}%)
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                
                # Add separator line
                if i < len(sorted_entries) - 1:
                    st.markdown("<hr style='margin:0.5rem 0; border-color:#eee;'>", unsafe_allow_html=True)
        else:
            st.info("No meals recorded for this day.")
        
        # If this is today and there are remaining calories, show meal suggestions
        if selected_date == datetime.now().date() and remaining_calories > 100:
            st.markdown("""
            <div class="custom-card">
                <h3>What to Eat Next?</h3>
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
        
        # Display insights based on the day's eating
        st.markdown("""
        <div class="custom-card">
            <h3>Daily Insights</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Generate insights
        insights = []
        
        # Calorie-related insights
        if remaining_calories < -200:
            insights.append(f"You consumed {-remaining_calories} calories over your goal. Consider more physical activity tomorrow.")
        elif remaining_calories > 500 and total_calories > 0:
            insights.append(f"You're {remaining_calories} calories under your goal. Make sure you're eating enough to support your metabolism.")
        elif abs(remaining_calories) < 100:
            insights.append("Great job staying on track with your calorie goal today!")
        
        # Protein-related insights
        protein_per_kg = total_protein / user_profile.get("weight", 70)
        if protein_per_kg < 1.2 and "Loss" in user_profile.get("goal", ""):
            insights.append(f"Your protein intake ({protein_per_kg:.1f}g per kg) is below optimal for fat loss. Aim for 1.6-2.2g per kg bodyweight.")
        elif protein_per_kg > 2.5:
            insights.append(f"Your protein intake is very high ({protein_per_kg:.1f}g per kg). Unless you're doing heavy resistance training, this may be excessive.")
        
        # Meal timing insights
        if len(sorted_entries) == 1:
            insights.append("Consider spreading your meals throughout the day for better energy levels and hunger management.")
        elif len(sorted_entries) > 5:
            insights.append("You're eating frequently today. This grazing pattern works well for some people but may make calorie control more challenging.")
        
        # Macronutrient balance insights
        if fat_ratio < 15:
            insights.append("Your fat intake is very low. Some fat is essential for hormone production and nutrient absorption.")
        elif fat_ratio > 45:
            insights.append("Your fat intake is quite high. While healthy fats are important, they're calorie-dense and may make calorie control more difficult.")
        
        if carbs_ratio < 15 and "Loss" not in user_profile.get("goal", ""):
            insights.append("Your carbohydrate intake is very low. Carbs provide energy for exercise and brain function.")
        
        # Display insights
        if insights:
            for insight in insights:
                st.markdown(f"• {insight}")
        else:
            st.info("Not enough data to generate insights for this day.")
    else:
        st.info(f"No meals logged for {date_str}. Go to 'Track Food' to log your meals.")
        
        # Show empty state with a call to action
        st.markdown("""
        <div style="text-align:center; padding:2rem 0;">
            <div style="font-size:4rem; margin-bottom:1rem;">📝</div>
            <h3>No meals recorded yet</h3>
            <p>Head over to the Track Food page to log your first meal of the day!</p>
        </div>
        """, unsafe_allow_html=True)