# configs/app_config.py

# Default timer settings (in seconds)
DEFAULT_WORKOUT_DURATION = 45
DEFAULT_REST_DURATION = 15

# Slider options
MIN_DURATION = 5
MAX_DURATION = 180  # 3 minutes
STEP_DURATION = 5

# Options for the select_slider (must be discrete values)
SLIDER_OPTIONS = list(range(MIN_DURATION, MAX_DURATION + STEP_DURATION, STEP_DURATION))

# Phase names
PHASE_WORKOUT = "WORKOUT"
PHASE_REST = "REST"
PHASE_COMPLETED = "COMPLETED" # Optional: If you want a finite number of sets

# --- Sound Configuration ---
BEEPY_SOUND_OPTIONS = [
    "None",
    "coin",
    "error",
    "ping",
    "ready",
    "success",
    "message",
]
DEFAULT_WORKOUT_START_SOUND = "ping"
DEFAULT_REST_START_SOUND = "ping"
DEFAULT_SESSION_START_SOUND = "ping"

# --- Insights Chart Configuration ---
CHART_TYPE_BAR = "Bar Chart"
CHART_TYPE_DOUGHNUT = "Doughnut Chart"
INSIGHTS_CHART_OPTIONS = [CHART_TYPE_DOUGHNUT, CHART_TYPE_BAR]
DEFAULT_INSIGHTS_CHART_TYPE = CHART_TYPE_DOUGHNUT

# --- AI Configuration Note ---
# It's best practice to store API keys securely using Streamlit Secrets or environment variables.
# For Streamlit Secrets, you would create a .streamlit/secrets.toml file with:
# GEMINI_API_KEY = "YOUR_ACTUAL_API_KEY"
# And access it in your code via st.secrets["GEMINI_API_KEY"]
# For this example, the key will be handled in the component using it, with a warning.
GEMINI_API_MODEL_NAME = "gemini-2.0-flash" # Using a recommended model