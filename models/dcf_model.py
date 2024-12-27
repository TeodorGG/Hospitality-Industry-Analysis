import pandas as pd
import numpy as np
import streamlit as st


class DCFModel:
    def __init__(self, financial_data, wacc, terminal_growth, forecast_years):
        self.financial_data = financial_data
        self.wacc = wacc
        self.terminal_growth = terminal_growth
        self.forecast_years = forecast_years

    def calculate_dcf(self):
        """Calculate DCF based on historical financial data"""
        try:
            # Get historical growth rate
            historical_data = self.financial_data['Corporate Profits Before Tax']
            growth_rates = historical_data.pct_change().dropna()
            avg_growth_rate = growth_rates.mean()

            # Last known values
            last_values = self.financial_data.iloc[-1]
            last_revenue = last_values['Corporate Profits Before Tax']

            # Create forecast DataFrame
            years = pd.date_range(start='2025', periods=self.forecast_years, freq='Y')
            forecast_df = pd.DataFrame(index=years)

            # Revenue forecast
            forecast_df['Revenue'] = [
                last_revenue * (1 + avg_growth_rate) ** (i + 1)
                for i in range(self.forecast_years)
            ]

            # Calculate effective tax rate
            tax_rate = 1 - (
                    self.financial_data['Corporate Profits After Tax'] /
                    self.financial_data['Corporate Profits Before Tax']
            ).mean()

            # Financial calculations
            forecast_df['Pre-Tax Income'] = forecast_df['Revenue']
            forecast_df['Taxes'] = forecast_df['Pre-Tax Income'] * tax_rate
            forecast_df['Net Income'] = forecast_df['Pre-Tax Income'] - forecast_df['Taxes']
            forecast_df['FCF'] = forecast_df['Net Income']  # Simplified FCF

            # Terminal value
            final_fcf = forecast_df['FCF'].iloc[-1]
            terminal_value = final_fcf * (1 + self.terminal_growth) / (
                    self.wacc - self.terminal_growth
            )

            # Present values
            present_values = [
                fcf / (1 + self.wacc) ** (i + 1)
                for i, fcf in enumerate(forecast_df['FCF'])
            ]

            # Terminal value present value
            terminal_value_pv = terminal_value / (1 + self.wacc) ** self.forecast_years

            # Enterprise value
            enterprise_value = sum(present_values) + terminal_value_pv

            return {
                'forecast': forecast_df,
                'terminal_value': terminal_value,
                'present_values': present_values,
                'terminal_value_pv': terminal_value_pv,
                'enterprise_value': enterprise_value
            }

        except Exception as e:
            st.error(f"Error in DCF calculation: {str(e)}")
            return None

    def sensitivity_analysis(self):
        """Perform sensitivity analysis on WACC and terminal growth"""
        wacc_range = np.linspace(self.wacc - 0.02, self.wacc + 0.02, 5)
        growth_range = np.linspace(
            self.terminal_growth - 0.02,
            self.terminal_growth + 0.02,
            5
        )

        sensitivity_matrix = np.zeros((len(wacc_range), len(growth_range)))

        for i, w in enumerate(wacc_range):
            for j, g in enumerate(growth_range):
                temp_model = DCFModel(
                    self.financial_data,
                    w, g,
                    self.forecast_years
                )
                result = temp_model.calculate_dcf()
                if result:
                    sensitivity_matrix[i, j] = result['enterprise_value']

        return sensitivity_matrix, wacc_range, growth_range