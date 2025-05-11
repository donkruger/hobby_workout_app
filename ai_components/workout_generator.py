# workout_app/ai_components/workout_generator.py
import streamlit as st
import google.generativeai as genai
from configs.app_config import GEMINI_API_MODEL_NAME
import re # For parsing user input for duration

# --- IMPORTANT: API KEY MANAGEMENT ---
# (Keeping the existing API key warning and handling logic)
# ... (Your existing API key handling logic here) ...

def get_ai_workout_suggestions(
    user_description: str,
    workout_duration_per_exercise_seconds: int,
    rest_duration_per_exercise_seconds: int
) -> list[str] | None:
    """
    Generates workout suggestions using the Gemini API, considering user description
    and current timer configurations.

    Args:
        user_description (str): The user's description of the desired workout.
        workout_duration_per_exercise_seconds (int): Duration of each single exercise in seconds.
        rest_duration_per_exercise_seconds (int): Duration of rest after each exercise in seconds.

    Returns:
        list[str] | None: A list of suggested exercises, or None if an error occurs.
    """
    api_key = None
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except (FileNotFoundError, KeyError): # Python 3.10+ uses FileNotFoundError for missing secrets
        st.error("Gemini API Key not found. Please add it to your Streamlit secrets (.streamlit/secrets.toml).")
        st.info("Example for secrets.toml:\nGEMINI_API_KEY=\"YOUR_AIza...KEY\"")
        # Fallback for testing - REMOVE FOR PRODUCTION
        # if not api_key:
        #     api_key = "YOUR_FALLBACK_OR_TEST_KEY_HERE_IF_ABSOLUTELY_NECESSARY" 
        #     if api_key == "YOUR_FALLBACK_OR_TEST_KEY_HERE_IF_ABSOLUTELY_NECESSARY":
        #          st.warning("Using a placeholder API key. Please set your GEMINI_API_KEY in st.secrets for proper operation.", icon="⚠️")
        #          return None # Or return a default list for UI testing if API key is missing
        return None


    if not api_key:
        # This check is a bit redundant if the try-except above handles it, but good for safety.
        st.error("Gemini API Key is not configured.")
        return None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(GEMINI_API_MODEL_NAME)

        # Enhanced prompt for contextual awareness
        prompt = f"""
        You are an expert workout planner. Your task is to generate a list of exercises
        for a looping workout schedule based on the user's request and their current timer settings.

        CONTEXT:
        1. User's request: "{user_description}"
           (This request might specify desired total active workout time like "15 minute workout",
           type of workout like "full body", intensity like "beginner", equipment like "no equipment", etc.)
        2. Current app configuration for each exercise cycle:
           - Duration of each single exercise: {workout_duration_per_exercise_seconds} seconds.
           - Rest duration after each exercise: {rest_duration_per_exercise_seconds} seconds.
        3. The generated list of exercises will be performed in a continuous loop by the user.

        YOUR TASK:
        - Analyze the "User's request" to understand their goals, including any specified total active exercise duration.
        - If the user specifies a total active exercise duration (e.g., "a 10-minute core workout", "workout for 30 minutes"),
          calculate the number of unique exercises needed. The number of exercises should be such that the sum of
          their individual durations (each at {workout_duration_per_exercise_seconds} seconds) approximately matches the user's
          requested total active exercise time. For example, if the user wants 5 minutes (300 seconds) of active exercise
          and each exercise is 30 seconds long, you should suggest 10 unique exercises. If they ask for a "15 minute workout"
          and each exercise is 60 seconds, suggest 15 unique exercises.
        - If no total duration is specified by the user, suggest a reasonable number of exercises (e.g., 5-8)
          that fit the theme of their request and the looping nature of the schedule.
        - Generate a list of specific exercises that are suitable for the user's request (considering type,
          intensity, equipment if mentioned) and are appropriate for the configured exercise duration.
        - Aim for a balanced workout if the request is general (e.g., "full body").

        OUTPUT FORMAT (Strictly adhere to this):
        - Provide ONLY the list of exercise names.
        - Each exercise name MUST be on a new line.
        - Do NOT include numbering, bullets, introductory/concluding remarks, or any other text.

        Example of a good response if user asks for "quick 2 minute upper body" and exercise duration is 30 seconds:
        Push-ups
        Dumbbell Rows
        Overhead Press
        Bicep Curls
        """

        response = model.generate_content(prompt)
        
        if response.text:
            suggestions = [exercise.strip() for exercise in response.text.splitlines() if exercise.strip()]
            if suggestions:
                return suggestions
            else:
                st.warning("AI returned an empty list of suggestions. Try rephrasing your request.", icon="💡")
                return None
        else:
            st.warning("AI did not return any suggestions. Try rephrasing your request.", icon="💡")
            return None
            
    except Exception as e:
        st.error(f"An error occurred while generating AI workout suggestions: {e}")
        # For more detailed debugging, you might want to see the full error.
        # import traceback
        # print(traceback.format_exc())
        return None