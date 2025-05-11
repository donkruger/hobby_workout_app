# core/session_manager.py
import streamlit as st
from configs.app_config import PHASE_WORKOUT, PHASE_REST
from utils.helpers import format_time
import beepy as bp

def _play_sound(sound_name_or_id):
    if sound_name_or_id and sound_name_or_id.lower() != "none":
        try:
            bp.beep(sound=sound_name_or_id)
        except Exception as e:
            print(f"Info: Could not play sound '{sound_name_or_id}' with beepy - {e}")

class WorkoutSession:
    def __init__(self):
        pass

    def update_durations(self, workout_duration: int, rest_duration: int):
        st.session_state.workout_duration = workout_duration
        st.session_state.rest_duration = rest_duration
        if not st.session_state.get('timer_running', False):
            st.session_state.current_phase = PHASE_WORKOUT
            st.session_state.current_time = workout_duration
            st.session_state.session_stats_initialized_for_run = False

    def start_session(self):
        if not st.session_state.get('timer_running', False):
            st.session_state.timer_running = True
            
            if not st.session_state.get('session_stats_initialized_for_run', False):
                st.session_state.accumulated_workout_seconds = 0
                st.session_state.accumulated_rest_seconds = 0
                st.session_state.completed_rounds = 0
                st.session_state.current_exercise_index = 0 # Reset exercise index for a new session
                st.session_state.session_stats_initialized_for_run = True
                _play_sound(st.session_state.get('sound_on_session_start'))

            if st.session_state.current_phase == PHASE_WORKOUT:
                if st.session_state.current_time == 0 :
                     st.session_state.current_time = st.session_state.get('workout_duration', 45)
            elif st.session_state.current_phase == PHASE_REST:
                if st.session_state.current_time == 0:
                    st.session_state.current_time = st.session_state.get('rest_duration', 15)
            else: 
                st.session_state.current_phase = PHASE_WORKOUT
                st.session_state.current_time = st.session_state.get('workout_duration', 45)

    def stop_session(self):
        st.session_state.timer_running = False

    def reset_session_stats(self):
        st.session_state.accumulated_workout_seconds = 0
        st.session_state.accumulated_rest_seconds = 0
        st.session_state.completed_rounds = 0
        st.session_state.current_exercise_index = 0 # Reset exercise index
        st.session_state.session_stats_initialized_for_run = False 
        if not st.session_state.get('timer_running', False):
            st.session_state.current_phase = PHASE_WORKOUT
            st.session_state.current_time = st.session_state.get('workout_duration', 45)

    def tick(self):
        if not st.session_state.get('timer_running', False):
            return

        if st.session_state.current_phase == PHASE_WORKOUT and st.session_state.current_time > 0:
            st.session_state.accumulated_workout_seconds += 1
        elif st.session_state.current_phase == PHASE_REST and st.session_state.current_time > 0:
            st.session_state.accumulated_rest_seconds += 1

        if st.session_state.current_time > 0:
            st.session_state.current_time -= 1
        else:
            previous_phase = st.session_state.current_phase
            if previous_phase == PHASE_WORKOUT:
                st.session_state.current_phase = PHASE_REST
                st.session_state.current_time = st.session_state.rest_duration
                st.session_state.completed_rounds += 1
                _play_sound(st.session_state.get('sound_on_rest_start'))
                
                # Advance exercise AFTER workout completion (and sound)
                schedule = st.session_state.get('workout_schedule', [])
                if schedule: # Only advance if there's a schedule
                    current_idx = st.session_state.get('current_exercise_index', 0)
                    st.session_state.current_exercise_index = (current_idx + 1) % len(schedule)

            elif previous_phase == PHASE_REST:
                st.session_state.current_phase = PHASE_WORKOUT
                st.session_state.current_time = st.session_state.workout_duration
                _play_sound(st.session_state.get('sound_on_workout_start'))
                # Current exercise for this new workout phase is already set by the end of the previous workout

    # --- Exercise Schedule Getters ---
    def get_current_exercise(self) -> str | None:
        schedule = st.session_state.get('workout_schedule', [])
        if not schedule:
            return None
        current_idx = st.session_state.get('current_exercise_index', 0)
        if 0 <= current_idx < len(schedule):
            return schedule[current_idx]
        return None # Should ideally not happen if index is managed correctly

    def get_next_exercise(self) -> str | None:
        schedule = st.session_state.get('workout_schedule', [])
        if not schedule or len(schedule) < 1: # Need at least 1 for a "next" to make sense, or handle single item
            return None
        if len(schedule) == 1: # If only one exercise, "next" is the same or conceptually none
            return None # Or return schedule[0] if you want it to show itself as next

        current_idx = st.session_state.get('current_exercise_index', 0)
        next_idx = (current_idx + 1) % len(schedule)
        return schedule[next_idx]

    # --- Other Getters ---
    def get_current_time_display(self) -> str:
        return format_time(st.session_state.get('current_time', 0))

    def get_current_phase(self) -> str:
        return st.session_state.get('current_phase', PHASE_WORKOUT)

    def is_running(self) -> bool:
        return st.session_state.get('timer_running', False)

    def get_progress_value(self) -> float:
        current_time = st.session_state.get('current_time', 0)
        total_duration = 1 
        if st.session_state.get('current_phase') == PHASE_WORKOUT:
            total_duration = st.session_state.get('workout_duration', 1)
        elif st.session_state.get('current_phase') == PHASE_REST:
            total_duration = st.session_state.get('rest_duration', 1)
        if total_duration == 0: return 0.0
        progress = (total_duration - current_time) / total_duration
        return min(max(progress, 0.0), 1.0)

    def get_completed_rounds(self) -> int:
        return st.session_state.get('completed_rounds', 0)

    def get_total_workout_time(self) -> int:
        return st.session_state.get('accumulated_workout_seconds', 0)

    def get_total_rest_time(self) -> int:
        return st.session_state.get('accumulated_rest_seconds', 0)

    def get_total_elapsed_active_time(self) -> int:
        return self.get_total_workout_time() + self.get_total_rest_time()