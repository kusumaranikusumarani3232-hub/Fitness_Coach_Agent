import streamlit as st
import os
import datetime
import pandas as pd
from dotenv import load_dotenv

# Import our custom modules
import database as db
import fitness_agent as fa
import nutrition_agent as na
import progress_tracker as pt

# Load environment variables
load_dotenv()

# Initialize DB on application startup
db.init_db()

# --- Page Configuration ---
st.set_page_config(
    page_title="FitCoach AI - Personalized Fitness & Nutrition Agent",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Premium Custom Styling (Aesthetics) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

    /* Global fonts and background */
    html, body, [data-testid="stSidebar"] {
        font-family: 'Outfit', sans-serif;
    }

    /* Style titles & headers */
    .app-title {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 5px;
        background: linear-gradient(90deg, #FF4B4B 0%, #FF758C 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .app-subtitle {
        font-size: 1.2rem;
        color: #8892b0;
        margin-bottom: 30px;
    }
    
    .section-header {
        border-left: 5px solid #FF4B4B;
        padding-left: 15px;
        margin-top: 20px;
        margin-bottom: 20px;
        font-weight: 700;
        font-size: 1.8rem;
    }

    /* Premium Metric Card */
    .metric-card {
        background: linear-gradient(135deg, #1f2635 0%, #171c26 100%);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.20);
        text-align: center;
        transition: all 0.3s ease;
        margin-bottom: 15px;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 25px rgba(255, 75, 75, 0.15);
        border-color: rgba(255, 75, 75, 0.25);
    }
    
    .metric-title {
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #8892b0;
        font-weight: 600;
        margin-bottom: 8px;
    }
    
    .metric-value {
        font-size: 28px;
        font-weight: 800;
        color: #FF4B4B;
    }
    
    .metric-subtitle {
        font-size: 12px;
        color: #5c6680;
        margin-top: 5px;
    }

    /* Custom sidebar header */
    .sidebar-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    /* Styled tags/badges */
    .badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 5px;
        color: #ffffff;
    }
    .badge-primary { background-color: #FF4B4B; }
    .badge-secondary { background-color: #34495e; }
    
    /* Clean container panels */
    .panel-box {
        background-color: #151a24;
        border-radius: 10px;
        padding: 20px;
        border: 1px solid rgba(255,255,255,0.03);
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Configuration & Credentials ---
with st.sidebar:
    st.markdown('<div class="sidebar-header">🏋️ FitCoach AI</div>', unsafe_allow_html=True)
    
    # Navigation Choice
    menu_options = [
        "📊 Dashboard", 
        "👤 User Profile", 
        "🏋️ AI Workout Coach", 
        "🥗 Nutrition Suggestions", 
        "📈 Log Progress"
    ]
    choice = st.radio("Navigate", menu_options)
    
    st.markdown("---")
    
    # API Key Configuration
    st.markdown("### 🔑 API Authentication")
    env_api_key = os.getenv("GEMINI_API_KEY")
    
    if env_api_key:
        st.success("API key loaded from system.")
        api_key = env_api_key
    else:
        user_key = st.text_input("Enter Gemini API Key", type="password", help="Create a key at https://aistudio.google.com/")
        if user_key:
            api_key = user_key
            st.success("API key set for session.")
        else:
            st.warning("Please provide a Gemini API Key to enable AI coaching features.")
            api_key = None

    st.markdown("---")
    st.markdown("<div style='font-size: 11px; color: #5c6680; text-align: center;'>FitCoach AI © 2026<br>Powered by Gemini 1.5 Flash</div>", unsafe_allow_html=True)

# Load profile data from Database
profile = db.get_profile()

# Helper function to generate clean summary metric cards
def render_metric_card(title, value, subtitle=""):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# PAGE: DASHBOARD
# ==========================================
if choice == "📊 Dashboard":
    st.markdown('<div class="app-title">FitCoach AI Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-subtitle">Welcome back! Here is a summary of your active metrics, goals, and weekly progress.</div>', unsafe_allow_html=True)
    
    if not profile:
        st.info("👋 Welcome to FitCoach AI! To get started, please navigate to **👤 User Profile** and complete your assessment form.")
        # Show an example dashboard layout for illustration
        col1, col2, col3 = st.columns(3)
        with col1:
            render_metric_card("Current Weight", "N/A", "Complete your profile first")
        with col2:
            render_metric_card("BMI Score", "N/A", "Requires height & weight")
        with col3:
            render_metric_card("Active Goal", "N/A", "Awaiting assessment")
    else:
        # Dashboard contents
        weight = profile.get("weight")
        height = profile.get("height")
        goal = profile.get("goal")
        name = profile.get("name")
        fitness_level = profile.get("fitness_level")
        
        # Calculate BMI
        bmi, bmi_category, bmi_color = pt.calculate_bmi(weight, height)
        
        # Fetch progress logs
        logs = db.get_progress_logs()
        
        # Streak / logs count
        total_logs = len(logs)
        last_logged_weight = weight
        if logs:
            valid_weights = [l["weight"] for l in logs if l.get("weight") is not None]
            if valid_weights:
                last_logged_weight = valid_weights[-1]
                
            # Basic completion rate averages
            scheduled_totals = sum(l.get("workouts_scheduled", 0) for l in logs)
            completed_totals = sum(l.get("workouts_completed", 0) for l in logs)
            avg_completion = round((completed_totals / scheduled_totals) * 100, 1) if scheduled_totals > 0 else 0.0
        else:
            avg_completion = 0.0

        # Render top header metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            render_metric_card("User Name", name, f"Level: {fitness_level}")
        with col2:
            render_metric_card("Current Weight", f"{last_logged_weight} kg", f"Starting: {weight} kg")
        with col3:
            render_metric_card("BMI Status", f"{bmi}", f"{bmi_category}")
        with col4:
            render_metric_card("Avg. Completion", f"{avg_completion}%", f"Total logs: {total_logs}")
            
        st.markdown("---")
        
        # Charts section
        col_c1, col_c2 = st.columns([1, 1])
        
        with col_c1:
            st.markdown('<div class="section-header">⚖️ BMI Analysis</div>', unsafe_allow_html=True)
            bmi_fig = pt.get_bmi_gauge_chart(bmi)
            st.plotly_chart(bmi_fig, use_container_width=True)
            st.markdown(f"""
            <div class="panel-box" style="text-align: center;">
                Your BMI is <strong>{bmi}</strong>, placing you in the <span style="color: {bmi_color}; font-weight: bold;">{bmi_category}</span> range.
                Keep up the good work to align with your goal of <strong>{goal}</strong>!
            </div>
            """, unsafe_allow_html=True)
            
        with col_c2:
            st.markdown('<div class="section-header">🏋️ Activity & Completion</div>', unsafe_allow_html=True)
            completion_fig = pt.get_workout_completion_chart()
            if completion_fig:
                st.plotly_chart(completion_fig, use_container_width=True)
            else:
                st.info("No workout logs available yet. Complete your workouts in the 'AI Workout Coach' page or submit them manually in 'Log Progress' to view charts.")
                
        st.markdown("---")
        st.markdown('<div class="section-header">📈 Weight Progression</div>', unsafe_allow_html=True)
        weight_fig = pt.get_weight_trend_chart()
        if weight_fig:
            st.plotly_chart(weight_fig, use_container_width=True)
        else:
            st.info("No weight logs available yet. Log your weight daily in the 'Log Progress' page to visualize your trends.")

# ==========================================
# PAGE: USER PROFILE
# ==========================================
elif choice == "👤 User Profile":
    st.markdown('<div class="app-title">User Profile Assessment</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-subtitle">Please input your current details. FitCoach AI uses these metrics to tailor workouts and meal plans.</div>', unsafe_allow_html=True)
    
    # Seed default values based on active DB profile
    d_name = profile.get("name", "") if profile else ""
    d_age = int(profile.get("age", 25)) if profile else 25
    d_gender = profile.get("gender", "Male") if profile else "Male"
    d_height = float(profile.get("height", 170.0)) if profile else 170.0
    d_weight = float(profile.get("weight", 70.0)) if profile else 70.0
    d_level = profile.get("fitness_level", "Beginner") if profile else "Beginner"
    d_goal = profile.get("goal", "General Fitness") if profile else "General Fitness"
    d_days = int(profile.get("workout_days", 3)) if profile else 3
    d_time = int(profile.get("time_per_session", 45)) if profile else 45
    d_equip = profile.get("equipment", "None") if profile else "None"
    d_injuries = profile.get("injuries", "") if profile else ""

    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name", value=d_name, placeholder="e.g. John Doe")
            age = st.number_input("Age", min_value=1, max_value=120, value=d_age)
            gender = st.selectbox("Gender", ["Male", "Female", "Non-Binary", "Prefer not to say"], index=["Male", "Female", "Non-Binary", "Prefer not to say"].index(d_gender))
            height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=d_height, step=0.1)
            weight = st.number_input("Weight (kg)", min_value=10.0, max_value=300.0, value=d_weight, step=0.1)
            
        with col2:
            fitness_level = st.selectbox(
                "Fitness Level", 
                ["Beginner", "Intermediate", "Advanced"],
                index=["Beginner", "Intermediate", "Advanced"].index(d_level)
            )
            goal = st.selectbox(
                "Primary Fitness Goal", 
                ["Weight Loss", "Muscle Gain", "Strength", "Endurance", "General Fitness"],
                index=["Weight Loss", "Muscle Gain", "Strength", "Endurance", "General Fitness"].index(d_goal)
            )
            workout_days = st.slider("Available Workout Days Per Week", min_value=1, max_value=7, value=d_days)
            time_per_session = st.slider("Available Time Per Session (minutes)", min_value=15, max_value=120, value=d_time, step=5)
            
            # Map equipment inputs
            equip_options = ["None", "Dumbbells", "Resistance Bands", "Gym Access"]
            equipment = st.selectbox(
                "Equipment Available", 
                equip_options,
                index=equip_options.index(d_equip) if d_equip in equip_options else 0
            )
            
            injuries = st.text_area("Any Injuries or Physical Limitations?", value=d_injuries, placeholder="e.g. Knee pain, Lower back discomfort, shoulder stiffness, or None")

        submit_btn = st.form_submit_button("Save Profile Settings")
        
        if submit_btn:
            if not name.strip():
                st.error("Please enter your name.")
            else:
                profile_data = {
                    "name": name,
                    "age": age,
                    "gender": gender,
                    "height": height,
                    "weight": weight,
                    "fitness_level": fitness_level,
                    "goal": goal,
                    "workout_days": workout_days,
                    "time_per_session": time_per_session,
                    "equipment": equipment,
                    "injuries": injuries if injuries.strip() else "None"
                }
                
                db.save_profile(profile_data)
                st.success("🎉 User profile updated successfully! You can now generate your custom workout plan.")
                
                # Automatically log starting weight as initial progress log if empty
                today_str = datetime.date.today().strftime("%Y-%m-%d")
                db.log_progress(today_str, weight=weight)
                
                # Force reload profile from database
                st.rerun()

# ==========================================
# PAGE: AI WORKOUT COACH
# ==========================================
elif choice == "🏋️ AI Workout Coach":
    st.markdown('<div class="app-title">FitCoach AI Workout Coach</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-subtitle">Generate, view, and interact with your custom workout planner. Check off exercises as you complete them.</div>', unsafe_allow_html=True)
    
    if not profile:
        st.warning("⚠️ Please complete your profile assessment first in the **👤 User Profile** tab.")
    else:
        # Check if we have a saved plan
        active_plan = db.get_latest_workout_plan()
        
        # Display trigger buttons
        col_btn1, col_btn2 = st.columns([2, 1])
        
        with col_btn1:
            if active_plan:
                st.info("💡 You have an active workout plan. You can view it below or re-generate a new one if your goals have changed.")
            else:
                st.warning("You do not have an active workout plan. Click below to generate your personalized routine.")
                
        with col_btn2:
            if not api_key:
                st.error("Provide a Gemini API Key in the sidebar to generate a plan.")
            else:
                btn_txt = "🔄 Regenerate Workout Plan" if active_plan else "🚀 Generate AI Workout Plan"
                if st.button(btn_txt, type="primary"):
                    with st.spinner("🏋️ Designing your fitness routine... Please hold on."):
                        try:
                            # Generate using our agent
                            new_plan = fa.generate_workout_plan(profile, api_key=api_key)
                            # Save to SQLite
                            db.save_workout_plan(new_plan)
                            st.success("🎉 New workout routine generated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to generate workout plan: {str(e)}")
                            
        # If we have an active plan, render it!
        if active_plan:
            st.markdown("---")
            
            # 1. Summary Box
            st.markdown('<div class="section-header">📜 Coach\'s Summary & Focus</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="panel-box">{active_plan.get("summary", "No summary provided.")}</div>', unsafe_allow_html=True)
            
            # 2. Safety Tips
            st.markdown('<div class="section-header">🛡️ Safety & Form Recommendations</div>', unsafe_allow_html=True)
            safety_html = "".join([f"<li>{tip}</li>" for tip in active_plan.get("safety_tips", [])])
            if safety_html:
                st.markdown(f'<div class="panel-box" style="border-left: 5px solid #FF4B4B;"><ul>{safety_html}</ul></div>', unsafe_allow_html=True)
            else:
                st.info("No explicit safety recommendations included.")
                
            # 3. Weekly Planner and Tracker
            st.markdown('<div class="section-header">📅 7-Day Workout Routine & Tracker</div>', unsafe_allow_html=True)
            st.write("Select a day below, perform the workout, and mark exercises as completed. Make sure to log your progress when done!")
            
            schedule = active_plan.get("schedule", {})
            days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            
            # Let's create tabs for Monday-Sunday
            tabs = st.tabs(days_of_week)
            
            for index, day in enumerate(days_of_week):
                with tabs[index]:
                    day_data = schedule.get(day, {})
                    
                    if not day_data:
                        st.info("No plan generated for this day.")
                        continue
                        
                    is_rest = day_data.get("rest_day", False)
                    focus = day_data.get("focus", "Rest / Active Recovery")
                    duration = day_data.get("duration_minutes", 0)
                    
                    # Display header for the day
                    st.markdown(f"### {day} - {focus}")
                    if is_rest:
                        st.success("🍵 Rest Day / Active Recovery. Let your body heal, hydrate well, and perform light stretching.")
                        warmup = day_data.get("warmup", [])
                        if warmup:
                            st.markdown("**Suggested recovery routines:**")
                            for w in warmup:
                                st.markdown(f"- {w}")
                    else:
                        st.markdown(f"⏱️ **Duration**: {duration} minutes | 🏋️ **Goal Focus**: {focus}")
                        
                        col_w, col_c = st.columns(2)
                        with col_w:
                            st.markdown("##### 🧘 Warm-up Routine")
                            for w in day_data.get("warmup", []):
                                st.markdown(f"- {w}")
                        with col_c:
                            st.markdown("##### ❄️ Cool-down Routine")
                            for c in day_data.get("cooldown", []):
                                st.markdown(f"- {c}")
                                
                        st.markdown("---")
                        st.markdown("##### 💪 Exercise Checklist")
                        
                        exercises = day_data.get("exercises", [])
                        
                        if not exercises:
                            st.write("No exercises defined for today.")
                        else:
                            # Create checkbox for each exercise
                            checked_statuses = []
                            for idx, ex in enumerate(exercises):
                                ex_name = ex.get("name", "Exercise")
                                ex_sets = ex.get("sets", 3)
                                ex_reps = ex.get("reps", 10)
                                ex_rest = ex.get("rest", "60s")
                                ex_why = ex.get("explanation", "")
                                
                                # Visual card formatting for the exercise
                                with st.container():
                                    st.markdown(f"""
                                    <div style='background-color:#1c2431; padding:12px; border-radius:8px; margin-bottom:8px;'>
                                        <strong>{ex_name}</strong> - {ex_sets} sets x {ex_reps} reps (Rest: {ex_rest})<br>
                                        <small style='color: #8892b0;'>{ex_why}</small>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # unique state key
                                    state_key = f"chk_{day}_{idx}"
                                    is_checked = st.checkbox("Mark as completed", key=state_key)
                                    checked_statuses.append(is_checked)
                                    
                            st.markdown("---")
                            
                            # Logging execution rate
                            completed_count = sum(checked_statuses)
                            total_count = len(exercises)
                            
                            # Log progress trigger
                            if st.button(f"💾 Submit Workout Logs for {day}", key=f"btn_log_{day}"):
                                today_str = datetime.date.today().strftime("%Y-%m-%d")
                                db.log_progress(
                                    date_str=today_str, 
                                    weight=None, # Weight isn't gathered from workout plan tab
                                    completed=completed_count, 
                                    scheduled=total_count
                                )
                                st.success(f"💪 Logged {completed_count}/{total_count} exercises completed on {today_str} ({round((completed_count/total_count)*100, 1)}%)!")
                                st.balloons()

# ==========================================
# PAGE: NUTRITION SUGGESTIONS
# ==========================================
elif choice == "🥗 Nutrition Suggestions":
    st.markdown('<div class="app-title">FitCoach AI Nutrition Guide</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-subtitle">Personalized daily macronutrient recommendations, hydration standards, and healthy meal options.</div>', unsafe_allow_html=True)
    
    if not profile:
        st.warning("⚠️ Please complete your profile assessment first in the **👤 User Profile** tab.")
    else:
        active_nutrition = db.get_latest_nutrition_plan()
        
        # Display trigger buttons
        col_btn1, col_btn2 = st.columns([2, 1])
        
        with col_btn1:
            if active_nutrition:
                st.info("💡 You have an active nutrition plan. You can view it below or re-generate if your physical attributes change.")
            else:
                st.warning("You do not have an active nutrition guide. Click below to generate your personalized meal suggestions.")
                
        with col_btn2:
            if not api_key:
                st.error("Provide a Gemini API Key in the sidebar to generate a plan.")
            else:
                btn_txt = "🔄 Regenerate Nutrition Plan" if active_nutrition else "🚀 Generate AI Nutrition Plan"
                if st.button(btn_txt, type="primary"):
                    with st.spinner("🥗 Calculating macro targets and recipes..."):
                        try:
                            # Generate using nutrition agent
                            new_nut = na.generate_nutrition_plan(profile, api_key=api_key)
                            # Save to SQLite
                            db.save_nutrition_plan(new_nut)
                            st.success("🎉 New nutrition guide generated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to generate nutrition plan: {str(e)}")
                            
        # If we have an active nutrition plan, render it!
        if active_nutrition:
            st.markdown("---")
            
            # 1. Summary Box
            st.markdown('<div class="section-header">🥗 Dietitian Coaching Overview</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="panel-box">{active_nutrition.get("summary", "No summary provided.")}</div>', unsafe_allow_html=True)
            
            # 2. Daily Targets (Macros + Hydration)
            st.markdown('<div class="section-header">🎯 Daily Nutrient & Hydration Targets</div>', unsafe_allow_html=True)
            targets = active_nutrition.get("daily_targets", {})
            
            col_t1, col_t2, col_t3, col_t4, col_t5 = st.columns(5)
            with col_t1:
                render_metric_card("Calories", targets.get("calories", "N/A"), "Target energy intake")
            with col_t2:
                render_metric_card("Protein", targets.get("protein", "N/A"), "Muscle recovery")
            with col_t3:
                render_metric_card("Carbohydrates", targets.get("carbs", "N/A"), "Sustained energy")
            with col_t4:
                render_metric_card("Healthy Fats", targets.get("fats", "N/A"), "Hormonal balance")
            with col_t5:
                render_metric_card("Daily Water", targets.get("water", "N/A"), "Hydration goal")
                
            st.markdown("---")
            
            # 3. Healthy Meal Ideas
            st.markdown('<div class="section-header">🍳 Custom Healthy Recipes & Meal Plan</div>', unsafe_allow_html=True)
            meals = active_nutrition.get("meal_ideas", {})
            
            meal_types = ["breakfast", "lunch", "dinner", "snacks"]
            meal_tabs = st.tabs([m.capitalize() for m in meal_types])
            
            for index, m_type in enumerate(meal_types):
                with meal_tabs[index]:
                    list_meals = meals.get(m_type, [])
                    if not list_meals:
                        st.info(f"No recipe recommendations for {m_type}.")
                    else:
                        for idx, meal in enumerate(list_meals):
                            name = meal.get("name", "Meal Option")
                            desc = meal.get("description", "")
                            ingredients = meal.get("ingredients", [])
                            calories = meal.get("calories", "N/A")
                            protein = meal.get("protein", "N/A")
                            
                            st.markdown(f"#### {idx + 1}. {name}")
                            st.write(desc)
                            
                            # Metrics for calories & protein
                            st.markdown(f"""
                            <span class="badge badge-primary">🔥 {calories}</span>
                            <span class="badge badge-secondary">🥚 Protein: {protein}</span>
                            """, unsafe_allow_html=True)
                            
                            st.markdown("**Key Ingredients:**")
                            ing_list = "".join([f"<li>{ing}</li>" for ing in ingredients])
                            st.markdown(f"<ul>{ing_list}</ul>", unsafe_allow_html=True)
                            st.markdown("---")
                            
            # 4. General Recommendations
            st.markdown('<div class="section-header">💡 General Nutrition Rules</div>', unsafe_allow_html=True)
            tips = active_nutrition.get("general_recommendations", [])
            tips_html = "".join([f"<li>{tip}</li>" for tip in tips])
            if tips_html:
                st.markdown(f'<div class="panel-box"><ul>{tips_html}</ul></div>', unsafe_allow_html=True)

# ==========================================
# PAGE: LOG PROGRESS
# ==========================================
elif choice == "📈 Log Progress":
    st.markdown('<div class="app-title">Log Today\'s Progress</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-subtitle">Log your daily weight updates and workout metrics manually. Plots on the Dashboard refresh automatically.</div>', unsafe_allow_html=True)
    
    col_l1, col_l2 = st.columns([1, 1])
    
    with col_l1:
        st.markdown('<div class="section-header">📝 Daily Tracker Entry Form</div>', unsafe_allow_html=True)
        with st.form("manual_progress_form"):
            log_date = st.date_input("Date", value=datetime.date.today())
            
            # Default weight from profile
            def_weight = float(profile.get("weight", 70.0)) if profile else 70.0
            
            weight_val = st.number_input("Current Weight (kg)", min_value=10.0, max_value=300.0, value=def_weight, step=0.1, help="Leave unchanged if not weighing today")
            
            completed_ex = st.number_input("Workouts/Exercises Completed", min_value=0, max_value=50, value=0)
            scheduled_ex = st.number_input("Workouts/Exercises Scheduled", min_value=0, max_value=50, value=0)
            
            submit_log = st.form_submit_button("Record Progress Entry")
            
            if submit_log:
                date_str = log_date.strftime("%Y-%m-%d")
                db.log_progress(
                    date_str=date_str, 
                    weight=weight_val, 
                    completed=completed_ex, 
                    scheduled=scheduled_ex
                )
                st.success(f"🎉 Progress recorded successfully for {date_str}!")
                st.balloons()
                
    with col_l2:
        st.markdown('<div class="section-header">📋 Log History</div>', unsafe_allow_html=True)
        logs = db.get_progress_logs()
        if not logs:
            st.info("No logs present in the local database. Start entry manually or via workouts.")
        else:
            df = pd.DataFrame(logs)
            # clean date parsing and columns order
            df = df.rename(columns={
                "log_date": "Date",
                "weight": "Weight (kg)",
                "workouts_completed": "Completed Exercises",
                "workouts_scheduled": "Scheduled Exercises",
                "completion_percentage": "Completion %"
            })
            # display table sorted by newest first
            st.dataframe(
                df[["Date", "Weight (kg)", "Completed Exercises", "Scheduled Exercises", "Completion %"]].sort_values("Date", ascending=False),
                use_container_width=True,
                hide_index=True
            )
