import streamlit as st
from config.settings import APP_CONFIG
from pages import dashboard, data_viewer

# Page configuration
st.set_page_config(
    page_title=APP_CONFIG['title'],
    page_icon=APP_CONFIG['icon'],
    layout="wide"
)

# Initialize session state
if 'category_data' not in st.session_state:
    st.session_state.category_data = None

# Sidebar navigation
st.sidebar.title('Navigation')
page = st.sidebar.radio(
    'Select Page:',
    ['Data Viewer', 'Dashboard']
)

# Display selected page
if page == 'Data Viewer':
    data_viewer.show_page()
elif page == 'Dashboard':
    if st.session_state.category_data is None:
        st.warning("Please load data first in the Data Viewer page")
    else:
        dashboard.show_page()