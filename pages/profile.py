 
import streamlit as st
from datetime import datetime
from utils.storage import save_user_profile, load_user_profile
from utils.calculations import (
    calculate_bmr, 
    calculate_tdee, 
    calculate_calorie_goal,
    calculate_macros,
    calculate_ideal_weight_range
)

def profile_page():
    """Profile setup page"""
    st.title("👤 Profile Setup")
    
    # Load existing profile
    user_profile = load_user_profile(st.session_state.user_id)
    
    # Create tabs for different profile sections
    tabs = st.tabs(["Basic Info", "Body Measurements", "Goals & Settings"])
    
    # Tab 1: Basic Info
    with tabs[0]:
        st.markdown("""
        <div class="custom-card">
            <h3>Personal Information</h3>
            <p>This information helps us calculate your daily calorie needs accurately.</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("basic_info_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Name", 
                                  value=user_profile.get("name", "") if user_profile else "")
                age = st.number_input("Age", 
                                   min_value=15, max_value=100, 
                                   value=user_profile.get("age", 30) if user_profile else 30)
                gender = st.selectbox("Gender", 
                                   ["Male", "Female"], 
                                   index=0 if not user_profile or user_profile.get("gender") == "Male" else 1)
            
            with col2:
                weight = st.number_input("Weight (kg)", 
                                     min_value=30.0, max_value=250.0, step=0.1,
                                     value=user_profile.get("weight", 70.0) if user_profile else 70.0)
                height = st.number_input("Height (cm)", 
                                     min_value=100.0, max_value=250.0, step=0.1,
                                     value=user_profile.get("height", 170.0) if user_profile else 170.0)
                
                # Calculate BMI and display
                bmi = weight / ((height/100) ** 2)
                bmi_categories = {
                    "Underweight": (0, 18.5),
                    "Normal weight": (18.5, 25),
                    "Overweight": (25, 30),
                    "Obesity": (30, float('inf'))
                }
                bmi_category = next((category for category, (lower, upper) in bmi_categories.items() 
                                 if lower <= bmi < upper), "Unknown")
                
                st.info(f"BMI: {bmi:.1f} ({bmi_category})")
            
            basic_info_submit = st.form_submit_button("Save Basic Info", use_container_width=True)
        
        if basic_info_submit:
            # Save basic info
            if not user_profile:
                user_profile = {}
            
            user_profile.update({
                "name": name,
                "age": age,
                "gender": gender,
                "weight": weight,
                "height": height,
                "bmi": bmi,
                "last_updated": datetime.now().isoformat()
            })
            
            if save_user_profile(st.session_state.user_id, user_profile):
                st.success("Basic information saved successfully!")
    
    # Tab 2: Body Measurements
    with tabs[1]:
        st.markdown("""
        <div class="custom-card">
            <h3>Body Measurements</h3>
            <p>Optional: These measurements help us estimate your body composition more accurately.</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("measurements_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                waist = st.number_input("Waist Circumference (cm)", 
                                     min_value=40.0, max_value=200.0, step=0.1,
                                     value=user_profile.get("waist", 80.0) if user_profile else 80.0)
                neck = st.number_input("Neck Circumference (cm)", 
                                    min_value=20.0, max_value=80.0, step=0.1,
                                    value=user_profile.get("neck", 35.0) if user_profile else 35.0)
            
            with col2:
                hip = None
                if not user_profile or user_profile.get("gender") == "Female":
                    hip = st.number_input("Hip Circumference (cm)", 
                                       min_value=50.0, max_value=200.0, step=0.1,
                                       value=user_profile.get("hip", 90.0) if user_profile else 90.0)
                
                # Body fat calculation would go here if using Navy method
                # Display ideal weight range
                if user_profile and "height" in user_profile:
                    lower, upper = calculate_ideal_weight_range(user_profile.get("height"), 
                                                              user_profile.get("gender", "Male"))
                    st.info(f"Ideal weight range: {lower} - {upper} kg")
            
            measurements_submit = st.form_submit_button("Save Measurements", use_container_width=True)
        
        if measurements_submit:
            # Save measurements
            if not user_profile:
                user_profile = {}
            
            measurements_update = {
                "waist": waist,
                "neck": neck,
                "last_updated": datetime.now().isoformat()
            }
            
            if hip:
                measurements_update["hip"] = hip
            
            user_profile.update(measurements_update)
            
            if save_user_profile(st.session_state.user_id, user_profile):
                st.success("Body measurements saved successfully!")
    
    # Tab 3: Goals & Settings
    with tabs[2]:
        st.markdown("""
        <div class="custom-card">
            <h3>Fitness Goals</h3>
            <p>Set your goals and activity level to calculate your daily calorie targets.</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("goals_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                goal = st.selectbox("Goal", 
                                 ["Fat Loss", "Maintenance", "Muscle Gain"], 
                                 index=0 if not user_profile else ["Fat Loss", "Maintenance", "Muscle Gain"].index(user_profile.get("goal", "Fat Loss")))
                
                if goal == "Fat Loss":
                    weekly_rate = st.slider("Target weekly fat loss (kg)", 
                                         min_value=0.1, max_value=1.0, step=0.1,
                                         value=user_profile.get("weekly_rate", 0.5) if user_profile else 0.5)
                    st.info(f"Recommended range: 0.5-1.0 kg per week")
                elif goal == "Muscle Gain":
                    weekly_rate = st.slider("Target weekly muscle gain (kg)", 
                                         min_value=0.1, max_value=0.5, step=0.1,
                                         value=user_profile.get("weekly_rate", 0.2) if user_profile else 0.2)
                    st.info(f"Recommended range: 0.1-0.5 kg per week")
            
            with col2:
                activity_level = st.selectbox(
                    "Activity Level",
                    [
                        "Sedentary (little or no exercise)",
                        "Lightly active (light exercise/sports 1-3 days/week)",
                        "Moderately active (moderate exercise/sports 3-5 days/week)",
                        "Very active (hard exercise/sports 6-7 days/week)",
                        "Extra active (very hard exercise, physical job or training twice a day)"
                    ],
                    index=0 if not user_profile else [
                        "Sedentary (little or no exercise)",
                        "Lightly active (light exercise/sports 1-3 days/week)",
                        "Moderately active (moderate exercise/sports 3-5 days/week)",
                        "Very active (hard exercise/sports 6-7 days/week)",
                        "Extra active (very hard exercise, physical job or training twice a day)"
                    ].index(user_profile.get("activity_level", "Sedentary (little or no exercise)"))
                )
                
                # Add any additional settings here
            
            goals_submit = st.form_submit_button("Save Goals & Calculate", use_container_width=True)
        
        if goals_submit:
            # Save goals and calculate nutritional values
            if not user_profile:
                st.error("Please fill out your basic information first!")
            else:
                # Calculate BMR, TDEE, and calorie goals
                bmr = calculate_bmr(user_profile.get("weight"), user_profile.get("height"), 
                                  user_profile.get("age"), user_profile.get("gender"))
                tdee = calculate_tdee(bmr, activity_level)
                
                # Calculate calorie goal based on goal and weekly rate if applicable
                if goal in ["Fat Loss", "Muscle Gain"]:
                    calorie_goal = calculate_calorie_goal(tdee, goal, weekly_rate)
                    
                    # Save weekly rate
                    user_profile["weekly_rate"] = weekly_rate
                else:
                    calorie_goal = calculate_tdee(bmr, activity_level)
                
                # Calculate macros
                macros = calculate_macros(calorie_goal, goal, user_profile.get("weight"))
                
                # Update user profile
                user_profile.update({
                    "goal": goal,
                    "activity_level": activity_level,
                    "bmr": bmr,
                    "tdee": tdee,
                    "calorie_goal": calorie_goal,
                    "protein_goal": macros.get("protein_g"),
                    "carbs_goal": macros.get("carbs_g"),
                    "fat_goal": macros.get("fat_g"),
                    "last_updated": datetime.now().isoformat()
                })
                
                if save_user_profile(st.session_state.user_id, user_profile):
                    st.success("Goals saved and calculations completed!")
                    st.balloons()
    
    # Display nutritional information if profile exists and has calculations
    if user_profile and "bmr" in user_profile:
        st.markdown("""
        <div class="custom-card">
            <h3>Your Nutritional Information</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Basal Metabolic Rate (BMR)", f"{int(user_profile.get('bmr', 0))} calories")
            st.markdown("""
            <div style="font-size:0.8rem; color:#666;">
            Calories your body needs at complete rest
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.metric("Total Daily Energy Expenditure (TDEE)", f"{int(user_profile.get('tdee', 0))} calories")
            st.markdown("""
            <div style="font-size:0.8rem; color:#666;">
            Calories you burn throughout a typical day
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.metric("Daily Calorie Goal", f"{int(user_profile.get('calorie_goal', 0))} calories")
            st.markdown("""
            <div style="font-size:0.8rem; color:#666;">
            Target calories based on your fitness goals
            </div>
            """, unsafe_allow_html=True)
        
        # Display macronutrient breakdown
        st.markdown("<h4>Recommended Macronutrients</h4>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            protein = user_profile.get('protein_goal', 0)
            protein_cals = protein * 4
            protein_pct = round((protein_cals / user_profile.get('calorie_goal', 1)) * 100)
            
            st.markdown(
                f"""
                <div class="custom-card" style="text-align:center;">
                    <div style="font-size:2rem; font-weight:bold;">{protein}g</div>
                    <div style="font-size:1.2rem;">Protein</div>
                    <div style="font-size:0.8rem; color:#666;">{protein_pct}% of calories</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col2:
            carbs = user_profile.get('carbs_goal', 0)
            carbs_cals = carbs * 4
            carbs_pct = round((carbs_cals / user_profile.get('calorie_goal', 1)) * 100)
            
            st.markdown(
                f"""
                <div class="custom-card" style="text-align:center;">
                    <div style="font-size:2rem; font-weight:bold;">{carbs}g</div>
                    <div style="font-size:1.2rem;">Carbs</div>
                    <div style="font-size:0.8rem; color:#666;">{carbs_pct}% of calories</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col3:
            fat = user_profile.get('fat_goal', 0)
            fat_cals = fat * 9
            fat_pct = round((fat_cals / user_profile.get('calorie_goal', 1)) * 100)
            
            st.markdown(
                f"""
                <div class="custom-card" style="text-align:center;">
                    <div style="font-size:2rem; font-weight:bold;">{fat}g</div>
                    <div style="font-size:1.2rem;">Fat</div>
                    <div style="font-size:0.8rem; color:#666;">{fat_pct}% of calories</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        # Display goal explanation
        goal = user_profile.get('goal', 'Maintenance')
        
        if goal == "Fat Loss":
            deficit = user_profile.get('tdee', 0) - user_profile.get('calorie_goal', 0)
            weekly_rate = user_profile.get('weekly_rate', 0.5)
            
            st.markdown(
                f"""
                <div class="custom-card">
                    <h4>Your Fat Loss Plan</h4>
                    <p>
                        You're in a <b>{deficit:.0f} calorie deficit</b> per day, which should result in 
                        approximately <b>{weekly_rate} kg</b> of fat loss per week.
                    </p>
                    <p>
                        The higher protein intake ({protein}g) will help preserve muscle mass while losing fat.
                        Stay hydrated and focus on nutrient-dense whole foods for best results.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        elif goal == "Muscle Gain":
            surplus = user_profile.get('calorie_goal', 0) - user_profile.get('tdee', 0)
            weekly_rate = user_profile.get('weekly_rate', 0.2)
            
            st.markdown(
                f"""
                <div class="custom-card">
                    <h4>Your Muscle Building Plan</h4>
                    <p>
                        You're in a <b>{surplus:.0f} calorie surplus</b> per day, which should support 
                        approximately <b>{weekly_rate} kg</b> of muscle gain per week.
                    </p>
                    <p>
                        Focus on progressive resistance training and ensure you're getting adequate protein 
                        ({protein}g) to maximize muscle protein synthesis.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        else:  # Maintenance
            st.markdown(
                f"""
                <div class="custom-card">
                    <h4>Your Maintenance Plan</h4>
                    <p>
                        You're eating at maintenance level, which will help sustain your current weight
                        while supporting your activity level and overall health.
                    </p>
                    <p>
                        This is ideal for body recomposition (building muscle while losing fat), improving athletic 
                        performance, or taking a break from a calorie deficit or surplus.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )