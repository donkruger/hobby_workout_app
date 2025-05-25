# ai_components/agent_rag_pipeline.py
import streamlit as st
import google.generativeai as genai
from configs.app_config import GEMINI_API_MODEL_NAME
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- IMPORTANT: API KEY MANAGEMENT ---
def get_gemini_api_key():
    """Retrieves the Gemini API key from Streamlit secrets."""
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        if not api_key:
            st.error("Gemini API Key is empty. Please check your Streamlit secrets.")
            return None
        return api_key
    except (FileNotFoundError, KeyError):
        st.error("Gemini API Key not found. Please add it to your Streamlit secrets (.streamlit/secrets.toml).")
        st.info("Example for secrets.toml:\nGEMINI_API_KEY=\"YOUR_AIza...KEY\"")
        return None

def generate_ai_feedback(workout_history: list, workout_schedule: list, last_session_stats: dict) -> str:
    """
    Generates AI feedback using Gemini based on workout history and last session.

    Args:
        workout_history (list): A list of dictionaries, each representing a past workout.
        workout_schedule (list): The list of exercises in the current/last schedule.
        last_session_stats (dict): Stats from the just-paused/completed session.

    Returns:
        str: AI-generated feedback or an error/info message.
    """
    api_key = get_gemini_api_key()
    if not api_key:
        return "AI feedback requires a configured Gemini API Key."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(GEMINI_API_MODEL_NAME)

        # Build a more informative context
        history_summary = "No extensive history available yet."
        if workout_history:
             history_summary = f"User has completed {len(workout_history)} sessions previously."

        schedule_str = ", ".join(workout_schedule) if workout_schedule else "No specific schedule was used (freestyle)."

        prompt = f"""
        You are a supportive and knowledgeable AI Workout Coach.
        A user has just paused their workout session. Your task is to provide brief, actionable feedback.

        Context:
        - Current Workout Schedule: {schedule_str}
        - Just Paused Session Stats: {last_session_stats}
        - Past Workout Summary: {history_summary}
        - User Preference: The user might appreciate Keto-friendly food advice if relevant.

        Instructions:
        1.  **Acknowledge the Pause:** Start with a brief, encouraging comment about taking a break or completing the session so far.
        2.  **Comment on the Session:** Based on '{schedule_str}' and '{last_session_stats}', comment on the workout.
            - If a schedule exists, identify the likely primary muscle groups targeted (e.g., "Great work hitting your chest and triceps!").
            - If no schedule exists, provide a general comment (e.g., "Good job staying active!").
        3.  **Suggest an Alternative/Next Step:** Based on the current schedule (if any), suggest ONE specific alternative exercise they could consider adding next time. Aim for variety or a complementary movement.
        4.  **Keep it Concise:** Aim for 2-4 sentences total.
        5.  **Keto Option (Optional):** If appropriate, briefly mention a keto-friendly post-workout snack idea.

        Example Output (if schedule existed):
        "Nice pause! You've put in some solid effort on those Push-ups and Squats, really working your chest, legs, and core. Next time, how about trying Diamond Push-ups to hit those triceps a bit more? Don't forget to refuel - maybe some grilled chicken strips?"

        Example Output (if no schedule):
        "Taking a breather? Smart move! You've clocked {last_session_stats.get('workout_time', 'some good')} of workout time. For your next session, try adding specific exercises like Jumping Jacks or Lunges using the 'Add Workout' menu. A handful of almonds is a great keto-friendly energy boost!"

        Generate the feedback now based on the provided context.
        """

        logger.info("Generating AI feedback with prompt.")
        response = model.generate_content(prompt)

        if response.text:
            logger.info("AI feedback generated successfully.")
            return response.text.strip()
        else:
            logger.warning("AI returned an empty response.")
            return "Couldn't generate specific feedback right now, but keep up the great work!"

    except Exception as e:
        logger.error(f"Error generating AI feedback: {e}", exc_info=True)
        return f"An error occurred while getting AI feedback: {e}"


# --- You can keep or remove the AgenticRAGPipeline class based on future plans ---
# --- For *this specific* request, we are using the direct function above ---

class AgenticRAGPipeline:
    def __init__(self):
        """
        Initializes the RAG pipeline.
        This could involve loading models, vector stores, etc.
        """
        logger.info("Placeholder: AgenticRAGPipeline initialized.")
        # This part is currently not used for the feedback feature.

    def query(self, user_question: str, workout_context: dict = None) -> str:
        """
        Placeholder for processing a user query through the RAG pipeline.
        """
        logger.info(f"Placeholder: RAG pipeline received query: {user_question}")
        logger.info(f"Placeholder: Workout context: {workout_context}")
        # This part is currently not used for the feedback feature.
        return "Placeholder AI Response from RAG."

def get_ai_feedback_for_session(session_manager) -> str:
    """
    Gets AI feedback based on the current session state.
    """
    if not st.session_state.get("timer_running", False):
         return "Start a workout to get feedback."

    schedule = st.session_state.get("workout_schedule", [])
    history = [] # In a real app, you'd load this: load_workout_history()
    stats = {
        "rounds": session_manager.get_completed_rounds(),
        "workout_time": session_manager.get_total_workout_time(),
        "rest_time": session_manager.get_total_rest_time(),
        "current_exercise": session_manager.get_current_exercise(),
    }

    # If no schedule, prompt to add one
    if not schedule and session_manager.is_paused():
        return 'It looks like you completed this workout without a pre-set list. For more targeted feedback and to track your exercises, try using the "Add Workout" option in the menu next time!'

    # If there is a schedule, generate feedback
    if schedule and session_manager.is_paused():
        return generate_ai_feedback(history, schedule, stats)

    return "Pause your workout to receive AI feedback."