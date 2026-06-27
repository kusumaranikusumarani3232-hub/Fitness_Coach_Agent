# FitCoach AI — Personalized AI Fitness, Nutrition & Motivation Coach

FitCoach AI is a premium, all-in-one personal health companion built with Python, Streamlit, and the Google Gemini API. It acts as an elite personal trainer, expert sports nutritionist, and mindset coach all rolled into one, tailoring routines and recipes around your body parameters, goals, equipment availability, and physical injuries.

---

## 🌟 Key Features

1. **📊 Interactive Dashboard**
   - Track key metrics at a glance: starting vs. current weight, BMI score, and average workout completion rate.
   - Visualizations powered by Plotly, including a **BMI Gauge Chart**, **Workout Completion Rate Bar Chart**, and a **Weight Progression Trend Line**.

2. **👤 User Profile Assessment**
   - Input your physical attributes (weight, height, age, gender).
   - Tailor constraints: specify fitness level, core goals (Weight Loss, Muscle Gain, etc.), available workout days/time, available equipment (None, Dumbbells, gym access), and physical injuries or limitations.

3. **🏋️ AI Workout Coach**
   - Generates a bespoke **7-day workout routine** using Gemini API.
   - Outputs daily focus, targeted warm-up routines, exercise sets, reps, rest durations, explanations, and cool-down routines.
   - Features an interactive checklist to mark off completed exercises and submit daily logs.

4. **🥗 AI Nutrition Guide**
   - Computes scientific daily macronutrient targets (Calories, Protein, Carbs, Fats, Hydration).
   - Recommends custom healthy recipes/meal options for breakfast, lunch, dinner, and snacks.
   - Outlines general sports nutrition rules based on your body composition goals.

5. **🔥 AI Motivation Coach**
   - Receive a customized **Mindset Pep Talk of the Day** that analyzes your profile and recent workout consistency.
   - Select a coaching persona:
     - 🤗 **Empathetic Friend**: Warm, encouraging, and understanding of setbacks.
     - ⚡ **No-Excuses Drill Sergeant**: High-energy, direct, focusing on mental toughness and discipline.
     - 🧘 **Zen Mindset Coach**: Calm, mindful, focusing on body awareness and longevity.
   - Chat in real-time with your selected coach style to get tips or address obstacles.

6. **📈 Progress Logger**
   - Manually record daily weight and workout completion rates to keep your progression logs up to date.

---

## 🛠️ Tech Stack & Architecture

- **Frontend Interface**: Streamlit (v1.30.0+)
- **Generative AI Core**: Google Gemini API (`gemini-2.5-flash` model via the `google-generativeai` SDK)
- **Data Analytics & Visualization**: Pandas & Plotly
- **Database**: SQLite (local database `data/fitcoach.db`)
- **Environment Management**: Python-dotenv

---

## 🚀 Getting Started

### Prerequisites
Make sure you have Python 3.9 or higher installed.

### 1. Clone & Navigate
```bash
cd fitness-coach-agent
```

### 2. Install Dependencies
Install all required libraries using the package manager:
```bash
pip install -r requirements.txt
```

### 3. Configure API Key
Get your Google Gemini API Key from [Google AI Studio](https://aistudio.google.com/). 

Create a `.env` file in the root directory and add your key:
```env
GEMINI_API_KEY="your_api_key_here"
```
*(Alternatively, you can input your Gemini API Key directly inside the app's sidebar during your session).*

### 4. Run the Application
Start the Streamlit local development server:
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser to start your fitness journey!

---

## 📁 Project Structure

```text
fitness-coach-agent/
├── data/                  # SQLite Database files (generated automatically)
├── app.py                 # Core Streamlit UI layout and controller
├── database.py            # SQLite schema initialization and DB operations
├── fitness_agent.py       # AI logic for generating workout plans
├── nutrition_agent.py     # AI logic for generating nutrition guides
├── motivational_agent.py  # AI logic for pep talks & interactive motivation coaching
├── progress_tracker.py    # Plotly visualization logic and BMI calculation
├── requirements.txt       # Project dependencies list
└── .env                   # Environment config (ignored in Git)
```
