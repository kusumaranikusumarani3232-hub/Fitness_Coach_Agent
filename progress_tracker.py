import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database import get_progress_logs

def calculate_bmi(weight_kg, height_cm):
    """Calculate BMI and return classification with color."""
    if not weight_kg or not height_cm or height_cm <= 0:
        return 0, "Unknown", "gray"
        
    height_m = height_cm / 100.0
    bmi = round(weight_kg / (height_m ** 2), 1)
    
    if bmi < 18.5:
        category = "Underweight"
        color = "#3498db" # Blue
    elif 18.5 <= bmi < 25.0:
        category = "Normal Weight"
        color = "#2ecc71" # Green
    elif 25.0 <= bmi < 30.0:
        category = "Overweight"
        color = "#f39c12" # Orange
    else:
        category = "Obese"
        color = "#e74c3c" # Red
        
    return bmi, category, color

def get_weight_trend_chart():
    """Generate a Plotly chart showing weight logs over time."""
    logs = get_progress_logs()
    if not logs:
        return None
        
    # Filter logs where weight is logged
    valid_logs = [log for log in logs if log.get("weight") is not None]
    if not valid_logs:
        return None
        
    df = pd.DataFrame(valid_logs)
    df["log_date"] = pd.to_datetime(df["log_date"])
    df = df.sort_values("log_date")
    
    fig = px.line(
        df, 
        x="log_date", 
        y="weight", 
        markers=True,
        title="Weight Progression Over Time",
        labels={"weight": "Weight (kg)", "log_date": "Date"},
        template="plotly_dark"
    )
    
    fig.update_traces(
        line=dict(color="#FF4B4B", width=3),
        marker=dict(size=8, color="#0E1117", line=dict(color="#FF4B4B", width=2))
    )
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Outfit, Inter, sans-serif"),
        title_font=dict(size=18, color="#ffffff"),
        xaxis=dict(showgrid=False, color="#888888"),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)", color="#888888")
    )
    
    return fig

def get_workout_completion_chart():
    """Generate a Plotly bar chart showing workout completion percentage."""
    logs = get_progress_logs()
    if not logs:
        return None
        
    # Filter logs where scheduling happened
    valid_logs = [log for log in logs if log.get("workouts_scheduled", 0) > 0]
    if not valid_logs:
        return None
        
    df = pd.DataFrame(valid_logs)
    df["log_date"] = pd.to_datetime(df["log_date"])
    df = df.sort_values("log_date")
    
    fig = px.bar(
        df, 
        x="log_date", 
        y="completion_percentage",
        title="Workout Completion Rates",
        labels={"completion_percentage": "Completion (%)", "log_date": "Date"},
        template="plotly_dark"
    )
    
    fig.update_traces(
        marker_color="#2ecc71",
        marker_line_color="#1abc9c",
        marker_line_width=1.5,
        opacity=0.85
    )
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Outfit, Inter, sans-serif"),
        title_font=dict(size=18, color="#ffffff"),
        xaxis=dict(showgrid=False, color="#888888"),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)", range=[0, 105], color="#888888")
    )
    
    return fig

def get_bmi_gauge_chart(bmi):
    """Generate a Plotly gauge chart for BMI."""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = bmi,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Body Mass Index (BMI)", 'font': {'size': 18, 'color': "#ffffff"}},
        gauge = {
            'axis': {'range': [10, 40], 'tickcolor': "#ffffff"},
            'bar': {'color': "#FF4B4B"},
            'bgcolor': "rgba(255,255,255,0.1)",
            'borderwidth': 2,
            'bordercolor': "#ffffff",
            'steps': [
                {'range': [10, 18.5], 'color': 'rgba(52, 152, 219, 0.4)'}, # Underweight - Blue
                {'range': [18.5, 25.0], 'color': 'rgba(46, 204, 113, 0.4)'}, # Normal - Green
                {'range': [25.0, 30.0], 'color': 'rgba(243, 156, 18, 0.4)'}, # Overweight - Orange
                {'range': [30.0, 40.0], 'color': 'rgba(231, 76, 60, 0.4)'}  # Obese - Red
            ]
        }
    ))
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "#ffffff", 'family': "Outfit, Inter, sans-serif"},
        height=250,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig
