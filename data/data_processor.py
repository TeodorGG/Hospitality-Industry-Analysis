import pandas as pd
import numpy as np
from config.settings import FRED_CONFIG
import streamlit as st


class FinancialDataProcessor:
    def __init__(self):
        self.required_metrics = FRED_CONFIG['required_metrics']
        self.calculated_metrics = FRED_CONFIG['calculated_metrics']

    def validate_data(self, df: pd.DataFrame) -> bool:
        """Validate that all required metrics are present"""
        required_columns = set(self.required_metrics.keys())
        existing_columns = set(df.columns)
        missing_columns = required_columns - existing_columns

        if missing_columns:
            st.error(f"Missing required metrics: {missing_columns}")
            return False
        return True

    def calculate_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all derived financial metrics"""
        if not self.validate_data(df):
            return df

        result_df = df.copy()

        # Calculate each metric in order
        for metric_name, metric_info in self.calculated_metrics.items():
            try:
                result_df[metric_name] = metric_info['formula'](result_df)
            except Exception as e:
                st.error(f"Error calculating {metric_name}: {str(e)}")

        return result_df

    def calculate_growth_rates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate year-over-year growth rates"""
        if df.empty:
            return pd.DataFrame()

        growth_df = pd.DataFrame()

        for column in df.columns:
            if column != 'date':
                growth_df[f'{column} Growth'] = df[column].pct_change(4)  # 4 quarters for annual growth

        return growth_df

    def calculate_margins(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate various profit margins"""
        if not self.validate_data(df):
            return pd.DataFrame()

        margins_df = pd.DataFrame()

        if 'Revenue' in df.columns:
            if 'Gross Income' in df.columns:
                margins_df['Gross Margin'] = df['Gross Income'] / df['Revenue']
            if 'Operating Income' in df.columns:
                margins_df['Operating Margin'] = df['Operating Income'] / df['Revenue']
            if 'Net Income' in df.columns:
                margins_df['Net Margin'] = df['Net Income'] / df['Revenue']

        return margins_df

    def process_data(self, raw_data: dict) -> dict:
        """Process raw financial data into analyzable format"""
        try:
            # Combine all series into a single DataFrame
            df = pd.DataFrame()
            for metric, data in raw_data.items():
                if 'date' in data.columns and 'value' in data.columns:
                    temp_df = data.pivot(index='date', columns=None, values='value')
                    temp_df.columns = [metric]
                    if df.empty:
                        df = temp_df
                    else:
                        df = df.join(temp_df, how='outer')

            # Sort by date
            df.sort_index(inplace=True)

            # Calculate derived metrics
            df = self.calculate_metrics(df)

            # Calculate additional analyses
            growth_rates = self.calculate_growth_rates(df)
            margins = self.calculate_margins(df)

            return {
                'main_data': df,
                'growth_rates': growth_rates,
                'margins': margins
            }

        except Exception as e:
            st.error(f"Error processing data: {str(e)}")
            return None

    def prepare_dcf_data(self, df: pd.DataFrame, forecast_years: int = 5) -> dict:
        """Prepare data for DCF analysis"""
        if not self.validate_data(df):
            return None

        try:
            # Calculate historical growth rates
            historical_growth = df['Revenue'].pct_change(4).mean()  # Using 4 quarters

            # Get last known values
            last_values = df.iloc[-1]

            # Create forecast DataFrame
            forecast_index = pd.date_range(
                start=df.index[-1] + pd.DateOffset(months=3),
                periods=forecast_years * 4,
                freq='Q'
            )

            forecast_df = pd.DataFrame(index=forecast_index)

            # Project revenues
            forecast_df['Revenue'] = [
                last_values['Revenue'] * (1 + historical_growth) ** (i / 4)
                for i in range(1, len(forecast_index) + 1)
            ]

            # Calculate other metrics based on historical ratios
            if 'Operating Expenses' in df.columns:
                opex_ratio = (df['Operating Expenses'] / df['Revenue']).mean()
                forecast_df['Operating Expenses'] = forecast_df['Revenue'] * opex_ratio

            if 'Income Tax' in df.columns:
                tax_ratio = (df['Income Tax'] / df['Revenue']).mean()
                forecast_df['Income Tax'] = forecast_df['Revenue'] * tax_ratio

            # Calculate derived metrics for forecast
            forecast_df = self.calculate_metrics(forecast_df)

            return {
                'historical_data': df,
                'forecast_data': forecast_df,
                'metrics': {
                    'historical_growth': historical_growth,
                    'opex_ratio': opex_ratio if 'Operating Expenses' in df.columns else None,
                    'tax_ratio': tax_ratio if 'Income Tax' in df.columns else None
                }
            }

        except Exception as e:
            st.error(f"Error preparing DCF data: {str(e)}")
            return None