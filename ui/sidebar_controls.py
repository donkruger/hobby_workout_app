# ui/sidebar_controls.py
import streamlit as st
# Updated imports: Using JS_SOUND_OPTIONS
from configs.app_config import SLIDER_OPTIONS, JS_SOUND_OPTIONS, INSIGHTS_CHART_OPTIONS

def render_sidebar_controls():
    """
    Renders Streamlit sliders in the sidebar for workout and rest durations,
    sound selection (now using JS sounds), and insights chart type selection.
    """
    st.sidebar.header("⚙️ Timer Settings")

    # Timer Duration Sliders
    workout_duration = st.sidebar.select_slider(
        "Workout Duration (seconds)",
        options=SLIDER_OPTIONS,
        value=st.session_state.get('workout_duration', SLIDER_OPTIONS[8]),
        key='workout_duration_slider'
    )
    rest_duration = st.sidebar.select_slider(
        "Rest Duration (seconds)",
        options=SLIDER_OPTIONS,
        value=st.session_state.get('rest_duration', SLIDER_OPTIONS[2]),
        key='rest_duration_slider'
    )

    if st.session_state.workout_duration_slider != st.session_state.workout_duration:
        st.session_state.workout_duration = st.session_state.workout_duration_slider
        if not st.session_state.get('timer_running', False) and st.session_state.get('current_phase') == "WORKOUT":
            st.session_state.current_time = st.session_state.workout_duration

    if st.session_state.rest_duration_slider != st.session_state.rest_duration:
        st.session_state.rest_duration = st.session_state.rest_duration_slider
        if not st.session_state.get('timer_running', False) and st.session_state.get('current_phase') == "REST":
            st.session_state.current_time = st.session_state.rest_duration

    st.sidebar.markdown("---")
    st.sidebar.header("🔊 Sound Settings (Browser Based)") # Updated header

    # Sound Selectboxes (Using JS_SOUND_OPTIONS)
    default_session_start_sound = st.session_state.get('sound_on_session_start', JS_SOUND_OPTIONS[0])
    st.session_state.sound_on_session_start = st.sidebar.selectbox(
        "Session Start Sound:", options=JS_SOUND_OPTIONS, # Use new options
        index=JS_SOUND_OPTIONS.index(default_session_start_sound) if default_session_start_sound in JS_SOUND_OPTIONS else 0,
        key='sb_sound_session_start'
    )
    default_workout_start_sound = st.session_state.get('sound_on_workout_start', JS_SOUND_OPTIONS[0])
    st.session_state.sound_on_workout_start = st.sidebar.selectbox(
        "Workout Start Sound (End of Rest):", options=JS_SOUND_OPTIONS, # Use new options
        index=JS_SOUND_OPTIONS.index(default_workout_start_sound) if default_workout_start_sound in JS_SOUND_OPTIONS else 0,
        key='sb_sound_workout_start'
    )
    default_rest_start_sound = st.session_state.get('sound_on_rest_start', JS_SOUND_OPTIONS[0])
    st.session_state.sound_on_rest_start = st.sidebar.selectbox(
        "Rest Start Sound (End of Workout):", options=JS_SOUND_OPTIONS, # Use new options
        index=JS_SOUND_OPTIONS.index(default_rest_start_sound) if default_rest_start_sound in JS_SOUND_OPTIONS else 0,
        key='sb_sound_rest_start'
    )
    st.sidebar.caption("Sounds play via your browser (requires interaction to enable).") # Added caption

    st.sidebar.markdown("---")
    st.sidebar.header("📊 Insights Chart Settings") # New Section for Chart Type

    default_chart_type = st.session_state.get('insights_chart_type', INSIGHTS_CHART_OPTIONS[0])
    st.session_state.insights_chart_type = st.sidebar.selectbox(
        "Chart Type for Workout vs. Rest:",
        options=INSIGHTS_CHART_OPTIONS,
        index=INSIGHTS_CHART_OPTIONS.index(default_chart_type) if default_chart_type in INSIGHTS_CHART_OPTIONS else 0,
        key='sb_insights_chart_type'
    )

    st.sidebar.markdown("---")
    st.sidebar.header("🤖 AI Coach (Future)")
    st.sidebar.info("AI-powered workout suggestions and RAG components will be managed here.")

    return workout_duration, rest_duration