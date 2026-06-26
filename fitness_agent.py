import json
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def generate_workout_plan(profile, api_key=None):
    """
    Generate a 7-day workout plan using Gemini API based on user profile.
    Returns a dictionary parsed from Gemini's JSON output.
    """
    # Use provided API key or fall back to environment variable
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("Gemini API Key is not set. Please provide it in settings or .env file.")
        
    genai.configure(api_key=key)
    
    # Prompt detailing the profile and requested JSON schema
    prompt = f"""
    You are an elite, certified personal trainer and AI Fitness Coach.
    Generate a personalized 7-day workout plan based on the following user profile:
    
    Name: {profile.get('name', 'User')}
    Age: {profile.get('age', 'N/A')}
    Gender: {profile.get('gender', 'N/A')}
    Height: {profile.get('height', 'N/A')} cm
    Weight: {profile.get('weight', 'N/A')} kg
    Fitness Level: {profile.get('fitness_level', 'Beginner')}
    Goal: {profile.get('goal', 'General Fitness')}
    Workout Days Per Week: {profile.get('workout_days', 3)} days
    Available Time Per Session: {profile.get('time_per_session', 45)} minutes
    Equipment Available: {profile.get('equipment', 'None')}
    Injuries/Limitations: {profile.get('injuries', 'None')}
    
    Please provide the plan strictly formatted as a JSON object with the following schema:
    {{
      "summary": "Overall coaching summary and how the plan aligns with their goals.",
      "safety_tips": ["tip 1", "tip 2", "tip 3"],
      "schedule": {{
        "Monday": {{
          "rest_day": true,
          "focus": "Active Recovery / Rest",
          "duration_minutes": 0,
          "warmup": ["5 mins deep breathing and light stretching"],
          "exercises": [],
          "cooldown": []
        }},
        "Tuesday": {{
          "rest_day": false,
          "focus": "Focus of the day (e.g. Upper Body Strength)",
          "duration_minutes": 45,
          "warmup": ["exercise 1 with description", "exercise 2 with description"],
          "exercises": [
            {{
              "name": "Exercise Name",
              "sets": 3,
              "reps": "10-12 (or '30s')",
              "rest": "60s",
              "explanation": "Why this exercise is included and how it helps the goal."
            }}
          ],
          "cooldown": ["stretch 1 with description", "stretch 2 with description"]
        }},
        "Wednesday": {{ ... }},
        "Thursday": {{ ... }},
        "Friday": {{ ... }},
        "Saturday": {{ ... }},
        "Sunday": {{ ... }}
      }}
    }}
    
    Important Constraints:
    - Match the number of workout days exactly ({profile.get('workout_days', 3)} days should have "rest_day": false, the other {7 - int(profile.get('workout_days', 3))} days should have "rest_day": true).
    - If equipment is 'None', generate bodyweight-only exercises. If equipment is 'Dumbbells', use dumbbells and bodyweight. Make sure exercises are appropriate.
    - Explicitly avoid exercises that aggravate any listed injuries or limitations: "{profile.get('injuries', 'None')}".
    - Provide realistic sets, reps, and rest times fitting their fitness level: {profile.get('fitness_level', 'Beginner')}.
    """
    
    try:
        # Use gemini-1.5-flash as the default model
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        # Parse output
        plan_dict = json.loads(response.text)
        return plan_dict
        
    except json.JSONDecodeError as je:
        raise RuntimeError(f"Failed to parse AI response as JSON. Response text: {response.text}") from je
    except Exception as e:
        raise RuntimeError(f"Error during AI plan generation: {str(e)}") from e
