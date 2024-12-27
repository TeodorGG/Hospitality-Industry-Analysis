import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from data.fred_api import FREDReader
from config.settings import FRED_CONFIG


def analyze_scales(df: pd.DataFrame, metrics: list) -> dict:
    """
    Analizează și grupează metricile bazat pe scala lor
    """
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

    # Grupează metricile bazat pe ordinul de mărime
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


def create_grouped_charts(df: pd.DataFrame, metrics_groups: dict, title: str) -> list:
    """
    Creează grafice separate pentru fiecare grup de metrici cu scală similară
    """
    figures = []

    for magnitude, metrics in metrics_groups.items():
        fig = go.Figure()

        for metric in metrics:
            if metric in df.columns:
                data = df[metric].dropna()
                fig.add_trace(go.Scatter(
                    x=data.index,
                    y=data.values,
                    name=metric,
                    mode='lines'
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


def show_category_data(df: pd.DataFrame, category_name: str, series_info: dict):
    """Display data for a specific category"""
    if df is None or df.empty:
        st.warning(f"No data available for {category_name}")
        return

    # Main metrics
    st.subheader(f"{category_name} Metrics")
    metrics = df.columns.tolist()
    base_metrics = [m for m in metrics if not (m.endswith('_YoY') or m.endswith('_MoM'))]

    if base_metrics:
        # Grupează metricile bazat pe scală
        grouped_metrics = analyze_scales(df, base_metrics)
        figures = create_grouped_charts(df, grouped_metrics, f"{category_name} Trends")

        # Afișează graficele grupate
        for fig in figures:
            st.plotly_chart(fig, use_container_width=True)

    # Changes (YoY or MoM)
    change_metrics = [m for m in metrics if m.endswith('_YoY') or m.endswith('_MoM')]
    if change_metrics:
        st.subheader("Rate of Change")
        # Grupează metricile de schimbare
        grouped_changes = analyze_scales(df, change_metrics)
        change_figures = create_grouped_charts(
            df,
            grouped_changes,
            f"{category_name} Changes"
        )

        # Afișează graficele de schimbare
        for fig in change_figures:
            st.plotly_chart(fig, use_container_width=True)

    # Data table with summary
    st.subheader(f"{category_name} Summary Statistics")
    summary_df = pd.DataFrame({
        'Mean': df.mean(),
        'Std Dev': df.std(),
        'Min': df.min(),
        'Max': df.max()
    }).round(2)
    st.dataframe(summary_df)

    # Raw data expandable
    with st.expander("Show Raw Data"):
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
    st.title("Hospitality Industry Analysis")

    # Initialize FRED reader
    fred_reader = FREDReader(api_key=FRED_CONFIG['api_key'])

    # Load data button
    if st.button("Load Industry Data"):
        with st.spinner("Loading data from FRED..."):
            category_data = fred_reader.load_all_categories(FRED_CONFIG)

            if category_data:
                st.session_state.category_data = category_data
                st.success("Data loaded successfully!")

                # Afișează sumarul datelor încărcate
                st.subheader("Data Overview")
                for category, data in category_data.items():
                    if data is not None and not data.empty:
                        st.write(f"{category}: {len(data.columns)} metrics, {len(data)} observations")
            else:
                st.error("Failed to load data")

    # Display data if available
    if hasattr(st.session_state, 'category_data') and st.session_state.category_data:
        # Create tabs for categories
        categories = list(FRED_CONFIG['series'].keys())
        tabs = st.tabs(categories)

        # Display each category in its tab
        for tab, category in zip(tabs, categories):
            with tab:
                if category in st.session_state.category_data:
                    category_df = st.session_state.category_data[category]
                    if category_df is not None and not category_df.empty:
                        show_category_data(
                            category_df,
                            category,
                            FRED_CONFIG['series'][category]
                        )
                    else:
                        st.warning(f"Empty or invalid data for {category}")
                else:
                    st.warning(f"No data available for {category}")

        # Cross-category analysis
        with st.expander("Cross-Category Analysis"):
            st.subheader("Correlation Analysis")

            # Combine all metrics
            all_data = pd.DataFrame()
            for category, df in st.session_state.category_data.items():
                if df is not None and not df.empty:
                    if all_data.empty:
                        all_data = df.copy()
                    else:
                        all_data = all_data.join(df, how='outer')

            if not all_data.empty:
                # Calculate and display correlation matrix
                corr_matrix = all_data.corr()
                fig_corr = px.imshow(
                    corr_matrix,
                    title="Cross-Category Correlation Matrix",
                    labels=dict(color="Correlation"),
                    color_continuous_scale="RdBu"
                )
                st.plotly_chart(fig_corr, use_container_width=True)