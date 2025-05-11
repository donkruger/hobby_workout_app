# workout_app/pages/1_🏋️‍♂️_Add_workouts.py
import streamlit as st
from utils.helpers import initialize_session_state_defaults
from ui.sidebar_controls import render_sidebar_controls
from ai_components.workout_generator import get_ai_workout_suggestions
from configs.app_config import DEFAULT_WORKOUT_DURATION, DEFAULT_REST_DURATION # For defaults

# --- Page Configuration ---
st.set_page_config(
    page_title="Add Workouts",
    page_icon="🏋️‍♂️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Initialize Session State & Render Sidebar ---
initialize_session_state_defaults() 
render_sidebar_controls()

# --- Callback Function for AI Suggestions ---
def handle_ai_suggestions():
    user_description = st.session_state.ai_workout_prompt_input
    if user_description:
        # Get current workout and rest durations from session state (set by sidebar)
        workout_duration = st.session_state.get('workout_duration', DEFAULT_WORKOUT_DURATION)
        rest_duration = st.session_state.get('rest_duration', DEFAULT_REST_DURATION)
        
        with st.spinner("🤖 Crafting your workout plan..."):
            suggestions = get_ai_workout_suggestions(
                user_description,
                workout_duration,
                rest_duration
            ) 
        
        if suggestions:
            st.session_state.ai_generated_schedule_text = "\n".join(suggestions)
            st.success("AI suggestions loaded into the editor below! Review and save.")
            st.session_state.ai_workout_prompt_input = "" 
        else:
            st.session_state.ai_generated_schedule_text = ""
    else:
        st.warning("Please describe the workout you'd like suggestions for.", icon="⚠️")

# --- Page Content ---
st.title("➕ Add or Generate Workouts")
st.write("""
    Describe your desired workout, including total time (e.g., "10 minute core workout"), 
    and let AI suggest exercises based on your current timer settings!
    Or, enter your own exercises manually below.
""")

# --- AI Suggestion Section ---
st.markdown("---")
st.subheader("🤖 Get AI Workout Suggestions")

current_w_duration = st.session_state.get('workout_duration', DEFAULT_WORKOUT_DURATION)
current_r_duration = st.session_state.get('rest_duration', DEFAULT_REST_DURATION)
st.caption(f"Current timer settings: {current_w_duration}s work / {current_r_duration}s rest per exercise.")

st.text_input(
    "Describe your desired workout:",
    key="ai_workout_prompt_input",
    placeholder="e.g., 20 minute full body, no equipment"
)

st.button(
    "✨ Get AI Suggestions",
    on_click=handle_ai_suggestions,
    key="get_ai_suggestions_button",
    use_container_width=True
)

st.markdown("---")
st.subheader("✍️ Your Workout List Editor")
st.write("Enter each exercise on a new line. This schedule will loop when you use the timer.")

default_text_area_value = st.session_state.get('ai_generated_schedule_text', "") \
                           if st.session_state.get('ai_generated_schedule_text') \
                           else "\n".join(st.session_state.get('workout_schedule', []))

new_schedule_text = st.text_area(
    "Exercises (one per line):",
    value=default_text_area_value,
    height=250,
    key="manual_schedule_text_area",
    placeholder="Example:\nPush-ups\nSquats\nPlank\nJumping Jacks\nBurpees"
)

col1, col2 = st.columns(2)
with col1:
    if st.button("💾 Save Workout List", use_container_width=True, key="save_workout_button"):
        current_text_area_content = st.session_state.manual_schedule_text_area 
        updated_schedule = [line.strip() for line in current_text_area_content.splitlines() if line.strip()]
        
        st.session_state.workout_schedule = updated_schedule
        st.session_state.current_exercise_index = 0
        st.session_state.ai_generated_schedule_text = "" 
        st.toast("Workout list saved!", icon="✅")
        st.success("Workout list updated successfully!")
        
        if updated_schedule:
            st.write("Current Saved Workout List:")
            for i, exercise in enumerate(updated_schedule):
                st.write(f"{i+1}. {exercise}")
        else:
            st.info("Your workout list is currently empty.")

with col2:
    if st.button("⏱️ Go to Timer", use_container_width=True, key="go_to_timer_page_button"):
        try:
            st.switch_page("Home.py")
        except Exception as e:
            st.error(f"Navigation error: {e}")
            st.info("Please use the sidebar to navigate to 'Home'.")

st.markdown("---")