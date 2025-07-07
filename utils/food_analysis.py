import os
import json
import google.generativeai as genai
from PIL import Image
import streamlit as st

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def analyze_food_image(image):
    """Analyze food image using Gemini Vision API
    
    Args:
        image: PIL.Image object
    
    Returns:
        dict: Analysis results or error
    """
    if not GEMINI_API_KEY:
        return {
            "success": False,
            "error": "No Gemini API key provided"
        }
    
    try:
        # Configure the model - UPDATED to use the current model version
        # Changed from 'gemini-pro-vision' to 'gemini-2.5-flash'
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Create the prompt for detailed nutrition analysis
        prompt = """
        Analyze this food image and provide a detailed nutritional breakdown:
        1. Identify all food items visible
        2. Estimate total calories for the entire meal
        3. Provide macronutrient breakdown (protein, carbs, fat in grams)
        4. List any notable micronutrients
        5. Suggest health considerations or improvements
        
        Format your response as a JSON object with these keys: 
        {
            "food_items": ["item1", "item2", ...],
            "total_calories": number,
            "protein_grams": number,
            "carbs_grams": number,
            "fat_grams": number,
            "notable_nutrients": ["nutrient1", "nutrient2", ...],
            "health_suggestions": ["suggestion1", "suggestion2", ...]
        }
        
        Make sure your response contains ONLY the JSON object, nothing else.
        """
        
        # Generate content
        response = model.generate_content([prompt, image])
        
        # Extract the JSON from the response
        response_text = response.text
        
        # Clean the response to get valid JSON
        # Remove markdown code blocks if present
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            json_str = response_text.split("```")[1].strip()
        else:
            json_str = response_text.strip()
        
        # Parse the JSON
        result = json.loads(json_str)
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def display_food_analysis_results(analysis_result, user_profile=None, manual_calories=0):
    """Display food analysis results in a well-formatted UI
    
    Args:
        analysis_result (dict): Analysis results from analyze_food_image
        user_profile (dict, optional): User profile data for context. Defaults to None.
        manual_calories (int, optional): Manual calorie override. Defaults to 0.
    
    Returns:
        dict: Processed food data
    """
    if not analysis_result.get("success"):
        st.error(f"Error analyzing image: {analysis_result.get('error')}")
        return None
    
    food_data = analysis_result.get("data")
    
    # Create columns for display
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("Food Items Detected")
        
        # Display items in a modern card-like style
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        
        for item in food_data.get("food_items", []):
            st.markdown(f"• {item}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Notable nutrients
        if food_data.get("notable_nutrients"):
            st.subheader("Notable Nutrients")
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            
            for nutrient in food_data.get("notable_nutrients", []):
                st.markdown(f"• {nutrient}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Health suggestions
        if food_data.get("health_suggestions"):
            st.subheader("Health Suggestions")
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            
            for suggestion in food_data.get("health_suggestions", []):
                st.markdown(f"• {suggestion}")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.subheader("Nutritional Summary")
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        
        # Use manual override if provided
        total_calories = food_data.get("total_calories", 0)
        if manual_calories > 0:
            total_calories = manual_calories
        
        # Calculate macros
        protein = food_data.get("protein_grams", 0)
        carbs = food_data.get("carbs_grams", 0)
        fat = food_data.get("fat_grams", 0)
        
        # Display calories with larger font
        st.markdown(f"<h1 style='font-size:2.5rem; text-align:center;'>{total_calories}</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; margin-top:-1rem;'>calories</p>", unsafe_allow_html=True)
        
        # Display macros in a visually appealing way
        st.markdown("<div style='display:flex; justify-content:space-between; margin-top:1rem;'>", unsafe_allow_html=True)
        
        # Calculate percentages
        total_macros = (protein * 4) + (carbs * 4) + (fat * 9)
        if total_macros > 0:
            protein_pct = round((protein * 4 / total_macros) * 100)
            carbs_pct = round((carbs * 4 / total_macros) * 100)
            fat_pct = round((fat * 9 / total_macros) * 100)
        else:
            protein_pct = carbs_pct = fat_pct = 0
        
        # Display macro columns
        st.markdown(
            f"""
            <div style='text-align:center; width:30%;'>
                <div style='font-size:1.5rem; font-weight:bold;'>{protein}g</div>
                <div>Protein</div>
                <div style='font-size:0.8rem; color:#666;'>{protein_pct}%</div>
            </div>
            <div style='text-align:center; width:30%;'>
                <div style='font-size:1.5rem; font-weight:bold;'>{carbs}g</div>
                <div>Carbs</div>
                <div style='font-size:0.8rem; color:#666;'>{carbs_pct}%</div>
            </div>
            <div style='text-align:center; width:30%;'>
                <div style='font-size:1.5rem; font-weight:bold;'>{fat}g</div>
                <div>Fat</div>
                <div style='font-size:0.8rem; color:#666;'>{fat_pct}%</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Display percentage of daily goal if profile exists
        if user_profile:
            daily_goal = user_profile.get("calorie_goal", 2000)
            percentage = (total_calories / daily_goal) * 100
            
            st.markdown("<div style='margin-top:1.5rem;'>", unsafe_allow_html=True)
            st.progress(min(percentage / 100, 1.0))
            st.markdown(
                f"<p style='text-align:center;'>{percentage:.1f}% of daily goal ({daily_goal} cal)</p>",
                unsafe_allow_html=True
            )
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Prepare processed data
    processed_data = {
        "food_items": food_data.get("food_items", []),
        "calories": total_calories,
        "protein": protein,
        "carbs": carbs,
        "fat": fat,
        "notable_nutrients": food_data.get("notable_nutrients", []),
        "health_suggestions": food_data.get("health_suggestions", [])
    }
    
    return processed_data

def get_meal_suggestions(user_profile, daily_intake, remaining_calories):
    """Get meal suggestions based on user profile and remaining calories
    
    Args:
        user_profile (dict): User profile data
        daily_intake (dict): Daily intake data
        remaining_calories (float): Remaining calories for the day
    
    Returns:
        dict: Meal suggestions
    """
    try:
        # Configure the model - UPDATED to use current model version
        # Changed from 'gemini-pro' to 'gemini-2.5-flash'
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Extract relevant data
        goal = user_profile.get("goal", "Maintenance")
        daily_goal = user_profile.get("calorie_goal", 2000)
        
        protein_consumed = daily_intake.get("protein", 0)
        carbs_consumed = daily_intake.get("carbs", 0)
        fat_consumed = daily_intake.get("fat", 0)
        
        # Calculate target macros based on goal
        if "Loss" in goal:
            protein_target = user_profile.get("weight", 70) * 2.0
            fat_target = (daily_goal * 0.25) / 9
            carbs_target = (daily_goal - (protein_target * 4) - (fat_target * 9)) / 4
        elif "Gain" in goal:
            protein_target = user_profile.get("weight", 70) * 1.8
            fat_target = (daily_goal * 0.30) / 9
            carbs_target = (daily_goal - (protein_target * 4) - (fat_target * 9)) / 4
        else:  # Maintenance
            protein_target = user_profile.get("weight", 70) * 1.6
            fat_target = (daily_goal * 0.30) / 9
            carbs_target = (daily_goal - (protein_target * 4) - (fat_target * 9)) / 4
        
        # Calculate remaining macros
        protein_remaining = max(0, protein_target - protein_consumed)
        fat_remaining = max(0, fat_target - fat_consumed)
        carbs_remaining = max(0, carbs_target - carbs_consumed)
        
        # Create the prompt
        prompt = f"""
        I need meal suggestions based on the following nutritional information:
        
        User's goal: {goal}
        Remaining calories for the day: {remaining_calories} calories
        Protein consumed today: {protein_consumed}g (target: {protein_target:.0f}g)
        Carbs consumed today: {carbs_consumed}g (target: {carbs_target:.0f}g)
        Fat consumed today: {fat_consumed}g (target: {fat_target:.0f}g)
        
        Please suggest three meal options that would help the user reach their daily goals.
        Each suggestion should include:
        1. Meal name
        2. Approximate calories
        3. Protein, carbs, and fat content
        4. A brief description of why this meal is appropriate
        
        Format your response as a JSON object with this structure:
        {{
            "meal_suggestions": [
                {{
                    "name": "Meal name",
                    "calories": number,
                    "protein": number,
                    "carbs": number,
                    "fat": number,
                    "description": "Brief description"
                }},
                ...
            ]
        }}
        
        Please provide ONLY the JSON object, nothing else.
        """
        
        # Generate content
        response = model.generate_content(prompt)
        
        # Extract the JSON from the response
        response_text = response.text
        
        # Clean the response to get valid JSON
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            json_str = response_text.split("```")[1].strip()
        else:
            json_str = response_text.strip()
        
        # Parse the JSON
        result = json.loads(json_str)
        
        return result
    except Exception as e:
        print(f"Error getting meal suggestions: {e}")
        return {
            "meal_suggestions": [
                {
                    "name": "Protein-rich snack",
                    "calories": min(remaining_calories, 300),
                    "protein": 20,
                    "carbs": 10,
                    "fat": 10,
                    "description": "A protein-rich snack to help meet your daily protein goals."
                }
            ]
        }

def display_meal_suggestions(suggestions):
    """Display meal suggestions in a visually appealing way
    
    Args:
        suggestions (dict): Meal suggestions from get_meal_suggestions
    """
    st.subheader("Meal Suggestions")
    
    meals = suggestions.get("meal_suggestions", [])
    
    # Create a row of cards
    cols = st.columns(min(3, len(meals)))
    
    for i, meal in enumerate(meals[:3]):  # Display up to 3 meals
        with cols[i]:
            st.markdown(
                f"""
                <div class="custom-card" style="height:100%;">
                    <h3 style="margin-top:0;">{meal.get("name")}</h3>
                    <div style="font-size:1.5rem; font-weight:bold; margin:0.5rem 0;">
                        {meal.get("calories")} cal
                    </div>
                    <div style="margin:1rem 0;">
                        <span style="margin-right:1rem;"><b>P:</b> {meal.get("protein")}g</span>
                        <span style="margin-right:1rem;"><b>C:</b> {meal.get("carbs")}g</span>
                        <span><b>F:</b> {meal.get("fat")}g</span>
                    </div>
                    <p style="margin-top:1rem;">{meal.get("description")}</p>
                </div>
                """,
                unsafe_allow_html=True
            )