
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
import numpy as np

from utils.storage import load_user_profile, load_food_logs
from utils.calculations import calculate_weight_change, calculate_estimated_goal_date

def progress_page():
    """Progress tracker page"""
    st.title("📈 Progress Tracker")
    
    # Check if user profile exists
    user_profile = load_user_profile(st.session_state.user_id)
    if not user_profile:
        st.warning("Please set up your profile first!")
        return
    
    # Determine date range
    today = datetime.now().date()
    
    # Create date range options
    date_ranges = {
        "Last 7 days": (today - timedelta(days=6), today),
        "Last 14 days": (today - timedelta(days=13), today),
        "Last 30 days": (today - timedelta(days=29), today),
        "Last 90 days": (today - timedelta(days=89), today)
    }
    
    # Date range selection
    selected_range = st.selectbox(
        "Select Date Range",
        list(date_ranges.keys())
    )
    
    # Get selected date range
    start_date, end_date = date_ranges[selected_range]
    
    # Format dates for display and query
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    
    # Load food logs for selected date range
    logs = load_food_logs(
        st.session_state.user_id,
        start_date=start_date_str,
        end_date=end_date_str
    )
    
    # Group logs by date
    dates = {}
    for log in logs:
        date = log.get("date")
        if date in dates:
            dates[date]["calories"] += log.get("calories", 0)
            dates[date]["protein"] += log.get("protein", 0)
            dates[date]["carbs"] += log.get("carbs", 0)
            dates[date]["fat"] += log.get("fat", 0)
            dates[date]["entries"] += 1
        else:
            dates[date] = {
                "calories": log.get("calories", 0),
                "protein": log.get("protein", 0),
                "carbs": log.get("carbs", 0),
                "fat": log.get("fat", 0),
                "entries": 1
            }
    
    if dates:
        # Create DataFrame for charts
        df_dates = []
        for date, values in dates.items():
            df_dates.append({
                "date": date,
                "calories": values["calories"],
                "protein": values["protein"],
                "carbs": values["carbs"],
                "fat": values["fat"],
                "entries": values["entries"]
            })
        
        df = pd.DataFrame(df_dates)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
        
        # Fill in missing dates with zeros
        date_range = pd.date_range(start=start_date, end=end_date)
        df_complete = pd.DataFrame({"date": date_range})
        df_complete["date_str"] = df_complete["date"].dt.strftime("%Y-%m-%d")
        df["date_str"] = df["date"].dt.strftime("%Y-%m-%d")
        
        df_complete = df_complete.merge(df, on="date_str", how="left")
        df_complete["date"] = df_complete["date_x"]
        df_complete = df_complete.drop(["date_x", "date_y", "date_str"], axis=1)
        df_complete = df_complete.fillna(0)
        
        # Calculate daily calorie goal line
        daily_goal = user_profile.get("calorie_goal", 2000)
        df_complete["goal"] = daily_goal
        
        # Calculate averages
        avg_calories = df["calories"].mean() if not df.empty else 0
        avg_protein = df["protein"].mean() if not df.empty else 0
        avg_carbs = df["carbs"].mean() if not df.empty else 0
        avg_fat = df["fat"].mean() if not df.empty else 0
        
        # Calculate consistency (percentage of days tracked)
        days_tracked = len(df)
        total_days = (end_date - start_date).days + 1
        consistency = (days_tracked / total_days) * 100 if total_days > 0 else 0
        
        # Display summary metrics
        st.markdown("""
        <div class="custom-card">
            <h3>Summary Metrics</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Avg. Daily Calories", f"{avg_calories:.0f}")
        
        with col2:
            calorie_diff = avg_calories - daily_goal
            if abs(calorie_diff) < 50:
                trend_value = "≈ Goal"
            elif calorie_diff < 0:
                trend_value = f"{-calorie_diff:.0f} under"
            else:
                trend_value = f"{calorie_diff:.0f} over"
            
            st.metric("vs. Goal", trend_value)
        
        with col3:
            st.metric("Tracking Consistency", f"{consistency:.0f}%")
        
        with col4:
            # Calculate estimated weight change
            if "goal" in user_profile and "tdee" in user_profile:
                # Average daily deficit/surplus
                avg_deficit = user_profile.get("tdee", 0) - avg_calories
                
                # Estimated weight change
                days = (end_date - start_date).days + 1
                weight_change = calculate_weight_change(avg_deficit, days)
                
                if abs(weight_change) < 0.1:
                    weight_change_str = "≈ Maintained"
                elif weight_change > 0:
                    weight_change_str = f"↓ {weight_change:.1f} kg"
                else:
                    weight_change_str = f"↑ {-weight_change:.1f} kg"
                
                st.metric("Est. Weight Change", weight_change_str)
            else:
                st.metric("Est. Weight Change", "N/A")
        
        # Calorie chart
        st.markdown("""
        <div class="custom-card">
            <h3>Calorie Intake Over Time</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Create Altair chart for calories
        calorie_chart = alt.Chart(df_complete).mark_line(point=True).encode(
            x=alt.X('date:T', title='Date'),
            y=alt.Y('calories:Q', title='Calories', scale=alt.Scale(zero=False)),
            tooltip=['date:T', 'calories:Q']
        ).properties(height=300)
        
        # Add goal line
        goal_line = alt.Chart(df_complete).mark_line(
            color='red',
            strokeDash=[4, 4]
        ).encode(
            x='date:T',
            y='goal:Q'
        )
        
        # Display chart
        st.altair_chart(calorie_chart + goal_line, use_container_width=True)
        
        # Macronutrient chart
        st.markdown("""
        <div class="custom-card">
            <h3>Macronutrient Breakdown</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Create long-form data for macronutrients
        macro_data = []
        for _, row in df_complete.iterrows():
            macro_data.append({"date": row["date"], "nutrient": "Protein", "grams": row["protein"]})
            macro_data.append({"date": row["date"], "nutrient": "Carbs", "grams": row["carbs"]})
            macro_data.append({"date": row["date"], "nutrient": "Fat", "grams": row["fat"]})
        
        macro_df = pd.DataFrame(macro_data)
        
        # Create Altair chart for macronutrients
        macro_chart = alt.Chart(macro_df).mark_line().encode(
            x=alt.X('date:T', title='Date'),
            y=alt.Y('grams:Q', title='Grams'),
            color=alt.Color('nutrient:N', scale=alt.Scale(
                domain=['Protein', 'Carbs', 'Fat'],
                range=['#4CAF50', '#2196F3', '#FFC107']
            )),
            tooltip=['date:T', 'nutrient:N', 'grams:Q']
        ).properties(height=300)
        
        # Display chart
        st.altair_chart(macro_chart, use_container_width=True)
        
        # Weekly averages
        st.markdown("""
        <div class="custom-card">
            <h3>Weekly Averages</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Add week column
        df["week"] = df["date"].dt.isocalendar().week
        df["year"] = df["date"].dt.isocalendar().year
        
        # Group by week
        weekly_avg = df.groupby(["year", "week"]).agg({
            "calories": "mean",
            "protein": "mean",
            "carbs": "mean",
            "fat": "mean"
        }).reset_index()
        
        # Create a week label
        week_labels = []
        for _, row in weekly_avg.iterrows():
            # Get first day of the week
            first_day = datetime.fromisocalendar(int(row["year"]), int(row["week"]), 1)
            week_labels.append(first_day.strftime("%b %d"))
        
        weekly_avg["week_label"] = week_labels
        
        # Create bar chart for weekly calories
        weekly_chart = alt.Chart(weekly_avg).mark_bar().encode(
            x=alt.X('week_label:N', title='Week Starting', sort=None),
            y=alt.Y('calories:Q', title='Avg. Daily Calories'),
            color=alt.condition(
                alt.datum.calories > daily_goal,
                alt.value('#FF9800'),  # Orange if over goal
                alt.value('#4CAF50')   # Green if under goal
            ),
            tooltip=['week_label:N', 'calories:Q']
        ).properties(height=300)
        
        # Add goal line
        weekly_goal_line = alt.Chart(pd.DataFrame({'goal': [daily_goal]})).mark_rule(
            color='red',
            strokeDash=[4, 4]
        ).encode(
            y='goal:Q'
        )
        
        # Display chart
        st.altair_chart(weekly_chart + weekly_goal_line, use_container_width=True)
        
        # Create weekly macros chart
        weekly_macro_data = []
        for _, row in weekly_avg.iterrows():
            weekly_macro_data.append({"week": row["week_label"], "nutrient": "Protein", "grams": row["protein"]})
            weekly_macro_data.append({"week": row["week_label"], "nutrient": "Carbs", "grams": row["carbs"]})
            weekly_macro_data.append({"week": row["week_label"], "nutrient": "Fat", "grams": row["fat"]})
        
        weekly_macro_df = pd.DataFrame(weekly_macro_data)
        
        # Create grouped bar chart for weekly macros
        weekly_macro_chart = alt.Chart(weekly_macro_df).mark_bar().encode(
            x=alt.X('week:N', title='Week Starting', sort=None),
            y=alt.Y('grams:Q', title='Avg. Daily Grams'),
            color=alt.Color('nutrient:N', scale=alt.Scale(
                domain=['Protein', 'Carbs', 'Fat'],
                range=['#4CAF50', '#2196F3', '#FFC107']
            )),
            column=alt.Column('nutrient:N', title=None),
            tooltip=['week:N', 'nutrient:N', 'grams:Q']
        ).properties(
            width=alt.Step(40),
            height=200
        )
        
        # Display chart
        st.altair_chart(weekly_macro_chart, use_container_width=True)
        
        # Progress analysis
        st.markdown("""
        <div class="custom-card">
            <h3>Progress Analysis</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Get goal and calculate projected progress
        goal = user_profile.get("goal", "Maintenance")
        
        if goal == "Fat Loss" and "tdee" in user_profile:
            # Calculate average deficit
            avg_deficit = user_profile.get("tdee", 0) - avg_calories
            
            # Only proceed if there's actually a deficit
            if avg_deficit > 0:
                # Calculate current progress
                days_tracked = len(df)
                current_weight_loss = calculate_weight_change(avg_deficit, days_tracked)
                
                # Calculate projected monthly loss
                projected_monthly_loss = calculate_weight_change(avg_deficit, 30)
                
                # Calculate days needed to reach goal (if goal weight is specified)
                if "weight" in user_profile and "goal_weight" in user_profile:
                    current_weight = user_profile.get("weight")
                    goal_weight = user_profile.get("goal_weight")
                    
                    if current_weight > goal_weight:
                        # Calculate days needed
                        weight_to_lose = current_weight - goal_weight
                        calories_to_lose = weight_to_lose * 7700  # ~7700 calories per kg of fat
                        days_needed = calories_to_lose / avg_deficit if avg_deficit > 0 else float('inf')
                        
                        # Calculate estimated goal date
                        if days_needed < float('inf'):
                            goal_date = today + timedelta(days=days_needed)
                            goal_date_str = goal_date.strftime("%B %d, %Y")
                        else:
                            goal_date_str = "N/A (no deficit)"
                        
                        # Display projected timeline
                        st.markdown(
                            f"""
                            <div style="margin-bottom:1.5rem;">
                                <h4>Projected Timeline</h4>
                                <p>
                                    At your current average deficit of <b>{avg_deficit:.0f} calories/day</b>, you could reach your 
                                    goal weight of <b>{goal_weight} kg</b> by approximately <b>{goal_date_str}</b>.
                                </p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                
                # Display progress metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Avg. Daily Deficit", f"{avg_deficit:.0f} cal")
                
                with col2:
                    st.metric("Est. Weight Loss So Far", f"{current_weight_loss:.2f} kg")
                
                with col3:
                    st.metric("Projected Monthly Loss", f"{projected_monthly_loss:.2f} kg")
                
                # Provide insights based on rate of loss
                if projected_monthly_loss > 4:
                    st.warning(
                        "Your calorie deficit appears to be very aggressive. While this may lead to faster weight loss initially, "
                        "it's generally not sustainable and may lead to muscle loss, metabolic slowdown, and potential nutrient deficiencies. "
                        "Consider a more moderate approach of 0.5-1 kg per week for better long-term results."
                    )
                elif projected_monthly_loss < 0.5:
                    st.info(
                        "Your current calorie deficit is resulting in a very slow rate of fat loss. This is perfectly fine if you're "
                        "comfortable with gradual progress, but if you'd like to speed things up slightly, consider reducing your "
                        "calorie intake by an additional 200-300 calories per day or increasing your activity level."
                    )
                else:
                    st.success(
                        f"You're on track to lose approximately {projected_monthly_loss:.1f} kg per month, which is within the "
                        "recommended range for sustainable fat loss. Great job finding a balanced approach!"
                    )
            else:
                st.warning(
                    "Based on your tracking data, you're not currently in a calorie deficit. To achieve fat loss, "
                    "aim to consume fewer calories than your TDEE (Total Daily Energy Expenditure)."
                )
        
        elif goal == "Muscle Gain" and "tdee" in user_profile:
            # Calculate average surplus
            avg_surplus = avg_calories - user_profile.get("tdee", 0)
            
            # Only proceed if there's actually a surplus
            if avg_surplus > 0:
                # Calculate current progress
                days_tracked = len(df)
                current_weight_gain = abs(calculate_weight_change(-avg_surplus, days_tracked))
                
                # Calculate projected monthly gain
                projected_monthly_gain = abs(calculate_weight_change(-avg_surplus, 30))
                
                # Display progress metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Avg. Daily Surplus", f"{avg_surplus:.0f} cal")
                
                with col2:
                    st.metric("Est. Weight Gain So Far", f"{current_weight_gain:.2f} kg")
                
                with col3:
                    st.metric("Projected Monthly Gain", f"{projected_monthly_gain:.2f} kg")
                
                # Provide insights based on rate of gain
                if projected_monthly_gain > 2:
                    st.warning(
                        "Your calorie surplus appears to be quite high. While this will lead to weight gain, a significant portion "
                        "may be fat rather than muscle. For optimal muscle growth with minimal fat gain, consider reducing your "
                        "surplus to target a gain of 0.5-1 kg per month."
                    )
                elif projected_monthly_gain < 0.2:
                    st.info(
                        "Your current calorie surplus is resulting in a very slow rate of weight gain. If your goal is to "
                        "build muscle, consider increasing your calorie intake by an additional 200-300 calories per day, "
                        "particularly from protein and carbohydrates."
                    )
                else:
                    st.success(
                        f"You're on track to gain approximately {projected_monthly_gain:.1f} kg per month, which is a good "
                        "rate for lean muscle growth. Keep up the consistent eating and training!"
                    )
            else:
                st.warning(
                    "Based on your tracking data, you're not currently in a calorie surplus. To effectively build muscle, "
                    "aim to consume more calories than your TDEE (Total Daily Energy Expenditure)."
                )
        
        else:  # Maintenance
            # Calculate average deviation from TDEE
            if "tdee" in user_profile:
                avg_deviation = abs(avg_calories - user_profile.get("tdee", 0))
                deviation_pct = (avg_deviation / user_profile.get("tdee", 1)) * 100
                
                if deviation_pct < 5:
                    st.success(
                        f"You're staying very close to your maintenance calories ({deviation_pct:.1f}% deviation), "
                        "which is perfect for maintaining your current weight and body composition."
                    )
                elif deviation_pct < 10:
                    st.info(
                        f"You're averaging a {deviation_pct:.1f}% deviation from your maintenance calories. "
                        "This is still within a reasonable range for weight maintenance, though you may see slight "
                        "fluctuations over time."
                    )
                else:
                    direction = "deficit" if avg_calories < user_profile.get("tdee", 0) else "surplus"
                    st.warning(
                        f"You're averaging a {deviation_pct:.1f}% {direction} from your maintenance calories. "
                        "If maintenance is your goal, consider adjusting your intake to more closely match your TDEE."
                    )
        
        # Consistency analysis
        st.markdown("<h4>Tracking Consistency</h4>", unsafe_allow_html=True)
        
        # Calculate days tracked vs. total days
        days_in_range = (end_date - start_date).days + 1
        missing_days = days_in_range - len(df)
        
        if missing_days == 0:
            st.success(
                f"Perfect tracking consistency! You've tracked your nutrition every day for the entire {days_in_range}-day period."
            )
        elif consistency >= 80:
            st.success(
                f"Great tracking consistency! You've tracked your nutrition on {len(df)} out of {days_in_range} days ({consistency:.0f}%)."
            )
        elif consistency >= 50:
            st.info(
                f"Moderate tracking consistency. You've tracked your nutrition on {len(df)} out of {days_in_range} days ({consistency:.0f}%). "
                "Try to increase your consistency for more reliable data and better results."
            )
        else:
            st.warning(
                f"Low tracking consistency. You've only tracked your nutrition on {len(df)} out of {days_in_range} days ({consistency:.0f}%). "
                "Consistent tracking is key to achieving your nutrition and fitness goals."
            )
        
        # Recommendations section
        st.markdown("""
        <div class="custom-card">
            <h3>Recommendations</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Generate recommendations based on tracking data
        recommendations = []
        
        # Calorie-related recommendations
        tdee = user_profile.get("tdee", 0)
        if goal == "Fat Loss":
            if avg_calories > tdee:
                recommendations.append(
                    "Your average calorie intake is above your TDEE. To achieve fat loss, aim to reduce your daily calories "
                    f"by {(avg_calories - tdee + 200):.0f} calories to create a moderate deficit."
                )
            elif avg_calories < tdee * 0.7:
                recommendations.append(
                    "Your calorie deficit appears to be very aggressive. Consider increasing your intake slightly to ensure "
                    "sustainable progress and adequate nutrition."
                )
        
        elif goal == "Muscle Gain":
            if avg_calories < tdee:
                recommendations.append(
                    "Your average calorie intake is below your TDEE. To support muscle growth, aim to increase your daily calories "
                    f"by {(tdee - avg_calories + 200):.0f} calories to create a slight surplus."
                )
            elif avg_calories > tdee * 1.2:
                recommendations.append(
                    "Your calorie surplus appears to be quite high, which may lead to excessive fat gain. Consider reducing your "
                    "intake slightly to promote leaner muscle growth."
                )
        
        # Protein-related recommendations
        protein_goal = user_profile.get("protein_goal", 0)
        if avg_protein < protein_goal * 0.8:
            recommendations.append(
                f"Your protein intake ({avg_protein:.0f}g) is below your target ({protein_goal}g). Adequate protein is crucial for "
                "muscle preservation during fat loss and muscle building during a surplus."
            )
        
        # Consistency recommendations
        if consistency < 80:
            recommendations.append(
                "Improve your tracking consistency to get more accurate insights. Try setting a daily reminder or tracking "
                "as you eat rather than at the end of the day."
            )
        
        # Display recommendations
        if recommendations:
            for i, recommendation in enumerate(recommendations):
                st.markdown(f"{i+1}. {recommendation}")
        else:
            st.success(
                "Based on your tracking data, you're doing well! Continue with your current approach and monitor your "
                "progress over time."
            )
    else:
        st.info(f"No meals logged between {start_date_str} and {end_date_str}.")
        
        # Show empty state with a call to action
        st.markdown("""
        <div style="text-align:center; padding:2rem 0;">
            <div style="font-size:4rem; margin-bottom:1rem;">📊</div>
            <h3>No tracking data yet</h3>
            <p>Start tracking your meals to see progress over time!</p>
        </div>
        """, unsafe_allow_html=True)