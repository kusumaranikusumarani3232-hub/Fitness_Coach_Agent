import json
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

COACH_STYLES = {
    "Empathetic Friend": {
        "description": "Warm, supportive, and compassionate. Focuses on small wins, self-care, and understanding setbacks.",
        "icon": "🤗"
    },
    "No-Excuses Drill Sergeant": {
        "description": "High-energy, direct, and tough. Focuses on discipline, mental strength, and accountability.",
        "icon": "⚡"
    },
    "Zen Mindset Coach": {
        "description": "Calm, mindful, and holistic. Focuses on breathing, longevity, consistency, and body-mind harmony.",
        "icon": "🧘"
    }
}

def get_system_instruction(profile, coach_style):
    """Generate the system instructions for the generative model based on profile and style."""
    profile_summary = f"""
    User Profile:
    - Name: {profile.get('name', 'User')}
    - Age: {profile.get('age', 'N/A')}
    - Gender: {profile.get('gender', 'N/A')}
    - Goal: {profile.get('goal', 'General Fitness')}
    - Fitness Level: {profile.get('fitness_level', 'Beginner')}
    - Equipment: {profile.get('equipment', 'None')}
    - Injuries/Limitations: {profile.get('injuries', 'None')}
    """
    
    style_instructions = ""
    if coach_style == "No-Excuses Drill Sergeant":
        style_instructions = """
        Your persona: You are a tough-love, high-energy, direct fitness drill sergeant (like David Goggins or Jocko Willink).
        Your style guidelines:
        - Use CAPS occasionally for strong emphasis, but don't yell continuously.
        - Emphasize discipline, consistency, and mental resilience over temporary motivation.
        - Refuse excuses. If they say they are tired, remind them that's when champions are built.
        - Keep your feedback punchy, action-oriented, and direct.
        - Address them as 'Soldier' or by their name.
        """
    elif coach_style == "Zen Mindset Coach":
        style_instructions = """
        Your persona: You are a calm, peaceful, wise lifestyle and movement coach (focusing on mindfulness, longevity, and posture).
        Your style guidelines:
        - Use gentle, serene, grounding, and respectful language.
        - Emphasize consistency, body awareness, deep breathing, and restorative recovery.
        - Encourage self-discovery, patience, and aligning physical exercise with mental clarity.
        - Suggest breathing techniques or light yoga stretching if they report feeling stressed or overwhelmed.
        - Focus on the journey rather than just the final number.
        """
    else: # "Empathetic Friend"
        style_instructions = """
        Your persona: You are an extremely supportive, empathetic, warm, and encouraging personal coach and best friend.
        Your style guidelines:
        - Be warm, conversational, friendly, and validate their feelings.
        - Highlight progress, congratulate small wins, and treat every step forward as a victory.
        - If they report a setback or skipped workout, validate that life happens, offer self-compassion, and focus on simple baby steps to resume.
        - Use encouraging emojis and positive reinforcement.
        """
        
    return f"""
    You are an expert AI Motivation Coach, trained in sports psychology and behavioral coaching.
    
    {profile_summary}
    
    {style_instructions}
    
    CRITICAL: Keep your responses highly conversational, tailored specifically to the user's details, and relatively concise (usually 1-3 paragraphs unless they ask for a detailed breakdown). Use markdown formatting for readability.
    """

def generate_pep_talk(profile, recent_logs, coach_style, api_key=None):
    """
    Generate a structured, personalized pep talk based on profile, recent progress, and coaching style.
    Returns a dictionary parsed from Gemini's JSON output.
    """
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("Gemini API Key is not set. Please provide it in settings or .env file.")
        
    genai.configure(api_key=key)
    
    # Process recent logs to provide context
    log_summary = "No workout logs available yet. They are just starting."
    if recent_logs:
        total_logs = len(recent_logs)
        scheduled = sum(l.get("workouts_scheduled", 0) for l in recent_logs)
        completed = sum(l.get("workouts_completed", 0) for l in recent_logs)
        completion_rate = round((completed / scheduled) * 100, 1) if scheduled > 0 else 0.0
        
        weights = [l["weight"] for l in recent_logs if l.get("weight") is not None]
        weight_change_str = ""
        if len(weights) >= 2:
            weight_change = round(weights[-1] - weights[0], 1)
            sign = "+" if weight_change > 0 else ""
            weight_change_str = f"Weight changed by {sign}{weight_change} kg over this period."
            
        log_summary = f"""
        Recent Progress Over {total_logs} logged days:
        - Workouts Scheduled: {scheduled}
        - Workouts Completed: {completed}
        - Completion Rate: {completion_rate}%
        {weight_change_str}
        """

    prompt = f"""
    You are an elite AI Motivation Coach.
    Generate a structured daily pep talk and mindset focus for the user based on their details:
    
    Name: {profile.get('name', 'User')}
    Age: {profile.get('age', 'N/A')}
    Goal: {profile.get('goal', 'General Fitness')}
    Fitness Level: {profile.get('fitness_level', 'Beginner')}
    Injuries/Limitations: {profile.get('injuries', 'None')}
    
    {log_summary}
    
    Coaching Style/Persona to adopt: {coach_style}
    
    Please provide the plan strictly formatted as a JSON object with the following schema:
    {{
      "title": "A short, catchy, inspiring focus title appropriate for the chosen persona (e.g. 'Embrace the Discomfort' or 'Healing Through Motion')",
      "quote": "A powerful quote (famous or customized by the coach style) matching today's focus.",
      "quote_author": "The author of the quote (use the coach style title like 'Coach Jocko', 'Zen Master', or a real person if appropriate).",
      "pep_talk": "The core pep talk. This should consist of 2-3 paragraphs of personalized, direct coaching. Reference their progress (praise consistency if high, troubleshoot respectfully or push discipline if low), and relate it to their core goal: {profile.get('goal', 'General Fitness')}. Avoid anything that aggravates their injuries: {profile.get('injuries', 'None')}.",
      "action_items": [
        "Action item 1 (mindset or minor physical task, e.g. 'Lay out your workout gear tonight')",
        "Action item 2 (e.g. 'Practice 2 minutes of mindful box breathing')",
        "Action item 3"
      ]
    }}
    """
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        pep_talk_dict = json.loads(response.text)
        return pep_talk_dict
        
    except json.JSONDecodeError as je:
        raise RuntimeError(f"Failed to parse AI pep talk response as JSON. Response text: {response.text}") from je
    except Exception as e:
        raise RuntimeError(f"Error during AI pep talk generation: {str(e)}") from e

def chat_with_motivation_agent(profile, chat_history, user_message, coach_style, api_key=None):
    """
    Handle multi-turn chat interaction with the user, incorporating system instructions
    tailored to the chosen coach style and user profile.
    """
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("Gemini API Key is not set. Please provide it in settings or .env file.")
        
    genai.configure(api_key=key)
    
    system_instruction = get_system_instruction(profile, coach_style)
    
    # Format the chat history for Gemini API (roles must be 'user' or 'model')
    gemini_history = []
    for msg in chat_history:
        role = "user" if msg["role"] == "user" else "model"
        gemini_history.append({"role": role, "parts": [msg["content"]]})
        
    try:
        # Initialize generative model with custom system instructions
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            system_instruction=system_instruction
        )
        
        # Start chat with loaded history
        chat = model.start_chat(history=gemini_history)
        response = chat.send_message(user_message)
        return response.text
        
    except Exception as e:
        raise RuntimeError(f"Error during chat interaction: {str(e)}") from e
