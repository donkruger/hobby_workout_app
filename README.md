# Streamlit Workout App

A timer-based workout application with configurable workout and rest durations, exercise scheduling, AI-powered workout suggestions, and session insights. Built with Streamlit for a responsive user interface.

## Table of Contents

- [Features](#features)
- [Planned Features](#planned-features)
- [Setup](#setup)
- [Project Structure](#project-structure)
- [Architecture Overview](#architecture-overview)
  - [Core Logic](#core-logic)
  - [UI Components](#ui-components)
  - [Configuration](#configuration)
  - [Data Tracking & Visualization](#data-tracking--visualization)
  - [AI Components](#ai-components)
  - [State Management](#state-management)
- [Key Workflows](#key-workflows)
  - [Timer Operation](#timer-operation)
  - [Workout Scheduling](#workout-scheduling)
  - [AI Workout Generation](#ai-workout-generation)
- [Contributing](#contributing)

## Features

- **Customizable Timer:** Set workout and rest durations using interactive sliders.
- **Continuous Loop:** Automatically cycles through workout and rest phases.
- **Exercise Scheduling:**
  - Dedicated page to create and save a list of exercises.
  - Display of current and next exercises on the main timer page.
  - Looping through the scheduled exercises.
- **AI-Powered Workout Suggestions:**
  - Users can describe their desired workout on the "Add Workouts" page.
  - Utilizes the Gemini API to generate a list of exercises based on user input and current timer settings (exercise duration, rest duration).
  - Generated exercises populate the schedule editor for review and saving.
- **Workout Insights:**
  - Tracks and displays:
    - Number of rounds completed.
    - Total time exercising.
    - Total time rested.
    - Total active time.
  - Visual comparison of workout vs. rest time using a doughnut or bar chart (user-selectable).
- **Auditory Cues:** Configurable `beepy` sounds for phase transitions (workout end/rest start, rest end/workout start) and session start.
- **Dynamic UI:**
  - Animated gradient text for timer display and phase headers, changing colors based on workout/rest state.
  - Custom HTML progress bar with phase-specific gradient colors.
- **Multi-Page App Structure:**
  - "Home" page for the main timer interface.
  - "Add Workouts" page for managing exercise schedules and getting AI suggestions.
- **Persistent Settings Pane:** Sidebar for all configurations (timer durations, sounds, chart types) accessible from all pages, with a collapsed default state.

## Planned Features

- **Advanced Data Storage:** Save workout history to a persistent store (CSV, database).
- **Historical Visualizations:** More detailed charts and analytics based on saved workout history.
- **User Accounts/Profiles:** (If applicable for future scope).
- **Enhanced AI Coach:** Deeper integration of RAG pipeline for personalized feedback and dynamic workout adjustments beyond initial schedule generation.

## Setup

1.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure API Key (for AI features):**
    - Create a file named `secrets.toml` in a `.streamlit` directory at the root of your project (`workout_app/.streamlit/secrets.toml`).
    - Add your Gemini API key to this file:
      ```toml
      GEMINI_API_KEY = "YOUR_ACTUAL_API_KEY_HERE"
      ```
    - The application will attempt to load this key using `st.secrets["GEMINI_API_KEY"]`.
4.  **Run the Streamlit app:**
    ```bash
    streamlit run Home.py
    ```

## Project Structure

````

workout*app/
├── Home.py # Main Streamlit application (Timer UI)
├── pages/
│ └── 1*🏋️‍♂️_Add_workouts.py # Page for managing workout schedules & AI suggestions
├── ai_components/
│ ├── **init**.py
│ ├── workout_generator.py # Handles Gemini API calls for workout suggestions
│ └── agent_rag_pipeline.py # Placeholder for future advanced RAG
├── configs/
│ ├── **init**.py
│ └── app_config.py # Default settings, constants, sound/chart options
├── core/
│ ├── **init**.py
│ └── session_manager.py # Core timer logic, phase management, stat tracking
├── data_tracking/
│ ├── **init**.py
│ ├── storage.py # Placeholder for saving/loading workout data
│ └── visualization.py # Logic for displaying workout insights and charts
├── ui/
│ ├── **init**.py
│ ├── main_display.py # Renders the main content area of the Home page
│ ├── sidebar_controls.py # Renders the settings sidebar
│ └── style.css # Custom CSS for styling
├── utils/
│ ├── **init**.py
│ └── helpers.py # Utility functions (e.g., time formatting, session state init)
├── .streamlit/
│ └── secrets.toml # For API keys (not version controlled)
└── requirements.txt # Python dependencies
└── README.md # This file

```

## Architecture Overview

The application is designed with a modular approach, separating concerns into different packages and modules. It leverages Streamlit's multi-page app functionality and session state for interactivity and persistence.

### Core Logic (`core/`)

* **`session_manager.py` (`WorkoutSession` class):**
    * This is the heart of the timer functionality.
    * Manages the current state of the workout: `timer_running`, `current_phase` (WORKOUT/REST), `current_time` (countdown).
    * Handles transitions between workout and rest phases.
    * Updates and stores workout statistics: `completed_rounds`, `accumulated_workout_seconds`, `accumulated_rest_seconds`.
    * Manages the `current_exercise_index` for the workout schedule and provides methods to get the current and next exercises.
    * Integrates `beepy` to play sounds at phase transitions, based on user configuration.
    * All its state is persisted in `st.session_state` to survive Streamlit reruns.

### UI Components (`ui/`)

* **`sidebar_controls.py` (`render_sidebar_controls` function):**
    * Responsible for rendering all user-configurable settings in the Streamlit sidebar.
    * Includes sliders for workout/rest durations, select boxes for sound preferences, and a select box for the insights chart type.
    * Updates `st.session_state` with the chosen settings.
    * This function is called on both `Home.py` and `pages/1_🏋️‍♂️_Add_workouts.py` to ensure a consistent settings pane.
* **`main_display.py` (`render_main_display` function):**
    * Renders the primary content area of the `Home.py` page.
    * Displays the main timer, current phase (WORKOUT/REST) with icons, and animated gradient text.
    * Conditionally displays the current and next exercises from the schedule if available and the timer is running.
    * Renders a custom HTML progress bar with phase-specific gradient colors.
    * Includes Start, Stop, and Reset buttons.
    * Calls `display_workout_insights` to show statistics and charts.
* **`style.css`:**
    * Contains all custom CSS rules for the application.
    * Manages global fonts (Questrial for titles, Open Sans for body).
    * Defines CSS classes and keyframes for animated gradient text (timer, phase headers).
    * Styles the custom HTML progress bar, including its phase-specific gradient backgrounds.

### Configuration (`configs/`)

* **`app_config.py`:**
    * Stores default application settings and constants:
        * Default workout and rest durations.
        * Slider parameters (min, max, step).
        * Phase name constants (`PHASE_WORKOUT`, `PHASE_REST`).
        * Lists of available sound options (`BEEPY_SOUND_OPTIONS`) and default sound choices.
        * Lists of available chart types for insights (`INSIGHTS_CHART_OPTIONS`) and the default chart type.
        * The Gemini API model name (`GEMINI_API_MODEL_NAME`).

### Data Tracking & Visualization (`data_tracking/`)

* **`visualization.py` (`display_workout_insights` function):**
    * Fetches live statistics from the `WorkoutSession` instance.
    * Displays metrics: rounds completed, total workout time, total rest time, total active time.
    * Generates and displays either a doughnut chart (using Plotly) or a bar chart (using `st.bar_chart`) to compare workout vs. rest durations, based on user selection in the sidebar. The chart colors correspond to the workout/rest phases.
* **`storage.py`:**
    * Currently contains placeholder functions for saving and loading workout session data. Intended for future expansion to persist workout history.

### AI Components (`ai_components/`)

* **`workout_generator.py` (`get_ai_workout_suggestions` function):**
    * Integrates with the Google Gemini API.
    * Takes a user's textual description of their desired workout, along with the app's current configured exercise and rest durations.
    * Constructs a detailed prompt for the Gemini model, instructing it to consider the context (user request, exercise/rest times) and to determine an appropriate number of exercises for the requested total active workout duration.
    * Requests the output as a simple list of exercise names, one per line.
    * Parses the AI's response into a list of strings.
    * Includes API key handling (preferring `st.secrets`) and error handling.
* **`agent_rag_pipeline.py`:**
    * A placeholder for a more advanced agentic RAG (Retrieval Augmented Generation) pipeline for future AI coaching features. Not actively used by the current AI suggestion feature.
* **`prompts/`:**
    * A designated directory for storing prompt templates, although the current Gemini prompt is constructed directly in `workout_generator.py`.

### State Management

* **`st.session_state`:** Heavily utilized throughout the app to maintain state across reruns and between pages.
    * Managed primarily by `utils/helpers.py` (`initialize_session_state_defaults`) for setting up default values.
    * `core/session_manager.py` reads from and writes to `st.session_state` to manage all timer, stats, and schedule-tracking variables.
    * `ui/sidebar_controls.py` updates `st.session_state` based on user selections for settings.
    * `pages/1_🏋️‍♂️_Add_workouts.py` uses `st.session_state` to store the user's workout schedule, the AI prompt, and AI-generated text.

## Key Workflows

### Timer Operation (`Home.py` & `core/session_manager.py`)

1.  **Initialization:** `Home.py` initializes `WorkoutSession` and default states via `initialize_session_state_defaults`. Sidebar settings are rendered by `render_sidebar_controls`, updating session state.
2.  **Start:** User clicks "Start". `session.start_session()` in `session_manager.py` sets `st.session_state.timer_running = True`. If it's a fresh session (based on `session_stats_initialized_for_run`), stats and exercise index are reset, and a session start sound plays.
3.  **Tick Loop:**
    * If `timer_running` is true, `Home.py` calls `session.tick()` and then `st.rerun()` after a 1-second pause.
    * `session.tick()`:
        * Decrements `st.session_state.current_time`.
        * Accumulates workout/rest seconds.
        * If `current_time` reaches 0:
            * Switches `current_phase` (WORKOUT <-> REST).
            * Resets `current_time` to the new phase's duration.
            * If WORKOUT ended: increments `completed_rounds`, advances `current_exercise_index` (looping through `workout_schedule`), and plays the configured sound.
            * If REST ended: plays the configured sound.
4.  **Display:** `render_main_display` (called on each rerun) reads the current state from `session_manager` (which reads from `st.session_state`) to show the timer, phase, current/next exercises, progress bar, and insights.
5.  **Stop/Pause:** User clicks "Stop". `session.stop_session()` sets `timer_running = False`, halting the tick loop. Stats are preserved.
6.  **Reset:** User clicks "Reset". `session.stop_session()` is called, then `session.reset_session_stats()` clears all statistics, resets the exercise index, and resets the timer to the start of a workout phase.

### Workout Scheduling (`pages/1_🏋️‍♂️_Add_workouts.py`)

1.  **Navigation:** User selects "Add workouts" from the Streamlit MPA sidebar.
2.  **Display:** The page renders, showing the sidebar (via `render_sidebar_controls`) and its main content.
3.  **Input:**
    * User can manually type exercises into a `st.text_area`. The text area is pre-filled with the last AI-generated schedule (if any) or the currently saved schedule.
    * Alternatively, user can type a description into an `st.text_input` for AI suggestions.
4.  **AI Suggestion (Optional):**
    * User types a description (e.g., "10 minute core workout") and clicks "Get AI Suggestions".
    * `handle_ai_suggestions` callback is triggered.
    * It retrieves current `workout_duration` and `rest_duration` from `st.session_state`.
    * Calls `get_ai_workout_suggestions` from `ai_components/workout_generator.py` with the description and duration context.
    * The AI function calls the Gemini API with an engineered prompt.
    * If successful, the returned list of exercises is joined by newlines and stored in `st.session_state.ai_generated_schedule_text`. This state variable then populates the main `st.text_area` on the next rerun.
    * The AI prompt input field is cleared.
5.  **Saving:** User edits/confirms the exercises in the `st.text_area` and clicks "Save Workout List".
    * The content of the text area is parsed into a list of exercises.
    * `st.session_state.workout_schedule` is updated with this new list.
    * `st.session_state.current_exercise_index` is reset to 0.
    * `st.session_state.ai_generated_schedule_text` is cleared.
6.  **Navigation Back:** User can click "Go to Timer" (which uses `st.switch_page`) or use the sidebar to return to the "Home" page.

## Contributing

(Placeholder for future contribution guidelines, e.g., coding standards, how to report issues, feature request process.)

* Ensure API keys are managed via `.streamlit/secrets.toml` and not committed.
* Maintain modularity when adding new features.
* Update `requirements.txt` for new dependencies.
* Write clear docstrings and comments.
```

**How to use this in your `README.md`:**

1.  Copy the entire Markdown content above.
2.  Open your existing `workout_app/README.md` file.
3.  You can either replace the entire content or append this detailed documentation under a new major heading like "## Application Architecture and Logic". I'd recommend replacing or significantly restructuring if your current README is brief.
4.  Review and adjust any minor details or wordings to perfectly match your vision or any subtle changes you might have made locally. For instance, ensure the filenames in the "Project Structure" section match exactly if you've used different emojis or slightly different names.

This documentation provides a good overview for anyone (including your future self) looking to understand or contribute to the project.
````
