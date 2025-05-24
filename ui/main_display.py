# ui/main_display.py
import streamlit as st
from core.session_manager import WorkoutSession
from configs.app_config import PHASE_WORKOUT, PHASE_REST
from data_tracking.visualization import display_workout_insights
from streamlit_js_eval import streamlit_js_eval # Import


def render_main_display(session: WorkoutSession) -> None:
    """
    Render the timer, phase header, controls, schedule labels, and insights.
    Uses a custom HTML progress bar with dynamic gradient styling.
    """
    # ---------------------- Title ---------------------------------
    st.markdown(
        # Changed h1 to h3 to reduce font size
        "<h3 style='text-align:center;margin-bottom:10px;'>⏱️ Workout Timer</h3>",
        unsafe_allow_html=True,
    )

    # ---------------------- Phase / timer -------------------------
    current_phase = session.get_current_phase()
    time_display = session.get_current_time_display()

    text_gradient_color_class = "default-gradient-colors"
    # This class is for the custom HTML progress bar's fill element
    progress_bar_fill_class = "custom-bar-default" # Default if no phase match
    phase_icon, phase_text = "🏁", current_phase.capitalize()

    if current_phase == PHASE_WORKOUT:
        text_gradient_color_class = "workout-gradient-colors"
        progress_bar_fill_class = "custom-bar-workout" # CSS class for workout progress bar fill
        phase_icon, phase_text = "💪", "WORKOUT!"
    elif current_phase == PHASE_REST:
        text_gradient_color_class = "rest-gradient-colors"
        progress_bar_fill_class = "custom-bar-rest" # CSS class for rest progress bar fill
        phase_icon, phase_text = "🧘", "REST"

    # Animated gradient phase header
    st.markdown(
        f"""
        <div class="animated-gradient-text-base phase-header-gradient {text_gradient_color_class}">
            {phase_icon} {phase_text}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Timer numbers
    st.markdown(
        f"""
        <div class="animated-gradient-text-base timer-numbers-display {text_gradient_color_class}">
            {time_display}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---------------------- Current / next exercise ---------------
    if st.session_state.get("workout_schedule") and session.is_running():
        cur_ex = session.get_current_exercise()
        next_ex = session.get_next_exercise()

        if current_phase == PHASE_WORKOUT and cur_ex:
            st.markdown(
                # Increased font-size from 1.5em to 2.2em
                f"<p style='text-align:center;font-size:2.2em;margin-top:-10px;margin-bottom:5px;'>"
                f"Current: <strong>{cur_ex}</strong></p>",
                unsafe_allow_html=True,
            )
            if next_ex:
                st.markdown(
                    # Increased font-size from 1.1em to 1.6em
                    f"<p style='text-align:center;font-size:1.6em;color:grey;margin-bottom:15px;'>"
                    f"Next: {next_ex}</p>",
                    unsafe_allow_html=True,
                )
        elif current_phase == PHASE_REST and next_ex:
            st.markdown(
                # Increased font-size from 1.5em to 2.2em
                f"<p style='text-align:center;font-size:2.2em;margin-top:-10px;margin-bottom:15px;'>"
                f"Next Up: <strong>{next_ex}</strong></p>",
                unsafe_allow_html=True,
            )

    # ---------------------- Custom HTML Progress bar --------------------------
    progress_value_percent = int(session.get_progress_value() * 100)
    # The inner div now combines a base style for fill mechanics AND the specific color gradient class
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

    # ---------------------- Control buttons -----------------------
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        if st.button("Start", use_container_width=True, key="start_button"):
            session.start_session()
            # Try to unlock audio context when the user clicks start
            streamlit_js_eval(js_code="if(typeof window.unlockAudio === 'function') { window.unlockAudio(); }")
            st.rerun()
    with col2:
        if st.button("Stop", use_container_width=True, key="stop_button"):
            session.stop_session()
            st.rerun()
    with col3:
        if st.button(
            "Reset",
            use_container_width=True,
            key="reset_stats_button",
            help="Resets timer and all session statistics.",
        ):
            session.stop_session()
            session.reset_session_stats()
            st.rerun()

    # ---------------------- Insights & placeholders ---------------
    st.markdown("---")
    display_workout_insights(session)

    st.markdown("---")
    st.subheader("🧠 AI Feedback (Future)")
    st.info("AI‑generated tips or analysis from the RAG pipeline will appear here.")