# utils/helpers.py
import streamlit as st

def format_time(seconds: int) -> str:
    """Converts seconds to MM:SS format."""
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"

def initialize_session_state_defaults():
    """Initializes session state with default values if not already set."""
    from configs.app_config import (
        DEFAULT_WORKOUT_DURATION, DEFAULT_REST_DURATION, PHASE_WORKOUT,
        # Updated to use JS sound defaults
        DEFAULT_WORKOUT_START_SOUND, DEFAULT_REST_START_SOUND, DEFAULT_SESSION_START_SOUND,
        DEFAULT_INSIGHTS_CHART_TYPE
    )

    # Timer settings
    if 'workout_duration' not in st.session_state:
        st.session_state.workout_duration = DEFAULT_WORKOUT_DURATION
    if 'rest_duration' not in st.session_state:
        st.session_state.rest_duration = DEFAULT_REST_DURATION
    if 'timer_running' not in st.session_state:
        st.session_state.timer_running = False
    if 'current_phase' not in st.session_state:
        st.session_state.current_phase = PHASE_WORKOUT
    if 'current_time' not in st.session_state:
        st.session_state.current_time = st.session_state.workout_duration

    # Stats
    if 'completed_rounds' not in st.session_state:
        st.session_state.completed_rounds = 0
    if 'accumulated_workout_seconds' not in st.session_state:
        st.session_state.accumulated_workout_seconds = 0
    if 'accumulated_rest_seconds' not in st.session_state:
        st.session_state.accumulated_rest_seconds = 0
    if 'session_stats_initialized_for_run' not in st.session_state:
        st.session_state.session_stats_initialized_for_run = False

    # Sound Settings (Using JS Defaults)
    if 'sound_on_workout_start' not in st.session_state:
        st.session_state.sound_on_workout_start = DEFAULT_WORKOUT_START_SOUND
    if 'sound_on_rest_start' not in st.session_state:
        st.session_state.sound_on_rest_start = DEFAULT_REST_START_SOUND
    if 'sound_on_session_start' not in st.session_state:
        st.session_state.sound_on_session_start = DEFAULT_SESSION_START_SOUND
    # New state variables for JS sound triggering
    if 'sound_to_play' not in st.session_state:
        st.session_state.sound_to_play = None
    if 'sound_trigger_count' not in st.session_state:
        st.session_state.sound_trigger_count = 0


    # Workout Schedule State
    if 'workout_schedule' not in st.session_state:
        st.session_state.workout_schedule = []
    if 'current_exercise_index' not in st.session_state:
        st.session_state.current_exercise_index = 0

    # Insights Chart Type State
    if 'insights_chart_type' not in st.session_state:
        st.session_state.insights_chart_type = DEFAULT_INSIGHTS_CHART_TYPE

    # --- AI Suggestion State for Add Workouts page ---
    if 'ai_workout_prompt' not in st.session_state: # For the AI text input
        st.session_state.ai_workout_prompt = ""
    if 'ai_generated_schedule_text' not in st.session_state: # For pre-filling the main text_area
        st.session_state.ai_generated_schedule_text = ""