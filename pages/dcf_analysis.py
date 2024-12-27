import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from data.fred_api import FREDReader
from config.settings import FRED_CONFIG, DISPLAY_CONFIG
import pandas as pd

def create_metric_chart(df, metrics, title="Financial Metrics Over Time"):
    """Create a line chart for selected metrics"""
    fig = go.Figure()

    for metric in metrics:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[metric],
            name=metric,
            mode='lines+markers'
        ))

    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Value (Billions USD)",
        hovermode='x unified',
        showlegend=True
    )

    return fig


def show_page():
    st.title("Financial Data Viewer")

    # Initialize FRED reader
    fred_reader = FREDReader()

    # Date selection
    st.header("Select Date Range")
    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input(
            "Start Date",
            datetime.now() - timedelta(days=365 * 5)
        )

    with col2:
        end_date = st.date_input(
            "End Date",
            datetime.now()
        )

    # Load data button
    if st.button("Load Financial Data"):
        with st.spinner("Loading data from FRED..."):
            # Load raw data
            raw_data = fred_reader.load_all_series(
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )

            if raw_data:
                # Process data
                processed_data = fred_reader.process_data(raw_data)
                if processed_data is not None:
                    st.session_state.financial_data = processed_data
                    st.success("Data loaded successfully!")

    # Display data if available
    if 'financial_data' in st.session_state and st.session_state.financial_data is not None:
        df = st.session_state.financial_data

        # Create tabs for different views
        tabs = st.tabs([
            "Data Overview",
            "Financial Charts",
            "Metrics Analysis"
        ])

        with tabs[0]:
            st.subheader("Financial Data Overview")
            st.dataframe(
                df.style.format(DISPLAY_CONFIG['number_format']),
                height=400
            )

            # Download button
            csv = df.to_csv()
            st.download_button(
                "Download Data (CSV)",
                csv,
                "financial_data.csv",
                "text/csv"
            )

        with tabs[1]:
            st.subheader("Financial Metrics Visualization")

            # Metric selection
            selected_metrics = st.multiselect(
                "Select metrics to display",
                df.columns.tolist(),
                default=list(FRED_CONFIG['required_metrics'].keys())[:2]
            )

            if selected_metrics:
                # Create and display chart
                fig = create_metric_chart(df, selected_metrics)
                st.plotly_chart(fig, use_container_width=True)

                # Display correlation heatmap
                st.subheader("Correlation Analysis")
                fig_corr = px.imshow(
                    df[selected_metrics].corr(),
                    title="Correlation Matrix",
                    labels=dict(color="Correlation")
                )
                st.plotly_chart(fig_corr, use_container_width=True)

        with tabs[2]:
            st.subheader("Financial Metrics Analysis")

            # Calculate basic statistics
            stats_df = df.describe()
            st.dataframe(
                stats_df.style.format(DISPLAY_CONFIG['number_format']),
                height=300
            )

            # Calculate growth rates
            st.subheader("Growth Rates")
            growth_rates = df.pct_change().mean() * 100
            growth_df = pd.DataFrame({
                'Metric': growth_rates.index,
                'Average Growth Rate (%)': growth_rates.values
            })
            st.dataframe(
                growth_df.set_index('Metric').style.format("{:.2f}%"),
                height=300
            )

            # Create growth rates chart
            fig_growth = go.Figure()
            for column in df.columns:
                fig_growth.add_trace(go.Scatter(
                    x=df.index,
                    y=df[column].pct_change() * 100,
                    name=column,
                    mode='lines'
                ))

            fig_growth.update_layout(
                title="Growth Rates Over Time",
                xaxis_title="Date",
                yaxis_title="Growth Rate (%)",
                showlegend=True
            )

            st.plotly_chart(fig_growth, use_container_width=True)