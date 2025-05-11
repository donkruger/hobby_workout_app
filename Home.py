# Home.py
import streamlit as st
import time
import os

# Custom modules
from configs.app_config import PHASE_WORKOUT, PHASE_REST
from utils.helpers import initialize_session_state_defaults
from core.session_manager import WorkoutSession
from ui.sidebar_controls import render_sidebar_controls
from ui.main_display import render_main_display

# --- Page Configuration (should be the first Streamlit command) ---
st.set_page_config(
    page_title="Workout Timer - Home", # Updated page title for browser tab
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="collapsed" # Changed to "collapsed"
)

# --- Function to Load Custom CSS ---
def load_css(file_path):
    if os.path.exists(file_path):
        with open(file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"Custom CSS file not found at {file_path}")

css_file_path = os.path.join(os.path.dirname(__file__), "ui", "style.css")
load_css(css_file_path)

initialize_session_state_defaults()
workout_session = WorkoutSession()
selected_workout_duration, selected_rest_duration = render_sidebar_controls()

if not workout_session.is_running():
    workout_session.update_durations(selected_workout_duration, selected_rest_duration)

render_main_display(workout_session)

if workout_session.is_running():
    workout_session.tick()
    time.sleep(1)
    st.rerun()

st.markdown("---")
st.caption("Built with Streamlit and ❤️ for fitness.")