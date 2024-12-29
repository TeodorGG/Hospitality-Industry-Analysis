import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from data.fred_api import FREDReader
from config.settings import FRED_CONFIG


def analyze_scales(df: pd.DataFrame, metrics: list) -> dict:
    """Analyze and group metrics based on their scale"""
    scale_info = {}
    for metric in metrics:
        if metric in df.columns:
            data = df[metric].dropna()
            if not data.empty:
                scale_info[metric] = {
                    'mean': data.mean(),
                    'std': data.std(),
                    'magnitude': np.log10(abs(data.mean())) if data.mean() != 0 else 0
                }

    # Group metrics by order of magnitude
    grouped_metrics = {}
    if scale_info:
        magnitudes = [info['magnitude'] for info in scale_info.values()]
        unique_magnitudes = sorted(set([int(m) for m in magnitudes]))

        for magnitude in unique_magnitudes:
            metrics_in_group = [
                metric for metric, info in scale_info.items()
                if int(info['magnitude']) == magnitude
            ]
            if metrics_in_group:
                grouped_metrics[magnitude] = metrics_in_group

    return grouped_metrics


def create_grouped_charts(df: pd.DataFrame, metrics_groups: dict, category: str, title: str) -> list:
    """Create separate charts for each group of metrics with similar scale"""
    figures = []

    for magnitude, metrics in metrics_groups.items():
        fig = go.Figure()

        for metric in metrics:
            if metric in df.columns:
                series_info = FRED_CONFIG['series'][category].get(metric, {})
                correlation = series_info.get('correlation', 'Direct')
                data = df[metric].dropna()
                name = series_info.get('name', metric)

                # Set color based on correlation
                color = 'green' if correlation == 'Direct' else 'red'

                fig.add_trace(go.Scatter(
                    x=data.index,
                    y=data.values,
                    name=name,
                    mode='lines',
                    line=dict(color=color)
                ))

        fig.update_layout(
            title=f"{title} - Scale 10^{magnitude}",
            xaxis_title="Date",
            yaxis_title="Value",
            height=400,
            template="plotly_white",
            hovermode='x unified',
            showlegend=True
        )

        figures.append(fig)

    return figures


def show_category_data(df: pd.DataFrame, category_name: str):
    """Display data for a specific category"""
    if df.empty:
        st.warning(f"No data available for {category_name}")
        return

    st.subheader(f"{category_name} Metrics")

    # Get available metrics
    metrics = df.columns.tolist()

    # Group metrics by type (percent vs non-percent)
    percent_metrics = [m for m in metrics
                       if FRED_CONFIG['series'][category_name].get(m, {}).get('is_percent', False)]
    non_percent_metrics = [m for m in metrics if m not in percent_metrics]

    # Display non-percentage metrics with scale grouping
    if non_percent_metrics:
        st.subheader("Value Metrics")
        grouped_metrics = analyze_scales(df, non_percent_metrics)
        figures = create_grouped_charts(
            df,
            grouped_metrics,
            category_name,
            "Value Metrics Trends"
        )
        for fig in figures:
            st.plotly_chart(fig, use_container_width=True)

    # Display percentage metrics (no scale grouping needed)
    if percent_metrics:
        st.subheader("Percentage Metrics")
        fig = go.Figure()

        for metric in percent_metrics:
            series_info = FRED_CONFIG['series'][category_name].get(metric, {})
            correlation = series_info.get('correlation', 'Direct')
            data = df[metric].dropna()
            name = series_info.get('name', metric)

            color = 'green' if correlation == 'Direct' else 'red'

            fig.add_trace(go.Scatter(
                x=data.index,
                y=data.values,
                name=name,
                mode='lines',
                line=dict(color=color)
            ))

        fig.update_layout(
            title="Percentage Metrics Trends",
            xaxis_title="Date",
            yaxis_title="Percent",
            height=400,
            template="plotly_white",
            hovermode='x unified',
            showlegend=True
        )

        st.plotly_chart(fig, use_container_width=True)

    # Data tables
    with st.expander("View Data Tables"):
        st.dataframe(df.round(2))

        # Export option
        csv = df.to_csv()
        st.download_button(
            f"Download {category_name} Data (CSV)",
            csv,
            f"{category_name.lower()}_data.csv",
            "text/csv"
        )


def show_page():
    """Main page function"""
    st.title("Financial Data Viewer")

    # Initialize FRED reader
    fred_reader = FREDReader(FRED_CONFIG['api_key'])

    if st.button("Load/Refresh Data"):
        try:
            with st.spinner("Loading data from FRED..."):
                category_data = fred_reader.load_all_categories(FRED_CONFIG)
                if category_data:
                    st.session_state.category_data = category_data
                    st.success("Data loaded successfully!")
                else:
                    st.error("No data loaded")
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")

    # Display data if available
    if hasattr(st.session_state, 'category_data') and st.session_state.category_data:
        # Create tabs for categories
        categories = list(FRED_CONFIG['series'].keys())
        tabs = st.tabs(categories)

        # Display each category
        for tab, category in zip(tabs, categories):
            with tab:
                if category in st.session_state.category_data:
                    show_category_data(
                        st.session_state.category_data[category],
                        category
                    )
                else:
                    st.warning(f"No data available for {category}")