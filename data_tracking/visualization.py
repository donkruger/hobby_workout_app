# data_tracking/visualization.py
import streamlit as st
import pandas as pd
from utils.helpers import format_time
import plotly.graph_objects as go
from configs.app_config import CHART_TYPE_BAR, CHART_TYPE_DOUGHNUT # Import chart type constants

def display_workout_insights(session_manager):
    """
    Displays key workout statistics and a chart comparing workout vs. rest time.
    The chart type (bar or doughnut) is selectable via session_state.
    """
    st.subheader("📊 Workout Insights")

    rounds = session_manager.get_completed_rounds()
    total_workout_secs = session_manager.get_total_workout_time()
    total_rest_secs = session_manager.get_total_rest_time()
    total_elapsed_active_secs = session_manager.get_total_elapsed_active_time()

    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Rounds Completed", value=f"{rounds}")
        st.metric(label="Total Workout Time", value=format_time(total_workout_secs))
    with col2:
        st.metric(label="Total Rest Time", value=format_time(total_rest_secs))
        st.metric(label="Total Active Time", value=format_time(total_elapsed_active_secs))

    st.markdown("##### Workout vs. Rest Duration")

    if total_workout_secs > 0 or total_rest_secs > 0:
        workout_color_hex = "#ff4b4b" # Main warm color
        rest_color_hex = "#10ddc2"   # Main cool color

        # Data for charts
        activities = ["Workout Time", "Rest Time"]
        durations = [total_workout_secs, total_rest_secs]
        colors = [workout_color_hex, rest_color_hex]

        # Filter out zero values to prevent issues with Plotly Pie if one is zero
        # and to make the chart cleaner.
        valid_indices = [i for i, v in enumerate(durations) if v > 0]
        
        if not valid_indices:
            st.caption("No activity with duration > 0 to display chart.")
            return

        filtered_labels = [activities[i] for i in valid_indices]
        filtered_values = [durations[i] for i in valid_indices]
        filtered_colors = [colors[i] for i in valid_indices]

        # Get selected chart type from session state
        selected_chart_type = st.session_state.get('insights_chart_type', CHART_TYPE_DOUGHNUT)

        if selected_chart_type == CHART_TYPE_DOUGHNUT:
            fig = go.Figure(data=[go.Pie(
                labels=filtered_labels,
                values=filtered_values,
                hole=.4,
                marker_colors=filtered_colors,
                hoverinfo='label+percent+value',
                textinfo='label+percent',
                insidetextorientation='radial',
                sort=False
            )])
            fig.update_layout(
                margin=dict(t=20, b=20, l=20, r=20),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        elif selected_chart_type == CHART_TYPE_BAR:
            chart_data_df = pd.DataFrame({
                "Activity": filtered_labels,
                "Duration (seconds)": filtered_values,
                "Color": filtered_colors
            })
            st.bar_chart(
                chart_data_df,
                x="Activity",
                y="Duration (seconds)",
                color="Color"
            )
        else:
            st.warning(f"Unknown chart type selected: {selected_chart_type}")
            
    else:
        st.caption("No activity yet to display chart.")

# Placeholder for historical charts
def render_historical_charts(history_data):
    if not history_data:
        st.write("No historical workout data available to display charts.")
        return
    st.write("Placeholder: Historical charts would be displayed here.")