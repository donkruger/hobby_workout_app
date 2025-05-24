# core/session_manager.py
import streamlit as st
from configs.app_config import (
    PHASE_GET_READY, PHASE_WORKOUT, PHASE_REST, PHASE_PAUSED,
    GET_READY_DURATION
)
from utils.helpers import format_time

def _play_sound_js(sound_name_or_id):
    # Check the master sound toggle first
    if not st.session_state.get('sound_master_enabled', True): # Default to True if key somehow missing
        # print(f"[INFO] Sound '{sound_name_or_id}' suppressed: Master sound disabled.") # Optional: for server-side logging
        return

    if sound_name_or_id and sound_name_or_id.lower() != "none":
        st.session_state.sound_to_play = {
            "name": sound_name_or_id,
            "trigger": st.session_state.get("sound_trigger_count", 0) + 1
        }
        st.session_state.sound_trigger_count = st.session_state.get("sound_trigger_count", 0) + 1

class WorkoutSession:
    def __init__(self):
        pass

    def update_durations(self, workout_duration: int, rest_duration: int):
        st.session_state.workout_duration = workout_duration
        st.session_state.rest_duration = rest_duration
        # If timer not running AND not paused, reset to GET_READY phase
        if not st.session_state.get('timer_running', False) and st.session_state.current_phase != PHASE_PAUSED:
            st.session_state.current_phase = PHASE_GET_READY
            st.session_state.current_time = GET_READY_DURATION
            st.session_state.session_stats_initialized_for_run = False
            self._clear_pause_state()

    def _clear_pause_state(self):
        st.session_state.phase_before_pause = None
        st.session_state.time_before_pause = 0

    def start_session(self):
        if not st.session_state.get('timer_running', False) and st.session_state.current_phase != PHASE_PAUSED:
            st.session_state.timer_running = True
            if not st.session_state.get('session_stats_initialized_for_run', False):
                st.session_state.current_phase = PHASE_GET_READY
                st.session_state.current_time = GET_READY_DURATION
                st.session_state.accumulated_workout_seconds = 0
                st.session_state.accumulated_rest_seconds = 0
                st.session_state.completed_rounds = 0
                st.session_state.current_exercise_index = 0
                self._clear_pause_state()
                _play_sound_js(st.session_state.get('sound_on_session_start'))
            elif st.session_state.current_time == 0:
                 self._set_time_for_current_phase()

    def _set_time_for_current_phase(self):
        if st.session_state.current_phase == PHASE_WORKOUT:
            st.session_state.current_time = st.session_state.workout_duration
        elif st.session_state.current_phase == PHASE_REST:
            st.session_state.current_time = st.session_state.rest_duration
        elif st.session_state.current_phase == PHASE_GET_READY:
            st.session_state.current_time = GET_READY_DURATION

    def pause_session(self):
        if st.session_state.timer_running and st.session_state.current_phase != PHASE_PAUSED:
            st.session_state.phase_before_pause = st.session_state.current_phase
            st.session_state.time_before_pause = st.session_state.current_time
            st.session_state.current_phase = PHASE_PAUSED

    def resume_session(self):
        if st.session_state.timer_running and st.session_state.current_phase == PHASE_PAUSED:
            st.session_state.current_phase = st.session_state.phase_before_pause
            st.session_state.current_time = st.session_state.time_before_pause
            self._clear_pause_state()

    def stop_session(self): 
        st.session_state.timer_running = False
        # If we want "Stop" to behave like "Pause" when running, then change this.
        # For now, it truly stops the timer_running flag.
        # If current_phase is PAUSED, and we stop, we should probably revert to phase_before_pause.
        if st.session_state.current_phase == PHASE_PAUSED:
            st.session_state.current_phase = st.session_state.phase_before_pause
            st.session_state.current_time = st.session_state.time_before_pause
            self._clear_pause_state()


    def reset_session_stats(self):
        st.session_state.timer_running = False
        st.session_state.current_phase = PHASE_GET_READY
        st.session_state.current_time = GET_READY_DURATION
        st.session_state.accumulated_workout_seconds = 0
        st.session_state.accumulated_rest_seconds = 0
        st.session_state.completed_rounds = 0
        st.session_state.current_exercise_index = 0
        st.session_state.session_stats_initialized_for_run = False
        self._clear_pause_state()

    def tick(self):
        if not st.session_state.get('timer_running', False):
            return

        current_phase = st.session_state.current_phase
        
        if current_phase == PHASE_PAUSED:
            st.session_state.accumulated_rest_seconds += 1
            return

        if (current_phase == PHASE_REST or current_phase == PHASE_GET_READY) and st.session_state.current_time > 0:
            st.session_state.accumulated_rest_seconds += 1
        elif current_phase == PHASE_WORKOUT and st.session_state.current_time > 0:
            st.session_state.accumulated_workout_seconds += 1

        if st.session_state.current_time > 0:
            st.session_state.current_time -= 1
        else: 
            previous_phase = st.session_state.current_phase
            
            if previous_phase == PHASE_GET_READY:
                st.session_state.current_phase = PHASE_WORKOUT
                st.session_state.current_time = st.session_state.workout_duration
                st.session_state.session_stats_initialized_for_run = True
                _play_sound_js(st.session_state.get('sound_on_workout_start'))
            
            elif previous_phase == PHASE_WORKOUT:
                st.session_state.current_phase = PHASE_REST
                st.session_state.current_time = st.session_state.rest_duration
                st.session_state.completed_rounds += 1
                _play_sound_js(st.session_state.get('sound_on_rest_start'))
                
                schedule = st.session_state.get('workout_schedule', [])
                if schedule:
                    current_idx = st.session_state.get('current_exercise_index', 0)
                    st.session_state.current_exercise_index = (current_idx + 1) % len(schedule)
            
            elif previous_phase == PHASE_REST:
                st.session_state.current_phase = PHASE_WORKOUT
                st.session_state.current_time = st.session_state.workout_duration
                _play_sound_js(st.session_state.get('sound_on_workout_start'))

    def get_current_time_display(self) -> str:
        if st.session_state.get('current_phase') == PHASE_PAUSED:
            return format_time(st.session_state.get('time_before_pause', 0))
        return format_time(st.session_state.get('current_time', 0))

    def get_current_exercise(self) -> str | None:
        schedule = st.session_state.get('workout_schedule', [])
        if not schedule: return None
        current_idx = st.session_state.get('current_exercise_index', 0)
        if 0 <= current_idx < len(schedule): return schedule[current_idx]
        return None

    def get_next_exercise(self) -> str | None:
        schedule = st.session_state.get('workout_schedule', [])
        if not schedule or len(schedule) < 1: return None
        if len(schedule) == 1: return None
        current_idx = st.session_state.get('current_exercise_index', 0)
        next_idx = (current_idx + 1) % len(schedule)
        return schedule[next_idx]

    def get_current_phase(self) -> str:
        return st.session_state.get('current_phase', PHASE_GET_READY)

    def is_running(self) -> bool: # *** ADDED THIS METHOD BACK ***
        """
        Returns True if the timer is actively counting down a non-paused phase
        (GET_READY, WORKOUT, REST).
        """
        return st.session_state.get('timer_running', False) and \
               st.session_state.get('current_phase') != PHASE_PAUSED

    def is_running_or_paused(self) -> bool:
        """Returns True if the timer_running flag is True (covers all active/paused states)."""
        return st.session_state.get('timer_running', False)

    def is_paused(self) -> bool:
        """Returns True if the timer is currently in a PAUSED state."""
        return st.session_state.get('timer_running', False) and \
               st.session_state.get('current_phase') == PHASE_PAUSED

    def get_progress_value(self) -> float:
        current_phase_for_progress = st.session_state.current_phase
        current_time_for_progress = st.session_state.current_time
        
        if current_phase_for_progress == PHASE_PAUSED:
            current_phase_for_progress = st.session_state.phase_before_pause
            current_time_for_progress = st.session_state.time_before_pause

        total_duration = 1
        if current_phase_for_progress == PHASE_WORKOUT:
            total_duration = st.session_state.get('workout_duration', 1)
        elif current_phase_for_progress == PHASE_REST:
            total_duration = st.session_state.get('rest_duration', 1)
        elif current_phase_for_progress == PHASE_GET_READY:
            total_duration = GET_READY_DURATION
        
        if total_duration == 0: return 0.0
        progress = (total_duration - current_time_for_progress) / total_duration
        return min(max(progress, 0.0), 1.0)

    def get_completed_rounds(self) -> int:
        return st.session_state.get('completed_rounds', 0)

    def get_total_workout_time(self) -> int:
        return st.session_state.get('accumulated_workout_seconds', 0)

    def get_total_rest_time(self) -> int:
        return st.session_state.get('accumulated_rest_seconds', 0)

    def get_total_elapsed_active_time(self) -> int:
        return self.get_total_workout_time() + self.get_total_rest_time()