# Home.py
import streamlit as st
import time
import os
from streamlit_js_eval import streamlit_js_eval # Import

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


# For custom icon in PWA

st.markdown(
    '<link rel="manifest" href="/manifest.json">',
    unsafe_allow_html=True
)
st.markdown(
    """
    <script>
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js').then(registration => {
          console.log('SW registered: ', registration);
        }).catch(registrationError => {
          console.log('SW registration failed: ', registrationError);
        });
      });
    }
    </script>
    """,
    unsafe_allow_html=True
)

# --- JavaScript Sound Engine Injection ---
js_sound_script = """
<script>
// Make functions and context global for accessibility
window.audioCtx = null;
window.isAudioUnlocked = false;

// Function to initialize/unlock AudioContext (MUST be called via user interaction)
window.unlockAudio = function() {
    if (!window.isAudioUnlocked && !window.audioCtx) {
        try {
            window.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            // Play a silent buffer to "prime" the audio context on some browsers
            const buffer = window.audioCtx.createBuffer(1, 1, 22050);
            const source = window.audioCtx.createBufferSource();
            source.buffer = buffer;
            source.connect(window.audioCtx.destination);
            source.start(0);
            window.isAudioUnlocked = true;
            console.log("Audio Context Unlocked/Primed.");
        } catch(e) {
            console.error("Audio Context could not be created/unlocked:", e);
            window.isAudioUnlocked = false; // Ensure it's false on error
        }
    } else if (window.audioCtx && window.audioCtx.state === 'suspended') {
        window.audioCtx.resume().then(() => {
            window.isAudioUnlocked = true;
            console.log("Audio Context Resumed.");
        }).catch(e => console.error("Audio Context resume failed:", e));
    }
}

// Function to play sounds using Web Audio API
window.playJsSound = function(soundType = 'Beep_High', durationMs = 150) {
    if (!window.audioCtx || !window.isAudioUnlocked) {
         console.warn("Audio Context not ready. Trying to unlock (might fail if not user-init).");
         window.unlockAudio(); // Try again, but it might fail here
         if (!window.isAudioUnlocked) {
            console.error("Audio remains locked. Cannot play sound:", soundType);
            return; // Exit if still locked
         }
    }
    // Ensure context is running
    if (window.audioCtx.state === 'suspended') {
        window.audioCtx.resume();
    }

    const ctx = window.audioCtx;
    const oscillator = ctx.createOscillator();
    const gainNode = ctx.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(ctx.destination);

    let freq1 = 880; // Default: High A
    let freq2 = 0;   // For double beep

    switch(soundType) {
        case 'Beep_High': freq1 = 880; break; // A5
        case 'Beep_Low': freq1 = 440; break; // A4
        case 'Double_Beep': freq1 = 660; freq2 = 880; break; // E5 -> A5
        case 'Success': freq1 = 523.25; freq2 = 783.99; durationMs = 300; break; // C5 -> G5
        case 'Error': freq1 = 300; oscillator.type = 'sawtooth'; break; // Low G# approx
        default: freq1 = 880; break;
    }

    const now = ctx.currentTime;
    const durationSec = durationMs / 1000;

    gainNode.gain.setValueAtTime(0.5, now); // Start at half volume
    gainNode.gain.linearRampToValueAtTime(0, now + durationSec); // Fade out

    oscillator.frequency.setValueAtTime(freq1, now);
    oscillator.type = (oscillator.type === 'sawtooth') ? 'sawtooth' : 'sine';
    oscillator.start(now);
    oscillator.stop(now + durationSec);

    // Handle second beep/note for Double_Beep and Success
    if (freq2 !== 0) {
        const osc2 = ctx.createOscillator();
        const gain2 = ctx.createGain();
        osc2.connect(gain2);
        gain2.connect(ctx.destination);

        const delay = (soundType === 'Success') ? 0.15 : 0.1; // Delay for 2nd note
        const duration2 = (soundType === 'Success') ? durationSec - delay : durationSec / 2;

        gain2.gain.setValueAtTime(0.5, now + delay);
        gain2.gain.linearRampToValueAtTime(0, now + delay + duration2);
        osc2.frequency.setValueAtTime(freq2, now + delay);
        osc2.type = 'sine';
        osc2.start(now + delay);
        osc2.stop(now + delay + duration2);
    }
}
</script>
"""
st.markdown(js_sound_script, unsafe_allow_html=True)


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

# --- JavaScript Sound Trigger ---
sound_info = st.session_state.pop('sound_to_play', None)
if sound_info:
    sound_name = sound_info.get("name")
    if sound_name and sound_name != "None":
        print(f"Triggering JS Sound: {sound_name}") # For debugging
        streamlit_js_eval(js_code=f"window.playJsSound('{sound_name}');")


# --- Timer Tick and Rerun ---
if workout_session.is_running():
    workout_session.tick()
    time.sleep(1)
    st.rerun()

st.markdown("---")
st.caption("Built with Streamlit and ❤️ for fitness.")