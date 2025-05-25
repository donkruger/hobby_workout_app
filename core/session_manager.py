# workout_app/core/session_manager.py
import streamlit as st
from configs.app_config import (
    PHASE_GET_READY,
    PHASE_WORKOUT,
    PHASE_REST,
    PHASE_PAUSED,
    GET_READY_DURATION,
)
from utils.helpers import format_time
from streamlit_push_notifications import send_push # ▶ NEW ◀


# ----------------------------------------------------------------------
# 🔊 Sound map – point each logical sound to the MP3 you prefer
# ----------------------------------------------------------------------
_SOUND_URLS: dict[str, str] = {
    "Beep_High": "https://cdn.pixabay.com/audio/2024/02/19/audio_e4043ea6be.mp3",
    "Beep_Low": "https://cdn.pixabay.com/audio/2024/02/19/audio_e4043ea6be.mp3",
    "Double_Beep": "https://cdn.pixabay.com/audio/2024/02/19/audio_e4043ea6be.mp3",
    "Success": "https://cdn.pixabay.com/audio/2024/02/19/audio_e4043ea6be.mp3",
    "Error": "https://cdn.pixabay.com/audio/2024/02/19/audio_e4043ea6be.mp3",
}


# ----------------------------------------------------------------------
# Core helper – plays sound with two fallbacks
# ----------------------------------------------------------------------
def _play_sound_js(sound_name_or_id: str | None) -> None:
    """
    Play the chosen sound.

    1. Fire a push-notification that embeds <audio> (works even when
       AudioContext is still locked on iOS/Android).
    2. ALSO trigger the legacy `window.playJsSound()` Synth-beep so you
       still get feedback if notifications are blocked or throttled.
    """
    if not st.session_state.get("sound_master_enabled", True):
        return
    if not sound_name_or_id or sound_name_or_id.lower() == "none":
        return

    # ------------------------------------------------------------------ #
    # 1️⃣ Push-notification with UNIQUE TAG (prevents browser merging)
    # ------------------------------------------------------------------ #
    import time, random, string

    tag = f"beep-{time.time_ns()}-{random.choice(string.ascii_lowercase)}"
    sound_url = _SOUND_URLS.get(sound_name_or_id, _SOUND_URLS["Beep_High"])

    # Empty title/body ⇒ no popup text, just invisible notification + audio
    send_push(
        title="",
        body="",
        sound_path=sound_url,
        tag=tag,                      # 👈 guarantees a fresh notification
        only_when_on_other_tab=False,
    )

    # ------------------------------------------------------------------ #
    # 2️⃣ Legacy Synth fallback – still used by Home.py
    # ------------------------------------------------------------------ #
    st.session_state.sound_to_play = {
        "name": sound_name_or_id,
        "trigger": st.session_state.get("sound_trigger_count", 0) + 1,
    }
    st.session_state.sound_trigger_count = st.session_state.get(
        "sound_trigger_count", 0
    ) + 1

