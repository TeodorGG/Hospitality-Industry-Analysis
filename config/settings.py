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
                'correlation': 'Direct'
            },
            'CES7000000003': {
                'name': 'Average Hourly Earnings',
                'correlation': 'Direct'
            },
            'AWHAELAH': {
                'name': 'Average Weekly Hours',
                'correlation': 'Direct'
            },
            'JTS7000JOL': {
                'name': 'Job Openings',
                'correlation': 'Direct'
            },
            'IHLIDXUSTPHOTO': {
                'name': 'Job Postings on Indeed',
                'correlation': 'Direct'
            },
            'LNU04032241': {
                'name': 'Unemployment Rate',
                'correlation': 'Inverse'
            }
        },
        'Revenues': {
            'DRCARC1Q027SBEA': {
                'name': 'Recreation Services Expenditures',
                'correlation': 'Direct'
            },
            'DFSARC1Q027SBEA': {
                'name': 'Food Services Expenditures',
                'correlation': 'Direct'
            }
        },
        'Inflation': {
            'PCU721110721110': {
                'name': 'PPI Hotels and Motels',
                'correlation': 'Inverse'
            },
            'PCU721110721110103': {
                'name': 'PPI Luxury Hotels',
                'correlation': 'Inverse'
            },
            'PCU5615105615102111': {
                'name': 'PPI Travel Agencies Hotel Bookings',
                'correlation': 'Inverse'
            }
        },
        'General': {
            'UMCSENT': {
                'name': 'Consumer Sentiment',
                'correlation': 'Direct'
            },
            'PI': {
                'name': 'Personal Income',
                'correlation': 'Direct'
            },
            'PCE': {
                'name': 'Personal Consumption Expenditures',
                'correlation': 'Direct'
            },
            'GDP': {
                'name': 'Gross Domestic Product',
                'correlation': 'Direct'
            },
            'UNRATE': {
                'name': 'Unemployment Rate',
                'correlation': 'Inverse'
            },
            'DSPI': {
                'name': 'Disposable Personal Income',
                'correlation': 'Direct'
            },
            'CPIAUCSL': {
                'name': 'Consumer Price Index',
                'correlation': 'Inverse'
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