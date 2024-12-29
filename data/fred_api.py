import requests
import pandas as pd
import streamlit as st
from typing import Dict, Optional
from datetime import datetime


class FREDReader:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.stlouisfed.org/fred"

    def get_series_data(self, series_id: str, series_info: dict) -> Optional[pd.DataFrame]:
        """Fetch series data with specified units"""
        end_date = datetime.now().strftime('%Y-%m-%d')

        params = {
            'series_id': series_id,
            'api_key': self.api_key,
            'file_type': 'json',
            'units': series_info.get('units', 'lin'),
            'observation_end': end_date
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

            # Remove missing values
            df = df.dropna()

            # Set date as index and get last value of each month
            df.set_index('date', inplace=True)
            monthly_df = df.resample('ME').agg({'value': 'last'})
            monthly_df = monthly_df['value']  # Convert back to series


            print(monthly_df)
            return monthly_df

        except Exception as e:
            st.error(f"Error fetching {series_id}: {str(e)}")
            return None

    def load_category_data(self, category_series: Dict) -> pd.DataFrame:
        """Load data for a specific category with independent date ranges for each series"""
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
                # Combine all series without restricting to a common date range
                df = pd.concat(data_frames, axis=1)
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