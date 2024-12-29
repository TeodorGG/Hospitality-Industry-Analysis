# Application configuration
APP_CONFIG = {
    'title': 'Hospitality Industry Analysis',
    'icon': '📊',
}

# FRED API configuration
FRED_CONFIG = {
    'api_key': '90b849f280d2ee435bcabc4484675f01',
    'base_url': 'https://api.stlouisfed.org/fred',
    'series': {
        'Employment': {
            'USLAH': {
                'name': 'All Employees, Leisure and Hospitality',
                'correlation': 'Direct',
                'units': 'lin'
            },
            'CES7000000003': {
                'name': 'Average Hourly Earnings',
                'correlation': 'Direct',
                'units': 'lin'
            },
            'AWHAELAH': {
                'name': 'Average Weekly Hours',
                'correlation': 'Direct',
                'units': 'lin'
            },
            'JTS7000JOL': {
                'name': 'Job Openings',
                'correlation': 'Direct',
                'units': 'lin'
            },
            'IHLIDXUSTPHOTO': {
                'name': 'Job Postings on Indeed',
                'correlation': 'Direct',
                'units': 'lin'
            },
            'LNU04032241': {
                'name': 'Unemployment Rate',
                'correlation': 'Inverse',
                'is_percent': True,
                'units': 'lin'
            },
            'CES7000000008': {
                'name': 'Average Hourly Earnings (Production)',
                'correlation': 'Direct',
                'units': 'lin'
            },
            'ADPWINDLSHPNERSA': {
                'name': 'Nonfarm Private Payroll',
                'correlation': 'Direct',
                'units': 'lin'
            },
            'JTS7000QUR': {
                'name': 'Quits',
                'correlation': 'Inverse',
                'units': 'lin'
            },
            'JTS7000HIL': {
                'name': 'Hires',
                'correlation': 'Direct',
                'units': 'lin'
            }
        },
        'Revenues': {
            'DRCARC1Q027SBEA': {
                'name': 'Recreation Services Expenditures',
                'correlation': 'Direct',
                'units': 'pc1',  # Percent change from year ago
                'is_percent': True
            },
            'DFSARC1Q027SBEA': {
                'name': 'Food Services Expenditures',
                'correlation': 'Direct',
                'units': 'pc1',  # Percent change from year ago
                'is_percent': True
            }
        },
        'Inflation': {
            'PCU721110721110': {
                'name': 'PPI Hotels and Motels',
                'correlation': 'Inverse',
                'units': 'pc1',  # Percent change from year ago
                'is_percent': True
            },
            'PCU721110721110103': {
                'name': 'PPI Luxury Hotels',
                'correlation': 'Inverse',
                'units': 'pc1',  # Percent change from year ago
                'is_percent': True
            },
            'PCU5615105615102111': {
                'name': 'PPI Travel Agencies Hotel Bookings',
                'correlation': 'Inverse',
                'units': 'pc1',  # Percent change from year ago
                'is_percent': True
            },
            'PCU561510561510211': {
                'name': 'PPI Travel Agencies Hotel & Car Rentals',
                'correlation': 'Inverse',
                'units': 'pc1',  # Percent change from year ago
                'is_percent': True
            }
        },
        'General': {
            'UMCSENT': {
                'name': 'Consumer Sentiment',
                'correlation': 'Direct',
                'units': 'lin'
            },
            'PI': {
                'name': 'Personal Income',
                'correlation': 'Direct',
                'units': 'pc1',  # Percent change from year ago
                'is_percent': True
            },
            'PCE': {
                'name': 'Personal Consumption Expenditures',
                'correlation': 'Direct',
                'units': 'pc1',  # Percent change from year ago
                'is_percent': True
            },
            'PAYEMS': {
                'name': 'All Employees, Total Nonfarm',
                'correlation': 'Direct',
                'units': 'lin'
            },
            'GDP': {
                'name': 'Gross Domestic Product',
                'correlation': 'Direct',
                'units': 'pc1',  # Percent change from year ago
                'is_percent': True
            },
            'UNRATE': {
                'name': 'Unemployment Rate',
                'correlation': 'Inverse',
                'is_percent': True,
                'units': 'lin'
            },
            'CCSA': {
                'name': 'Continued Claims',
                'correlation': 'Inverse',
                'units': 'lin'
            },
            'DSPI': {
                'name': 'Disposable Personal Income',
                'correlation': 'Direct',
                'units': 'pc1',  # Percent change from year ago
                'is_percent': True
            },
            'CPIAUCSL': {
                'name': 'Consumer Price Index',
                'correlation': 'Inverse',
                'units': 'pc1',  # Percent change from year ago
                'is_percent': True
            },
            'DGS20': {
                'name': 'Treasury Yield 20Y',
                'correlation': 'Inverse',
                'is_percent': True,
                'units': 'lin'
            },
            'DGS10': {
                'name': 'Treasury Yield 10Y',
                'correlation': 'Inverse',
                'is_percent': True,
                'units': 'lin'
            },
            'DGS2': {
                'name': 'Treasury Yield 2Y',
                'correlation': 'Inverse',
                'is_percent': True,
                'units': 'lin'
            }
        }
    }
}

# Display settings
DISPLAY_CONFIG = {
    'number_format': '{:,.2f}',
    'percentage_format': '{:.2%}',
    'chart_defaults': {
        'height': 600,
        'template': 'plotly_white',
        'colors': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    }
}