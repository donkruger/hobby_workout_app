# configs/app_config.py

# Default timer settings (in seconds)
DEFAULT_WORKOUT_DURATION = 45
DEFAULT_REST_DURATION = 15
GET_READY_DURATION = 10

# Slider options
MIN_DURATION = 5
MAX_DURATION = 180
STEP_DURATION = 5
SLIDER_OPTIONS = list(range(MIN_DURATION, MAX_DURATION + STEP_DURATION, STEP_DURATION))

# Phase names
PHASE_GET_READY = "GET_READY"
PHASE_WORKOUT = "WORKOUT"
PHASE_REST = "REST"
PHASE_PAUSED = "PAUSED" # New: For when the timer is paused
PHASE_COMPLETED = "COMPLETED"

# Motivational messages for Paused state
MOTIVATIONAL_MESSAGES = [
    "Don't give up, you're doing great!",
    "Keep pushing, every second counts!",
    "You're stronger than you think!",
    "Almost there, take a breather!",
    "You got this! Ready to go again?",
    "Pause is part of the process. Come back stronger!",
]

# --- Sound Configuration ---
JS_SOUND_OPTIONS = [
    "None", "Beep_High", "Beep_Low", "Double_Beep", "Success", "Error",
]
DEFAULT_WORKOUT_START_SOUND = "Beep_High"
DEFAULT_REST_START_SOUND = "Beep_Low"
DEFAULT_SESSION_START_SOUND = "Success"

# --- Insights Chart Configuration ---
CHART_TYPE_BAR = "Bar Chart"
CHART_TYPE_DOUGHNUT = "Doughnut Chart"
INSIGHTS_CHART_OPTIONS = [CHART_TYPE_DOUGHNUT, CHART_TYPE_BAR]
DEFAULT_INSIGHTS_CHART_TYPE = CHART_TYPE_DOUGHNUT

# --- AI Configuration ---
GEMINI_API_MODEL_NAME = "gemini-1.5-flash"