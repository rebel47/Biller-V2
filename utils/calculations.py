 
import math
from datetime import datetime, timedelta

def calculate_bmr(weight, height, age, gender):
    """Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation
    
    Args:
        weight (float): Weight in kilograms
        height (float): Height in centimeters
        age (int): Age in years
        gender (str): 'Male' or 'Female'
    
    Returns:
        float: BMR in calories per day
    """
    if gender.lower() == "male":
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:  # Female
        return 10 * weight + 6.25 * height - 5 * age - 161

def calculate_tdee(bmr, activity_level):
    """Calculate Total Daily Energy Expenditure
    
    Args:
        bmr (float): Basal Metabolic Rate
        activity_level (str): Activity level description
    
    Returns:
        float: TDEE in calories per day
    """
    activity_multipliers = {
        "sedentary": 1.2,
        "lightly active": 1.375,
        "moderately active": 1.55,
        "very active": 1.725,
        "extra active": 1.9
    }
    
    # Convert activity level to lowercase and extract main keywords
    activity_key = activity_level.lower()
    for key in activity_multipliers.keys():
        if key in activity_key:
            return bmr * activity_multipliers[key]
    
    # Default to sedentary if no match
    return bmr * 1.2

def calculate_calorie_goal(tdee, goal, rate=None):
    """Calculate daily calorie goal based on TDEE and user goal
    
    Args:
        tdee (float): Total Daily Energy Expenditure
        goal (str): 'Fat Loss', 'Maintenance', or 'Muscle Gain'
        rate (float, optional): Rate of loss/gain (kg per week). Defaults to None.
    
    Returns:
        float: Daily calorie goal
    """
    goal = goal.lower()
    
    if "loss" in goal or "fat" in goal:
        # For fat loss, default is 20% deficit
        deficit_pct = 0.2
        
        if rate:
            # If rate is specified, calculate deficit
            # 7700 calories = 1 kg of fat
            deficit = rate * 7700 / 7
            deficit_pct = min(deficit / tdee, 0.30)  # Cap at 30%
        
        return tdee * (1 - deficit_pct)
    
    elif "gain" in goal or "muscle" in goal or "bulk" in goal:
        # For muscle gain, default is 10% surplus
        surplus_pct = 0.1
        
        if rate:
            # If rate is specified, calculate surplus
            # ~3500 calories = 1 kg of muscle (approximate)
            surplus = rate * 3500 / 7
            surplus_pct = min(surplus / tdee, 0.20)  # Cap at 20%
        
        return tdee * (1 + surplus_pct)
    
    else:  # Maintenance
        return tdee

def calculate_macros(calories, goal, weight, body_fat=None):
    """Calculate recommended macronutrient distribution
    
    Args:
        calories (float): Daily calorie goal
        goal (str): 'Fat Loss', 'Maintenance', or 'Muscle Gain'
        weight (float): Weight in kilograms
        body_fat (float, optional): Body fat percentage. Defaults to None.
    
    Returns:
        dict: Recommended macros in grams (protein, carbs, fat)
    """
    goal = goal.lower()
    
    # Calculate lean body mass if body fat is provided
    lean_mass = weight
    if body_fat is not None:
        lean_mass = weight * (1 - (body_fat / 100))
    
    # Set protein based on goal and lean mass
    if "loss" in goal or "fat" in goal:
        # Higher protein for fat loss (2.0-2.2g per kg of lean mass)
        protein_g = lean_mass * 2.2
    elif "gain" in goal or "muscle" in goal or "bulk" in goal:
        # High protein for muscle gain (1.8-2.0g per kg of lean mass)
        protein_g = lean_mass * 2.0
    else:  # Maintenance
        # Moderate protein (1.6-1.8g per kg of lean mass)
        protein_g = lean_mass * 1.6
    
    # Calculate calories from protein
    protein_cals = protein_g * 4
    
    # Calculate remaining calories
    remaining_cals = calories - protein_cals
    
    # Set fat based on goal (percent of total calories)
    if "loss" in goal or "fat" in goal:
        # Lower fat for fat loss (20-25% of total calories)
        fat_pct = 0.25
    elif "gain" in goal or "muscle" in goal or "bulk" in goal:
        # Moderate fat for muscle gain (25-30% of total calories)
        fat_pct = 0.30
    else:  # Maintenance
        # Moderate fat (25-30% of total calories)
        fat_pct = 0.30
    
    # Calculate fat in grams
    fat_cals = calories * fat_pct
    fat_g = fat_cals / 9
    
    # Remaining calories go to carbs
    carb_cals = calories - protein_cals - fat_cals
    carb_g = carb_cals / 4
    
    # Round values to the nearest gram
    return {
        "protein_g": round(protein_g),
        "carbs_g": round(carb_g),
        "fat_g": round(fat_g)
    }

