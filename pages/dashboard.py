import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
from config.settings import FRED_CONFIG


def get_metric_name(series_id, category):
    """Get friendly name for metric from config"""
    if category in FRED_CONFIG['series']:
        if series_id in FRED_CONFIG['series'][category]:
            return FRED_CONFIG['series'][category][series_id]['name']
    return series_id


def calculate_status(series):
    """
    Calculate status based on last 3 months of data
    Returns: status, color
    """
    last_three = series.tail(3)
    if len(last_three) < 3:
        return "Insufficient data", "gray"

    changes = last_three.pct_change()
    positive_changes = (changes > 0).sum()

    if positive_changes == 3:
        return "All clear", "green"
    elif positive_changes == 2 and changes.iloc[-1] > 0:
        return "Keep an eye", "lightgreen"
    elif positive_changes == 1 and changes.iloc[-1] < 0:
        return "Potential danger", "orange"
    elif positive_changes == 0:
        return "Danger", "red"
    else:
        return "Keep an eye", "yellow"


def create_metric_card(title, value, change, status, color):
    """Create a card for a single metric"""
    card_html = f"""
    <div style="
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin: 10px;
        background-color: {color}20;  /* 20 for transparency */
        border-left: 5px solid {color};">
        <h4 style="margin: 0; color: black;">{title}</h4>
        <p style="font-size: 24px; margin: 10px 0; color: black;">{value:,.2f}</p>
        <p style="margin: 0; color: {'green' if change >= 0 else 'red'}">
            {change:+.2f}% ({status})
        </p>
    </div>
    """
    return card_html


def show_dashboard(data_dict):
    """Display main dashboard"""
    st.title("Hospitality Industry Dashboard")

    # Organize indicators by category
    for category_name, category_df in data_dict.items():
        if category_df is not None and not category_df.empty:
            st.header(category_name)

            # Create grid for cards (3 per row)
            cols = st.columns(3)
            col_idx = 0

            for series_id in category_df.columns:
                series = category_df[series_id]

                # Get friendly metric name
                metric_name = get_metric_name(series_id, category_name)

                # Calculate required metrics
                current_value = series.iloc[-1]
                status, color = calculate_status(series)

                # Calculate month-over-month percentage change
                monthly_change = (series.iloc[-1] / series.iloc[-2] - 1) * 100 if len(series) > 1 else 0

                # Create and display the card
                card = create_metric_card(
                    metric_name,
                    current_value,
                    monthly_change,
                    status,
                    color
                )

                cols[col_idx].markdown(card, unsafe_allow_html=True)

                # Add mini chart below card
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=series.index[-12:],  # Last 12 months
                    y=series.values[-12:],
                    mode='lines',
                    line=dict(color=color)
                ))
                fig.update_layout(
                    height=100,
                    margin=dict(l=0, r=0, t=0, b=0),
                    showlegend=False,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                cols[col_idx].plotly_chart(fig, use_container_width=True)

                # Move to next column
                col_idx = (col_idx + 1) % 3

            # Add separator between categories
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
        st.warning("Please load data first")
        return

    show_dashboard(st.session_state.category_data)