import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from data.fred_api import FREDReader
from config.settings import FRED_CONFIG

# Define color palette
COLORS = {
    'Employment': {
        'USLAH': '#1f77b4',  # blue
        'CES7000000003': '#ff7f0e',  # orange
        'AWHAELAH': '#2ca02c',  # green
        'JTS7000JOL': '#d62728',  # red
        'IHLIDXUSTPHOTO': '#9467bd',  # purple
        'LNU04032241': '#8c564b',  # brown
        'CES7000000008': '#e377c2',  # pink
        'ADPWINDLSHPNERSA': '#7f7f7f',  # gray
        'JTS7000QUR': '#bcbd22',  # yellow-green
        'JTS7000HIL': '#17becf'  # cyan
    },
    'Revenues': {
        'DRCARC1Q027SBEA': '#1f77b4',  # blue
        'DFSARC1Q027SBEA': '#ff7f0e'  # orange
    },
    'Inflation': {
        'PCU721110721110': '#1f77b4',  # blue
        'PCU721110721110103': '#ff7f0e',  # orange
        'PCU5615105615102111': '#2ca02c',  # green
        'PCU561510561510211': '#d62728'  # red
    },
    'General': {
        'UMCSENT': '#1f77b4',  # blue
        'PI': '#ff7f0e',  # orange
        'PCE': '#2ca02c',  # green
        'PAYEMS': '#d62728',  # red
        'GDP': '#9467bd',  # purple
        'UNRATE': '#8c564b',  # brown
        'CCSA': '#e377c2',  # pink
        'DSPI': '#7f7f7f',  # gray
        'CPIAUCSL': '#bcbd22',  # yellow-green
        'DGS20': '#17becf',  # cyan
        'DGS10': '#ff9896',  # light red
        'DGS2': '#98df8a'  # light green
    }
}


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
                # Get metric info and friendly name
                series_info = FRED_CONFIG['series'][category].get(metric, {})
                friendly_name = series_info.get('name', metric)
                data = df[metric].dropna()

                # Get metric color
                color = COLORS[category].get(metric, '#000000')

                fig.add_trace(go.Scatter(
                    x=data.index,
                    y=data.values,
                    name=friendly_name,  # Use friendly name here
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
    """Display data for a specific category, treating each series independently"""
    if df.empty:
        st.warning(f"No data available for {category_name}")
        return

    st.subheader(f"{category_name} Metrics")

    # Create a mapping of metric codes to friendly names
    metric_names = {
        metric: FRED_CONFIG['series'][category_name][metric]['name']
        for metric in df.columns
    }

    # Iterate over each series individually
    for series_id in df.columns:
        st.subheader(metric_names[series_id])

        series = df[series_id].dropna()
        if series.empty:
            st.warning(f"No data available for {metric_names[series_id]}")
            continue

        # Display trend chart for the series
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=series.index,
            y=series.values,
            mode='lines',
            name=metric_names[series_id],
            line=dict(color=COLORS[category_name].get(series_id, '#000000'))
        ))
        fig.update_layout(
            title=f"Trend for {metric_names[series_id]}",
            xaxis_title="Date",
            yaxis_title="Value",
            height=400,
            template="plotly_white",
            hovermode='x unified',
            showlegend=True
        )

        st.plotly_chart(fig, use_container_width=True)

        # Display summary statistics for the series
        st.write(f"Summary Statistics for {metric_names[series_id]}")
        st.dataframe(series.describe().to_frame().T)

        # Export option with unique key
        csv = series.to_csv()
        st.download_button(
            label=f"Download {metric_names[series_id]} Data (CSV)",
            data=csv,
            file_name=f"{metric_names[series_id].replace(' ', '_').lower()}_data.csv",
            mime="text/csv",
            key=f"{category_name}_{series_id}_download"  # Unique key
        )

    # Provide an option to view the full data table
    with st.expander("View Full Data Table"):
        st.dataframe(df)



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
                    st.session_state['category_data'] = category_data
                    st.success("Data loaded successfully!")
                else:
                    st.error("No data loaded")
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")

    # Display data if available
    if 'category_data' in st.session_state and st.session_state['category_data']:
        # Create tabs for categories
        categories = list(FRED_CONFIG['series'].keys())
        tabs = st.tabs(categories)

        # Display each category
        for tab, category in zip(tabs, categories):
            with tab:
                if category in st.session_state['category_data']:
                    show_category_data(
                        st.session_state['category_data'][category],
                        category
                    )
                else:
                    st.warning(f"No data available for {category}")