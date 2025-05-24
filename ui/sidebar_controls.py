# ui/sidebar_controls.py
import streamlit as st
from configs.app_config import SLIDER_OPTIONS, JS_SOUND_OPTIONS, INSIGHTS_CHART_OPTIONS
from streamlit_js_eval import streamlit_js_eval # Ensure this is imported

def render_sidebar_controls():
    st.sidebar.header("⚙️ Timer Settings")

    # ... (timer duration sliders remain the same) ...
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
        if not st.session_state.get('timer_running', False) and st.session_state.get('current_phase') == "WORKOUT": # Assuming PHASE_WORKOUT exists
            st.session_state.current_time = st.session_state.workout_duration

    if st.session_state.rest_duration_slider != st.session_state.rest_duration:
        st.session_state.rest_duration = st.session_state.rest_duration_slider
        if not st.session_state.get('timer_running', False) and st.session_state.get('current_phase') == "REST": # Assuming PHASE_REST exists
            st.session_state.current_time = st.session_state.rest_duration


    st.sidebar.markdown("---")
    st.sidebar.header("🔊 Sound Control")

    # Master Sound Toggle Button
    sound_is_on = st.session_state.get('sound_master_enabled', True)
    sound_button_emoji = "🔊" if sound_is_on else "🔇"
    sound_button_label = "Sound ON" if sound_is_on else "Sound OFF"

    if st.sidebar.button(f"{sound_button_emoji} {sound_button_label}", key="master_sound_toggle"):
        st.session_state.sound_master_enabled = not sound_is_on
        if st.session_state.sound_master_enabled:
            # If turning sound ON, explicitly try to unlock AudioContext
            streamlit_js_eval(js_code="if(typeof window.unlockAudio === 'function') { window.unlockAudio(); console.log('[AUDIO DEBUG] unlockAudio explicitly called from sound toggle ON.'); } else { console.warn('[AUDIO DEBUG] unlockAudio function not found when trying to toggle sound ON.'); }")
        st.rerun() # Rerun to update button label/emoji

    st.sidebar.caption("Toggle all app sounds. Individual sounds below.")

    # Individual Sound Selectboxes (only if master sound is enabled)
    if st.session_state.get('sound_master_enabled', True):
        default_session_start_sound = st.session_state.get('sound_on_session_start', JS_SOUND_OPTIONS[0])
        st.session_state.sound_on_session_start = st.sidebar.selectbox(
            "Session Start Sound:", options=JS_SOUND_OPTIONS,
            index=JS_SOUND_OPTIONS.index(default_session_start_sound) if default_session_start_sound in JS_SOUND_OPTIONS else 0,
            key='sb_sound_session_start'
        )
        default_workout_start_sound = st.session_state.get('sound_on_workout_start', JS_SOUND_OPTIONS[0])
        st.session_state.sound_on_workout_start = st.sidebar.selectbox(
            "Workout Start Sound (End of Rest):", options=JS_SOUND_OPTIONS,
            index=JS_SOUND_OPTIONS.index(default_workout_start_sound) if default_workout_start_sound in JS_SOUND_OPTIONS else 0,
            key='sb_sound_workout_start'
        )
        default_rest_start_sound = st.session_state.get('sound_on_rest_start', JS_SOUND_OPTIONS[0])
        st.session_state.sound_on_rest_start = st.sidebar.selectbox(
            "Rest Start Sound (End of Workout):", options=JS_SOUND_OPTIONS,
            index=JS_SOUND_OPTIONS.index(default_rest_start_sound) if default_rest_start_sound in JS_SOUND_OPTIONS else 0,
            key='sb_sound_rest_start'
        )
    else:
        st.sidebar.info("Sound is currently OFF. Enable master sound to select event sounds.")


    st.sidebar.markdown("---")
    # ... (rest of the sidebar controls like Chart Settings, AI Coach) ...
    st.sidebar.header("📊 Insights Chart Settings")
    default_chart_type = st.session_state.get('insights_chart_type', INSIGHTS_CHART_OPTIONS[0]) # Assuming INSIGHTS_CHART_OPTIONS exists
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