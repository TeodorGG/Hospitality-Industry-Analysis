import requests
import pandas as pd
import streamlit as st
from typing import Dict, Optional


class FREDReader:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.stlouisfed.org/fred"

    def get_series_data(self, series_id: str, series_info: dict) -> Optional[pd.DataFrame]:
        """Fetch series data with specified units"""
        params = {
            'series_id': series_id,
            'api_key': self.api_key,
            'file_type': 'json',
            'units': series_info.get('units', 'lin')  # Use specified units or default to linear
        }

        try:
            response = requests.get(
                f"{self.base_url}/series/observations",
                params=params
            )
            response.raise_for_status()

            data = response.json()
            if not data.get('observations'):
                return None

            # Convert to DataFrame
            df = pd.DataFrame(data['observations'])
            df['date'] = pd.to_datetime(df['date'])
            df['value'] = pd.to_numeric(df['value'], errors='coerce')

            # Handle missing values
            df = df.dropna()

            # Set date as index and resample to monthly
            df.set_index('date', inplace=True)
            monthly_df = df['value'].resample('M').last()

            # Forward fill for up to 3 months of missing data
            monthly_df = monthly_df.fillna(method='ffill', limit=3)
            monthly_df = monthly_df.dropna()

            return monthly_df

        except Exception as e:
            st.error(f"Error fetching {series_id}: {str(e)}")
            return None

    def load_category_data(self, category_series: Dict) -> pd.DataFrame:
        """Load data for a specific category"""
        data_frames = {}

        for series_id, info in category_series.items():
            with st.spinner(f"Loading {info['name']}..."):
                series_data = self.get_series_data(series_id, info)
                if series_data is not None and not series_data.empty:
                    data_frames[series_id] = series_data
                    st.success(f"Loaded {info['name']}")
                else:
                    st.error(f"Failed to load {info['name']}")

        if data_frames:
            try:
                # Find common date range
                start_date = max(df.first_valid_index() for df in data_frames.values())
                end_date = min(df.last_valid_index() for df in data_frames.values())

                # Combine all series and trim to common date range
                df = pd.DataFrame(data_frames)
                df = df.loc[start_date:end_date]

                return df
            except Exception as e:
                st.error(f"Error combining data: {str(e)}")
                return None

        return None

    def load_all_categories(self, config: Dict) -> Dict[str, pd.DataFrame]:
        """Load data for all categories"""
        category_data = {}

        for category_name, series_dict in config['series'].items():
            st.subheader(f"Loading {category_name} Data")
            df = self.load_category_data(series_dict)
            if df is not None and not df.empty:
                category_data[category_name] = df

        return category_data