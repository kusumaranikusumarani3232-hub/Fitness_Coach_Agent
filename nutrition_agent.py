import json
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def generate_nutrition_plan(profile, api_key=None):
    """
    Generate custom nutrition suggestions using Gemini API based on user profile.
    Returns a dictionary parsed from Gemini's JSON output.
    """
    # Use provided API key or fall back to environment variable
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("Gemini API Key is not set. Please provide it in settings or .env file.")
        
    genai.configure(api_key=key)
    
    prompt = f"""
    You are an expert sports nutritionist and dietician.
    Generate a personalized nutrition plan and daily dietary targets based on the following user profile:
    
    Name: {profile.get('name', 'User')}
    Age: {profile.get('age', 'N/A')}
    Gender: {profile.get('gender', 'N/A')}
    Height: {profile.get('height', 'N/A')} cm
    Weight: {profile.get('weight', 'N/A')} kg
    Fitness Level: {profile.get('fitness_level', 'Beginner')}
    Goal: {profile.get('goal', 'General Fitness')}
    Workout Days Per Week: {profile.get('workout_days', 3)} days
    Injuries/Limitations: {profile.get('injuries', 'None')}
    
    Please provide the plan strictly formatted as a JSON object with the following schema:
    {{
      "summary": "Overall nutrition summary explaining the strategy based on their goals.",
      "daily_targets": {{
        "calories": "Target daily calories (e.g. 2100 kcal)",
        "protein": "Target daily protein (e.g. 140g)",
        "carbs": "Target daily carbohydrates (e.g. 230g)",
        "fats": "Target daily fats (e.g. 70g)",
        "water": "Target daily water intake (e.g. 3.0 liters)"
      }},
      "meal_ideas": {{
        "breakfast": [
          {{
            "name": "Meal name",
            "description": "Short description of the meal, highlighting why it is beneficial for their goal.",
            "ingredients": ["ingredient 1", "ingredient 2"],
            "calories": "Estimate calories",
            "protein": "Estimate protein"
          }}
        ],
        "lunch": [
          {{
            "name": "Meal name",
            "description": "Short description.",
            "ingredients": ["ingredient 1"],
            "calories": "Estimate calories",
            "protein": "Estimate protein"
          }}
        ],
        "dinner": [
          {{
            "name": "Meal name",
            "description": "Short description.",
            "ingredients": ["ingredient 1"],
            "calories": "Estimate calories",
            "protein": "Estimate protein"
          }}
        ],
        "snacks": [
          {{
            "name": "Meal name",
            "description": "Short description.",
            "ingredients": ["ingredient 1"],
            "calories": "Estimate calories",
            "protein": "Estimate protein"
          }}
        ]
      }},
      "general_recommendations": [
        "Recommendation 1 (e.g. Pre-workout fueling tips)",
        "Recommendation 2 (e.g. Post-workout recovery food)",
        "Recommendation 3 (e.g. Supplement advice like Whey or Creatine if appropriate)"
      ]
    }}
    
    Important Constraints:
    - Daily protein intake target should align with the goal (e.g. for Muscle Gain/Strength, use ~1.6 - 2.2g per kg of body weight; for Weight Loss, prioritize high protein density to preserve lean mass).
    - Meal plans should avoid any known limitations and fit their goal profile.
    - Provide estimates for calories, protein, carbs, and fats that are scientifically backed.
    """
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        plan_dict = json.loads(response.text)
        return plan_dict
        
    except json.JSONDecodeError as je:
        raise RuntimeError(f"Failed to parse AI nutrition response as JSON. Response text: {response.text}") from je
    except Exception as e:
        raise RuntimeError(f"Error during AI nutrition generation: {str(e)}") from e