# ----------------------------------------------------------------------
# Workout-timer state machine (unchanged apart from sound helper)
# ----------------------------------------------------------------------
class WorkoutSession:
    def __init__(self):
        pass

    # ----- utility -----------------------------------------------------
    def _clear_pause_state(self):
        st.session_state.phase_before_pause = None
        st.session_state.time_before_pause = 0

    def _set_time_for_current_phase(self):
        if st.session_state.current_phase == PHASE_WORKOUT:
            st.session_state.current_time = st.session_state.workout_duration
        elif st.session_state.current_phase == PHASE_REST:
            st.session_state.current_time = st.session_state.rest_duration
        elif st.session_state.current_phase == PHASE_GET_READY:
            st.session_state.current_time = GET_READY_DURATION

    # ----- external API ------------------------------------------------
    def update_durations(self, workout_duration: int, rest_duration: int):
        st.session_state.workout_duration = workout_duration
        st.session_state.rest_duration = rest_duration
        if (
            not st.session_state.get("timer_running", False)
            and st.session_state.current_phase != PHASE_PAUSED
        ):
            st.session_state.current_phase = PHASE_GET_READY
            st.session_state.current_time = GET_READY_DURATION
            st.session_state.session_stats_initialized_for_run = False
            self._clear_pause_state()

    def start_session(self):
        if (
            not st.session_state.get("timer_running", False)
            and st.session_state.current_phase != PHASE_PAUSED
        ):
            st.session_state.timer_running = True
            if not st.session_state.get("session_stats_initialized_for_run", False):
                st.session_state.current_phase = PHASE_GET_READY
                st.session_state.current_time = GET_READY_DURATION
                st.session_state.accumulated_workout_seconds = 0
                st.session_state.accumulated_rest_seconds = 0
                st.session_state.completed_rounds = 0
                st.session_state.current_exercise_index = 0
                self._clear_pause_state()
                _play_sound_js(st.session_state.get("sound_on_session_start"))
            elif st.session_state.current_time == 0:
                self._set_time_for_current_phase()

    def pause_session(self):
        if (
            st.session_state.timer_running
            and st.session_state.current_phase != PHASE_PAUSED
        ):
            st.session_state.phase_before_pause = st.session_state.current_phase
            st.session_state.time_before_pause = st.session_state.current_time
            st.session_state.current_phase = PHASE_PAUSED

    def resume_session(self):
        if (
            st.session_state.timer_running
            and st.session_state.current_phase == PHASE_PAUSED
        ):
            st.session_state.current_phase = st.session_state.phase_before_pause
            st.session_state.current_time = st.session_state.time_before_pause
            self._clear_pause_state()

    def stop_session(self):
        st.session_state.timer_running = False
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

    # ----- main tick ---------------------------------------------------
    def tick(self):
        if not st.session_state.get("timer_running", False):
            return

        current_phase = st.session_state.current_phase

        if current_phase == PHASE_PAUSED:
            st.session_state.accumulated_rest_seconds += 1
            return

        if (
            current_phase in (PHASE_REST, PHASE_GET_READY)
            and st.session_state.current_time > 0
        ):
            st.session_state.accumulated_rest_seconds += 1
        elif current_phase == PHASE_WORKOUT and st.session_state.current_time > 0:
            st.session_state.accumulated_workout_seconds += 1

        if st.session_state.current_time > 0:
            st.session_state.current_time -= 1
            return  # still counting down

        # -------------------------------- phase finished ---------------
        previous_phase = st.session_state.current_phase

        if previous_phase == PHASE_GET_READY:
            st.session_state.current_phase = PHASE_WORKOUT
            st.session_state.current_time = st.session_state.workout_duration
            st.session_state.session_stats_initialized_for_run = True
            _play_sound_js(st.session_state.get("sound_on_workout_start"))

        elif previous_phase == PHASE_WORKOUT:
            st.session_state.current_phase = PHASE_REST
            st.session_state.current_time = st.session_state.rest_duration
            st.session_state.completed_rounds += 1
            _play_sound_js(st.session_state.get("sound_on_rest_start"))
            # <<< CHANGE: Index increment is REMOVED from here >>>

        elif previous_phase == PHASE_REST:
            # <<< CHANGE: Index increment is ADDED here >>>
            schedule = st.session_state.get("workout_schedule", [])
            if schedule:
                # Only increment if we are *not* on the very last exercise AND
                # about to loop. However, the modulo handles looping.
                # We need to increment *before* starting the next workout.
                current_idx = st.session_state.get("current_exercise_index", 0)
                st.session_state.current_exercise_index = (current_idx + 1) % len(
                    schedule
                )

            st.session_state.current_phase = PHASE_WORKOUT
            st.session_state.current_time = st.session_state.workout_duration
            _play_sound_js(st.session_state.get("sound_on_workout_start"))

    # ----- getters -----------------------------------------------------
    def get_current_time_display(self) -> str:
        if st.session_state.get("current_phase") == PHASE_PAUSED:
            return format_time(st.session_state.get("time_before_pause", 0))
        return format_time(st.session_state.get("current_time", 0))

    def get_current_exercise(self) -> str | None:
        schedule = st.session_state.get("workout_schedule", [])
        if not schedule:
            return None
        idx = st.session_state.get("current_exercise_index", 0)
        return schedule[idx] if 0 <= idx < len(schedule) else None

    def get_next_exercise(self) -> str | None:
        schedule = st.session_state.get("workout_schedule", [])
        if len(schedule) < 2:
            return None
        idx = st.session_state.get("current_exercise_index", 0)
        return schedule[(idx + 1) % len(schedule)]

    def get_current_phase(self) -> str:
        return st.session_state.get("current_phase", PHASE_GET_READY)

    def is_running(self) -> bool:
        return st.session_state.get("timer_running", False) and st.session_state.get(
            "current_phase"
        ) != PHASE_PAUSED

    def is_running_or_paused(self) -> bool:
        return st.session_state.get("timer_running", False)

    def is_paused(self) -> bool:
        return st.session_state.get("timer_running", False) and st.session_state.get(
            "current_phase"
        ) == PHASE_PAUSED

    def get_progress_value(self) -> float:
        phase = st.session_state.current_phase
        secs_left = st.session_state.current_time

        if phase == PHASE_PAUSED:
            phase = st.session_state.phase_before_pause
            secs_left = st.session_state.time_before_pause

        total = (
            st.session_state.get("workout_duration", 1)
            if phase == PHASE_WORKOUT
            else st.session_state.get("rest_duration", 1)
            if phase == PHASE_REST
            else GET_READY_DURATION
            if phase == PHASE_GET_READY
            else 1
        )

        # Handle division by zero or negative total gracefully
        if total <= 0:
            return 0.0

        return min(max((total - secs_left) / total, 0.0), 1.0)

    def get_completed_rounds(self) -> int:
        return st.session_state.get("completed_rounds", 0)

    def get_total_workout_time(self) -> int:
        return st.session_state.get("accumulated_workout_seconds", 0)

    def get_total_rest_time(self) -> int:
        return st.session_state.get("accumulated_rest_seconds", 0)

    def get_total_elapsed_active_time(self) -> int:
        return self.get_total_workout_time() + self.get_total_rest_time()