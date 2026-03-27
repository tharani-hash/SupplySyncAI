import streamlit as st
import time
import functools
from typing import Any, Callable
import pandas as pd

def check_connection_state():
    """Check if WebSocket connection is still active"""
    try:
        # Test if we can still write to session state
        st.session_state._test_connection = True
        del st.session_state._test_connection
        return True
    except Exception:
        return False

def connection_retry_decorator(max_retries: int = 3, delay: float = 1.0):
    """Decorator to add connection retry logic to functions"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for attempt in range(max_retries):
                try:
                    if not check_connection_state():
                        if attempt < max_retries - 1:
                            time.sleep(delay)
                            continue
                        else:
                            st.error("Connection lost. Please refresh the page.")
                            return None
                    return func(*args, **kwargs)
                except Exception as e:
                    if "WebSocketClosedError" in str(e) or "StreamClosedError" in str(e):
                        if attempt < max_retries - 1:
                            st.warning(f"Connection interrupted. Retrying... ({attempt + 1}/{max_retries})")
                            time.sleep(delay)
                            continue
                        else:
                            st.error("Connection lost. Please refresh the page.")
                            return None
                    else:
                        raise e
            return None
        return wrapper
    return decorator

def safe_rerun():
    """Safely rerun the Streamlit app with connection check"""
    try:
        if check_connection_state():
            st.rerun()
    except Exception:
        st.error("Connection lost. Please refresh the page manually.")

def show_connection_status():
    """Display connection status indicator"""
    if "connection_status" not in st.session_state:
        st.session_state.connection_status = "Connected"
    
    status_color = {
        "Connected": "🟢",
        "Reconnecting": "🟡", 
        "Disconnected": "🔴"
    }.get(st.session_state.connection_status, "🔴")
    
    st.markdown(f"**Connection Status:** {status_color} {st.session_state.connection_status}")

def safe_dataframe_operation(operation_func, df: pd.DataFrame, *args, **kwargs):
    """Safely perform DataFrame operations with connection checks"""
    try:
        if not check_connection_state():
            st.error("Connection lost during data processing.")
            return None
        
        # For large DataFrames, show progress
        if len(df) > 10000:
            st.info(f"Processing large dataset ({len(df):,} rows). This may take a moment...")
            
        result = operation_func(df, *args, **kwargs)
        
        if not check_connection_state():
            st.warning("Connection was lost during processing. Results may be incomplete.")
            
        return result
        
    except Exception as e:
        if "WebSocketClosedError" in str(e) or "StreamClosedError" in str(e):
            st.error("Connection lost during data operation. Please try again.")
        else:
            st.error(f"Error during data operation: {str(e)}")
        return None

@connection_retry_decorator(max_retries=2, delay=0.5)
def safe_feature_selection(operation_func, *args, **kwargs):
    """Wrapper for feature selection operations with connection safety"""
    try:
        return operation_func(*args, **kwargs)
    except Exception as e:
        if "WebSocketClosedError" in str(e) or "StreamClosedError" in str(e):
            st.error("Connection lost during feature selection. Please try again.")
            return None
        else:
            raise e

def safe_altair_chart(chart_func, *args, **kwargs):
    """Safely create and display Altair charts with WebSocket error handling"""
    try:
        if not check_connection_state():
            st.error("Connection lost. Cannot create chart.")
            return None
            
        chart = chart_func(*args, **kwargs)
        
        # Validate chart before returning
        if chart is None:
            raise Exception("Chart function returned None")
            
        return chart
        
    except Exception as e:
        error_msg = str(e)
        if "WebSocketClosedError" in error_msg or "StreamClosedError" in error_msg:
            st.error("🔴 Connection lost while creating chart. Please try refreshing the page.")
        elif "ValueError" in error_msg and "to_dict" in error_msg:
            st.error("🔴 Chart configuration error. Falling back to matplotlib chart.")
        else:
            st.error(f"🔴 Error creating chart: {error_msg}")
        return None
