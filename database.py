import os
import sqlite3
import json
from datetime import datetime

DB_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_PATH = os.path.join(DB_DIR, "fitcoach.db")

def get_connection():
    """Establish database connection."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database schema."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. User Profile Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        gender TEXT,
        height REAL,
        weight REAL,
        fitness_level TEXT,
        goal TEXT,
        workout_days INTEGER,
        time_per_session INTEGER,
        equipment TEXT,
        injuries TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 2. Workout Plans Table (stores the full AI response and metadata)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS workout_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plan_json TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 2b. Nutrition Plans Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS nutrition_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plan_json TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 3. Progress Logs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS progress_logs (
        log_date TEXT PRIMARY KEY,
        weight REAL,
        workouts_completed INTEGER DEFAULT 0,
        workouts_scheduled INTEGER DEFAULT 0,
        completion_percentage REAL DEFAULT 0.0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()

def save_profile(profile_dict):
    """Save or update user profile (single user assumption, ID = 1)."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if profile already exists
    cursor.execute("SELECT id FROM user_profiles WHERE id = 1")
    exists = cursor.fetchone()
    
    if exists:
        cursor.execute("""
        UPDATE user_profiles
        SET name = ?, age = ?, gender = ?, height = ?, weight = ?,
            fitness_level = ?, goal = ?, workout_days = ?,
            time_per_session = ?, equipment = ?, injuries = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = 1
        """, (
            profile_dict.get("name"),
            profile_dict.get("age"),
            profile_dict.get("gender"),
            profile_dict.get("height"),
            profile_dict.get("weight"),
            profile_dict.get("fitness_level"),
            profile_dict.get("goal"),
            profile_dict.get("workout_days"),
            profile_dict.get("time_per_session"),
            profile_dict.get("equipment"),
            profile_dict.get("injuries")
        ))
    else:
        cursor.execute("""
        INSERT INTO user_profiles (
            id, name, age, gender, height, weight, fitness_level,
            goal, workout_days, time_per_session, equipment, injuries
        ) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            profile_dict.get("name"),
            profile_dict.get("age"),
            profile_dict.get("gender"),
            profile_dict.get("height"),
            profile_dict.get("weight"),
            profile_dict.get("fitness_level"),
            profile_dict.get("goal"),
            profile_dict.get("workout_days"),
            profile_dict.get("time_per_session"),
            profile_dict.get("equipment"),
            profile_dict.get("injuries")
        ))
    
    conn.commit()
    conn.close()

def get_profile():
    """Retrieve the user profile if exists."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_profiles WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None

def save_workout_plan(plan_dict):
    """Save generated workout plan."""
    conn = get_connection()
    cursor = conn.cursor()
    plan_json = json.dumps(plan_dict)
    cursor.execute("INSERT INTO workout_plans (plan_json) VALUES (?)", (plan_json,))
    conn.commit()
    conn.close()

def get_latest_workout_plan():
    """Retrieve the latest workout plan."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT plan_json FROM workout_plans ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return json.loads(row["plan_json"])
    return None

def save_nutrition_plan(plan_dict):
    """Save generated nutrition plan."""
    conn = get_connection()
    cursor = conn.cursor()
    plan_json = json.dumps(plan_dict)
    cursor.execute("INSERT INTO nutrition_plans (plan_json) VALUES (?)", (plan_json,))
    conn.commit()
    conn.close()

def get_latest_nutrition_plan():
    """Retrieve the latest nutrition plan."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT plan_json FROM nutrition_plans ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return json.loads(row["plan_json"])
    return None


def log_progress(date_str, weight=None, completed=0, scheduled=0):
    """Log or update progress for a specific day."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Calculate percentage
    pct = 0.0
    if scheduled > 0:
        pct = round((completed / scheduled) * 100, 1)
        
    # Check if log already exists for this date
    cursor.execute("SELECT weight, workouts_completed, workouts_scheduled FROM progress_logs WHERE log_date = ?", (date_str,))
    exists = cursor.fetchone()
    
    if exists:
        # Keep old weight if not provided
        w = weight if weight is not None else exists["weight"]
        cursor.execute("""
        UPDATE progress_logs
        SET weight = ?, workouts_completed = ?, workouts_scheduled = ?,
            completion_percentage = ?, updated_at = CURRENT_TIMESTAMP
        WHERE log_date = ?
        """, (w, completed, scheduled, pct, date_str))
    else:
        cursor.execute("""
        INSERT INTO progress_logs (log_date, weight, workouts_completed, workouts_scheduled, completion_percentage)
        VALUES (?, ?, ?, ?, ?)
        """, (date_str, weight, completed, scheduled, pct))
        
    conn.commit()
    conn.close()

def get_progress_logs():
    """Retrieve all progress logs sorted by date."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM progress_logs ORDER BY log_date ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
