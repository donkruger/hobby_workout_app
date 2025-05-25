# workout_app/ui/sidebar_controls.py
import streamlit as st
from streamlit_js_eval import streamlit_js_eval

from configs.app_config import (
    SLIDER_OPTIONS,
    INSIGHTS_CHART_OPTIONS,
)

# ──────────────────────────────────────────────────────────────────────────────
# Sidebar controls
# ──────────────────────────────────────────────────────────────────────────────
def render_sidebar_controls():
    # ------------------------------------------------------------------ #
    # ⏱️  Timer sliders
    # ------------------------------------------------------------------ #
    st.sidebar.header("⚙️ Timer Settings")

    workout_duration = st.sidebar.select_slider(
        "Workout Duration (seconds)",
        options=SLIDER_OPTIONS,
        value=st.session_state.get("workout_duration", SLIDER_OPTIONS[8]),
        key="workout_duration_slider",
    )
    rest_duration = st.sidebar.select_slider(
        "Rest Duration (seconds)",
        options=SLIDER_OPTIONS,
        value=st.session_state.get("rest_duration", SLIDER_OPTIONS[2]),
        key="rest_duration_slider",
    )

    # push the new values into session_state immediately
    if st.session_state.workout_duration_slider != st.session_state.workout_duration:
        st.session_state.workout_duration = st.session_state.workout_duration_slider
        if (
            not st.session_state.get("timer_running", False)
            and st.session_state.get("current_phase") == "WORKOUT"
        ):
            st.session_state.current_time = st.session_state.workout_duration

    if st.session_state.rest_duration_slider != st.session_state.rest_duration:
        st.session_state.rest_duration = st.session_state.rest_duration_slider
        if (
            not st.session_state.get("timer_running", False)
            and st.session_state.get("current_phase") == "REST"
        ):
            st.session_state.current_time = st.session_state.rest_duration

    # ------------------------------------------------------------------ #
    # 🔊 Master sound toggle (all per-event pickers removed)
    # ------------------------------------------------------------------ #
    st.sidebar.markdown("---")
    st.sidebar.header("🔊 Sound")

    sound_is_on = st.session_state.get("sound_master_enabled", True)
    btn_label   = "Sound ON  🔊" if sound_is_on else "Sound OFF 🔇"

    if st.sidebar.button(btn_label, key="master_sound_toggle"):
        st.session_state.sound_master_enabled = not sound_is_on

        # When turning sound ON ask the browser for permission / unlock audio
        if st.session_state.sound_master_enabled:
            streamlit_js_eval(
                js_code=(
                    "if (typeof window.requestSoundPermissionAndUnlock==='function') "
                    "{ window.requestSoundPermissionAndUnlock(); }"
                )
            )
        st.rerun()

    st.sidebar.caption("Quickly mute or un-mute all app sounds.")

    # ------------------------------------------------------------------ #
    # 📊  Insights chart picker (unchanged)
    # ------------------------------------------------------------------ #
    st.sidebar.markdown("---")
    st.sidebar.header("📊 Insights Chart Settings")

    default_chart_type = st.session_state.get(
        "insights_chart_type", INSIGHTS_CHART_OPTIONS[0]
    )
    st.session_state.insights_chart_type = st.sidebar.selectbox(
        "Chart Type for Workout vs. Rest:",
        options=INSIGHTS_CHART_OPTIONS,
        index=INSIGHTS_CHART_OPTIONS.index(default_chart_type)
        if default_chart_type in INSIGHTS_CHART_OPTIONS
        else 0,
        key="sb_insights_chart_type",
    )

    st.sidebar.markdown("---")
    st.sidebar.header("🤖 AI Coach (Future)")
    st.sidebar.info(
        "AI-powered workout suggestions and RAG components will be managed here."
    )

    return workout_duration, rest_duration