def calculate_weight_change(calorie_deficit, days):
    """Calculate estimated weight change based on calorie deficit/surplus
    
    Args:
        calorie_deficit (float): Daily calorie deficit (negative for weight loss)
        days (int): Number of days
    
    Returns:
        float: Estimated weight change in kilograms
    """
    # Total calorie deficit/surplus
    total_deficit = calorie_deficit * days
    
    # Weight change (7700 calories = 1 kg of fat)
    weight_change = total_deficit / 7700
    
    return weight_change

def calculate_estimated_goal_date(current_weight, goal_weight, daily_calorie_deficit):
    """Calculate estimated date to reach weight goal
    
    Args:
        current_weight (float): Current weight in kilograms
        goal_weight (float): Goal weight in kilograms
        daily_calorie_deficit (float): Daily calorie deficit
    
    Returns:
        datetime: Estimated date to reach goal
    """
    # Weight difference
    weight_diff = current_weight - goal_weight
    
    # If goal is higher than current, return None (not applicable)
    if weight_diff <= 0:
        return None
    
    # Total calories needed to lose
    total_calories = weight_diff * 7700
    
    # Days needed
    days_needed = total_calories / daily_calorie_deficit
    
    # Estimated date
    estimated_date = datetime.now() + timedelta(days=days_needed)
    
    return estimated_date

def calculate_body_fat_percentage(weight, height, age, gender, waist, neck, hip=None):
    """Calculate estimated body fat percentage using US Navy method
    
    Args:
        weight (float): Weight in kilograms
        height (float): Height in centimeters
        age (int): Age in years
        gender (str): 'Male' or 'Female'
        waist (float): Waist circumference in centimeters
        neck (float): Neck circumference in centimeters
        hip (float, optional): Hip circumference in centimeters (for females). Defaults to None.
    
    Returns:
        float: Estimated body fat percentage
    """
    # Convert height to inches
    height_in = height / 2.54
    
    # Convert circumferences to inches
    waist_in = waist / 2.54
    neck_in = neck / 2.54
    
    if gender.lower() == "male":
        # US Navy formula for males
        bf_pct = 495 / (1.0324 - 0.19077 * math.log10(waist_in - neck_in) + 0.15456 * math.log10(height_in)) - 450
    else:
        # US Navy formula for females (requires hip measurement)
        if hip is None:
            return None
        
        hip_in = hip / 2.54
        bf_pct = 495 / (1.29579 - 0.35004 * math.log10(waist_in + hip_in - neck_in) + 0.22100 * math.log10(height_in)) - 450
    
    return max(0, min(bf_pct, 60))  # Clamp to reasonable range

def calculate_ideal_weight_range(height, gender):
    """Calculate ideal weight range based on BMI
    
    Args:
        height (float): Height in centimeters
        gender (str): 'Male' or 'Female'
    
    Returns:
        tuple: Lower and upper bounds of ideal weight in kilograms
    """
    # Convert height to meters
    height_m = height / 100
    
    # Calculate weight ranges for BMI 18.5 - 24.9 (healthy range)
    lower_bound = 18.5 * (height_m ** 2)
    upper_bound = 24.9 * (height_m ** 2)
    
    # Round to 1 decimal place
    return (round(lower_bound, 1), round(upper_bound, 1))

def calculate_calories_from_macros(protein_g, carbs_g, fat_g):
    """Calculate calories from macronutrients
    
    Args:
        protein_g (float): Protein in grams
        carbs_g (float): Carbohydrates in grams
        fat_g (float): Fat in grams
    
    Returns:
        float: Total calories
    """
    protein_cals = protein_g * 4
    carbs_cals = carbs_g * 4
    fat_cals = fat_g * 9
    
    return protein_cals + carbs_cals + fat_cals