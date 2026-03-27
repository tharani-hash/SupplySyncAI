# Configuration for dup.py WebSocket stability and performance
import streamlit as st
import os

def configure_dup_streamlit():
    """Configure Streamlit settings for stable WebSocket connections"""
    
    # Set environment variables for better connection handling
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    os.environ['STREAMLIT_SERVER_ENABLE_CORS'] = 'false'
    os.environ['STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION'] = 'false'
    
    # WebSocket timeout settings
    os.environ['STREAMLIT_SERVER_WEB_SOCKET_TIMEOUT'] = '120'  # Increased for feature selection
    
    # Configure session state for connection monitoring
    if 'connection_timeout' not in st.session_state:
        st.session_state.connection_timeout = 45  # seconds - longer for data processing
    if 'max_retries' not in st.session_state:
        st.session_state.max_retries = 3
    if 'retry_delay' not in st.session_state:
        st.session_state.retry_delay = 1.5  # seconds

# Performance optimization settings for data processing
DUP_PERFORMANCE_CONFIG = {
    'max_rows_display': 2000,  # Higher limit for feature selection
    'chunk_size': 1000,        # Larger chunks for data processing
    'cache_ttl': 7200,         # 2 hours cache for feature selection
    'enable_lazy_loading': True,
    'websocket_ping_interval': 30,  # seconds
    'connection_timeout': 45,   # seconds
    'feature_selection_timeout': 300,  # 5 minutes for feature selection
    'correlation_matrix_limit': 50,   # Max features for correlation display
    'outlier_processing_limit': 100,  # Max numeric columns for outlier processing
}

def get_dup_config(key, default=None):
    """Get configuration value for dup.py"""
    return DUP_PERFORMANCE_CONFIG.get(key, default)

def get_processing_limits(df):
    """Get appropriate processing limits based on dataset size"""
    rows = len(df)
    cols = len(df.columns)
    
    if rows > 100000:
        return {
            'max_display_rows': 500,
            'chunk_size': 2000,
            'enable_sampling': True,
            'sample_size': 10000
        }
    elif rows > 50000:
        return {
            'max_display_rows': 1000,
            'chunk_size': 1500,
            'enable_sampling': False,
            'sample_size': None
        }
    else:
        return {
            'max_display_rows': get_dup_config('max_rows_display'),
            'chunk_size': get_dup_config('chunk_size'),
            'enable_sampling': False,
            'sample_size': None
        }
