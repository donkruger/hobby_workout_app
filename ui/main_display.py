# ui/main_display.py
import streamlit as st
from core.session_manager import WorkoutSession
from configs.app_config import (
    PHASE_GET_READY, PHASE_WORKOUT, PHASE_REST, PHASE_PAUSED, # Import new phase
    MOTIVATIONAL_MESSAGES
)
from data_tracking.visualization import display_workout_insights
from streamlit_js_eval import streamlit_js_eval
import html
import random


def render_main_display(session: WorkoutSession) -> None:
    st.markdown(
        "<h3 style='text-align:center;margin-bottom:10px;'>⏱️ Workout Timer</h3>",
        unsafe_allow_html=True,
    )

    current_phase = session.get_current_phase()
    time_display = session.get_current_time_display() # Already handles paused time
    current_exercise = session.get_current_exercise()
    schedule_exists = bool(st.session_state.get("workout_schedule"))

    text_gradient_color_class = "default-gradient-colors"
    progress_bar_fill_class = "custom-bar-default"
    phase_icon = "🏁"
    phase_text_content = current_phase.capitalize()

    if current_phase == PHASE_GET_READY:
        text_gradient_color_class = "rest-gradient-colors"
        progress_bar_fill_class = "custom-bar-rest"
        phase_icon = "⏱️"
        phase_text_content = "GET READY!"
    elif current_phase == PHASE_WORKOUT:
        text_gradient_color_class = "workout-gradient-colors"
        progress_bar_fill_class = "custom-bar-workout"
        phase_icon = "💪"
        phase_text_content = html.escape(current_exercise) if schedule_exists and current_exercise else "WORKOUT!"
    elif current_phase == PHASE_REST:
        text_gradient_color_class = "rest-gradient-colors"
        progress_bar_fill_class = "custom-bar-rest"
        phase_icon = "🧘"
        phase_text_content = "REST"
    elif current_phase == PHASE_PAUSED:
        text_gradient_color_class = "default-gradient-colors" # Neutral gradient for paused
        progress_bar_fill_class = "custom-bar-default"
        phase_icon = "⏸️"
        phase_text_content = "PAUSED"


    st.markdown(
        f"""
        <div class="animated-gradient-text-base phase-header-gradient {text_gradient_color_class}">
            {phase_icon} {phase_text_content}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="animated-gradient-text-base timer-numbers-display {text_gradient_color_class}">
            {time_display}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Motivational message or Next exercise display
    placeholder_div = "<div style='height: 60px; margin-bottom: 15px;'></div>" # Default placeholder

    if session.is_running_or_paused(): # Show this section if timer is running or paused
        if current_phase == PHASE_PAUSED:
            if 'motivational_message' not in st.session_state or \
               st.session_state.get('last_phase_for_motivation') != PHASE_PAUSED :
                st.session_state.motivational_message = random.choice(MOTIVATIONAL_MESSAGES)
            st.session_state.last_phase_for_motivation = PHASE_PAUSED
            st.markdown(
                f"<p style='text-align:center;font-size:1.6em;color:grey;margin-top:10px;margin-bottom:15px;font-style:italic;'>"
                f"{st.session_state.motivational_message}</p>",
                unsafe_allow_html=True,
            )
        elif schedule_exists:
            st.session_state.last_phase_for_motivation = current_phase # Reset for next pause
            cur_ex_for_display = current_exercise
            next_ex = session.get_next_exercise()

            if current_phase == PHASE_GET_READY and cur_ex_for_display:
                st.markdown(
                    f"<p style='text-align:center;font-size:2.2em;margin-top:-10px;margin-bottom:15px;'>"
                    f"Starting with: <strong>{html.escape(cur_ex_for_display)}</strong></p>",
                    unsafe_allow_html=True,
                )
            elif current_phase == PHASE_WORKOUT and cur_ex_for_display:
                if next_ex:
                    st.markdown(
                        f"<p style='text-align:center;font-size:1.6em;color:grey;margin-top:10px;margin-bottom:15px;'>"
                        f"Next: {html.escape(next_ex)}</p>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown("<div style='height: 40px; margin-bottom: 15px;'></div>", unsafe_allow_html=True)
            elif current_phase == PHASE_REST and next_ex:
                st.markdown(
                    f"<p style='text-align:center;font-size:2.2em;margin-top:-10px;margin-bottom:15px;'>"
                    f"Next Up: <strong>{html.escape(next_ex)}</strong></p>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(placeholder_div, unsafe_allow_html=True)
        else: # Schedule doesn't exist but timer might be running (e.g. Get Ready then no schedule)
            st.markdown(placeholder_div, unsafe_allow_html=True)
    else: # Timer not running and not paused
        st.markdown(placeholder_div, unsafe_allow_html=True)


    progress_value_percent = int(session.get_progress_value() * 100)
    st.markdown(
        f"""
        <div class="custom-progress-wrapper">
            <div class="custom-progress-bg">
                <div class="custom-bar-fill {progress_bar_fill_class}" style="width:{progress_value_percent}%;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- Control buttons ---
    col1, col2, col3 = st.columns([2, 2, 1]) # Keep 3 columns for Start/Resume, Pause, Reset

    with col1: # Start / Resume Button
        if session.is_paused():
            if st.button("▶️ Resume", use_container_width=True, key="resume_button"):
                session.resume_session()
                st.rerun()
        elif not session.is_running_or_paused(): # Initial state, or after reset
            if st.button("🚀 Start", use_container_width=True, key="start_button"):
                session.start_session()
                # Fallback/secondary attempt to unlock audio context
                streamlit_js_eval(js_code="if(typeof window.unlockAudio === 'function') { window.unlockAudio(); console.log('[AUDIO DEBUG] unlockAudio called from Start button.'); }")
                st.rerun()
        else: # Running, not paused
             st.button("🚀 Start", use_container_width=True, key="start_button_disabled", disabled=True)


    with col2: # Pause Button (replaces old Stop button's position)
        if session.is_running_or_paused() and not session.is_paused():
            if st.button("⏸️ Pause", use_container_width=True, key="pause_button"):
                session.pause_session()
                st.rerun()
        else: # Not running or already paused
            st.button("⏸️ Pause", use_container_width=True, key="pause_button_disabled", disabled=True)
            
    with col3: # Reset Button
        if st.button("🔄 Reset", use_container_width=True, key="reset_button"):
            session.reset_session_stats()
            st.rerun()

    st.markdown("---")
    display_workout_insights(session)

    st.markdown("---")
    st.subheader("🧠 AI Feedback (Future)")
    st.info("AI‑generated tips or analysis from the RAG pipeline will appear here.")