# Home.py
import streamlit as st
import time
import os
from streamlit_js_eval import streamlit_js_eval

# Custom modules
from configs.app_config import PHASE_PAUSED
from utils.helpers import initialize_session_state_defaults
from core.session_manager import WorkoutSession # Ensure it uses the fixed version
from ui.sidebar_controls import render_sidebar_controls
from ui.main_display import render_main_display
from ai_components.agent_rag_pipeline import get_ai_feedback_for_session

# --- Page Configuration (should be the first Streamlit command) ---
st.set_page_config(
    page_title="Workout Timer - Home",
    page_icon="⏱️", # You can use an actual icon URL here later
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- PWA Setup: Link Manifest and Service Worker ---
# Ensure these paths are correct for your deployment.
# These assume manifest.json and sw.js are served from the root.
st.markdown(
    '<link rel="manifest" href="/manifest.json">',
    unsafe_allow_html=True
)
# Add theme color for browser UI (esp. mobile)
st.markdown(
    '<meta name="theme-color" content="#10ddc2">',
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


# --- JavaScript Sound Engine Injection (as provided) ---
js_sound_script = """
<script>
// Make functions and context global for accessibility
window.audioCtx = null;
window.isAudioUnlocked = false;

// Function to initialize/unlock AudioContext
window.unlockAudio = function() {
    // Only proceed if not already unlocked and running
    if (window.isAudioUnlocked && window.audioCtx && window.audioCtx.state === 'running') {
        // console.log("[AUDIO DEBUG] Audio Context already unlocked and running.");
        return;
    }

    if (!window.audioCtx) {
        try {
            window.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            console.log("[AUDIO DEBUG] Audio Context Created.");
        } catch(e) {
            console.error("[AUDIO DEBUG] Audio Context could not be created:", e);
            return; // Exit if creation failed
        }
    }

    if (window.audioCtx.state === 'suspended') {
        console.log("[AUDIO DEBUG] Audio Context is suspended, attempting to resume...");
        window.audioCtx.resume().then(() => {
            window.isAudioUnlocked = true;
            console.log("[AUDIO DEBUG] Audio Context Resumed successfully.");
            // Play a silent buffer to "prime" the audio context
            const buffer = window.audioCtx.createBuffer(1, 1, 22050);
            const source = window.audioCtx.createBufferSource();
            source.buffer = buffer;
            source.connect(window.audioCtx.destination);
            source.start(0);
            console.log("[AUDIO DEBUG] Silent buffer played.");
        }).catch(e => {
            console.error("[AUDIO DEBUG] Audio Context resume failed:", e);
            window.isAudioUnlocked = false;
        });
    } else if (window.audioCtx.state === 'running') {
        window.isAudioUnlocked = true;
        console.log("[AUDIO DEBUG] Audio Context is already running.");
    } else {
         console.log(`[AUDIO DEBUG] Audio Context in state: ${window.audioCtx.state}`);
    }
}

// Function to request permission AND unlock audio (NEW/MODIFIED)
window.requestSoundPermissionAndUnlock = function() {
    console.log("[AUDIO DEBUG] requestSoundPermissionAndUnlock called.");
    // 1. Try unlocking directly first
    window.unlockAudio();

    // 2. Check if Notification API exists
    if (!("Notification" in window)) {
        console.warn("[AUDIO DEBUG] Notification API not supported. Relying on click to unlock.");
        return;
    }

    // 3. Request Notification Permission
    Notification.requestPermission().then(perm => {
        if (perm === 'granted') {
            console.log('[AUDIO DEBUG] Notification permission granted.');
            // Try unlocking AGAIN after permission (important!)
            window.unlockAudio();
        } else {
            console.warn('[AUDIO DEBUG] Notification permission denied. Sound might not work.');
            // Still try unlocking, as the click itself might be enough
            window.unlockAudio();
        }
    }).catch(error => {
        console.error('[AUDIO DEBUG] Error requesting notification permission:', error);
        window.unlockAudio(); // Try unlocking even on error
    });
}

// Function to play sounds using Web Audio API (MODIFIED for robustness)
window.playJsSound = function(soundType = 'Beep_High', durationMs = 150) {
    if (!window.audioCtx || !window.isAudioUnlocked || window.audioCtx.state !== 'running') {
       console.warn(`[AUDIO DEBUG] Cannot play sound '${soundType}'. Context not ready (State: ${window.audioCtx ? window.audioCtx.state : 'null'}, Unlocked: ${window.isAudioUnlocked}). Needs user interaction/permission.`);
        // Try a final, gentle unlock attempt - MIGHT NOT WORK but worth a try
        if (window.audioCtx && window.audioCtx.state === 'suspended') {
            window.audioCtx.resume();
        }
        // If still not running, we must exit to avoid errors.
        if (!window.audioCtx || window.audioCtx.state !== 'running') {
            return;
        }
    }

    console.log(`[AUDIO DEBUG] Playing sound: ${soundType}`);
    const ctx = window.audioCtx;
    const oscillator = ctx.createOscillator();
    const gainNode = ctx.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(ctx.destination);

    let freq1 = 880; // Default: High A
    let freq2 = 0;   // For double beep
    let oscType = 'sine';

    switch(soundType) {
        case 'Beep_High': freq1 = 880; break; // A5
        case 'Beep_Low': freq1 = 440; break; // A4
        case 'Double_Beep': freq1 = 660; freq2 = 880; break; // E5 -> A5
        case 'Success': freq1 = 523.25; freq2 = 783.99; durationMs = 300; break; // C5 -> G5
        case 'Error': freq1 = 300; oscType = 'sawtooth'; break; // Low G# approx
        default: freq1 = 880; break;
    }

    const now = ctx.currentTime;
    const durationSec = durationMs / 1000;

    gainNode.gain.setValueAtTime(0.5, now); // Start at half volume
    gainNode.gain.linearRampToValueAtTime(0, now + durationSec); // Fade out

    oscillator.frequency.setValueAtTime(freq1, now);
    oscillator.type = oscType;
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
    # Check relative path first, then absolute. This helps in deployment.
    if not os.path.exists(file_path):
        file_path = os.path.join(os.path.dirname(__file__), "ui", "style.css")

    if os.path.exists(file_path):
        with open(file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"Custom CSS file not found at {file_path}")

load_css("ui/style.css") # Try relative first

# --- App Initialization ---
initialize_session_state_defaults()
workout_session = WorkoutSession()
selected_workout_duration, selected_rest_duration = render_sidebar_controls()

if not workout_session.is_running_or_paused(): # Update only if not running/paused
    workout_session.update_durations(selected_workout_duration, selected_rest_duration)

# --- AI Feedback State ---
if 'ai_feedback' not in st.session_state:
    st.session_state.ai_feedback = None
if 'ai_feedback_triggered' not in st.session_state:
    st.session_state.ai_feedback_triggered = False

# --- AI Feedback Trigger Function ---
def trigger_ai_feedback():
    st.session_state.ai_feedback_triggered = True
    st.session_state.ai_feedback = "🧠 Generating feedback..."

# --- Main Display Rendering ---
render_main_display(workout_session, trigger_ai_feedback)

# --- Generate AI Feedback (if flagged and paused) ---
if st.session_state.ai_feedback_triggered and workout_session.is_paused():
    st.session_state.ai_feedback_triggered = False # Reset flag
    with st.spinner("🤖 Getting AI feedback..."):
         st.session_state.ai_feedback = get_ai_feedback_for_session(workout_session)
    st.rerun()

# --- JavaScript Sound Trigger ---
sound_info = st.session_state.pop('sound_to_play', None)
if sound_info:
    sound_name = sound_info.get("name")
    if sound_name and sound_name != "None":
        print(f"Triggering JS Sound: {sound_name}")
        streamlit_js_eval(js_code=f"window.playJsSound('{sound_name}');")


# --- Timer Tick and Rerun ---
if workout_session.is_running():
    workout_session.tick()
    time.sleep(1) # Use time.sleep(1) for a 1-second interval
    st.rerun()
elif workout_session.is_paused() and st.session_state.ai_feedback is None and not st.session_state.ai_feedback_triggered:
     st.session_state.ai_feedback = "Pause your workout to receive AI feedback."

# --- Footer ---
st.markdown("---")
st.caption("Built with Streamlit and ❤️ for fitness.")