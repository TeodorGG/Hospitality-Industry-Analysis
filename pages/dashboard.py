import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from config.settings import FRED_CONFIG


def calculate_change_value(series, series_info):
    """Calculate change value based on series type and settings"""
    if len(series) < 2:
        return 0

    correlation = series_info.get('correlation', 'Direct')
    units = series_info.get('units', 'lin')
    is_percent = series_info.get('is_percent', False)

    # For series already in YoY percent change (units='pc1')
    if units == 'pc1':
        change = series.iloc[-1]
    else:
        if is_percent:
            # For percentage metrics, use absolute change
            change = series.iloc[-1] - series.iloc[-2]
        else:
            # For non-percentage metrics, calculate percent change
            change = (series.iloc[-1] / series.iloc[-2] - 1) * 100

    # Inverse the change for inverse correlation
    return -change if correlation == 'Inverse' else change


def calculate_status(series, series_info):
    """Calculate status based on series configuration"""
    if len(series) < 4:  # Need at least 4 values to get 3 changes
        return "Insufficient data", "gray"

    correlation = series_info.get('correlation', 'Direct')
    units = series_info.get('units', 'lin')

    # For YoY percent change series, use the values directly
    if units == 'pc1':
        changes = series.tail(3)
    else:
        # Get last 4 values and calculate 3 changes
        last_four = series.tail(4)
        changes = last_four.pct_change().tail(3)

    # Adjust for inverse correlation
    if correlation == 'Inverse':
        changes = -changes

    positive_changes = (changes > 0).sum()
    latest_change = changes.iloc[-1] > 0

    if positive_changes == 3:
        return "All clear", "green"
    elif positive_changes == 2 and latest_change:
        return "Keep an eye", "lightgreen"
    elif positive_changes == 1 and not latest_change:
        return "Potential danger", "orange"
    elif positive_changes == 0:
        return "Danger", "red"
    else:
        return "Keep an eye", "yellow"


def create_metric_card(title, value, change, status, color, is_percent=False):
    """Create a metric card with proper formatting"""
    value_display = f"{value:.2f}%" if is_percent else f"{value:,.2f}"

    card_html = f"""
    <div style="
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin: 10px;
        background-color: {color}20;
        border-left: 5px solid {color};">
        <h4 style="margin: 0; color: black;">{title}</h4>
        <p style="font-size: 24px; margin: 10px 0; color: black;">{value_display}</p>
        <p style="margin: 0; color: {'green' if change >= 0 else 'red'}">
            {change:+.2f}% ({status})
        </p>
    </div>
    """
    return card_html


def show_dashboard(data_dict):
    """Display the main dashboard with grouped metrics for each category"""
    st.title("Hospitality Industry Dashboard")

    for category_name, category_df in data_dict.items():
        if category_df is not None and not category_df.empty:
            st.header(category_name)

            # Iterate through metrics in the category
            cols = st.columns(3)  # Layout: 3 columns for metric cards and charts
            col_idx = 0

            for metric in category_df.columns:
                series = category_df[metric].dropna()
                if series.empty:
                    st.warning(f"No data available for {metric}")
                    continue

                # Retrieve metric info
                series_info = FRED_CONFIG['series'][category_name].get(metric, {})
                metric_name = series_info.get('name', metric)
                is_percent = series_info.get('is_percent', False)

                # Calculate metrics
                current_value = series.iloc[-1]
                change = calculate_change_value(series, series_info)
                status, color = calculate_status(series, series_info)

                # Create and display card
                card = create_metric_card(
                    metric_name,
                    current_value,
                    change,
                    status,
                    color,
                    is_percent or series_info.get('units') == 'pc1'
                )
                cols[col_idx].markdown(card, unsafe_allow_html=True)

                # Add trend chart
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=series.index,
                    y=series.values,
                    mode='lines',
                    name=metric_name,
                    line=dict(color=color)
                ))

                fig.update_layout(
                    title=f"Trend for {metric_name}",
                    xaxis_title="Date",
                    yaxis_title="Value",
                    height=300,
                    template="plotly_white",
                    hovermode='x unified',
                    showlegend=False
                )

                cols[col_idx].plotly_chart(fig, use_container_width=True)

                # Add download button with unique key
                csv = series.to_csv()
                cols[col_idx].download_button(
                    label=f"Download {metric_name} Data (CSV)",
                    data=csv,
                    file_name=f"{metric_name.replace(' ', '_').lower()}_data.csv",
                    mime="text/csv",
                    key=f"{category_name}_{metric}_download"  # Unique key for each button
                )

                col_idx = (col_idx + 1) % 3

            st.markdown("---")

    # Status legend
    st.sidebar.header("Status Legend")
    statuses = {
        "All clear": "green",
        "Keep an eye": "yellow",
        "Potential danger": "orange",
        "Danger": "red"
    }

    for status, color in statuses.items():
        st.sidebar.markdown(
            f'<div style="padding: 10px; border-radius: 5px; background-color: {color}20; '
            f'border-left: 5px solid {color}; margin: 5px 0;">{status}</div>',
            unsafe_allow_html=True
        )



def show_page():
    """Main page function"""
    if not hasattr(st.session_state, 'category_data'):
        st.warning("Please load data first in the Data Viewer page")
        return

    show_dashboard(st.session_state.category_data)