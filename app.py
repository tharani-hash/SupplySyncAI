import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import io
import numpy as np
import altair as alt
import sys
import traceback
import os

try:
    from streamlit_option_menu import option_menu
except Exception:
    option_menu = None

# SupplySync.AI optional dependencies (keep imports at top; do not crash if missing)
try:
    import xgboost as xgb
except Exception:
    xgb = None

try:
    import lightgbm as lgb
except Exception:
    lgb = None

try:
    import shap
except Exception:
    shap = None

try:
    import lime
    import lime.lime_tabular
except Exception:
    lime = None

try:
    import networkx as nx
except Exception:
    nx = None

from datetime import datetime, timedelta
import time
import warnings

from scipy.optimize import linprog
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.ensemble import IsolationForest, RandomForestRegressor, RandomForestClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, mean_absolute_error, mean_squared_error, r2_score, accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.inspection import permutation_importance
from sklearn.feature_selection import SelectKBest, f_regression, mutual_info_regression, RFE
import plotly.graph_objects as go
import plotly.express as px

# Add current directory to Python path to resolve imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from dup_connection_utils import connection_retry_decorator, check_connection_state, safe_rerun, show_connection_status, safe_dataframe_operation, safe_feature_selection, safe_altair_chart
from dup_config import configure_dup_streamlit, get_dup_config, get_processing_limits

# Configure Streamlit for better WebSocket handling
configure_dup_streamlit()

st.set_page_config(page_title="SupplySyncAI – Supply Chain Intelligence", layout="wide")

st.markdown("""
<style>

/* App background */
.stApp {
    background-color: #EDEDED;
    margin: 0;
    padding: 0;
}

/* Remove block spacing */
.block-container {
    padding-top: 0rem !important;
    margin-top: -5.5rem !important;
}
/* keep app background */
.main {
    background-color: #f0f2f6 !important;
}

/* Remove main section spacing */
section.main > div:first-child {
    padding-top: 0rem !important;
    margin-top: 0rem !important;
}

/* REMOVE TOP GAP COMPLETELY */
[data-testid="stAppViewContainer"] {
    padding-top: 0rem !important;
    margin-top: 0rem !important;
}

/* REMOVE TOP SPACER DIV */
[data-testid="stAppViewContainer"] > div:first-child {
    margin-top: 0rem !important;
    padding-top: 0rem !important;
}

/* KEEP header visible */
header[data-testid="stHeader"] {
    position: relative;
    background-color: #EDEDED !important;
}

header[data-testid="stHeader"] * {
    color: #000000 !important;
}



</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

/* Block container — single source of truth */
.block-container {
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 100% !important;
    overflow-x: hidden !important;
}

section.main > div {
    padding-left: 0rem !important;
    padding-right: 0rem !important;
    max-width: 100% !important;
    overflow-x: hidden !important;
}

[data-testid="stAppViewContainer"] {
    padding-left: 0rem !important;
    padding-right: 0rem !important;
    overflow-x: hidden !important;
}
            
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

/* RADIO CONTAINER – FULL WIDTH */
div.element-container:has(div.stRadio) {
    width: 100% !important;
}

/* GREEN WRAP BOX – FULL PAGE WIDTH */
div.stRadio > div {
    background-color:  #00D05E;
    padding: 16px 0px;
    border-radius: 8px;
    width: 100%;
    box-sizing: border-box;
    display: flex;
    justify-content: center;
}

/* RADIO GROUP ALIGNMENT */
div[data-baseweb="radio-group"] {
    display: flex !important;
    justify-content: center !important;
    align-items: center;
    gap: 50px;
    width: 100%;
    margin: 0 auto;
}
            
div[data-baseweb="radio"] {
    display: flex;
    align-items: center;
    justify-content: center;
}

/* RADIO OPTION TEXT */
div[data-baseweb="radio"] label,
div[data-baseweb="radio"] label span {
    font-size: 18px !important;
    font-weight: 800 !important;
    color: #FFFFFF !important;
    white-space: nowrap;
}

/* SPACE BETWEEN OPTIONS */
div[data-baseweb="radio"] {
    margin-right: 28px;
}

</style>
""", unsafe_allow_html=True)

st.markdown(""" 
 <style> /* Expander outer card */ 
    div[data-testid="stExpander"]
        { background-color: #2F75B5;
        border-radius: 20px; 
        border: 1px solid #9EDAD0; 
        overflow: hidden; }
    /* Hide expander header completely */
    div[data-testid="stExpander"]:nth-of-type(1)
             summary { display: none; }
    /* Inner content padding fix */
     div[data-testid="stExpander"]:nth-of-type(1) > 
            div { padding: 22px 18px; } 
            </style> """, unsafe_allow_html=True)


st.markdown(
    """
    <style>
        /* Dark blue themed button */
        div.stButton > button {
            background-color: #0B2C5D;
            color: #FFFFFF;
            border-radius: 8px;
            padding: 8px 18px;
            border: none;
            font-weight: 600;
        }

        div.stButton > button:hover {
            background-color: #08306B;
            color: #FFFFFF;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("""
<style>

/* SUMMARY GRID */
.summary-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 14px;
    margin: 6px 0 10px 0;
    justify-content: center;
}

/* SUMMARY CARD */
.summary-card {
    border: 2px solid #6B7280;
    border-radius: 2px;
    background-color: #F8FAFC;
    overflow: hidden;
    text-align: center;
}

/* HEADER ROW */
.summary-title {
    background-color:#1F3A5F;
    color: #ffffff;
    font-size: 14px;
    font-weight: 700;
    padding: 8px 6px;
    border-bottom: 1px solid #6B7280;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* VALUE CELL */
.summary-value {
    font-size: 22px;
    font-weight: 600;
    color: #000000;
    padding: 1px 0;
}

</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>
/* Outer gray wrap */
.gray-analytics-wrap {
    background-color: #E6E6E6;
    padding: 16px 400px;
    border-radius: 8px;
    width: 100%;
    box-sizing: border-box;
}

/* Inner blue analytics bar */
.analytics-container {
    background-color:#1F6FB2;
    padding:18px;
    border-radius:14px;
}
</style>
""", unsafe_allow_html=True)


# ================================================================
# QUALITY CARD & CLEAN TABLE CSS
# ================================================================
st.markdown("""
<style>

/* =====================================================
   GLOBAL / COMMON STYLES
   ===================================================== */

/* Clean report-style table */
.clean-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13.5px;
}

.clean-table th {
    background-color: #F4F6F7;
    padding: 8px;
    text-align: left;
    font-weight: 600;
    border-bottom: 1px solid #D6DBDF;
    color: #34495E;
}

.clean-table td {
    padding: 7px 8px;
    border-bottom: 1px solid #ECF0F1;
    color: #2C3E50;
}

.clean-table tr:hover {
    background-color: #F8F9F9;
}


/* =====================================================
   DATA QUALITY – LAYOUT
   ===================================================== */

/* Horizontal row for cards */
.quality-row {
    display: flex;
    gap: 16px;
    margin-bottom: 48px;
}

/* Individual card */
.quality-card {
    flex: 1;
    background-color: white;
    border-radius: 12px;
    padding: 16px 18px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.06);
    border-left: 5px solid #2F75B5;
    margin-bottom: 48px;
}

/* Section title */
.quality-title {
    font-size: 15px;
    font-weight: 600;
    color: #ffffff;
    background-color:#123A72;
    padding: 10px 14px;
    border-radius: 6px;
    margin-bottom: 18px;
}

/* Scrollable content inside card */
.table-scroll {
    max-height: 260px;
    overflow-y: auto;
}

.quality-card table {
    width: 100%;
    border-collapse: collapse;
    background-color: #FFFFFF;
    font-size: 14px;
}

/* Table header */
.quality-card th {
    background-color: #E5ECF4;
    color: #1F2937;
    font-weight: 600;
    text-align: left;
    padding: 10px 12px;
    border-bottom: 1px solid #D6DEE8;
}

/* Table cells */
.quality-card td {
    padding: 9px 12px;
    color: #111827;
    border-bottom: 1px solid #EEF2F7;
}

/* Zebra rows */
.quality-card tr:nth-child(even) td {
    background-color: #FFFFFF;
}

.quality-card tr:nth-child(odd) td {
    background-color: #F3F6FA;
}

/* Subtle hover */
.quality-card tr:hover td {
    background-color: #E9F1FF;
}

.report-card {
    background-color: #FFFFFF;
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 22px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.06);
    border-left: 6px solid #2F75B5;
}

.report-title {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 12px;
    color: #2C3E50;
}

.metric-pill {
    display: inline-block;
    background-color: #EBF5FB;
    color: #1F618D;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
    margin-right: 8px;
}

</style>
""", unsafe_allow_html=True)


# ================================================================
# ALTAIR TRANSPARENT THEME
# ================================================================
def transparent_theme():
    return {
        "config": {
            "background": "transparent",
            "view": {"fill": "transparent", "stroke": "transparent"},
            "axis": {
                "labelColor": "rgba(255,255,255,0.8)",
                "titleColor": "rgba(255,255,255,0.9)",
                "gridColor": "rgba(255,255,255,0.25)",
                "domainColor": "rgba(255,255,255,0.4)"
            },
            "text": {"color": "white"}
        }
    }

alt.themes.register("transparent_theme", transparent_theme)
alt.themes.enable("transparent_theme")


# ================================================================
# HTML TABLE RENDERER
# ================================================================
def render_html_table(df, title=None, max_height=300):
    """Optimized HTML table renderer with performance limits and WebSocket safety"""
    if df is None or df.empty:
        st.info("No data to display")
        return
        
    # Get processing limits based on dataset size
    limits = get_processing_limits(df) if hasattr(df, 'shape') else {}
    max_rows = limits.get('max_display_rows', get_dup_config('max_rows_display', 2000))
    
    if len(df) > max_rows:
        df = df.head(max_rows)
        st.warning(f"⚠️ Showing first {max_rows:,} rows of {len(df):,} total rows for performance")
    
    if title:
        st.markdown(f"**{title}**")
    
    try:
        html = f"""
        <div style="overflow-x:auto; overflow-y:auto; max-height:{max_height}px;
                    border:1px solid #D1D5DB; border-radius:8px;">
        <table style="width:100%; border-collapse:collapse; font-size:13px; background:#fff;">
            <thead style="position:sticky; top:0; z-index:1;">
                <tr>
        """
        for c in df.columns:
            html += f'<th style="background:#1F3A5F;color:white;padding:8px 10px;text-align:left;font-weight:600;white-space:nowrap;">{c}</th>'
        html += "</tr></thead><tbody>"
        
        # Process in chunks for better performance
        chunk_size = limits.get('chunk_size', get_dup_config('chunk_size', 1000))
        for i in range(0, len(df), chunk_size):
            chunk = df.iloc[i:i+chunk_size]
            for _, row in chunk.iterrows():
                html += "<tr style='border-bottom:1px solid #E5E7EB;'>"
                for val in row:
                    html += f"<td style='padding:6px 10px;white-space:nowrap;'>{val}</td>"
                html += "</tr>"
        
        html += "</tbody></table></div>"
        st.markdown(html, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error rendering table: {str(e)}")
        # Fallback to simple display
        st.dataframe(df.head(10))


# ================================================================
# MAIN HEADER
# ================================================================
st.markdown(
    """
    <div style="
        background-color:#0B2C5D;
        padding:35px;
        border-radius:12px;
        color:white;
        text-align:center;
        margin:0 0 20px 0;
    ">
        <h1 style="margin:0 0 8px 0;">
            AI-Powered Supply Chain Optimization & Inventory Intelligence Engine
        </h1>
        <h3 style="font-weight:400; margin:0;">
            From Warehouse to Last-Mile – End-to-End Supply Chain Analytics
        </h3>
        <p style="font-size:17px; margin-top:15px;">
            Optimize inventory levels, shipment routing, supplier performance,
            cluster-based transfers, and demand-supply balancing across
            products, stores, regions, and time.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:28px;
        border-radius:12px;
        color:white;
        font-size:16px;
        line-height:1.6;
        margin-bottom:25px;
    ">

    <p>
    This application enables <b>granular supply chain optimization and inventory intelligence</b>
    by combining inventory snapshots, shipment records, routing efficiency scores, cluster-based
    transfer recommendations, supplier metrics, product master data, and time-calendar signals
    into a unified AI-driven analytics pipeline.
    </p>

    <p>
    Unlike traditional supply chain systems that operate at an
    <b>aggregate or category level</b>, this platform provides
    <b>fine-grained insights at the SKU × Store × Route × Cluster × Supplier × Time level</b>,
    empowering data-driven decisions across inventory planning, logistics, and procurement.
    </p>

    <h4 style="margin-top:22px;">Why This Matters</h4>

    <p>
    Supply chain performance is influenced by far more than historical stock levels.
    This engine captures <b>real-world drivers of supply chain efficiency</b>, including:
    </p>

    <ul>
        <li>Inventory health — overstock, understock, fill rates, stockout rates, turnover</li>
        <li>Shipment performance — delivery times, fuel costs, route efficiency scores</li>
        <li>Cluster-based transfer intelligence — optimal transfer quantities, cost minimization</li>
        <li>Supplier reliability — lead times, rating scores, contract terms, payment preferences</li>
        <li>Product lifecycle signals — shelf life, pricing, category and subcategory patterns</li>
        <li>Time and seasonality — holidays, weekends, quarterly and monthly demand shifts</li>
    </ul>

    <p style="margin-top:15px;">
        <b>The result:</b> Reduced stockouts, lower overstock costs, optimized routing,
        improved service levels, and stronger supplier partnerships.
    </p>

    </div>
    """,
    unsafe_allow_html=True
)

# ================================================================
# CONNECTION STATUS DISPLAY
# ================================================================
show_connection_status()

# ================================================================
# ERROR HANDLING AND CONNECTION MANAGEMENT
# ================================================================
def handle_streamlit_errors(func):
    """Global error handler for Streamlit operations"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if "WebSocketClosedError" in str(e) or "StreamClosedError" in str(e):
                st.session_state.connection_status = "Disconnected"
                st.error("🔴 Connection lost. The application is trying to reconnect...")
                return None
            else:
                st.error(f"❌ An error occurred: {str(e)}")
                st.code(traceback.format_exc())
                return None
    return wrapper

@connection_retry_decorator(max_retries=2, delay=0.5)
@handle_streamlit_errors
def safe_data_operation(operation_func, *args, **kwargs):
    """Wrapper for data operations with connection safety"""
    return operation_func(*args, **kwargs)

# ================================================================
# CACHED FUNCTIONS FOR PERFORMANCE
# ================================================================
@st.cache_data
def remove_duplicates_cached(df):
    """Optimized cached function for duplicate removal processing"""
    try:
        # Quick check for duplicates without full scan
        total_rows = len(df)
        
        # Full duplicate check (optimized)
        before_df = df.copy()
        
        # Use duplicated() with keep=False for better performance
        dup_mask = before_df.duplicated(keep=False)
        dup_rows = before_df[dup_mask]
        
        # More efficient drop_duplicates
        after_df = before_df.drop_duplicates().reset_index(drop=True)
        
        # Check connection state
        if not check_connection_state():
            st.warning("Connection lost during duplicate detection. Results may be incomplete.")
        
        return before_df, after_df, dup_rows
        
    except Exception as e:
        if "WebSocketClosedError" in str(e) or "StreamClosedError" in str(e):
            st.error("Connection lost during duplicate removal. Please try again.")
            return df, df.copy().drop_duplicates().reset_index(drop=True), pd.DataFrame()
        else:
            raise e

@st.cache_data
def remove_outliers_cached(df, delete_cols):
    """Cached function for outlier removal processing"""
    try:
        before_df = df.copy()
        after_df = before_df.copy()
        numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
        
        outlier_count = pd.Series(0, index=before_df.index)

        for col in numeric_cols:
            Q1 = before_df[col].quantile(0.25)
            Q3 = before_df[col].quantile(0.75)
            IQR = Q3 - Q1

            mild_lower = Q1 - 1.5 * IQR
            mild_upper = Q3 + 1.5 * IQR

            extreme_lower = Q1 - 2.0 * IQR
            extreme_upper = Q3 + 2.0 * IQR

            is_mild = (
                (before_df[col] < mild_lower) |
                (before_df[col] > mild_upper)
            )

            outlier_count += is_mild.astype(int)

            if col in delete_cols:
                outlier_count += (
                    (before_df[col] < extreme_lower) |
                    (before_df[col] > extreme_upper)
                ).astype(int) * 2

            after_df[col] = after_df[col].clip(mild_lower, mild_upper)
            
            # Check connection state periodically during processing
            if len(numeric_cols) > 10 and numeric_cols.index(col) % 5 == 0:
                if not check_connection_state():
                    st.warning("Connection lost during outlier processing. Results may be incomplete.")

        extreme_mask = outlier_count >= 4
        removed_df = before_df[extreme_mask]
        after_df = after_df[~extreme_mask].reset_index(drop=True)
        
        return before_df, after_df, removed_df
        
    except Exception as e:
        if "WebSocketClosedError" in str(e) or "StreamClosedError" in str(e):
            st.error("Connection lost during outlier removal. Please try again.")
            return df, df.copy(), pd.DataFrame()
        else:
            raise e

@st.cache_data
def handle_missing_values_cached(df, replace_null_with_unknown=True):
    """Handle missing values in categorical columns by replacing with 'Unknown'"""
    try:
        before_df = df.copy()
        after_df = df.copy()
        
        # Identify categorical columns (object and category dtypes)
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Exclude ID columns from processing
        id_patterns = ['id', 'code', 'key', 'identifier']
        non_critical_categorical = []
        
        for col in categorical_cols:
            col_lower = col.lower()
            # Skip ID-like columns
            if not any(pattern in col_lower for pattern in id_patterns):
                non_critical_categorical.append(col)
        
        missing_info = {}
        
        if replace_null_with_unknown:
            for col in non_critical_categorical:
                null_count = before_df[col].isnull().sum()
                if null_count > 0:
                    missing_info[col] = {
                        'null_count': null_count,
                        'null_percentage': (null_count / len(before_df)) * 100
                    }
                    after_df[col] = after_df[col].fillna('Unknown')
        
        # Check connection state
        if not check_connection_state():
            st.warning("Connection lost during missing value handling. Results may be incomplete.")
        
        return before_df, after_df, missing_info
        
    except Exception as e:
        if "WebSocketClosedError" in str(e) or "StreamClosedError" in str(e):
            st.error("Connection lost during missing value handling. Please try again.")
            return df, df.copy(), {}
        else:
            raise e

@st.cache_data
def convert_to_numeric_safe_cached(df):
    """Convert safe measurable columns to numeric format only"""
    try:
        before_df = df.copy()
        after_df = df.copy()
        
        conversion_info = {}
        
        # Identify safe numeric columns
        safe_numeric_patterns = [
            'quantity', 'amount', 'price', 'sales', 'cost', 'revenue', 
            'score', 'rating', 'count', 'total', 'sum', 'discount',
            'tax', 'forecast', 'weight', 'height', 'length', 'width'
        ]
        
        # Identify ID-like columns to exclude
        id_patterns = ['id', 'code', 'key', 'identifier', 'number']
        
        for col in df.columns:
            col_lower = col.lower()
            
            # Skip ID-like columns and already numeric columns
            if (any(pattern in col_lower for pattern in id_patterns) or 
                pd.api.types.is_numeric_dtype(df[col])):
                continue
            
            # Check if column looks like a safe numeric column
            if any(pattern in col_lower for pattern in safe_numeric_patterns):
                try:
                    # Attempt conversion to numeric
                    converted = pd.to_numeric(df[col], errors='coerce')
                    
                    # Only keep conversion if most values convert successfully (>80%)
                    non_null_count = converted.notna().sum()
                    total_count = len(df)
                    
                    if non_null_count / total_count > 0.8:
                        after_df[col] = converted
                        conversion_info[col] = {
                            'original_dtype': str(df[col].dtype),
                            'converted_values': non_null_count,
                            'conversion_rate': (non_null_count / total_count) * 100
                        }
                except Exception:
                    # Skip column if conversion fails
                    continue
        
        # Check connection state
        if not check_connection_state():
            st.warning("Connection lost during numeric conversion. Results may be incomplete.")
        
        return before_df, after_df, conversion_info
        
    except Exception as e:
        if "WebSocketClosedError" in str(e) or "StreamClosedError" in str(e):
            st.error("Connection lost during numeric conversion. Please try again.")
            return df, df.copy(), {}
        else:
            raise e

@st.cache_data
def compute_correlation_cached(numeric_df, target_column):
    """Cached function for correlation computation"""
    corr = numeric_df.corr()[target_column]
    corr_df = corr.reset_index()
    corr_df.columns = ["Feature", "Correlation"]
    corr_df = corr_df[corr_df["Feature"] != target_column]
    corr_df["Abs_Correlation"] = corr_df["Correlation"].abs()
    corr_df = corr_df.sort_values("Abs_Correlation", ascending=False)
    return corr_df.head(20)

@st.cache_data
def compute_selectkbest_cached(X, y, k=20):
    """Cached function for SelectKBest feature selection"""
    from sklearn.feature_selection import SelectKBest, f_regression
    selector = SelectKBest(f_regression, k=min(k, X.shape[1]))
    selector.fit(X, y)
    scores = pd.Series(selector.scores_, index=X.columns)
    scores = scores.sort_values(ascending=False).head(k)
    return scores

@st.cache_data
def compute_rfe_cached(X, y, n_features=20):
    """Cached function for Recursive Feature Elimination with optimization"""
    from sklearn.feature_selection import RFE
    from sklearn.ensemble import RandomForestRegressor
    
    # Use fewer estimators for faster processing
    model = RandomForestRegressor(
        n_estimators=25,  # Reduced from 50
        max_depth=10,     # Limit depth
        random_state=42,
        n_jobs=-1         # Use all cores
    )
    rfe = RFE(model, n_features_to_select=min(n_features, X.shape[1]))
    rfe.fit(X, y)
    selected_features = X.columns[rfe.support_].tolist()
    return selected_features

@st.cache_data
def compute_mutual_info_cached(X, y):
    """Cached function for Mutual Information feature selection"""
    from sklearn.feature_selection import mutual_info_regression
    
    mi = mutual_info_regression(X, y)
    mi_series = pd.Series(mi, index=X.columns)
    top_mi = mi_series.sort_values(ascending=False).head(20)
    return top_mi

@st.cache_data
def compute_permutation_importance_cached(X, y, selected_features):
    """Cached function for permutation importance computation"""
    from sklearn.inspection import permutation_importance
    from sklearn.linear_model import LinearRegression
    
    X_subset = X[selected_features]
    model = LinearRegression()
    model.fit(X_subset, y)
    
    result = permutation_importance(
        model,
        X_subset,
        y,
        n_repeats=10,
        random_state=42,
        n_jobs=-1
    )
    
    importances = pd.Series(
        result.importances_mean,
        index=X_subset.columns
    ).clip(lower=0)
    
    return importances.sort_values(ascending=False)

@st.cache_data
def replace_nulls_cached(df):
    """Cached function for NULL value replacement"""
    null_mask = df.isnull()
    affected_rows_before = df[null_mask.any(axis=1)]
    null_counts = null_mask.sum()
    null_counts = null_counts[null_counts > 0]
    
    if null_counts.empty:
        return df, None, None, None
    else:
        df_updated = df.fillna("Unknown")
        null_counts_df = null_counts.to_frame("NULL Count")
        after_rows = df_updated.loc[affected_rows_before.index].copy()
        return df_updated, affected_rows_before, after_rows, null_counts_df

@st.cache_data
def compute_eda_aggregations(df, sample_size=10000):
    """Optimized cached function for common EDA aggregations with sampling support"""
    results = {}
    
    # Use sampling for large datasets to improve performance
    if sample_size and len(df) > sample_size:
        df_work = df.sample(n=sample_size, random_state=42)
        st.info(f"📊 Using sample of {sample_size:,} rows for faster analysis")
    else:
        df_work = df
    
    # Pre-compute common groupby objects to avoid repetition
    try:
        # Cache groupby objects for reuse
        if 'category' in df_work.columns and 'stock_value' in df_work.columns:
            cat_group = df_work.groupby('category')['stock_value']
            results['category_stockval'] = cat_group.sum().sort_values(ascending=False)
        
        if 'subcategory' in df_work.columns and 'fill_rate_pct' in df_work.columns:
            subcat_group = df_work.groupby('subcategory')['fill_rate_pct']
            results['subcategory_fillrate'] = subcat_group.mean().sort_values(ascending=False).head(15)
        
        if 'zone' in df_work.columns and 'stock_value' in df_work.columns:
            zone_group = df_work.groupby('zone')['stock_value']
            results['zone_stockval'] = zone_group.sum().sort_values(ascending=False)
        
        if 'city' in df_work.columns and 'stockout_pct' in df_work.columns:
            city_group = df_work.groupby('city')['stockout_pct']
            results['city_stockout'] = city_group.mean().sort_values(ascending=False).head(15)
            
        if 'vehicle_id' in df_work.columns and 'delivery_time_mins' in df_work.columns:
            vehicle_group = df_work.groupby('vehicle_id')['delivery_time_mins']
            results['vehicle_delivery'] = vehicle_group.mean().sort_values(ascending=False).head(15)
            
        if 'region' in df_work.columns and 'overstock_index' in df_work.columns:
            region_group = df_work.groupby('region')['overstock_index']
            results['region_overstock'] = region_group.mean().sort_values(ascending=False)
            
    except Exception as e:
        st.warning(f"⚠️ Some aggregations failed: {str(e)}")
    
    return results

@st.cache_data
def apply_feature_scaling_cached(X):
    """Cached function for feature scaling"""
    from sklearn.preprocessing import StandardScaler
    
    scaler = StandardScaler()
    scaled_values = scaler.fit_transform(X)
    
    scaled_df = pd.DataFrame(
        scaled_values,
        columns=X.columns,
        index=X.index
    )
    
    return scaled_df, scaler

@st.cache_data
def compute_data_quality_stats(df):
    """Cached function for data quality statistics"""
    stats = {}
    
    # Basic stats
    stats['shape'] = df.shape
    stats['memory_mb'] = df.memory_usage(deep=True).sum() / 1024**2
    
    # Missing values analysis
    mv = (df.isnull().mean() * 100).round(2).sort_values(ascending=False)
    stats['missing_values'] = mv[mv > 0]
    
    # Duplicate analysis
    stats['duplicates'] = df.duplicated().sum()
    
    # Data types
    stats['dtypes'] = df.dtypes.value_counts()
    
    # Numeric stats (sample for large datasets)
    if len(df) > 10000:
        numeric_sample = df.select_dtypes(include=np.number).sample(n=min(5000, len(df)), random_state=42)
        stats['numeric_desc'] = numeric_sample.describe().round(2)
    else:
        stats['numeric_desc'] = df.select_dtypes(include=np.number).describe().round(2)
    
    return stats

# ================================================================
# CSV LOADER
# ================================================================
@st.cache_data
def load_data():
    # Optimize CSV loading with dtype specification and chunking for preview
    dtype_spec = {
        'product_id': 'category',
        'store_id': 'category', 
        'route_id': 'category',
        'vehicle_id': 'category',
        'supplier_id': 'category',
        'cluster_id': 'category',
        'category': 'category',
        'subcategory': 'category',
        'region': 'category',
        'zone': 'category',
        'store_type': 'category',
        'is_holiday': 'bool',
        'is_weekend': 'bool'
    }
    
    try:
        # Read with optimized dtypes
        df = pd.read_csv("smart_inventory_app/data/FACT_SUPPLY_CHAIN_DATA.csv", dtype=dtype_spec)
        return df
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return pd.DataFrame()


def show_small_plot(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    buf.seek(0)
    st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
    st.image(buf, width=480)
    st.markdown("</div>", unsafe_allow_html=True)


# ================================================================
# STEP 1 – DATA COLLECTION & INTEGRATION
# ================================================================
st.markdown(
    """
    <div style="
        background-color:#0B2C5D;
        padding:18px 25px;
        border-radius:10px;
        color:white;
        margin-top:20px;
        margin-bottom:10px;
    ">
        <h3 style="margin:0;">
            Data Collection & Integration (Unified Supply Chain Data Ingestion)
        </h3>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:28px;
        border-radius:12px;
        color:white;
        font-size:16px;
        line-height:1.6;
        margin-bottom:20px;
    ">

    <p>
    This section consolidates data from multiple enterprise supply chain sources
    into a single analytical model.
    </p>

    <b>Integrated Data Domains:</b>
    <ul>
        <li>Inventory — on-hand, reserved, in-transit, overstock, understock quantities and stock value</li>
        <li>Shipments — shipment IDs, routes, vehicles, departure and delivery timelines</li>
        <li>Transfer Recommendations — cluster-based optimal transfer quantities, cost and service optimization scores</li>
        <li>Product Master — SKU codes, product names, brands, categories, subcategories, shelf life, pricing</li>
        <li>Store & Location — store names, regions, zones, cities, store types, area, operating hours</li>
        <li>Supplier — supplier names, lead times, rating scores, payment terms, contract periods</li>
        <li>Time & Calendar — date, day, week, month, quarter, year, holidays, weekends</li>
    </ul>

    <p>
    All data is validated and aligned using a <b>consistent dimensional model</b>
    to ensure supply chain optimization accuracy.
    </p>

    </div>
    """,
    unsafe_allow_html=True
)


if "df" not in st.session_state:
    st.session_state.df = None

if st.button("Load Data"):
    try:
        st.session_state.connection_status = "Connected"
        with st.spinner("Loading supply chain data..."):
            result = safe_data_operation(load_data)
            if result is not None and not result.empty:
                st.session_state.df = result
                st.success("✅ Data loaded successfully!")
            else:
                st.error("❌ Failed to load data. Please try again.")
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.session_state.connection_status = "Disconnected"

df = st.session_state.df

if df is not None:
    st.markdown(
        "<h3 style='color:#000000;'>Data Preview</h3>",
        unsafe_allow_html=True
    )
    render_html_table(df.head(20), max_height=260)
    st.info(f"**Shape:** {df.shape[0]} rows × {df.shape[1]} columns")

# ================================================================
# STEP 2 – DATA PRE-PROCESSING
# ================================================================
if "preprocess_history" not in st.session_state:
    st.session_state.preprocess_history = {
        "duplicates": None,
        "null_replaced_cols": None,
        "null_replaced_rows": None,
        "numeric_converted": None
    }

if "preprocessing_completed" not in st.session_state:
    st.session_state.preprocessing_completed = False


st.markdown("""
<div style="
    background-color:#0B2C5D;
    padding:18px 25px;
    border-radius:10px;
    color:white;
    margin-top:25px;
    margin-bottom:12px;
">
    <h3 style="margin:0;">
        Data Pre-Processing (Data Quality & Readiness)
    </h3>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="
    background-color:#2F75B5;
    padding:24px;
    border-radius:12px;
    color:white;
    font-size:16px;
    line-height:1.7;
    margin-bottom:20px;
">
This section ensures the dataset is <b>model-ready</b> by handling:
<ul>
    <li>Missing values and inconsistencies across supply chain fields</li>
    <li>Outliers and anomalies in inventory quantities, delivery times, and cost metrics</li>
    <li>Data type validation for numeric, categorical, and date fields</li>
    <li>Referential integrity checks across product, store, route, and supplier dimensions</li>
    <li>Time alignment and granularity normalization across shipment and inventory records</li>
</ul>

This step guarantees that downstream models are trained on
<b>clean, reliable, and trustworthy supply chain data.</b>
</div>
""", unsafe_allow_html=True)

if st.session_state.df is None:
    st.warning("⚠ Load data first.")
    st.stop()

df = st.session_state.df

st.markdown(
    "<div style='font-size:20px; font-weight:600; margin-bottom:8px;'>"
    "Select a Data Pre-Processing Step"
    "</div>",
    unsafe_allow_html=True
)
st.write("")

step = st.radio(
    "Select a Data Pre-Processing Step",
    [
        "Remove Duplicate Rows",
        "Replace Missing Values",
        "Convert to Numeric (Safe Columns Only)"
    ],
    index=None,
    horizontal=True,
    label_visibility="visible"
)


# ================================================================
# 1. REMOVE DUPLICATE ROWS
# ================================================================
if "dup_before_df" not in st.session_state:
    st.session_state.dup_before_df = None
if "dup_removed_df" not in st.session_state:
    st.session_state.dup_removed_df = None
if "dup_after_df" not in st.session_state:
    st.session_state.dup_after_df = None

if step == "Remove Duplicate Rows":

    st.markdown("### Remove Duplicate Rows")
    st.write("")

    st.markdown("""
<div style="
    background-color:#2F75B5;
    padding:28px;
    border-radius:12px;
    color:white;
    font-size:16px;
    line-height:1.6;
    margin-bottom:20px;
">
<b>What this does:</b>
This step identifies and removes <b>exact duplicate records</b> from the supply chain dataset.<br>

<b>Duplicate rows often occur due to:</b>
<ul>
    <li>Multiple ETL pipeline runs or batch ingestion retries</li>
    <li>System sync failures between WMS, TMS, and ERP systems</li>
    <li>Manual data merges during consolidation from multiple warehouses</li>
    <li>Duplicate shipment or inventory snapshot records from automated feeds</li>
</ul><br>

<b>Why this is important:</b>
<ul>
    <li>Prevents double-counting of inventory quantities and shipment records</li>
    <li>Avoids inflated stock values and misleading supply chain KPIs</li>
    <li>Ensures transfer recommendation logic operates on clean, unique records</li>
    <li>Maintains data integrity across product, store, and supplier dimensions</li>
</ul>
</div>
""", unsafe_allow_html=True)

    before_df = st.session_state.df
    dataset_size = len(before_df)
    
    # Quick duplicate check for preview
    if dataset_size > 50000:
        st.warning(f"⚠️ Large dataset detected ({dataset_size:,} rows). Duplicate check may take a moment...")
        # Use sample for quick preview
        sample_size = min(10000, dataset_size // 10)
        sample_duplicates = before_df.sample(n=sample_size, random_state=42).duplicated().sum()
        estimated_dup_rate = sample_duplicates / sample_size
        estimated_dups = int(dataset_size * estimated_dup_rate)
        
        st.info(f"📊 Based on sample analysis: ~{estimated_dups:,} duplicate rows estimated")
        dup_rows_preview = pd.DataFrame()  # Don't show actual dup rows for large datasets
    else:
        dup_rows = before_df[before_df.duplicated()]
        dup_rows_preview = dup_rows

    st.markdown(f"""
    <div class="summary-grid">
        <div class="summary-card">
            <div class="summary-title">Total Rows</div>
            <div class="summary-value">{dataset_size:,}</div>
        </div>
        <div class="summary-card">
            <div class="summary-title">Duplicate Rows Found</div>
            <div class="summary-value">{dup_rows_preview.shape[0] if not dup_rows_preview.empty else 'See estimate above'}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Apply Duplicate Removal"):
        if st.session_state.dup_removed_df is not None:
            st.info("Duplicate rows were already removed in this session.")
        else:
            # Check if we have actual duplicate data or just estimates
            if dataset_size > 50000:
                # For large datasets, proceed with optimized processing
                with st.spinner("Analyzing duplicates for large dataset..."):
                    before_df, after_df, removed_df = remove_duplicates_cached(st.session_state.df)
                    
                    if removed_df.empty:
                        st.info("✅ No duplicate rows found in the full dataset.")
                    else:
                        st.session_state.dup_before_df = before_df
                        st.session_state.dup_removed_df = removed_df
                        st.session_state.dup_after_df = after_df
                        st.session_state.df = after_df
                        st.session_state.preprocessing_completed = True
                        st.success(f"✔ Removed {len(removed_df):,} duplicate rows successfully")
            else:
                # For smaller datasets, use the preview data
                if dup_rows_preview.empty:
                    st.info("No duplicate rows found in this dataset.")
                else:
                    with st.spinner("Removing duplicate rows..."):
                        before_df, after_df, removed_df = remove_duplicates_cached(st.session_state.df)
                        st.session_state.dup_before_df = before_df
                        st.session_state.dup_removed_df = removed_df
                        st.session_state.dup_after_df = after_df
                        st.session_state.df = after_df
                        st.session_state.preprocessing_completed = True
                        st.success("✔ Duplicate rows removed successfully")

    if st.session_state.dup_removed_df is not None:
        before_df = st.session_state.dup_before_df
        after_df = st.session_state.dup_after_df
        removed_df = st.session_state.dup_removed_df

        st.markdown("#### Duplicate Removal Summary")
        st.write("")
        st.markdown("""
        <div class="summary-grid">
            <div class="summary-card">
                <div class="summary-title">Rows Before</div>
                <div class="summary-value">{}</div>
            </div>
            <div class="summary-card">
                <div class="summary-title">Rows After</div>
                <div class="summary-value">{}</div>
            </div>
            <div class="summary-card">
                <div class="summary-title">Duplicates Removed</div>
                <div class="summary-value">{}</div>
            </div>
        </div>
        """.format(
            before_df.shape[0],
            after_df.shape[0],
            removed_df.shape[0]
        ), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"#### Before Duplicate Removal ({before_df.shape[0]} Rows)")
        st.write("")
        render_html_table(before_df, title=None, max_height=300)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"#### After Duplicate Removal ({after_df.shape[0]} Rows)")
        st.write("")
        render_html_table(after_df, title=None, max_height=300)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"#### Duplicates Removed ({removed_df.shape[0]} Rows)")
        st.write("")
        render_html_table(removed_df, title=None, max_height=300)




# ================================================================
# 3. REPLACE MISSING VALUES
# ================================================================
if "null_before_rows" not in st.session_state:
    st.session_state.null_before_rows = None
if "null_after_rows" not in st.session_state:
    st.session_state.null_after_rows = None
if "null_replaced_cols" not in st.session_state:
    st.session_state.null_replaced_cols = None

elif step == "Replace Missing Values":

    st.markdown("### Replace Missing Values")
    st.write("")

    st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:28px;
        border-radius:12px;
        color:white;
        font-size:16px;
        line-height:1.6;
        margin-bottom:20px;
    ">

    <b>What this does:</b><br>

    For non-critical categorical fields, missing values are replaced with a placeholder:<br>
    "<b>Unknown</b>"<br><br>

    <b>Supply chain examples where this applies:</b>
    <li>Cluster Name — stores not yet assigned to an optimization cluster</li>
    <li>Model Version — records without a transfer model version tag</li>
    <li>Operating Hours — stores with no recorded operating schedule</li>
    <li>Preferred Payment Terms — suppliers with pending contract details</li><br>

    <b>Why this is important:</b>
    <li>Preserves valuable supply chain records instead of discarding them</li>
    <li>Keeps categorical columns consistent for downstream encoding</li>
    <li>Allows models to learn from "unknown" patterns — e.g., unassigned cluster nodes</li><br>

    <b>Modelling advantage:</b><br>
    Many ML models handle a distinct "<b>Unknown</b>" category better than missing values.<br>

    This improves:
    <li>Model stability across cluster and routing assignments</li>
    <li>Feature completeness for supplier and product dimensions</li>
    <li>Interpretability — unknown entries are explicitly flagged, not hidden</li>

    </div>
    """,
    unsafe_allow_html=True
)

    df = st.session_state.df

    null_mask = df.isnull()
    affected_rows_before = df[null_mask.any(axis=1)]
    null_counts = null_mask.sum()
    null_counts = null_counts[null_counts > 0]

    if st.button("Apply NULL Replacement"):

        if null_counts.empty:
            st.info("This dataset has no missing values — no replacement needed.")

        else:
            with st.spinner("Replacing NULL values..."):
                df_updated, before_rows, after_rows, null_counts_df = replace_nulls_cached(df)
                
                st.session_state.null_before_rows = before_rows
                st.session_state.null_replaced_cols = null_counts_df
                st.session_state.df = df_updated
                st.session_state.preprocessing_completed = True
                st.session_state.null_after_rows = after_rows

                st.success("✔ NULL values replaced with 'Unknown'")

    if (
        st.session_state.null_before_rows is not None and
        st.session_state.null_after_rows is not None and
        st.session_state.null_replaced_cols is not None
    ):

        before_rows = st.session_state.null_before_rows
        after_rows = st.session_state.null_after_rows
        replaced_cols = st.session_state.null_replaced_cols

        st.markdown("#### Columns Where NULL Values Were Replaced")
        st.write("")

        if not replaced_cols.empty:
            value_col = replaced_cols.columns[0]

            html_cards = "".join(
                f"""
                <div class="summary-card">
                    <div class="summary-title">{str(idx).replace('_', ' ').title()}</div>
                    <div class="summary-value">{row[value_col]}</div>
                </div>
                """
                for idx, row in replaced_cols.iterrows()
            )

            st.markdown(
                f"""
                <div class="summary-grid">
                    {html_cards}
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.info("No NULL values were replaced.")

        st.write("")
        st.markdown(
            f"#### Rows Before Missing Values Replacement ({before_rows.shape[0]} Rows)"
        )
        st.write("")
        render_html_table(before_rows)

        st.markdown(
            f"#### Rows After Missing Values Replacement ({after_rows.shape[0]} Rows)"
        )
        st.write("")
        render_html_table(after_rows)

    elif null_counts.empty and st.session_state.null_before_rows is None:
        st.info("ℹ This dataset has no missing values — all fields are complete.")


# ================================================================
# 4. CONVERT TO NUMERIC (SAFE COLUMNS ONLY)
# ================================================================
elif step == "Convert to Numeric (Safe Columns Only)":

    st.markdown("### Convert Columns to Numeric (Safe Columns Only)")
    st.write("")

    st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:28px;
        border-radius:12px;
        color:white;
        font-size:16px;
        line-height:1.6;
        margin-bottom:20px;
    ">

    <b>What this does:</b><br>
    Converts safe, measurable columns into numeric formats so they can be used in analysis and ML models.<br><br>

    <b>Examples of safe numeric columns:</b>
    <li>Quantity Sold, Unit Price, Total Sales Amount</li>
    <li>Discount Applied, Tax Amount, Satisfaction Score</li>
    <li>Forecast Quantity, Weight, Height, Length</li><br>

    <b>What is NOT converted:</b>
    <li>IDs (Product ID, Store ID, Customer ID)</li>
    <li>Categorical labels, Descriptive text fields</li><br>

    <b>Why this is important:</b>
    <li>Enables mathematical operations and aggregations</li>
    <li>Required for correlation analysis and model training</li>
    <li>Prevents runtime errors in ML pipelines</li><br>

    <b>Why "safe columns only" matters:</b>
    Blindly converting columns can corrupt IDs, break joins, and create misleading numerical patterns.

    </div>
    """,
    unsafe_allow_html=True
)

    if "numeric_before_df" not in st.session_state:
        st.session_state.numeric_before_df = None
    if "numeric_after_df" not in st.session_state:
        st.session_state.numeric_after_df = None
    if "numeric_conversion_info" not in st.session_state:
        st.session_state.numeric_conversion_info = None

    df = st.session_state.df
    
    # Quick analysis of potential numeric columns
    potential_numeric_cols = []
    for col in df.columns:
        if not pd.api.types.is_numeric_dtype(df[col]):
            col_lower = col.lower()
            safe_patterns = ['quantity', 'amount', 'price', 'sales', 'cost', 'revenue', 
                           'score', 'rating', 'count', 'total', 'sum', 'discount',
                           'tax', 'forecast', 'weight', 'height', 'length', 'width']
            if any(pattern in col_lower for pattern in safe_patterns):
                potential_numeric_cols.append(col)

    if potential_numeric_cols:
        st.markdown(f"**Found {len(potential_numeric_cols)} potential numeric columns for conversion:**")
        st.write(", ".join(potential_numeric_cols))
    else:
        st.info("No obvious numeric columns found for conversion.")

    if st.button("Apply Numeric Conversion"):

        if st.session_state.numeric_conversion_info is not None:
            st.info("Numeric conversion was already applied earlier.")
        else:
            with st.spinner("Converting columns to numeric..."):
                before_df, after_df, conversion_info = convert_to_numeric_safe_cached(df)
                
                st.session_state.numeric_before_df = before_df
                st.session_state.numeric_after_df = after_df
                st.session_state.numeric_conversion_info = conversion_info

                st.session_state.df = after_df
                st.session_state.preprocessing_completed = True

                st.success("✔ Numeric conversion applied successfully")

    if st.session_state.numeric_conversion_info is not None:

        before_df = st.session_state.numeric_before_df
        after_df = st.session_state.numeric_after_df
        conversion_info = st.session_state.numeric_conversion_info

        st.markdown("#### Numeric Conversion Summary")
        st.write("")
        
        if conversion_info:
            st.markdown("**Columns Successfully Converted:**")
            for col, info in conversion_info.items():
                st.markdown(f"- **{col}**: {info['original_dtype']} - numeric ({info['conversion_rate']:.1f}% success rate)")
        else:
            st.info("No columns were converted (no suitable numeric columns found).")

        st.write("")
        st.markdown(f"#### Dataset Overview After Conversion")
        st.write("")
        
        # Show before/after data types comparison
        before_dtypes = before_df.dtypes
        after_dtypes = after_df.dtypes
        
        changed_cols = []
        for col in before_df.columns:
            if before_dtypes[col] != after_dtypes[col]:
                changed_cols.append({
                    'Column': col,
                    'Before': str(before_dtypes[col]),
                    'After': str(after_dtypes[col])
                })
        
        if changed_cols:
            changes_df = pd.DataFrame(changed_cols)
            st.dataframe(changes_df, use_container_width=True)
        else:
            st.info("No data type changes occurred.")


# ================================================================
# STEP 3 – EDA (LOCKED UNTIL PREPROCESSING)
# ================================================================

if not st.session_state.preprocessing_completed:
    st.info("ℹ Please apply at least one data pre-processing step to unlock EDA.")
    st.stop()

df = st.session_state.get("df", None)

if df is None:
    st.warning("⚠ No dataset available.")
    st.stop()

if "eda_completed" not in st.session_state:
    st.session_state.eda_completed = False

st.markdown(
    """
    <div style="
        background-color:#0B2C5D;
        padding:18px 25px;
        border-radius:10px;
        color:white;
        margin-top:20px;
        margin-bottom:10px;
    ">
        <h3 style="margin:0;">Exploratory Data Analysis (EDA)</h3>
    </div>
    """,
    unsafe_allow_html=True
)
st.write("")
if df is not None:
    st.info(f"Dataset Loaded: **{df.shape[0]} rows × {df.shape[1]} columns**")
st.write("")

st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:28px;
        border-radius:12px;
        color:white;
        font-size:16px;
        line-height:1.6;
        margin-bottom:20px;
    ">

    <b>Exploratory Data Analysis (EDA)</b><br><br>

    Provides <b>high-level supply chain intelligence</b> to understand operational behavior
    before model engineering.<br><br>

    <b>Key Insights Generated:</b>
    <ul>
        <li>Inventory health patterns over time — overstock, understock, fill rates, stockouts</li>
        <li>Product-level stock value, turnover, and demand index distributions</li>
        <li>Store and regional performance — which locations drive most inventory risk</li>
        <li>Shipment and routing efficiency — delivery times, fuel costs, route scores</li>
        <li>Cluster-based transfer analysis — optimal transfer quantities and cost savings</li>
        <li>Supplier performance — lead times, ratings, pricing, and contract quality</li>
        <li>Time and seasonality signals — holiday vs non-holiday, weekly and monthly patterns</li>
    </ul>

    This section focuses on <b>interpretability</b> and operational insight, not deep statistical modeling.

    </div>
    """,
    unsafe_allow_html=True
)

# ================================================================
# COLUMN MAPPING (only if data is loaded)
# ================================================================
if df is not None:
    def map_col(candidates):
        for c in candidates:
            if c in df.columns:
                return c
        return None

    col_product   = map_col(["product_id"])
    col_store     = map_col(["store_id"])
    col_route     = map_col(["route_id"])
    col_vehicle   = map_col(["vehicle_id"])
    col_supplier  = map_col(["supplier_id"])
    col_cluster   = map_col(["cluster_id"])
    col_cluster_name = map_col(["cluster_name"])
    col_date      = map_col(["date"])
    col_onhand    = map_col(["on_hand_qty"])
    col_overstock = map_col(["overstock_qty"])
    col_understock = map_col(["understock_qty"])
    col_stockval  = map_col(["stock_value"])
    col_fill_rate = map_col(["fill_rate_pct"])
    col_stockout  = map_col(["stockout_pct"])
    col_turnover  = map_col(["inventory_turnover"])
    col_excess    = map_col(["excess_inventory_pct"])
    col_delivery  = map_col(["delivery_time_mins"])
    col_fuel      = map_col(["fuel_cost"])
    col_efficiency = map_col(["route_efficiency_score"])
    col_transfer_qty = map_col(["transfer_qty"])
    col_transfer_cost = map_col(["transfer_cost"])
    col_opt_qty   = map_col(["optimal_transfer_qty"])
    col_cost_min  = map_col(["cost_minimization_pct"])
    col_service_gain = map_col(["service_level_gain_pct"])
    col_confidence = map_col(["model_confidence_score"])
    col_demand_index = map_col(["demand_index"])
    col_overstock_index = map_col(["overstock_index"])
    col_lead_time = map_col(["lead_time_days"])
    col_rating    = map_col(["rating_score"])
    col_cost_price = map_col(["cost_price"])
    col_mrp       = map_col(["mrp"])
    col_category  = map_col(["category"])
    col_region    = map_col(["region"])
    col_zone      = map_col(["zone"])
    col_store_type = map_col(["store_type"])
    col_year      = map_col(["year"])
    col_month     = map_col(["month"])
    col_quarter   = map_col(["quarter"])
    col_is_holiday = map_col(["is_holiday"])
    col_is_weekend = map_col(["is_weekend"])
    col_distance  = map_col(["distance_km"])
    col_shelf_life = map_col(["shelf_life_days"])

    num_df = df.select_dtypes(include=np.number)

    # Use sampling for large EDA operations
    SAMPLE_SIZE = 15000 if len(df) > 15000 else len(df)
    if len(df) > SAMPLE_SIZE:
        st.info(f"📊 Using sample of {SAMPLE_SIZE:,} rows for faster EDA visualizations")
        df_sample = df.sample(n=SAMPLE_SIZE, random_state=42)
    else:
        df_sample = df
else:
    # Set default values when no data is loaded
    col_product = col_store = col_route = col_vehicle = col_supplier = None
    col_cluster = col_cluster_name = col_date = col_onhand = col_overstock = None
    col_understock = col_stockval = col_fill_rate = col_stockout = None
    col_turnover = col_excess = col_delivery = col_fuel = col_efficiency = None
    col_transfer_qty = col_transfer_cost = col_opt_qty = col_cost_min = None
    col_service_gain = col_confidence = col_demand_index = col_overstock_index = None
    col_lead_time = col_rating = col_cost_price = col_mrp = col_category = None
    col_region = col_zone = col_store_type = col_year = col_month = None
    col_quarter = col_is_holiday = col_is_weekend = col_distance = None
    col_shelf_life = None
    num_df = pd.DataFrame()
    df_sample = pd.DataFrame()

# ================================================================
# EDA NAVIGATION
# ================================================================
st.markdown("### List of Analytics")
st.markdown("<div style='margin-top:6px'></div>", unsafe_allow_html=True)

if "eda_option" not in st.session_state:
    st.session_state.eda_option = None


def nav_button(label, value):
    if st.session_state.eda_option == value:
        st.markdown(
            f"""
            <div style="
                background-color:#4F97EE;
                color:white;
                padding:14px;
                border-radius:10px;
                font-weight:600;
                text-align:center;
                margin-bottom:12px;
            ">
                {label}
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        if st.button(label, use_container_width=True):
            st.session_state.eda_option = value
            st.rerun()


with st.expander(" ", expanded=True):
    row1 = st.columns(4)
    row2 = st.columns(4)
    row3 = st.columns(4)
    row4 = st.columns(3)

    with row1[0]:
        nav_button("Data Quality Overview", "Data Quality Overview")
    with row1[1]:
        nav_button("Sales Analysis", "Sales Analysis")
    with row1[2]:
        nav_button("Supplier Analysis", "Supplier Analysis")
    with row1[3]:
        nav_button("Product-Level Analysis", "Product-Level Analysis")

    with row2[0]:
        nav_button("Customer Analysis", "Customer Analysis")
    with row2[1]:
        nav_button("Store Analysis", "Store Analysis")
    with row2[2]:
        nav_button("Vendor Analysis", "Vendor Analysis")
    with row2[3]:
        nav_button("Location Analysis", "Location Analysis")

    with row3[0]:
        nav_button("Warehouse Analysis", "Warehouse Analysis")
    with row3[1]:
        nav_button("Transport Route Analysis", "Transport Route Analysis")
    with row3[2]:
        nav_button("Inventory Analysis", "Inventory Analysis")

    with row4[0]:
        nav_button("Redistribution Analysis", "Redistribution Analysis")
    with row4[1]:
        nav_button("Reallocation Analysis", "Reallocation Analysis")
    with row4[2]:
        nav_button("Summary Report", "Summary Report")


eda_option = st.session_state.eda_option
if eda_option is not None:
    st.session_state.eda_completed = True

st.markdown("<div style='margin-top:6px'></div>", unsafe_allow_html=True)

if eda_option is None:
    st.info("Select an analysis to view insights.")


# ================================================================
# COMMON CHART THEME VARS
# ================================================================
GREEN_BG   = "#00D05E"
GRID_GREEN = "#3B3B3B"
BAR_BLUE   = "#001F5C"


def blue_title(title):
    st.markdown(
        f"""
        <div style="
            background-color:#2F75B5;
            padding:14px;
            border-radius:8px;
            font-size:16px;
            color:white;
            margin-bottom:8px;
            text-align:center;
            font-weight:600;
        ">
            {title}
        </div>
        """,
        unsafe_allow_html=True
    )


# ================================================================
# EDA – DATA QUALITY OVERVIEW
# ================================================================
if eda_option == "Data Quality Overview":

    st.markdown(
        """
        <div style="
            background-color:#2F75B5;
            padding:28px;
            border-radius:12px;
            color:white;
            font-size:16px;
            line-height:1.6;
            margin-bottom:20px;
        ">

        <b>What this section does:</b>

        This provides a <b>high-level health check</b> of the supply chain dataset
        before any optimization or forecasting is attempted.

        It evaluates:
        <ul>
            <li>Missing values across all 82 supply chain fields</li>
            <li>Duplicate records that may inflate inventory counts</li>
            <li>Data type consistency across numeric, categorical, and date fields</li>
            <li>Overall row and column completeness</li>
        </ul>

        <b>Why this matters:</b>

        Supply chain optimization models are highly sensitive to <b>poor data quality</b>.
        Even small inconsistencies — duplicate shipment records, invalid inventory quantities,
        missing route IDs — can significantly distort recommendations.<br>

        <b>Key insights users get:</b>
        <ul>
            <li>Whether the dataset is <b>model-ready</b></li>
            <li>Which columns require cleaning or transformation</li>
            <li>Confidence in the reliability of downstream supply chain analysis</li>
        </ul>

        </div>
        """,
        unsafe_allow_html=True
    )

    with st.spinner("Analyzing data quality..."):
        stats = compute_data_quality_stats(df)
        
        rows_count = stats['shape'][0]
        cols_count = stats['shape'][1]
        dup_count = stats['duplicates']
        dtype_counts = stats['dtypes']
        mv_nonzero = stats['missing_values']

    st.markdown(
        f"""
        <div class="quality-card">
            <div class="quality-title">Dataset Shape</div>
            <table class="clean-table">
                <tr><th>Metric</th><th>Value</th></tr>
                <tr><td>Total Rows</td><td>{rows_count:,}</td></tr>
                <tr><td>Total Columns</td><td>{cols_count}</td></tr>
                <tr><td>Numeric Columns</td><td>{len(df.select_dtypes(include=np.number).columns)}</td></tr>
                <tr><td>Categorical Columns</td><td>{len(df.select_dtypes(exclude=np.number).columns)}</td></tr>
                <tr><td>Memory Usage</td><td>{df.memory_usage(deep=True).sum() / 1024**2:.1f} MB</td></tr>
            </table>
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        if mv_nonzero.empty:
            mv_rows = "<tr><td colspan='2' style='text-align:center;color:green;'>✔ No missing values</td></tr>"
        else:
            mv_rows = "".join(f"<tr><td>{c}</td><td>{v}%</td></tr>" for c, v in mv_nonzero.items())

        st.markdown(
            f"""
            <div class="quality-card">
                <div class="quality-title">Missing Value Analysis (%)</div>
                <div class="table-scroll">
                    <table class="clean-table">
                        <tr><th>Column Name</th><th>Missing (%)</th></tr>
                        {mv_rows}
                    </table>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f"""
            <div class="quality-card">
                <div class="quality-title">Duplicate Analysis</div>
                <table class="clean-table">
                    <tr><th>Metric</th><th>Value</th></tr>
                    <tr><td>Total Duplicate Rows</td><td>{dup_count:,}</td></tr>
                </table>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            f"""
            <div class="quality-card">
                <div class="quality-title">Data Types Summary</div>
                <table class="clean-table">
                    <tr><th>Data Type</th><th>Column Count</th></tr>
                    {''.join([f"<tr><td>{d}</td><td>{c}</td></tr>" for d, c in dtype_counts.items()])}
                </table>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("#### Numeric Column Statistics")
    render_html_table(
        stats['numeric_desc'].T.reset_index().rename(columns={"index": "Column"}),
        max_height=400
    )


# ================================================================
# EDA – INVENTORY OVERVIEW
# ================================================================
elif eda_option == "Inventory Overview":

    st.markdown(
        """
        <div style="
            background-color:#2F75B5;
            padding:28px;
            border-radius:12px;
            color:white;
            font-size:16px;
            line-height:1.6;
            margin-bottom:20px;
        ">

        <b>What this section does:</b>

        This provides a <b>macro-level snapshot of inventory health</b> across all
        products, stores, and time periods, answering the question:
        "What does our overall inventory position look like — and where are the risks?"

        It typically highlights:
        <ul>
            <li>Total on-hand, overstock, and understock quantities</li>
            <li>Average fill rate and stockout rate</li>
            <li>Inventory turnover and excess inventory percentages</li>
            <li>Stock value distribution over time</li>
        </ul><br>

        <b>Why this matters:</b>

        Before drilling into product or store details, it is important to understand:
        <ul>
            <li>Overall inventory health and balance</li>
            <li>Presence of systemic overstock or understock patterns</li>
            <li>Seasonal variation in inventory levels</li>
        </ul><br>

        <b>Key insights users get:</b>
        <ul>
            <li>Baseline inventory behavior across time</li>
            <li>Early signals of overstock accumulation or stockout risk</li>
            <li>Context for all deeper supply chain analyses</li>
        </ul>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### Inventory Overview")

    # Add progress indicator for large datasets
    if len(df) > 100000:
        st.info("📊 Processing inventory metrics for large dataset...")
    
    with st.spinner("Calculating inventory metrics..."):
        total_onhand    = df[col_onhand].sum()
        total_overstock = df[col_overstock].sum()
        total_understock = df[col_understock].sum()
        total_stockval  = df[col_stockval].sum()
        avg_fill_rate   = df[col_fill_rate].mean()
        avg_stockout    = df[col_stockout].mean()
        avg_turnover    = df[col_turnover].mean()
        avg_excess      = df[col_excess].mean()

    st.markdown(f"""
    <div class="summary-grid">
        <div class="summary-card"><div class="summary-title">Total On-Hand Qty</div><div class="summary-value">{total_onhand:,.0f}</div></div>
        <div class="summary-card"><div class="summary-title">Total Overstock Qty</div><div class="summary-value">{total_overstock:,.0f}</div></div>
        <div class="summary-card"><div class="summary-title">Total Understock Qty</div><div class="summary-value">{total_understock:,.0f}</div></div>
        <div class="summary-card"><div class="summary-title">Total Stock Value</div><div class="summary-value">₹{total_stockval:,.0f}</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="summary-grid">
        <div class="summary-card"><div class="summary-title">Avg Fill Rate (%)</div><div class="summary-value">{avg_fill_rate:.1f}%</div></div>
        <div class="summary-card"><div class="summary-title">Avg Stockout Rate (%)</div><div class="summary-value">{avg_stockout:.1f}%</div></div>
        <div class="summary-card"><div class="summary-title">Avg Inventory Turnover</div><div class="summary-value">{avg_turnover:.2f}</div></div>
        <div class="summary-card"><div class="summary-title">Avg Excess Inventory (%)</div><div class="summary-value">{avg_excess:.1f}%</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    st.write("")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df["Year"]    = df["date"].dt.year
    df["Quarter"] = df["date"].dt.to_period("Q").astype(str)
    df["Month"]   = df["date"].dt.to_period("M").astype(str)

    # -- Stock Value by Year --
    st.markdown("""
    <div style="background-color:#2F75B5;padding:18px 25px;border-radius:10px;font-size:20px;color:white;margin-top:20px;margin-bottom:10px;text-align:center;">
        <b>Stock Value by Year</b>
    </div>
    """, unsafe_allow_html=True)

    sv_year = df.groupby("Year")[col_stockval].sum().sort_index()
    chart_yr = (
        alt.Chart(sv_year.reset_index())
        .mark_bar(color=BAR_BLUE, cornerRadiusEnd=6)
        .encode(
            x=alt.X("Year:O", title="Year"),
            y=alt.Y(f"{col_stockval}:Q", title="Total Stock Value", scale=alt.Scale(padding=10)),
            tooltip=["Year", col_stockval]
        )
        .properties(height=380, background=GREEN_BG,
                    padding={"top":10,"left":10,"right":10,"bottom":10})
        .configure_view(fill=GREEN_BG, strokeOpacity=0)
        .configure_axis(labelColor="#000000", titleColor="#000000",
                        gridColor="rgba(0,0,0,0.2)", domainColor="rgba(0,0,0,0.3)")
    )
    st.altair_chart(chart_yr, use_container_width=True)

    # -- Stock Value by Quarter --
    st.markdown("""
    <div style="background-color:#2F75B5;padding:18px 25px;border-radius:10px;font-size:20px;color:white;margin-top:20px;margin-bottom:10px;text-align:center;">
        <b>Stock Value by Quarter</b>
    </div>
    """, unsafe_allow_html=True)

    sv_qtr = df.groupby("Quarter")[col_stockval].sum().sort_index()
    chart_qtr = (
        alt.Chart(sv_qtr.reset_index())
        .mark_bar(color=BAR_BLUE, cornerRadiusEnd=6)
        .encode(
            x=alt.X("Quarter:O", title="Quarter"),
            y=alt.Y(f"{col_stockval}:Q", title="Total Stock Value", scale=alt.Scale(padding=10)),
            tooltip=["Quarter", col_stockval]
        )
        .properties(height=380, background=GREEN_BG,
                    padding={"top":10,"left":10,"right":10,"bottom":10})
        .configure_view(fill=GREEN_BG, strokeOpacity=0)
        .configure_axis(labelColor="#000000", titleColor="#000000",
                        gridColor="rgba(0,0,0,0.2)", domainColor="rgba(0,0,0,0.3)")
    )
    st.altair_chart(chart_qtr, use_container_width=True)

    # -- Stock Value by Month --
    st.markdown("""
    <div style="background-color:#2F75B5;padding:18px 25px;border-radius:10px;font-size:20px;color:white;margin-top:20px;margin-bottom:10px;text-align:center;">
        <b>Stock Value by Month</b>
    </div>
    """, unsafe_allow_html=True)

    sv_month = df.groupby("Month")[col_stockval].sum().sort_index()
    chart_month = (
        alt.Chart(sv_month.reset_index())
        .mark_bar(color=BAR_BLUE, cornerRadiusEnd=6)
        .encode(
            x=alt.X("Month:O", title="Month"),
            y=alt.Y(f"{col_stockval}:Q", title="Total Stock Value", scale=alt.Scale(padding=10)),
            tooltip=["Month", col_stockval]
        )
        .properties(height=380, background=GREEN_BG,
                    padding={"top":10,"left":10,"right":10,"bottom":10})
        .configure_view(fill=GREEN_BG, strokeOpacity=0)
        .configure_axis(labelColor="#000000", titleColor="#000000",
                        gridColor="rgba(0,0,0,0.2)", domainColor="rgba(0,0,0,0.3)")
    )
    st.altair_chart(chart_month, use_container_width=True)

    # -- Overstock vs Understock by Region --
    st.markdown("""
    <div style="background-color:#2F75B5;padding:18px 25px;border-radius:10px;font-size:20px;color:white;margin-top:20px;margin-bottom:10px;text-align:center;">
        <b>Overstock vs Understock by Region</b>
    </div>
    """, unsafe_allow_html=True)

    reg_inv = df.groupby(col_region).agg(
        total_overstock=(col_overstock, "sum"),
        total_understock=(col_understock, "sum")
    ).sort_values("total_overstock", ascending=False)

    x_reg = np.arange(len(reg_inv))
    w = 0.35
    fig_reg, ax_reg = plt.subplots(figsize=(10, 4))
    fig_reg.patch.set_facecolor(GREEN_BG)
    ax_reg.set_facecolor(GREEN_BG)
    ax_reg.bar(x_reg - w/2, reg_inv["total_overstock"], w, label="Overstock", color=BAR_BLUE)
    ax_reg.bar(x_reg + w/2, reg_inv["total_understock"], w, label="Understock", color="#EF4444")
    ax_reg.set_xticks(x_reg)
    ax_reg.set_xticklabels(reg_inv.index.astype(str), rotation=45, ha="right")
    ax_reg.set_ylabel("Quantity")
    ax_reg.set_xlabel("Region")
    ax_reg.legend()
    ax_reg.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
    ax_reg.spines["top"].set_visible(False)
    ax_reg.spines["right"].set_visible(False)
    st.pyplot(fig_reg)
    plt.close(fig_reg)


# ================================================================
# EDA – PRODUCT-LEVEL ANALYSIS
# ================================================================
elif eda_option == "Product-Level Analysis":

    st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:28px;
        border-radius:12px;
        color:white;
        font-size:16px;
        line-height:1.6;
        margin-bottom:20px;
    ">
    <b>What this section does:</b>
    <li>This section analyzes <b>inventory and supply chain performance at the SKU / product level</b></li>

    It focuses on:
    <ul>
        <li>Top and bottom-performing products by stock value</li>
        <li>Demand index vs overstock index per product</li>
        <li>Inventory turnover and shelf life risk across SKUs</li>
        <li>Cost price vs MRP margin distribution by category</li>
    </ul>

    <b>Why this matters:</b>

    Supply chain decisions at an aggregate level hide <b>SKU-specific behavior</b>.
    Some products are fast-moving, others have long shelf life and accumulate overstock.<br>

    <b>Key insights users get:</b>
    <ul>
        <li>Which products drive the majority of stock value</li>
        <li>Which SKUs have misaligned demand vs supply</li>
        <li>Candidates for product-level replenishment model optimization</li>
    </ul>

    </div>
    """,
    unsafe_allow_html=True
    )

    TOP_N = 20

    product_metrics = (
        df.groupby(col_product)
        .agg(
            total_stock_value=(col_stockval, "sum"),
            avg_on_hand=(col_onhand, "mean"),
            avg_overstock=(col_overstock, "mean"),
            avg_understock=(col_understock, "mean"),
            avg_demand_index=(col_demand_index, "mean"),
            avg_overstock_index=(col_overstock_index, "mean"),
            avg_turnover=(col_turnover, "mean"),
            avg_fill_rate=(col_fill_rate, "mean")
        )
        .sort_values("total_stock_value", ascending=False)
    )

    top_products = product_metrics.head(TOP_N)
    top_demand  = product_metrics.sort_values("avg_demand_index", ascending=False).head(5)
    top_turnover = product_metrics.sort_values("avg_turnover", ascending=False).head(5)
    label_products = pd.concat([top_demand, top_turnover]).drop_duplicates()

    col1, col2 = st.columns(2)

    # Plot 1: Stock Value by Product
    with col1:
        blue_title("Stock Value Contribution by Product")
        fig1, ax1 = plt.subplots(figsize=(7, 4))
        fig1.patch.set_facecolor(GREEN_BG)
        ax1.set_facecolor(GREEN_BG)
        fig1.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.32)
        ax1.bar(top_products.index.astype(str), top_products["total_stock_value"], color=BAR_BLUE)
        ax1.set_xlabel("Product ID")
        ax1.set_ylabel("Total Stock Value")
        ax1.tick_params(axis="x", rotation=45)
        ax1.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax1.spines["top"].set_visible(False)
        ax1.spines["right"].set_visible(False)
        st.pyplot(fig1)
        plt.close(fig1)

    # Plot 2: Demand Index vs Overstock Index
    with col2:
        blue_title("Product Demand Index vs Overstock Index")
        fig2, ax2 = plt.subplots(figsize=(7, 4))
        fig2.patch.set_facecolor(GREEN_BG)
        ax2.set_facecolor(GREEN_BG)
        fig2.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.13)
        ax2.scatter(
            product_metrics["avg_demand_index"],
            product_metrics["avg_overstock_index"],
            alpha=0.6, color=BAR_BLUE
        )
        ax2.set_xlabel("Avg Demand Index")
        ax2.set_ylabel("Avg Overstock Index")
        ax2.grid(True, linestyle="-", color=GRID_GREEN, alpha=0.5)
        for pid, row in label_products.iterrows():
            ax2.annotate(pid, (row["avg_demand_index"], row["avg_overstock_index"]),
                         xytext=(5, 5), textcoords="offset points", fontsize=8, alpha=0.9)
        ax2.spines["top"].set_visible(False)
        ax2.spines["right"].set_visible(False)
        st.pyplot(fig2)
        plt.close(fig2)

    col3, col4 = st.columns(2)

    # Plot 3: Inventory Turnover vs Fill Rate
    with col3:
        blue_title("Inventory Turnover vs Fill Rate by Product")
        product_tv = (
            df.groupby(col_product)
            .agg(
                avg_turnover=(col_turnover, "mean"),
                avg_fill_rate=(col_fill_rate, "mean")
            )
            .sort_values("avg_turnover", ascending=False)
            .head(20)
        )
        x_tv = np.arange(len(product_tv))
        w_tv = 0.35
        fig3, ax3 = plt.subplots(figsize=(7, 4))
        fig3.patch.set_facecolor(GREEN_BG)
        ax3.set_facecolor(GREEN_BG)
        fig3.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.32)
        ax3.bar(x_tv - w_tv/2, product_tv["avg_turnover"], w_tv, label="Avg Turnover", color=BAR_BLUE)
        ax3_r = ax3.twinx()
        ax3_r.bar(x_tv + w_tv/2, product_tv["avg_fill_rate"], w_tv, label="Avg Fill Rate %", color="#F59E0B")
        ax3.set_xticks(x_tv)
        ax3.set_xticklabels(product_tv.index.astype(str), rotation=45, ha="right", fontsize=7)
        ax3.set_ylabel("Inventory Turnover")
        ax3_r.set_ylabel("Fill Rate (%)")
        h1, l1 = ax3.get_legend_handles_labels()
        h2, l2 = ax3_r.get_legend_handles_labels()
        ax3.legend(h1 + h2, l1 + l2, loc="upper right", fontsize=8)
        ax3.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax3.spines["top"].set_visible(False)
        ax3.spines["right"].set_visible(False)
        st.pyplot(fig3)
        plt.close(fig3)

    # Plot 4: Cost Price vs MRP by Category
    with col4:
        blue_title("Cost Price vs MRP by Category")
        cat_pricing = (
            df.groupby(col_category)
            .agg(
                avg_cost_price=(col_cost_price, "mean"),
                avg_mrp=(col_mrp, "mean")
            )
            .sort_values("avg_mrp", ascending=False)
        )
        x_cp = np.arange(len(cat_pricing))
        w_cp = 0.35
        fig4, ax4 = plt.subplots(figsize=(7, 4))
        fig4.patch.set_facecolor(GREEN_BG)
        ax4.set_facecolor(GREEN_BG)
        fig4.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.17)
        ax4.bar(x_cp - w_cp/2, cat_pricing["avg_cost_price"], w_cp, label="Avg Cost Price", color=BAR_BLUE)
        ax4.bar(x_cp + w_cp/2, cat_pricing["avg_mrp"], w_cp, label="Avg MRP", color="#F59E0B")
        ax4.set_xticks(x_cp)
        ax4.set_xticklabels(cat_pricing.index.astype(str), rotation=45, ha="right")
        ax4.set_ylabel("Price (₹)")
        ax4.set_xlabel("Category")
        ax4.legend()
        ax4.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax4.spines["top"].set_visible(False)
        ax4.spines["right"].set_visible(False)
        st.pyplot(fig4)
        plt.close(fig4)



    st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:28px;
        border-radius:12px;
        color:white;
        font-size:16px;
        line-height:1.6;
        margin-bottom:22px;
    ">

    <b>What this section does:</b>

    This examines how <b>inventory health varies across stores, regions, zones, and store types</b>.

    It evaluates:
    <ul>
        <li>Store-wise stock value and inventory levels</li>
        <li>Performance comparison across regions and zones</li>
        <li>High-risk vs low-risk stores for stockout and overstock</li>
    </ul><br>

    <b>Why this matters:</b>

    Inventory optimization accuracy improves when <b>store heterogeneity</b> is understood.<br>
    Not all stores carry the same product mix, face the same demand patterns,
    or have the same fill rate targets.<br><br>

    <b>Key insights users get:</b>
    <ul>
        <li>Store and regional inventory demand clusters</li>
        <li>Regional fill rate and stockout disparities</li>
        <li>Inputs for store-level or region-level inventory optimization models</li>
    </ul>

    </div>
    """,
    unsafe_allow_html=True
)

    TOP_STORES   = 20
    TOP_PRODUCTS = 20

    top_stores = (
        df.groupby(col_store, observed=True)[col_stockval]
        .sum()
        .sort_values(ascending=False)
        .head(TOP_STORES)
        .index
    )

    store_product_qty = (
        df[df[col_store].isin(top_stores)]
        .groupby([col_store, col_product], observed=True)[col_onhand]
        .sum()
        .reset_index()
    )

    store_top_products = (
        store_product_qty
        .sort_values([col_store, col_onhand], ascending=[True, False])
        .groupby(col_store, observed=True)
        .head(TOP_PRODUCTS)
    )

    pivot_qty = store_top_products.pivot_table(
        index=col_store,
        columns=col_product,
        values=col_onhand,
        fill_value=0,
        observed=True
    )

    col1, col2 = st.columns(2)

    # Plot 1: Stock Value Concentration by Store
    with col1:
        blue_title("Stock Value Concentration Across Stores")

        store_sv = (
            df.groupby(col_store, observed=True)[col_stockval]
            .sum()
            .loc[top_stores]
        )

        fig1, ax1 = plt.subplots(figsize=(7, 4))
        fig1.patch.set_facecolor(GREEN_BG)
        ax1.set_facecolor(GREEN_BG)
        fig1.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.16)
        ax1.bar(store_sv.index.astype(str), store_sv.values, color=BAR_BLUE)
        ax1.set_xlabel("Store ID")
        ax1.set_ylabel("Total Stock Value")
        ax1.tick_params(axis="x", rotation=45)
        ax1.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax1.spines["top"].set_visible(False)
        ax1.spines["right"].set_visible(False)
        st.pyplot(fig1)
        plt.close(fig1)

    # Plot 2: Store-wise Product Mix (On-Hand Qty)
    with col2:
        blue_title("Store-wise Product Mix (On-Hand Quantity)")

        fig2, ax2 = plt.subplots(figsize=(7, 4))
        fig2.patch.set_facecolor(GREEN_BG)
        ax2.set_facecolor(GREEN_BG)
        fig2.subplots_adjust(left=0.08, right=0.78, top=0.92, bottom=0.25)

        bottom = np.zeros(len(pivot_qty))
        for product in pivot_qty.columns:
            ax2.bar(
                pivot_qty.index.astype(str),
                pivot_qty[product],
                bottom=bottom,
                width=0.6,
                label=str(product)
            )
            bottom += pivot_qty[product].values

        ax2.set_xlabel("Store ID")
        ax2.set_ylabel("On-Hand Quantity")
        ax2.tick_params(axis="x", rotation=45)
        for label in ax2.get_xticklabels():
            label.set_ha("right")
        ax2.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax2.legend(title="Product ID", bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
        ax2.spines["top"].set_visible(False)
        ax2.spines["right"].set_visible(False)
        st.pyplot(fig2)
        plt.close(fig2)

    col3, col4 = st.columns(2)

    # Plot 3: Store Fill Rate vs Stockout Rate
    with col3:
        blue_title("Store Fill Rate vs Stockout Rate")

        store_rates = (
            df.groupby(col_store, observed=True)
            .agg(
                avg_fill_rate=(col_fill_rate, "mean"),
                avg_stockout=(col_stockout, "mean")
            )
            .loc[top_stores]
        )

        x_sr = np.arange(len(store_rates))
        w_sr = 0.35

        fig3, ax3 = plt.subplots(figsize=(7, 4))
        fig3.patch.set_facecolor(GREEN_BG)
        ax3.set_facecolor(GREEN_BG)
        fig3.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.28)

        ax3.bar(x_sr - w_sr/2, store_rates["avg_fill_rate"], w_sr, label="Fill Rate %", color=BAR_BLUE)
        ax3.bar(x_sr + w_sr/2, store_rates["avg_stockout"], w_sr, label="Stockout %", color="#EF4444")
        ax3.set_xticks(x_sr)
        ax3.set_xticklabels(store_rates.index.astype(str), rotation=45, ha="right")
        ax3.set_ylabel("Percentage (%)")
        ax3.set_xlabel("Store ID")
        ax3.legend()
        ax3.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax3.spines["top"].set_visible(False)
        ax3.spines["right"].set_visible(False)
        st.pyplot(fig3)
        plt.close(fig3)

    # Plot 4: On-Hand vs Stock Value by Store
    with col4:
        blue_title("On-Hand Quantity vs Stock Value by Store")

        store_eff = (
            df.groupby(col_store, observed=True)
            .agg(
                total_on_hand=(col_onhand, "sum"),
                total_stock_value=(col_stockval, "sum")
            )
            .loc[top_stores]
        )

        x_eff = np.arange(len(store_eff))
        w_eff = 0.35

        fig4, ax4a = plt.subplots(figsize=(7, 4))
        fig4.patch.set_facecolor(GREEN_BG)
        ax4a.set_facecolor(GREEN_BG)
        fig4.subplots_adjust(left=0.10, right=0.90, top=0.92, bottom=0.26)

        ax4a.bar(x_eff - w_eff/2, store_eff["total_on_hand"], w_eff, label="On-Hand Qty", color=BAR_BLUE)
        ax4a.set_ylabel("On-Hand Quantity")

        ax4b = ax4a.twinx()
        ax4b.bar(x_eff + w_eff/2, store_eff["total_stock_value"], w_eff, label="Stock Value", color="#F59E0B")
        ax4b.set_ylabel("Stock Value (₹)")

        ax4a.set_xticks(x_eff)
        ax4a.set_xticklabels(store_eff.index.astype(str), rotation=45, ha="right")
        ax4a.set_xlabel("Store ID")

        h1, l1 = ax4a.get_legend_handles_labels()
        h2, l2 = ax4b.get_legend_handles_labels()
        ax4a.legend(h1 + h2, l1 + l2, loc="upper right")

        ax4a.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax4a.spines["top"].set_visible(False)
        ax4a.spines["right"].set_visible(False)
        ax4b.spines["top"].set_visible(False)
        st.pyplot(fig4)
        plt.close(fig4)



    st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:28px;
        border-radius:12px;
        color:white;
        font-size:16px;
        line-height:1.6;
        margin-bottom:20px;
    ">

    <b>What this section does:</b><br><br>

    This provides a <b>high-level view of logistics performance</b> across shipments,
    routes, and vehicles. It evaluates:
    <ul>
        <li>Delivery time distribution and outliers</li>
        <li>Fuel cost patterns by route</li>
        <li>Route efficiency scores across the network</li>
        <li>Distance vs travel time relationships</li>
    </ul>

    <b>Why this matters:</b>

    Understanding logistics behavior helps identify
    <b>inefficient routes, high-cost corridors, and delivery delays</b>.
    It establishes a routing baseline before deeper optimization.

    <b>Key insights users get:</b>
    <ul>
        <li>Which routes consistently underperform on efficiency</li>
        <li>Delivery time vs fuel cost trade-offs</li>
        <li>Inputs for route optimization and vehicle assignment models</li>
    </ul>

    </div>
    """,
    unsafe_allow_html=True
)

    avg_delivery  = df[col_delivery].mean()
    avg_fuel      = df[col_fuel].mean()
    avg_eff       = df[col_efficiency].mean()
    avg_dist      = df[col_distance].mean()

    st.markdown(f"""
    <div class="summary-grid">
        <div class="summary-card"><div class="summary-title">Avg Delivery Time (mins)</div><div class="summary-value">{avg_delivery:.0f}</div></div>
        <div class="summary-card"><div class="summary-title">Avg Fuel Cost (₹)</div><div class="summary-value">₹{avg_fuel:.2f}</div></div>
        <div class="summary-card"><div class="summary-title">Avg Route Efficiency Score</div><div class="summary-value">{avg_eff:.3f}</div></div>
        <div class="summary-card"><div class="summary-title">Avg Distance (km)</div><div class="summary-value">{avg_dist:.1f} km</div></div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # Plot 1: Delivery Time Distribution
    with col1:
        blue_title("Delivery Time Distribution (mins)")
        fig1, ax1 = plt.subplots(figsize=(7, 4))
        fig1.patch.set_facecolor(GREEN_BG)
        ax1.set_facecolor(GREEN_BG)
        ax1.hist(df[col_delivery].dropna(), bins=30, color=BAR_BLUE, edgecolor="white", alpha=0.9)
        ax1.set_xlabel("Delivery Time (mins)")
        ax1.set_ylabel("Frequency")
        ax1.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax1.spines["top"].set_visible(False)
        ax1.spines["right"].set_visible(False)
        st.pyplot(fig1)
        plt.close(fig1)

    # Plot 2: Fuel Cost vs Route Efficiency Score
    with col2:
        blue_title("Fuel Cost vs Route Efficiency Score")
        fig2, ax2 = plt.subplots(figsize=(7, 4))
        fig2.patch.set_facecolor(GREEN_BG)
        ax2.set_facecolor(GREEN_BG)
        fig2.subplots_adjust(left=0.10, right=0.98, top=0.92, bottom=0.13)
        ax2.scatter(df[col_fuel], df[col_efficiency], alpha=0.3, color=BAR_BLUE, s=15)
        ax2.set_xlabel("Fuel Cost (₹)")
        ax2.set_ylabel("Route Efficiency Score")
        ax2.grid(True, linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax2.spines["top"].set_visible(False)
        ax2.spines["right"].set_visible(False)
        st.pyplot(fig2)
        plt.close(fig2)

    col3, col4 = st.columns(2)

    # Plot 3: Top Routes by Avg Efficiency Score
    with col3:
        blue_title("Top Routes by Avg Efficiency Score")
        TOP_ROUTES = 15
        route_eff = (
            df.groupby(col_route)[col_efficiency]
            .mean()
            .sort_values(ascending=False)
            .head(TOP_ROUTES)
        )
        fig3, ax3 = plt.subplots(figsize=(7, 4))
        fig3.patch.set_facecolor(GREEN_BG)
        ax3.set_facecolor(GREEN_BG)
        fig3.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.32)
        ax3.bar(route_eff.index.astype(str), route_eff.values, color=BAR_BLUE)
        ax3.set_xlabel("Route ID")
        ax3.set_ylabel("Avg Efficiency Score")
        ax3.tick_params(axis="x", rotation=45)
        ax3.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax3.spines["top"].set_visible(False)
        ax3.spines["right"].set_visible(False)
        st.pyplot(fig3)
        plt.close(fig3)

    # Plot 4: Fuel Cost vs Delivery Time (Scatter with Labels)
    with col4:
        blue_title("Fuel Cost vs Delivery Time by Route")
        route_scatter = (
            df.groupby(col_route)
            .agg(
                avg_fuel=(col_fuel, "mean"),
                avg_delivery=(col_delivery, "mean"),
                total_shipments=(col_efficiency, "count")
            )
            .sort_values("avg_fuel", ascending=False)
            .head(20)
        )
        max_fuel = route_scatter["avg_fuel"].max()
        fig4, ax4 = plt.subplots(figsize=(7, 4))
        fig4.patch.set_facecolor(GREEN_BG)
        ax4.set_facecolor(GREEN_BG)
        fig4.subplots_adjust(left=0.10, right=0.98, top=0.92, bottom=0.17)
        ax4.scatter(
            route_scatter["avg_fuel"],
            route_scatter["avg_delivery"],
            s=route_scatter["total_shipments"] * 5,
            alpha=0.75,
            color=BAR_BLUE,
            edgecolors="black",
            linewidth=0.5
        )
        ax4.plot([0, max_fuel], [0, max_fuel],
                 linestyle="--", color=GRID_GREEN, alpha=0.6)
        top_labels_r = route_scatter.sort_values("avg_delivery", ascending=False).head(7)
        for rid, row in top_labels_r.iterrows():
            ax4.annotate(rid, (row["avg_fuel"], row["avg_delivery"]),
                         xytext=(6, 6), textcoords="offset points", fontsize=9)
        ax4.set_xlabel("Avg Fuel Cost (₹)")
        ax4.set_ylabel("Avg Delivery Time (mins)")
        ax4.grid(True, linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax4.spines["top"].set_visible(False)
        ax4.spines["right"].set_visible(False)
        st.pyplot(fig4)
        plt.close(fig4)



    st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:28px;
        border-radius:12px;
        color:white;
        font-size:16px;
        line-height:1.6;
        margin-bottom:20px;
    ">

    <b>What this section does:</b><br><br>

    This analyzes how <b>cluster-based transfer recommendations</b> perform across the supply network.
    It evaluates:
    <ul>
        <li>Optimal transfer quantity vs actual transfer quantity per cluster</li>
        <li>Cost minimization percentage achieved by each cluster</li>
        <li>Service level gain from transfer recommendations</li>
        <li>Model confidence scores across clusters</li>
    </ul>
    <br>

    <b>Why this matters:</b>

    Cluster-based transfers reduce imbalances between overstock and understock nodes.
    This analysis identifies <b>which clusters are most efficiently optimized</b>
    and where model confidence gaps exist.<br>

    <b>Key insights users get:</b>
    <ul>
        <li>High-performing vs underperforming clusters</li>
        <li>Transfer cost efficiency across cluster pairs</li>
        <li>Which clusters should be prioritized for re-optimization</li>
    </ul>

    </div>
    """,
    unsafe_allow_html=True
)

    TOP_CLUSTERS = 15

    cluster_metrics = (
        df.groupby(col_cluster_name)
        .agg(
            avg_optimal_qty=(col_opt_qty, "mean"),
            avg_transfer_qty=(col_transfer_qty, "mean"),
            avg_transfer_cost=(col_transfer_cost, "mean"),
            avg_cost_min=(col_cost_min, "mean"),
            avg_service_gain=(col_service_gain, "mean"),
            avg_confidence=(col_confidence, "mean"),
            total_shipments=(col_transfer_qty, "count")
        )
        .sort_values("avg_cost_min", ascending=False)
        .head(TOP_CLUSTERS)
    )

    col1, col2 = st.columns(2)

    # Plot 1: Cluster Profitability (Cost Minimization %)
    with col1:
        blue_title("Cluster Cost Minimization % (Top 15 Clusters)")
        fig1, ax1 = plt.subplots(figsize=(7, 4))
        fig1.patch.set_facecolor(GREEN_BG)
        ax1.set_facecolor(GREEN_BG)
        fig1.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.28)
        ax1.bar(cluster_metrics.index.astype(str), cluster_metrics["avg_cost_min"], alpha=0.85, color=BAR_BLUE)
        ax1.axhline(0, color="black", linewidth=1)
        ax1.set_xlabel("Cluster Name")
        ax1.set_ylabel("Avg Cost Minimization %")
        ax1.tick_params(axis="x", rotation=45)
        ax1.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax1.spines["top"].set_visible(False)
        ax1.spines["right"].set_visible(False)
        st.pyplot(fig1)
        plt.close(fig1)

    # Plot 2: Optimal Qty vs Transfer Cost (Scatter)
    with col2:
        blue_title("Cluster Effectiveness: Optimal Qty vs Transfer Cost")
        fig2, ax2 = plt.subplots(figsize=(7, 4))
        fig2.patch.set_facecolor(GREEN_BG)
        ax2.set_facecolor(GREEN_BG)
        fig2.subplots_adjust(left=0.10, right=0.98, top=0.92, bottom=0.13)
        ax2.scatter(
            cluster_metrics["avg_transfer_cost"],
            cluster_metrics["avg_optimal_qty"],
            s=cluster_metrics["avg_optimal_qty"] / 3,
            alpha=0.75,
            color=BAR_BLUE,
            edgecolors="black",
            linewidth=0.5
        )
        max_cost_c = cluster_metrics["avg_transfer_cost"].max()
        ax2.plot([0, max_cost_c], [0, max_cost_c],
                 linestyle="--", color=GRID_GREEN, alpha=0.6)
        top_labels_c = cluster_metrics.sort_values("avg_optimal_qty", ascending=False).head(7)
        for cname, row in top_labels_c.iterrows():
            ax2.annotate(cname, (row["avg_transfer_cost"], row["avg_optimal_qty"]),
                         xytext=(6, 6), textcoords="offset points", fontsize=9)
        ax2.set_xlabel("Avg Transfer Cost (₹)")
        ax2.set_ylabel("Avg Optimal Transfer Qty")
        ax2.grid(True, linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax2.spines["top"].set_visible(False)
        ax2.spines["right"].set_visible(False)
        st.pyplot(fig2)
        plt.close(fig2)

    col3, col4 = st.columns(2)

    # Plot 3: Optimal Qty vs Actual Transfer Qty
    with col3:
        blue_title("Optimal Transfer Qty vs Actual Transfer Qty (Execution Gap)")
        x_cq = np.arange(len(cluster_metrics))
        w_cq = 0.35
        fig3, ax3 = plt.subplots(figsize=(8, 4))
        fig3.patch.set_facecolor(GREEN_BG)
        ax3.set_facecolor(GREEN_BG)
        fig3.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.18)
        ax3.bar(x_cq - w_cq/2, cluster_metrics["avg_optimal_qty"], w_cq, label="Optimal Qty", color=BAR_BLUE)
        ax3.bar(x_cq + w_cq/2, cluster_metrics["avg_transfer_qty"], w_cq, label="Actual Transfer Qty", color="#EF4444")
        ax3.set_xticks(x_cq)
        ax3.set_xticklabels(cluster_metrics.index.astype(str), rotation=45, ha="right")
        ax3.set_xlabel("Cluster Name")
        ax3.set_ylabel("Quantity")
        ax3.legend()
        ax3.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax3.spines["top"].set_visible(False)
        ax3.spines["right"].set_visible(False)
        st.pyplot(fig3)
        plt.close(fig3)

    # Plot 4: Service Gain vs Model Confidence
    with col4:
        blue_title("Service Level Gain vs Model Confidence by Cluster")
        x_sg = np.arange(len(cluster_metrics))
        w_sg = 0.35
        fig4, ax4s = plt.subplots(figsize=(8, 4))
        fig4.patch.set_facecolor(GREEN_BG)
        ax4s.set_facecolor(GREEN_BG)
        fig4.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.28)
        ax4s.bar(x_sg - w_sg/2, cluster_metrics["avg_service_gain"], w_sg, label="Service Level Gain %", color=BAR_BLUE)
        ax4sc = ax4s.twinx()
        ax4sc.bar(x_sg + w_sg/2, cluster_metrics["avg_confidence"], w_sg, label="Model Confidence", color="#F59E0B")
        ax4s.set_xticks(x_sg)
        ax4s.set_xticklabels(cluster_metrics.index.astype(str), rotation=45, ha="right")
        ax4s.set_xlabel("Cluster Name")
        ax4s.set_ylabel("Service Level Gain %")
        ax4sc.set_ylabel("Model Confidence Score")
        h1, l1 = ax4s.get_legend_handles_labels()
        h2, l2 = ax4sc.get_legend_handles_labels()
        ax4s.legend(h1 + h2, l1 + l2, loc="upper right", fontsize=8)
        ax4s.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax4s.spines["top"].set_visible(False)
        ax4s.spines["right"].set_visible(False)
        ax4sc.spines["top"].set_visible(False)
        st.pyplot(fig4)
        plt.close(fig4)


# ================================================================
# EDA – SUPPLIER ANALYSIS
# ================================================================
elif eda_option == "Supplier Analysis":

    st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:28px;
        border-radius:12px;
        color:white;
        font-size:16px;
        line-height:1.6;
        margin-bottom:20px;
    ">

    <b>What this section does:</b><br><br>

    This analyzes how <b>supplier performance impacts supply chain reliability</b> by evaluating
    lead time efficiency, rating scores, pricing, and product coverage.

    It evaluates:
    <ul>
        <li>Supplier rating scores — which suppliers consistently deliver high quality</li>
        <li>Lead time vs rating trade-offs</li>
        <li>Average cost price contribution per supplier</li>
        <li>Supplier coverage across product categories</li>
    </ul>
    <br>

    <b>Why this matters:</b>

    Procurement decisions and inventory replenishment policies are directly tied to
    <b>supplier reliability</b>. High lead times from low-rated suppliers can cascade
    into stockouts and missed service levels.

    <b>Key insights users get:</b>
    <ul>
        <li>High-performing vs underperforming suppliers</li>
        <li>Which suppliers should be prioritized for contract renewal</li>
        <li>Better data-driven procurement and supplier segmentation planning</li>
    </ul>

    </div>
    """,
    unsafe_allow_html=True
    )

    TOP_SUPPLIERS = 20

    all_sup_metrics = df.groupby(col_supplier).agg(
        avg_lead_time=(col_lead_time, "mean"),
        avg_rating=(col_rating, "mean"),
        avg_cost_price=(col_cost_price, "mean"),
        product_count=(col_product, "nunique"),
        total_stock_value=(col_stockval, "sum")
    )

    top_sup = all_sup_metrics.sort_values("avg_rating", ascending=False).head(TOP_SUPPLIERS)
    label_sups = all_sup_metrics.sort_values("avg_lead_time", ascending=True).head(5)
    label_sups2 = all_sup_metrics.sort_values("avg_rating", ascending=False).head(5)
    label_combined = pd.concat([label_sups, label_sups2]).drop_duplicates()

    col1, col2 = st.columns(2)

    # Plot 1: Top Suppliers by Rating Score
    with col1:
        blue_title("Supplier Rating Score (Top 20)")
        fig1, ax1 = plt.subplots(figsize=(7, 4))
        fig1.patch.set_facecolor(GREEN_BG)
        ax1.set_facecolor(GREEN_BG)
        fig1.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.32)
        ax1.bar(top_sup.index.astype(str), top_sup["avg_rating"], color=BAR_BLUE)
        ax1.set_xlabel("Supplier ID")
        ax1.set_ylabel("Avg Rating Score")
        ax1.tick_params(axis="x", rotation=45)
        ax1.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax1.spines["top"].set_visible(False)
        ax1.spines["right"].set_visible(False)
        st.pyplot(fig1)
        plt.close(fig1)

    # Plot 2: Lead Time vs Rating Score (Scatter)
    with col2:
        blue_title("Supplier Lead Time vs Rating Score")
        fig2, ax2 = plt.subplots(figsize=(7, 4))
        fig2.patch.set_facecolor(GREEN_BG)
        ax2.set_facecolor(GREEN_BG)
        fig2.subplots_adjust(left=0.10, right=0.98, top=0.92, bottom=0.13)
        ax2.scatter(
            all_sup_metrics["avg_lead_time"],
            all_sup_metrics["avg_rating"],
            alpha=0.6,
            color=BAR_BLUE
        )
        for sid, row in label_combined.iterrows():
            ax2.annotate(sid, (row["avg_lead_time"], row["avg_rating"]),
                         xytext=(5, 5), textcoords="offset points", fontsize=8, alpha=0.9)
        ax2.set_xlabel("Avg Lead Time (days)")
        ax2.set_ylabel("Avg Rating Score")
        ax2.grid(True, linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax2.spines["top"].set_visible(False)
        ax2.spines["right"].set_visible(False)
        st.pyplot(fig2)
        plt.close(fig2)

    col3, col4 = st.columns(2)

    # Plot 3: Lead Time vs Cost Price
    with col3:
        blue_title("Supplier Lead Time vs Avg Cost Price")
        x_slc = np.arange(len(top_sup))
        w_slc = 0.35
        fig3, ax3 = plt.subplots(figsize=(7, 4))
        fig3.patch.set_facecolor(GREEN_BG)
        ax3.set_facecolor(GREEN_BG)
        fig3.subplots_adjust(left=0.08, right=0.90, top=0.92, bottom=0.28)
        ax3.bar(x_slc - w_slc/2, top_sup["avg_lead_time"], w_slc, label="Lead Time (days)", color=BAR_BLUE)
        ax3r = ax3.twinx()
        ax3r.bar(x_slc + w_slc/2, top_sup["avg_cost_price"], w_slc, label="Avg Cost Price (₹)", color="#F59E0B")
        ax3.set_xticks(x_slc)
        ax3.set_xticklabels(top_sup.index.astype(str), rotation=45, ha="right", fontsize=7)
        ax3.set_ylabel("Avg Lead Time (days)")
        ax3r.set_ylabel("Avg Cost Price (₹)")
        ax3.set_xlabel("Supplier ID")
        h1, l1 = ax3.get_legend_handles_labels()
        h2, l2 = ax3r.get_legend_handles_labels()
        ax3.legend(h1 + h2, l1 + l2, loc="upper right", fontsize=8)
        ax3.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax3.spines["top"].set_visible(False)
        ax3.spines["right"].set_visible(False)
        ax3r.spines["top"].set_visible(False)
        st.pyplot(fig3)
        plt.close(fig3)

    # Plot 4: Supplier Stock Value vs Product Coverage
    with col4:
        blue_title("Supplier Stock Value vs Product Coverage")
        fig4, ax4 = plt.subplots(figsize=(7, 4))
        fig4.patch.set_facecolor(GREEN_BG)
        ax4.set_facecolor(GREEN_BG)
        fig4.subplots_adjust(left=0.10, right=0.98, top=0.92, bottom=0.13)
        ax4.scatter(
            all_sup_metrics["product_count"],
            all_sup_metrics["total_stock_value"],
            alpha=0.6, color=BAR_BLUE, s=40
        )
        ax4.set_xlabel("Product Count (SKUs Supplied)")
        ax4.set_ylabel("Total Stock Value (₹)")
        ax4.grid(True, linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax4.spines["top"].set_visible(False)
        ax4.spines["right"].set_visible(False)
        st.pyplot(fig4)
        plt.close(fig4)


# ================================================================
# EDA – CATEGORY & SUBCATEGORY ANALYSIS
# ================================================================
elif eda_option == "Category & Subcategory Analysis":

    st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:28px;
        border-radius:12px;
        color:white;
        font-size:16px;
        line-height:1.6;
        margin-bottom:25px;">

    <b>What this section does:</b><br><br>

    This analyzes <b>supply chain performance at the product category and subcategory level</b>.

    It focuses on:
    <ul>
        <li>Stock value and inventory concentration by category</li>
        <li>Fill rate variation across subcategories</li>
        <li>Delivery time patterns by product category</li>
        <li>Overstock vs understock exposure by subcategory</li>
    </ul><br>

    <b>Why this matters:</b>

    Category-level supply chain behavior differs significantly.
    Premium products may have longer lead times, while food categories
    require tighter fill rate management due to shelf life constraints.<br>

    <b>Key insights users get:</b>
    <ul>
        <li>Which categories accumulate the most inventory risk</li>
        <li>Subcategory-level fill rate gaps for targeted replenishment</li>
        <li>Category-specific delivery performance benchmarks</li>
    </ul>
    </div>
    """,
    unsafe_allow_html=True
    )

    # Use mapped columns instead of hardcoded names
    col_category  = col_category if col_category else "category"
    col_subcategory = col_subcategory if col_subcategory else "subcategory"
    col_stockval  = col_stockval if col_stockval else "stock_value"
    col_fill_rate = col_fill_rate if col_fill_rate else "fill_rate_pct"
    col_delivery  = col_delivery if col_delivery else "delivery_time_mins"
    col_overstock = col_overstock if col_overstock else "overstock_qty"
    col_understock = col_understock if col_understock else "understock_qty"

    def blue_title_ext(title):
        st.markdown(
            f"""
            <div style="background-color:#2F75B5;padding:14px;border-radius:8px;
            font-size:16px;color:white;margin-bottom:8px;text-align:center;font-weight:600;">
                {title}
            </div>
            """,
            unsafe_allow_html=True
        )

    col1, col2 = st.columns(2)

    with col1:
        blue_title_ext("Total Stock Value by Category")
        cat_sv = df.groupby(col_category, observed=True)[col_stockval].sum().sort_values(ascending=False)
        
        def create_altair_chart():
            chart_cat = (
                alt.Chart(cat_sv.reset_index())
                .mark_bar(color=BAR_BLUE, cornerRadiusEnd=6)
                .encode(
                    x=alt.X(f"{col_category}:O", title="Category"),
                    y=alt.Y(f"{col_stockval}:Q", title="Total Stock Value (₹)", scale=alt.Scale(padding=10)),
                    tooltip=[col_category, col_stockval]
                )
                .properties(height=340, background=GREEN_BG,
                            padding={"top":10,"left":10,"right":10,"bottom":10})
                .configure_view(fill=GREEN_BG, strokeOpacity=0)
                .configure_axis(labelColor="#000000", titleColor="#000000",
                                gridColor="rgba(0,0,0,0.2)", domainColor="rgba(0,0,0,0.3)")
            )
            return chart_cat
        
        try:
            chart_cat = safe_altair_chart(create_altair_chart)
            if chart_cat is not None:
                st.altair_chart(chart_cat, use_container_width=True)
            else:
                raise Exception("Chart creation failed")
        except Exception as e:
            st.error(f"Error creating Altair chart: {str(e)}")
            # Fallback to matplotlib
            fig_cat, ax_cat = plt.subplots(figsize=(7, 4))
            fig_cat.patch.set_facecolor(GREEN_BG)
            ax_cat.set_facecolor(GREEN_BG)
            fig_cat.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.32)
            ax_cat.bar(cat_sv.index.astype(str), cat_sv.values, color=BAR_BLUE)
            ax_cat.set_xlabel("Category")
            ax_cat.set_ylabel("Total Stock Value (₹)")
            ax_cat.tick_params(axis="x", rotation=45)
            ax_cat.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
            ax_cat.spines["top"].set_visible(False)
            ax_cat.spines["right"].set_visible(False)
            st.pyplot(fig_cat)
            plt.close(fig_cat)

    with col2:
        blue_title_ext("Avg Fill Rate by Subcategory")
        sub_fill = df.groupby(col_subcategory, observed=True)[col_fill_rate].mean().sort_values(ascending=False).head(15)
        fig_sf, ax_sf = plt.subplots(figsize=(7, 4))
        fig_sf.patch.set_facecolor(GREEN_BG)
        ax_sf.set_facecolor(GREEN_BG)
        fig_sf.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.32)
        ax_sf.bar(sub_fill.index.astype(str), sub_fill.values, color=BAR_BLUE)
        ax_sf.set_xlabel("Subcategory")
        ax_sf.set_ylabel("Avg Fill Rate (%)")
        ax_sf.tick_params(axis="x", rotation=45)
        ax_sf.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax_sf.spines["top"].set_visible(False)
        ax_sf.spines["right"].set_visible(False)
        st.pyplot(fig_sf)
        plt.close(fig_sf)

    col3, col4 = st.columns(2)

    with col3:
        blue_title_ext("Avg Delivery Time by Product Category")
        cat_del = df.groupby(col_category, observed=True)[col_delivery].mean().sort_values(ascending=False)
        fig_cd, ax_cd = plt.subplots(figsize=(7, 4))
        fig_cd.patch.set_facecolor(GREEN_BG)
        ax_cd.set_facecolor(GREEN_BG)
        fig_cd.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.17)
        ax_cd.bar(cat_del.index.astype(str), cat_del.values, color=BAR_BLUE)
        ax_cd.set_xlabel("Category")
        ax_cd.set_ylabel("Avg Delivery Time (mins)")
        ax_cd.tick_params(axis="x", rotation=45)
        ax_cd.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax_cd.spines["top"].set_visible(False)
        ax_cd.spines["right"].set_visible(False)
        st.pyplot(fig_cd)
        plt.close(fig_cd)

    with col4:
        blue_title_ext("Overstock vs Understock by Category")
        cat_ov = df.groupby(col_category, observed=True).agg(
            total_overstock=(col_overstock, "sum"),
            total_understock=(col_understock, "sum")
        ).sort_values("total_overstock", ascending=False)
        x_ov = np.arange(len(cat_ov))
        w_ov = 0.35
        fig_ov, ax_ov = plt.subplots(figsize=(7, 4))
        fig_ov.patch.set_facecolor(GREEN_BG)
        ax_ov.set_facecolor(GREEN_BG)
        fig_ov.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.17)
        ax_ov.bar(x_ov - w_ov/2, cat_ov["total_overstock"], w_ov, label="Overstock", color=BAR_BLUE)
        ax_ov.bar(x_ov + w_ov/2, cat_ov["total_understock"], w_ov, label="Understock", color="#EF4444")
        ax_ov.set_xticks(x_ov)
        ax_ov.set_xticklabels(cat_ov.index.astype(str), rotation=45, ha="right")
        ax_ov.set_xlabel("Category")
        ax_ov.set_ylabel("Quantity")
        ax_ov.legend()
        ax_ov.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax_ov.spines["top"].set_visible(False)
        ax_ov.spines["right"].set_visible(False)
        st.pyplot(fig_ov)
        plt.close(fig_ov)


# ================================================================
# EDA – SALES ANALYSIS
# ================================================================
elif eda_option == "Sales Analysis":
    st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:28px;
        border-radius:12px;
        color:white;
        font-size:16px;
        line-height:1.6;
        margin-bottom:25px;">
    <b>What this section does:</b><br><br>
    This analyzes <b>sales performance across products, categories, and regions</b>.
    It focuses on:
    <ul>
        <li>Sales trends over time</li>
        <li>Top-selling products and categories</li>
        <li>Regional sales distribution</li>
        <li>Sales seasonality patterns</li>
    </ul><br>
    <b>Why this matters:</b>
    Understanding sales patterns helps in demand forecasting, inventory planning, and marketing strategy optimization.<br>
    <b>Key insights users get:</b>
    <ul>
        <li>Which products drive maximum revenue</li>
        <li>Seasonal sales trends for better planning</li>
        <li>Regional performance comparison</li>
    </ul>
    </div>
    """,
    unsafe_allow_html=True
    )
    
    st.info("📊 Sales Analysis module - Select data columns to visualize sales metrics")

    # Sales Analysis Visualizations
    GREEN_BG = "#00D05E"
    GRID_GREEN = "#3B3B3B"
    BAR_BLUE = "#001F5C"

    # Sales by Category
    if "category" in df.columns and "stock_value" in df.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            blue_title("Total Stock Value by Category")
            cat_sales = df.groupby("category", observed=True)["stock_value"].sum().sort_values(ascending=False)
            fig1, ax1 = plt.subplots(figsize=(7, 4))
            fig1.patch.set_facecolor(GREEN_BG)
            ax1.set_facecolor(GREEN_BG)
            fig1.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.32)
            ax1.bar(cat_sales.index.astype(str), cat_sales.values, color=BAR_BLUE)
            ax1.set_xlabel("Category")
            ax1.set_ylabel("Total Stock Value (₹)")
            ax1.tick_params(axis="x", rotation=45)
            ax1.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
            ax1.spines["top"].set_visible(False)
            ax1.spines["right"].set_visible(False)
            st.pyplot(fig1)
            plt.close(fig1)

        with col2:
            blue_title("Fill Rate by Category")
            if "fill_rate_pct" in df.columns:
                cat_fill = df.groupby("category", observed=True)["fill_rate_pct"].mean().sort_values(ascending=False)
                fig2, ax2 = plt.subplots(figsize=(7, 4))
                fig2.patch.set_facecolor(GREEN_BG)
                ax2.set_facecolor(GREEN_BG)
                fig2.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.32)
                ax2.bar(cat_fill.index.astype(str), cat_fill.values, color="#F59E0B")
                ax2.set_xlabel("Category")
                ax2.set_ylabel("Avg Fill Rate (%)")
                ax2.tick_params(axis="x", rotation=45)
                ax2.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
                ax2.spines["top"].set_visible(False)
                ax2.spines["right"].set_visible(False)
                st.pyplot(fig2)
                plt.close(fig2)

    # Sales Trend over Time
    if "date" in df.columns:
        blue_title("Stock Value Trend Over Time")
        df_sorted = df.sort_values("date")
        daily_sales = df_sorted.groupby("date")["stock_value"].sum()
        fig3, ax3 = plt.subplots(figsize=(10, 4))
        fig3.patch.set_facecolor(GREEN_BG)
        ax3.set_facecolor(GREEN_BG)
        fig3.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.15)
        ax3.plot(daily_sales.index, daily_sales.values, color=BAR_BLUE, linewidth=2)
        ax3.set_xlabel("Date")
        ax3.set_ylabel("Total Stock Value (₹)")
        ax3.tick_params(axis="x", rotation=45)
        ax3.grid(True, linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax3.spines["top"].set_visible(False)
        ax3.spines["right"].set_visible(False)
        st.pyplot(fig3)
        plt.close(fig3)


# ================================================================
# EDA – CUSTOMER ANALYSIS
# ================================================================
elif eda_option == "Customer Analysis":
    st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:28px;
        border-radius:12px;
        color:white;
        font-size:16px;
        line-height:1.6;
        margin-bottom:25px;">
    <b>What this section does:</b><br><br>
    This analyzes <b>customer behavior and store performance</b>.
    It focuses on:
    <ul>
        <li>Store-wise customer traffic</li>
        <li>Customer purchase patterns</li>
        <li>Store performance metrics</li>
        <li>Customer satisfaction indicators</li>
    </ul><br>
    <b>Why this matters:</b>
    Customer insights help optimize store operations, improve service levels, and enhance customer experience.<br>
    <b>Key insights users get:</b>
    <ul>
        <li>High-performing vs underperforming stores</li>
        <li>Customer traffic patterns</li>
        <li>Service level gaps by location</li>
    </ul>
    </div>
    """,
    unsafe_allow_html=True
    )
    
    st.info("📊 Customer Analysis module - Select data columns to visualize customer metrics")

    # Customer/Store Analysis Visualizations
    GREEN_BG = "#00D05E"
    GRID_GREEN = "#3B3B3B"
    BAR_BLUE = "#001F5C"

    if "store_id" in df.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            blue_title("Stock Value by Store")
            store_stock = df.groupby("store_id", observed=True)["stock_value"].sum().sort_values(ascending=False).head(15)
            fig1, ax1 = plt.subplots(figsize=(7, 4))
            fig1.patch.set_facecolor(GREEN_BG)
            ax1.set_facecolor(GREEN_BG)
            fig1.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.32)
            ax1.bar(store_stock.index.astype(str), store_stock.values, color=BAR_BLUE)
            ax1.set_xlabel("Store ID")
            ax1.set_ylabel("Total Stock Value (₹)")
            ax1.tick_params(axis="x", rotation=45)
            ax1.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
            ax1.spines["top"].set_visible(False)
            ax1.spines["right"].set_visible(False)
            st.pyplot(fig1)
            plt.close(fig1)

        with col2:
            blue_title("Fill Rate by Store")
            if "fill_rate_pct" in df.columns:
                store_fill = df.groupby("store_id", observed=True)["fill_rate_pct"].mean().sort_values(ascending=False).head(15)
                fig2, ax2 = plt.subplots(figsize=(7, 4))
                fig2.patch.set_facecolor(GREEN_BG)
                ax2.set_facecolor(GREEN_BG)
                fig2.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.32)
                ax2.bar(store_fill.index.astype(str), store_fill.values, color="#F59E0B")
                ax2.set_xlabel("Store ID")
                ax2.set_ylabel("Avg Fill Rate (%)")
                ax2.tick_params(axis="x", rotation=45)
                ax2.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
                ax2.spines["top"].set_visible(False)
                ax2.spines["right"].set_visible(False)
                st.pyplot(fig2)
                plt.close(fig2)

    if "store_id" in df.columns and "on_hand_qty" in df.columns:
        blue_title("On-Hand Quantity by Store")
        store_qty = df.groupby("store_id", observed=True)["on_hand_qty"].sum().sort_values(ascending=False).head(15)
        fig3, ax3 = plt.subplots(figsize=(10, 4))
        fig3.patch.set_facecolor(GREEN_BG)
        ax3.set_facecolor(GREEN_BG)
        fig3.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.32)
        ax3.bar(store_qty.index.astype(str), store_qty.values, color="#10B981")
        ax3.set_xlabel("Store ID")
        ax3.set_ylabel("Total On-Hand Quantity")
        ax3.tick_params(axis="x", rotation=45)
        ax3.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax3.spines["top"].set_visible(False)
        ax3.spines["right"].set_visible(False)
        st.pyplot(fig3)
        plt.close(fig3)


# ================================================================
# EDA – STORE ANALYSIS
# ================================================================
elif eda_option == "Store Analysis":
    st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:28px;
        border-radius:12px;
        color:white;
        font-size:16px;
        line-height:1.6;
        margin-bottom:25px;">
    <b>What this section does:</b><br><br>
    This analyzes <b>store performance and inventory health</b>.
    It focuses on:
    <ul>
        <li>Store-wise inventory levels</li>
        <li>Store performance metrics</li>
        <li>Fill rates by store</li>
        <li>Stockout patterns by location</li>
    </ul><br>
    <b>Why this matters:</b>
    Store-level analysis helps identify underperforming locations and optimize inventory distribution.<br>
    <b>Key insights users get:</b>
    <ul>
        <li>Which stores need inventory attention</li>
        <li>Store performance ranking</li>
        <li>Optimal inventory allocation per store</li>
    </ul>
    </div>
    """,
    unsafe_allow_html=True
    )
    
    st.info("📊 Store Analysis module - Select data columns to visualize store metrics")

    # Store Analysis Visualizations
    GREEN_BG = "#00D05E"
    GRID_GREEN = "#3B3B3B"
    BAR_BLUE = "#001F5C"

    if "store_id" in df.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            blue_title("Store Performance - Stockout Percentage")
            if "stockout_pct" in df.columns:
                store_stockout = df.groupby("store_id", observed=True)["stockout_pct"].mean().sort_values(ascending=False).head(15)
                fig1, ax1 = plt.subplots(figsize=(7, 4))
                fig1.patch.set_facecolor(GREEN_BG)
                ax1.set_facecolor(GREEN_BG)
                fig1.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.32)
                ax1.bar(store_stockout.index.astype(str), store_stockout.values, color="#EF4444")
                ax1.set_xlabel("Store ID")
                ax1.set_ylabel("Avg Stockout %")
                ax1.tick_params(axis="x", rotation=45)
                ax1.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
                ax1.spines["top"].set_visible(False)
                ax1.spines["right"].set_visible(False)
                st.pyplot(fig1)
                plt.close(fig1)

        with col2:
            blue_title("Store Performance - Inventory Turnover")
            if "inventory_turnover" in df.columns:
                store_turnover = df.groupby("store_id", observed=True)["inventory_turnover"].mean().sort_values(ascending=False).head(15)
                fig2, ax2 = plt.subplots(figsize=(7, 4))
                fig2.patch.set_facecolor(GREEN_BG)
                ax2.set_facecolor(GREEN_BG)
                fig2.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.32)
                ax2.bar(store_turnover.index.astype(str), store_turnover.values, color="#10B981")
                ax2.set_xlabel("Store ID")
                ax2.set_ylabel("Avg Inventory Turnover")
                ax2.tick_params(axis="x", rotation=45)
                ax2.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
                ax2.spines["top"].set_visible(False)
                ax2.spines["right"].set_visible(False)
                st.pyplot(fig2)
                plt.close(fig2)

    if "store_id" in df.columns and "overstock_qty" in df.columns and "understock_qty" in df.columns:
        blue_title("Overstock vs Understock by Store")
        store_over = df.groupby("store_id", observed=True)["overstock_qty"].sum().head(15)
        store_under = df.groupby("store_id", observed=True)["understock_qty"].sum().head(15)
        fig3, ax3 = plt.subplots(figsize=(10, 4))
        fig3.patch.set_facecolor(GREEN_BG)
        ax3.set_facecolor(GREEN_BG)
        fig3.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.32)
        x = np.arange(len(store_over))
        w = 0.35
        ax3.bar(x - w/2, store_over.values, w, label="Overstock", color=BAR_BLUE)
        ax3.bar(x + w/2, store_under.values, w, label="Understock", color="#EF4444")
        ax3.set_xticks(x)
        ax3.set_xticklabels(store_over.index.astype(str), rotation=45, ha="right")
        ax3.set_xlabel("Store ID")
        ax3.set_ylabel("Quantity")
        ax3.legend()
        ax3.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax3.spines["top"].set_visible(False)
        ax3.spines["right"].set_visible(False)
        st.pyplot(fig3)
        plt.close(fig3)


# ================================================================
# EDA – VENDOR ANALYSIS
# ================================================================
elif eda_option == "Vendor Analysis":
    st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:28px;
        border-radius:12px;
        color:white;
        font-size:16px;
        line-height:1.6;
        margin-bottom:25px;">
    <b>What this section does:</b><br><br>
    This analyzes <b>vendor/supplier performance and reliability</b>.
    It focuses on:
    <ul>
        <li>Vendor rating scores</li>
        <li>Lead time performance</li>
        <li>Cost analysis by vendor</li>
        <li>Vendor reliability metrics</li>
    </ul><br>
    <b>Why this matters:</b>
    Vendor performance directly impacts inventory availability and supply chain reliability.<br>
    <b>Key insights users get:</b>
    <ul>
        <li>Best-performing vendors</li>
        <li>Vendors needing performance improvement</li>
        <li>Cost-effective vendor selection</li>
    </ul>
    </div>
    """,
    unsafe_allow_html=True
    )
    
    st.info("📊 Vendor Analysis module - Select data columns to visualize vendor metrics")

    # Vendor Analysis Visualizations (similar to Supplier Analysis)
    GREEN_BG = "#00D05E"
    GRID_GREEN = "#3B3B3B"
    BAR_BLUE = "#001F5C"

    if "supplier_id" in df.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            blue_title("Supplier Rating Score")
            if "rating_score" in df.columns:
                sup_rating = df.groupby("supplier_id", observed=True)["rating_score"].mean().sort_values(ascending=False).head(15)
                fig1, ax1 = plt.subplots(figsize=(7, 4))
                fig1.patch.set_facecolor(GREEN_BG)
                ax1.set_facecolor(GREEN_BG)
                fig1.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.32)
                ax1.bar(sup_rating.index.astype(str), sup_rating.values, color=BAR_BLUE)
                ax1.set_xlabel("Supplier ID")
                ax1.set_ylabel("Avg Rating Score")
                ax1.tick_params(axis="x", rotation=45)
                ax1.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
                ax1.spines["top"].set_visible(False)
                ax1.spines["right"].set_visible(False)
                st.pyplot(fig1)
                plt.close(fig1)

        with col2:
            blue_title("Supplier Lead Time")
            if "lead_time_days" in df.columns:
                sup_lead = df.groupby("supplier_id", observed=True)["lead_time_days"].mean().sort_values(ascending=True).head(15)
                fig2, ax2 = plt.subplots(figsize=(7, 4))
                fig2.patch.set_facecolor(GREEN_BG)
                ax2.set_facecolor(GREEN_BG)
                fig2.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.32)
                ax2.bar(sup_lead.index.astype(str), sup_lead.values, color="#F59E0B")
                ax2.set_xlabel("Supplier ID")
                ax2.set_ylabel("Avg Lead Time (days)")
                ax2.tick_params(axis="x", rotation=45)
                ax2.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
                ax2.spines["top"].set_visible(False)
                ax2.spines["right"].set_visible(False)
                st.pyplot(fig2)
                plt.close(fig2)

    if "supplier_id" in df.columns and "cost_price" in df.columns:
        blue_title("Supplier Cost Price Distribution")
        sup_cost = df.groupby("supplier_id", observed=True)["cost_price"].mean().sort_values(ascending=False).head(15)
        fig3, ax3 = plt.subplots(figsize=(10, 4))
        fig3.patch.set_facecolor(GREEN_BG)
        ax3.set_facecolor(GREEN_BG)
        fig3.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.32)
        ax3.bar(sup_cost.index.astype(str), sup_cost.values, color="#10B981")
        ax3.set_xlabel("Supplier ID")
        ax3.set_ylabel("Avg Cost Price (₹)")
        ax3.tick_params(axis="x", rotation=45)
        ax3.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax3.spines["top"].set_visible(False)
        ax3.spines["right"].set_visible(False)
        st.pyplot(fig3)
        plt.close(fig3)


# ================================================================
# EDA – LOCATION ANALYSIS
# ================================================================
elif eda_option == "Location Analysis":
    st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:28px;
        border-radius:12px;
        color:white;
        font-size:16px;
        line-height:1.6;
        margin-bottom:25px;">
    <b>What this section does:</b><br><br>
    This analyzes <b>geographic performance across regions, zones, and cities</b>.
    It focuses on:
    <ul>
        <li>Regional inventory distribution</li>
        <li>Zone-wise performance metrics</li>
        <li>City-level demand patterns</li>
        <li>Geographic fill rate analysis</li>
    </ul><br>
    <b>Why this matters:</b>
    Geographic insights help optimize regional distribution networks and improve service levels.<br>
    <b>Key insights users get:</b>
    <ul>
        <li>High-demand regions</li>
        <li>Regional inventory imbalances</li>
        <li>Optimal regional allocation strategies</li>
    </ul>
    </div>
    """,
    unsafe_allow_html=True
    )
    
    st.info("📊 Location Analysis module - Select data columns to visualize location metrics")

    # Location Analysis Visualizations
    GREEN_BG = "#00D05E"
    GRID_GREEN = "#3B3B3B"
    BAR_BLUE = "#001F5C"

    col1, col2 = st.columns(2)
    
    with col1:
        if "region" in df.columns:
            blue_title("Stock Value by Region")
            region_stock = df.groupby("region", observed=True)["stock_value"].sum().sort_values(ascending=False)
            fig1, ax1 = plt.subplots(figsize=(7, 4))
            fig1.patch.set_facecolor(GREEN_BG)
            ax1.set_facecolor(GREEN_BG)
            fig1.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.32)
            ax1.bar(region_stock.index.astype(str), region_stock.values, color=BAR_BLUE)
            ax1.set_xlabel("Region")
            ax1.set_ylabel("Total Stock Value (₹)")
            ax1.tick_params(axis="x", rotation=45)
            ax1.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
            ax1.spines["top"].set_visible(False)
            ax1.spines["right"].set_visible(False)
            st.pyplot(fig1)
            plt.close(fig1)

    with col2:
        if "zone" in df.columns:
            blue_title("Fill Rate by Zone")
            if "fill_rate_pct" in df.columns:
                zone_fill = df.groupby("zone", observed=True)["fill_rate_pct"].mean().sort_values(ascending=False)
                fig2, ax2 = plt.subplots(figsize=(7, 4))
                fig2.patch.set_facecolor(GREEN_BG)
                ax2.set_facecolor(GREEN_BG)
                fig2.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.32)
                ax2.bar(zone_fill.index.astype(str), zone_fill.values, color="#F59E0B")
                ax2.set_xlabel("Zone")
                ax2.set_ylabel("Avg Fill Rate (%)")
                ax2.tick_params(axis="x", rotation=45)
                ax2.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
                ax2.spines["top"].set_visible(False)
                ax2.spines["right"].set_visible(False)
                st.pyplot(fig2)
                plt.close(fig2)

    if "city" in df.columns:
        blue_title("Stock Value by City (Top 15)")
        city_stock = df.groupby("city", observed=True)["stock_value"].sum().sort_values(ascending=False).head(15)
        fig3, ax3 = plt.subplots(figsize=(10, 4))
        fig3.patch.set_facecolor(GREEN_BG)
        ax3.set_facecolor(GREEN_BG)
        fig3.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.32)
        ax3.bar(city_stock.index.astype(str), city_stock.values, color="#10B981")
        ax3.set_xlabel("City")
        ax3.set_ylabel("Total Stock Value (₹)")
        ax3.tick_params(axis="x", rotation=45)
        ax3.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax3.spines["top"].set_visible(False)
        ax3.spines["right"].set_visible(False)
        st.pyplot(fig3)
        plt.close(fig3)


# ================================================================
# EDA – WAREHOUSE ANALYSIS
# ================================================================
elif eda_option == "Warehouse Analysis":
    st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:28px;
        border-radius:12px;
        color:white;
        font-size:16px;
        line-height:1.6;
        margin-bottom:25px;">
    <b>What this section does:</b><br><br>
    This analyzes <b>warehouse performance and storage optimization</b>.
    It focuses on:
    <ul>
        <li>Warehouse capacity utilization</li>
        <li>Storage efficiency metrics</li>
        <li>Warehouse throughput analysis</li>
        <li>Inventory turnover by warehouse</li>
    </ul><br>
    <b>Why this matters:</b>
    Warehouse optimization reduces storage costs and improves fulfillment speed.<br>
    <b>Key insights users get:</b>
    <ul>
        <li>Underutilized warehouse capacity</li>
        <li>Storage bottlenecks</li>
        <li>Optimal warehouse allocation</li>
    </ul>
    </div>
    """,
    unsafe_allow_html=True
    )
    
    st.info("📊 Warehouse Analysis module - Select data columns to visualize warehouse metrics")

    # Warehouse Analysis Visualizations
    GREEN_BG = "#00D05E"
    GRID_GREEN = "#3B3B3B"
    BAR_BLUE = "#001F5C"

    if "cluster_id" in df.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            blue_title("Stock Value by Cluster")
            cluster_stock = df.groupby("cluster_id", observed=True)["stock_value"].sum().sort_values(ascending=False)
            fig1, ax1 = plt.subplots(figsize=(7, 4))
            fig1.patch.set_facecolor(GREEN_BG)
            ax1.set_facecolor(GREEN_BG)
            fig1.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.32)
            ax1.bar(cluster_stock.index.astype(str), cluster_stock.values, color=BAR_BLUE)
            ax1.set_xlabel("Cluster ID")
            ax1.set_ylabel("Total Stock Value (₹)")
            ax1.tick_params(axis="x", rotation=45)
            ax1.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
            ax1.spines["top"].set_visible(False)
            ax1.spines["right"].set_visible(False)
            st.pyplot(fig1)
            plt.close(fig1)

        with col2:
            blue_title("Inventory Turnover by Cluster")
            if "inventory_turnover" in df.columns:
                cluster_turnover = df.groupby("cluster_id", observed=True)["inventory_turnover"].mean().sort_values(ascending=False)
                fig2, ax2 = plt.subplots(figsize=(7, 4))
                fig2.patch.set_facecolor(GREEN_BG)
                ax2.set_facecolor(GREEN_BG)
                fig2.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.32)
                ax2.bar(cluster_turnover.index.astype(str), cluster_turnover.values, color="#F59E0B")
                ax2.set_xlabel("Cluster ID")
                ax2.set_ylabel("Avg Inventory Turnover")
                ax2.tick_params(axis="x", rotation=45)
                ax2.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
                ax2.spines["top"].set_visible(False)
                ax2.spines["right"].set_visible(False)
                st.pyplot(fig2)
                plt.close(fig2)

    if "cluster_id" in df.columns and "on_hand_qty" in df.columns:
        blue_title("On-Hand Quantity by Cluster")
        cluster_qty = df.groupby("cluster_id", observed=True)["on_hand_qty"].sum().sort_values(ascending=False)
        fig3, ax3 = plt.subplots(figsize=(10, 4))
        fig3.patch.set_facecolor(GREEN_BG)
        ax3.set_facecolor(GREEN_BG)
        fig3.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.32)
        ax3.bar(cluster_qty.index.astype(str), cluster_qty.values, color="#10B981")
        ax3.set_xlabel("Cluster ID")
        ax3.set_ylabel("Total On-Hand Quantity")
        ax3.tick_params(axis="x", rotation=45)
        ax3.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax3.spines["top"].set_visible(False)
        ax3.spines["right"].set_visible(False)
        st.pyplot(fig3)
        plt.close(fig3)


# ================================================================
# EDA – TRANSPORT ROUTE ANALYSIS
# ================================================================
elif eda_option == "Transport Route Analysis":
    st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:28px;
        border-radius:12px;
        color:white;
        font-size:16px;
        line-height:1.6;
        margin-bottom:25px;">
    <b>What this section does:</b><br><br>
    This analyzes <b>transportation route efficiency and performance</b>.
    It focuses on:
    <ul>
        <li>Route efficiency scores</li>
        <li>Delivery time analysis</li>
        <li>Fuel cost optimization</li>
        <li>Route distance vs time analysis</li>
    </ul><br>
    <b>Why this matters:</b>
    Route optimization reduces transportation costs and improves delivery times.<br>
    <b>Key insights users get:</b>
    <ul>
        <li>Most efficient routes</li>
        <li>Routes needing optimization</li>
        <li>Cost-saving opportunities</li>
    </ul>
    </div>
    """,
    unsafe_allow_html=True
    )
    
    st.info("📊 Transport Route Analysis module - Select data columns to visualize route metrics")

    # Transport Route Analysis Visualizations
    GREEN_BG = "#00D05E"
    GRID_GREEN = "#3B3B3B"
    BAR_BLUE = "#001F5C"

    if "route_id" in df.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            blue_title("Route Efficiency Score")
            if "route_efficiency_score" in df.columns:
                route_eff = df.groupby("route_id", observed=True)["route_efficiency_score"].mean().sort_values(ascending=False).head(15)
                fig1, ax1 = plt.subplots(figsize=(7, 4))
                fig1.patch.set_facecolor(GREEN_BG)
                ax1.set_facecolor(GREEN_BG)
                fig1.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.32)
                ax1.bar(route_eff.index.astype(str), route_eff.values, color=BAR_BLUE)
                ax1.set_xlabel("Route ID")
                ax1.set_ylabel("Avg Route Efficiency Score")
                ax1.tick_params(axis="x", rotation=45)
                ax1.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
                ax1.spines["top"].set_visible(False)
                ax1.spines["right"].set_visible(False)
                st.pyplot(fig1)
                plt.close(fig1)

        with col2:
            blue_title("Delivery Time by Route")
            if "delivery_time_mins" in df.columns:
                route_delivery = df.groupby("route_id", observed=True)["delivery_time_mins"].mean().sort_values(ascending=True).head(15)
                fig2, ax2 = plt.subplots(figsize=(7, 4))
                fig2.patch.set_facecolor(GREEN_BG)
                ax2.set_facecolor(GREEN_BG)
                fig2.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.32)
                ax2.bar(route_delivery.index.astype(str), route_delivery.values, color="#F59E0B")
                ax2.set_xlabel("Route ID")
                ax2.set_ylabel("Avg Delivery Time (mins)")
                ax2.tick_params(axis="x", rotation=45)
                ax2.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
                ax2.spines["top"].set_visible(False)
                ax2.spines["right"].set_visible(False)
                st.pyplot(fig2)
                plt.close(fig2)

    if "route_id" in df.columns and "fuel_cost" in df.columns:
        blue_title("Fuel Cost by Route")
        route_fuel = df.groupby("route_id", observed=True)["fuel_cost"].mean().sort_values(ascending=False).head(15)
        fig3, ax3 = plt.subplots(figsize=(10, 4))
        fig3.patch.set_facecolor(GREEN_BG)
        ax3.set_facecolor(GREEN_BG)
        fig3.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.32)
        ax3.bar(route_fuel.index.astype(str), route_fuel.values, color="#EF4444")
        ax3.set_xlabel("Route ID")
        ax3.set_ylabel("Avg Fuel Cost (₹)")
        ax3.tick_params(axis="x", rotation=45)
        ax3.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax3.spines["top"].set_visible(False)
        ax3.spines["right"].set_visible(False)
        st.pyplot(fig3)
        plt.close(fig3)


# ================================================================
# EDA – INVENTORY ANALYSIS
# ================================================================
elif eda_option == "Inventory Analysis":
    st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:28px;
        border-radius:12px;
        color:white;
        font-size:16px;
        line-height:1.6;
        margin-bottom:25px;">
    <b>What this section does:</b><br><br>
    This analyzes <b>overall inventory health and optimization opportunities</b>.
    It focuses on:
    <ul>
        <li>Inventory turnover rates</li>
        <li>Overstock and understock analysis</li>
        <li>Stock value distribution</li>
        <li>Inventory aging analysis</li>
    </ul><br>
    <b>Why this matters:</b>
    Inventory optimization reduces holding costs and improves cash flow.<br>
    <b>Key insights users get:</b>
    <ul>
        <li>Slow-moving inventory</li>
        <li>Stockout risk items</li>
        <li>Optimal inventory levels</li>
    </ul>
    </div>
    """,
    unsafe_allow_html=True
    )
    
    st.info("📊 Inventory Analysis module - Select data columns to visualize inventory metrics")

    # Inventory Analysis Visualizations
    GREEN_BG = "#00D05E"
    GRID_GREEN = "#3B3B3B"
    BAR_BLUE = "#001F5C"

    col1, col2 = st.columns(2)
    
    with col1:
        blue_title("Overall Inventory Distribution")
        if "on_hand_qty" in df.columns:
            fig1, ax1 = plt.subplots(figsize=(7, 4))
            fig1.patch.set_facecolor(GREEN_BG)
            ax1.set_facecolor(GREEN_BG)
            fig1.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.15)
            ax1.hist(df["on_hand_qty"], bins=30, color=BAR_BLUE, alpha=0.7)
            ax1.set_xlabel("On-Hand Quantity")
            ax1.set_ylabel("Frequency")
            ax1.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
            ax1.spines["top"].set_visible(False)
            ax1.spines["right"].set_visible(False)
            st.pyplot(fig1)
            plt.close(fig1)

    with col2:
        blue_title("Stock Value Distribution")
        if "stock_value" in df.columns:
            fig2, ax2 = plt.subplots(figsize=(7, 4))
            fig2.patch.set_facecolor(GREEN_BG)
            ax2.set_facecolor(GREEN_BG)
            fig2.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.15)
            ax2.hist(df["stock_value"], bins=30, color="#F59E0B", alpha=0.7)
            ax2.set_xlabel("Stock Value (₹)")
            ax2.set_ylabel("Frequency")
            ax2.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
            ax2.spines["top"].set_visible(False)
            ax2.spines["right"].set_visible(False)
            st.pyplot(fig2)
            plt.close(fig2)

    if "category" in df.columns:
        blue_title("Excess Inventory Percentage by Category")
        if "excess_inventory_pct" in df.columns:
            cat_excess = df.groupby("category", observed=True)["excess_inventory_pct"].mean().sort_values(ascending=False)
            fig3, ax3 = plt.subplots(figsize=(10, 4))
            fig3.patch.set_facecolor(GREEN_BG)
            ax3.set_facecolor(GREEN_BG)
            fig3.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.32)
            ax3.bar(cat_excess.index.astype(str), cat_excess.values, color="#EF4444")
            ax3.set_xlabel("Category")
            ax3.set_ylabel("Avg Excess Inventory %")
            ax3.tick_params(axis="x", rotation=45)
            ax3.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
            ax3.spines["top"].set_visible(False)
            ax3.spines["right"].set_visible(False)
            st.pyplot(fig3)
            plt.close(fig3)


# ================================================================
# EDA – REDISTRIBUTION ANALYSIS
# ================================================================
elif eda_option == "Redistribution Analysis":
    st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:28px;
        border-radius:12px;
        color:white;
        font-size:16px;
        line-height:1.6;
        margin-bottom:25px;">
    <b>What this section does:</b><br><br>
    This analyzes <b>inventory redistribution and transfer opportunities</b>.
    It focuses on:
    <ul>
        <li>Transfer quantity analysis</li>
        <li>Inter-store transfer patterns</li>
        <li>Redistribution cost analysis</li>
        <li>Optimal transfer recommendations</li>
    </ul><br>
    <b>Why this matters:</b>
    Smart redistribution reduces stockouts and excess inventory across the network.<br>
    <b>Key insights users get:</b>
    <ul>
        <li>Best transfer opportunities</li>
        <li>Cost-effective redistribution</li>
        <li>Network balance improvements</li>
    </ul>
    </div>
    """,
    unsafe_allow_html=True
    )
    
    st.info("📊 Redistribution Analysis module - Select data columns to visualize redistribution metrics")

    # Redistribution Analysis Visualizations
    GREEN_BG = "#00D05E"
    GRID_GREEN = "#3B3B3B"
    BAR_BLUE = "#001F5C"

    if "from_store_id" in df.columns and "to_store_id" in df.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            blue_title("Transfer Quantity by From Store")
            if "transfer_qty" in df.columns:
                from_transfer = df.groupby("from_store_id", observed=True)["transfer_qty"].sum().sort_values(ascending=False).head(15)
                fig1, ax1 = plt.subplots(figsize=(7, 4))
                fig1.patch.set_facecolor(GREEN_BG)
                ax1.set_facecolor(GREEN_BG)
                fig1.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.32)
                ax1.bar(from_transfer.index.astype(str), from_transfer.values, color=BAR_BLUE)
                ax1.set_xlabel("From Store ID")
                ax1.set_ylabel("Total Transfer Quantity")
                ax1.tick_params(axis="x", rotation=45)
                ax1.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
                ax1.spines["top"].set_visible(False)
                ax1.spines["right"].set_visible(False)
                st.pyplot(fig1)
                plt.close(fig1)

        with col2:
            blue_title("Transfer Quantity by To Store")
            if "transfer_qty" in df.columns:
                to_transfer = df.groupby("to_store_id", observed=True)["transfer_qty"].sum().sort_values(ascending=False).head(15)
                fig2, ax2 = plt.subplots(figsize=(7, 4))
                fig2.patch.set_facecolor(GREEN_BG)
                ax2.set_facecolor(GREEN_BG)
                fig2.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.32)
                ax2.bar(to_transfer.index.astype(str), to_transfer.values, color="#F59E0B")
                ax2.set_xlabel("To Store ID")
                ax2.set_ylabel("Total Transfer Quantity")
                ax2.tick_params(axis="x", rotation=45)
                ax2.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
                ax2.spines["top"].set_visible(False)
                ax2.spines["right"].set_visible(False)
                st.pyplot(fig2)
                plt.close(fig2)

    if "cluster_id" in df.columns and "optimal_transfer_qty" in df.columns:
        blue_title("Optimal Transfer Quantity by Cluster")
        cluster_transfer = df.groupby("cluster_id", observed=True)["optimal_transfer_qty"].sum().sort_values(ascending=False)
        fig3, ax3 = plt.subplots(figsize=(10, 4))
        fig3.patch.set_facecolor(GREEN_BG)
        ax3.set_facecolor(GREEN_BG)
        fig3.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.32)
        ax3.bar(cluster_transfer.index.astype(str), cluster_transfer.values, color="#10B981")
        ax3.set_xlabel("Cluster ID")
        ax3.set_ylabel("Optimal Transfer Quantity")
        ax3.tick_params(axis="x", rotation=45)
        ax3.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax3.spines["top"].set_visible(False)
        ax3.spines["right"].set_visible(False)
        st.pyplot(fig3)
        plt.close(fig3)


# ================================================================
# EDA – REALLOCATION ANALYSIS
# ================================================================
elif eda_option == "Reallocation Analysis":
    st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:28px;
        border-radius:12px;
        color:white;
        font-size:16px;
        line-height:1.6;
        margin-bottom:25px;">
    <b>What this section does:</b><br><br>
    This analyzes <b>inventory reallocation strategies and their impact</b>.
    It focuses on:
    <ul>
        <li>Reallocation effectiveness</li>
        <li>Service level improvements</li>
        <li>Cost-benefit analysis</li>
        <li>Reallocation timing optimization</li>
    </ul><br>
    <b>Why this matters:</b>
    Strategic reallocation improves overall network efficiency and customer service.<br>
    <b>Key insights users get:</b>
    <ul>
        <li>Most beneficial reallocations</li>
        <li>Service level gains</li>
        <li>Optimal reallocation timing</li>
    </ul>
    </div>
    """,
    unsafe_allow_html=True
    )
    
    st.info("📊 Reallocation Analysis module - Select data columns to visualize reallocation metrics")

    # Reallocation Analysis Visualizations
    GREEN_BG = "#00D05E"
    GRID_GREEN = "#3B3B3B"
    BAR_BLUE = "#001F5C"

    if "cluster_id" in df.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            blue_title("Cost Minimization by Cluster")
            if "cost_minimization_pct" in df.columns:
                cluster_cost = df.groupby("cluster_id", observed=True)["cost_minimization_pct"].mean().sort_values(ascending=False)
                fig1, ax1 = plt.subplots(figsize=(7, 4))
                fig1.patch.set_facecolor(GREEN_BG)
                ax1.set_facecolor(GREEN_BG)
                fig1.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.32)
                ax1.bar(cluster_cost.index.astype(str), cluster_cost.values, color=BAR_BLUE)
                ax1.set_xlabel("Cluster ID")
                ax1.set_ylabel("Avg Cost Minimization %")
                ax1.tick_params(axis="x", rotation=45)
                ax1.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
                ax1.spines["top"].set_visible(False)
                ax1.spines["right"].set_visible(False)
                st.pyplot(fig1)
                plt.close(fig1)

        with col2:
            blue_title("Service Level Gain by Cluster")
            if "service_level_gain_pct" in df.columns:
                cluster_service = df.groupby("cluster_id", observed=True)["service_level_gain_pct"].mean().sort_values(ascending=False)
                fig2, ax2 = plt.subplots(figsize=(7, 4))
                fig2.patch.set_facecolor(GREEN_BG)
                ax2.set_facecolor(GREEN_BG)
                fig2.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.32)
                ax2.bar(cluster_service.index.astype(str), cluster_service.values, color="#F59E0B")
                ax2.set_xlabel("Cluster ID")
                ax2.set_ylabel("Avg Service Level Gain %")
                ax2.tick_params(axis="x", rotation=45)
                ax2.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
                ax2.spines["top"].set_visible(False)
                ax2.spines["right"].set_visible(False)
                st.pyplot(fig2)
                plt.close(fig2)

    if "cluster_id" in df.columns and "model_confidence_score" in df.columns:
        blue_title("Model Confidence Score by Cluster")
        cluster_conf = df.groupby("cluster_id", observed=True)["model_confidence_score"].mean().sort_values(ascending=False)
        fig3, ax3 = plt.subplots(figsize=(10, 4))
        fig3.patch.set_facecolor(GREEN_BG)
        ax3.set_facecolor(GREEN_BG)
        fig3.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.32)
        ax3.bar(cluster_conf.index.astype(str), cluster_conf.values, color="#10B981")
        ax3.set_xlabel("Cluster ID")
        ax3.set_ylabel("Avg Model Confidence Score")
        ax3.tick_params(axis="x", rotation=45)
        ax3.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax3.spines["top"].set_visible(False)
        ax3.spines["right"].set_visible(False)
        st.pyplot(fig3)
        plt.close(fig3)


# ================================================================
# EDA – SUMMARY REPORT
# ================================================================
elif eda_option == "Summary Report":
    st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:28px;
        border-radius:12px;
        color:white;
        font-size:16px;
        line-height:1.6;
        margin-bottom:25px;">
    <b>What this section does:</b><br><br>
    This provides a <b>comprehensive summary of all supply chain metrics</b>.
    It focuses on:
    <ul>
        <li>Overall inventory health score</li>
        <li>Key performance indicators (KPIs)</li>
        <li>Trend analysis across all dimensions</li>
        <li>Actionable recommendations</li>
    </ul><br>
    <b>Why this matters:</b>
    A consolidated view helps executives make informed decisions quickly.<br>
    <b>Key insights users get:</b>
    <ul>
        <li>Overall supply chain health</li>
        <li>Critical areas needing attention</li>
        <li>Strategic improvement recommendations</li>
    </ul>
    </div>
    """,
    unsafe_allow_html=True
    )
    
    st.info("📊 Summary Report module - Generate comprehensive supply chain summary")

    # Summary Report Visualizations
    GREEN_BG = "#00D05E"
    GRID_GREEN = "#3B3B3B"
    BAR_BLUE = "#001F5C"

    # Key Metrics Summary
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if "stock_value" in df.columns:
            total_stock = df["stock_value"].sum()
            st.metric("Total Stock Value", f"₹{total_stock:,.0f}")
    
    with col2:
        if "on_hand_qty" in df.columns:
            total_qty = df["on_hand_qty"].sum()
            st.metric("Total On-Hand Quantity", f"{total_qty:,.0f}")
    
    with col3:
        if "fill_rate_pct" in df.columns:
            avg_fill = df["fill_rate_pct"].mean()
            st.metric("Average Fill Rate", f"{avg_fill:.1f}%")
    
    with col4:
        if "stockout_pct" in df.columns:
            avg_stockout = df["stockout_pct"].mean()
            st.metric("Average Stockout %", f"{avg_stockout:.1f}%")

    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        blue_title("Stock Value by Category")
        if "category" in df.columns:
            cat_summary = df.groupby("category", observed=True)["stock_value"].sum().sort_values(ascending=False)
            fig1, ax1 = plt.subplots(figsize=(7, 4))
            fig1.patch.set_facecolor(GREEN_BG)
            ax1.set_facecolor(GREEN_BG)
            fig1.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.32)
            ax1.bar(cat_summary.index.astype(str), cat_summary.values, color=BAR_BLUE)
            ax1.set_xlabel("Category")
            ax1.set_ylabel("Total Stock Value (₹)")
            ax1.tick_params(axis="x", rotation=45)
            ax1.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
            ax1.spines["top"].set_visible(False)
            ax1.spines["right"].set_visible(False)
            st.pyplot(fig1)
            plt.close(fig1)

    with col2:
        blue_title("Fill Rate by Region")
        if "region" in df.columns and "fill_rate_pct" in df.columns:
            region_summary = df.groupby("region", observed=True)["fill_rate_pct"].mean().sort_values(ascending=False)
            fig2, ax2 = plt.subplots(figsize=(7, 4))
            fig2.patch.set_facecolor(GREEN_BG)
            ax2.set_facecolor(GREEN_BG)
            fig2.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.32)
            ax2.bar(region_summary.index.astype(str), region_summary.values, color="#F59E0B")
            ax2.set_xlabel("Region")
            ax2.set_ylabel("Avg Fill Rate (%)")
            ax2.tick_params(axis="x", rotation=45)
            ax2.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
            ax2.spines["top"].set_visible(False)
            ax2.spines["right"].set_visible(False)
            st.pyplot(fig2)
            plt.close(fig2)

    # Additional Insights
    blue_title("Key Insights")
    insights = []
    if "stockout_pct" in df.columns:
        high_stockout = df[df["stockout_pct"] > 20].shape[0]
        insights.append(f"🔴 {high_stockout} records with high stockout (>20%)")
    if "excess_inventory_pct" in df.columns:
        high_excess = df[df["excess_inventory_pct"] > 30].shape[0]
        insights.append(f"🟡 {high_excess} records with excess inventory (>30%)")
    if "inventory_turnover" in df.columns:
        low_turnover = df[df["inventory_turnover"] < 2].shape[0]
        insights.append(f"🟢 {low_turnover} records with low turnover (<2)")
    
    for insight in insights:
        st.info(insight)


# ============================================================
# SECTION B: VEHICLE & FLEET ANALYSIS
# ============================================================

if eda_option in [
    "Shipment & Routing Analysis",
    "Cluster Transfer Analysis"
]:

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="
        background-color:#0B2C5D;
        padding:18px 25px;
        border-radius:10px;
        color:white;
        margin-top:20px;
        margin-bottom:12px;
    ">
        <h3 style="margin:0;">Vehicle & Fleet Performance Analysis</h3>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="
        background-color:#2F75B5;
        padding:24px;
        border-radius:12px;
        color:white;
        font-size:16px;
        line-height:1.7;
        margin-bottom:20px;
    ">
    <b>What this section does:</b><br>
    This analyzes <b>fleet performance across vehicles</b>, evaluating delivery speed,
    fuel efficiency, utilisation rates, and route coverage.

    It focuses on:
    <ul>
        <li>Vehicle-wise average delivery times</li>
        <li>Fuel cost vs route efficiency per vehicle</li>
        <li>Fleet utilisation — shipments per vehicle</li>
        <li>Average distance covered vs delivery time</li>
    </ul><br>

    <b>Why this matters:</b>

    Vehicle allocation directly impacts delivery performance and logistics cost.
    Under-utilised vehicles increase fixed costs, while overloaded ones cause delays.<br>

    <b>Key insights users get:</b>
    <ul>
        <li>Which vehicles consistently underperform on speed or efficiency</li>
        <li>Fuel cost outliers by vehicle</li>
        <li>Fleet rebalancing opportunities to improve last-mile performance</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    GREEN_BG   = "#00D05E"
    GRID_GREEN = "#3B3B3B"
    BAR_BLUE   = "#001F5C"

    col_vehicle  = "vehicle_id"
    col_delivery = "delivery_time_mins"
    col_fuel     = "fuel_cost"
    col_efficiency = "route_efficiency_score"
    col_distance = "distance_km"

    TOP_VEH = 15

    veh_metrics = df.groupby(col_vehicle).agg(
        avg_delivery=(col_delivery, "mean"),
        avg_fuel=(col_fuel, "mean"),
        avg_efficiency=(col_efficiency, "mean"),
        total_shipments=(col_delivery, "count"),
        avg_distance=(col_distance, "mean")
    ).sort_values("avg_delivery", ascending=False).head(TOP_VEH)

    def blue_title_veh(title):
        st.markdown(
            f"""
            <div style="background-color:#2F75B5;padding:14px;border-radius:8px;
            font-size:16px;color:white;margin-bottom:8px;text-align:center;font-weight:600;">
                {title}
            </div>
            """,
            unsafe_allow_html=True
        )

    col1, col2 = st.columns(2)

    with col1:
        blue_title_veh("Vehicle-wise Avg Delivery Time (Top 15 Slowest)")
        fig_vd, ax_vd = plt.subplots(figsize=(7, 4))
        fig_vd.patch.set_facecolor(GREEN_BG)
        ax_vd.set_facecolor(GREEN_BG)
        fig_vd.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.32)
        ax_vd.bar(veh_metrics.index.astype(str), veh_metrics["avg_delivery"], color=BAR_BLUE)
        ax_vd.set_xlabel("Vehicle ID")
        ax_vd.set_ylabel("Avg Delivery Time (mins)")
        ax_vd.tick_params(axis="x", rotation=45)
        ax_vd.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax_vd.spines["top"].set_visible(False)
        ax_vd.spines["right"].set_visible(False)
        st.pyplot(fig_vd)
        plt.close(fig_vd)

    with col2:
        blue_title_veh("Vehicle Fuel Cost vs Route Efficiency")
        all_veh = df.groupby(col_vehicle).agg(
            avg_fuel=(col_fuel, "mean"),
            avg_efficiency=(col_efficiency, "mean")
        )
        fig_vfe, ax_vfe = plt.subplots(figsize=(7, 4))
        fig_vfe.patch.set_facecolor(GREEN_BG)
        ax_vfe.set_facecolor(GREEN_BG)
        fig_vfe.subplots_adjust(left=0.10, right=0.98, top=0.92, bottom=0.13)
        ax_vfe.scatter(all_veh["avg_fuel"], all_veh["avg_efficiency"], alpha=0.6, color=BAR_BLUE)
        ax_vfe.set_xlabel("Avg Fuel Cost (₹)")
        ax_vfe.set_ylabel("Avg Route Efficiency Score")
        ax_vfe.grid(True, linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax_vfe.spines["top"].set_visible(False)
        ax_vfe.spines["right"].set_visible(False)
        st.pyplot(fig_vfe)
        plt.close(fig_vfe)

    col3, col4 = st.columns(2)

    with col3:
        blue_title_veh("Fleet Utilisation (Shipments per Vehicle – Top 15)")
        fleet_util = df.groupby(col_vehicle)[col_delivery].count().sort_values(ascending=False).head(TOP_VEH)
        fig_fu, ax_fu = plt.subplots(figsize=(7, 4))
        fig_fu.patch.set_facecolor(GREEN_BG)
        ax_fu.set_facecolor(GREEN_BG)
        fig_fu.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.32)
        ax_fu.bar(fleet_util.index.astype(str), fleet_util.values, color="#00897B")
        ax_fu.set_xlabel("Vehicle ID")
        ax_fu.set_ylabel("Total Shipments")
        ax_fu.tick_params(axis="x", rotation=45)
        ax_fu.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax_fu.spines["top"].set_visible(False)
        ax_fu.spines["right"].set_visible(False)
        st.pyplot(fig_fu)
        plt.close(fig_fu)

    with col4:
        blue_title_veh("Vehicle Avg Distance vs Avg Delivery Time")
        x_vda = np.arange(len(veh_metrics))
        w_vda = 0.35
        fig_vda, ax_vda1 = plt.subplots(figsize=(7, 4))
        fig_vda.patch.set_facecolor(GREEN_BG)
        ax_vda1.set_facecolor(GREEN_BG)
        fig_vda.subplots_adjust(left=0.10, right=0.90, top=0.92, bottom=0.28)
        ax_vda1.bar(x_vda - w_vda/2, veh_metrics["avg_distance"], w_vda, label="Avg Distance (km)", color=BAR_BLUE)
        ax_vda1.set_ylabel("Avg Distance (km)")
        ax_vda2 = ax_vda1.twinx()
        ax_vda2.bar(x_vda + w_vda/2, veh_metrics["avg_delivery"], w_vda, label="Avg Delivery (mins)", color="#F59E0B")
        ax_vda2.set_ylabel("Avg Delivery Time (mins)")
        ax_vda1.set_xticks(x_vda)
        ax_vda1.set_xticklabels(veh_metrics.index.astype(str), rotation=45, ha="right", fontsize=7)
        ax_vda1.set_xlabel("Vehicle ID")
        h1, l1 = ax_vda1.get_legend_handles_labels()
        h2, l2 = ax_vda2.get_legend_handles_labels()
        ax_vda1.legend(h1 + h2, l1 + l2, loc="upper right", fontsize=8)
        ax_vda1.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax_vda1.spines["top"].set_visible(False)
        ax_vda1.spines["right"].set_visible(False)
        ax_vda2.spines["top"].set_visible(False)
        st.pyplot(fig_vda)
        plt.close(fig_vda)


# ============================================================
# SECTION C: ZONE & CITY INVENTORY ANALYSIS
# ============================================================

if eda_option in [
    "Store & Regional Analysis",
    "Inventory Overview"
]:

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="
        background-color:#0B2C5D;
        padding:18px 25px;
        border-radius:10px;
        color:white;
        margin-top:20px;
        margin-bottom:12px;
    ">
        <h3 style="margin:0;">Zone & City Inventory Analysis</h3>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="
        background-color:#2F75B5;
        padding:24px;
        border-radius:12px;
        color:white;
        font-size:16px;
        line-height:1.7;
        margin-bottom:20px;
    ">
    <b>What this section does:</b><br>
    This provides a <b>granular geographic view of inventory health</b>
    at the zone and city level — going deeper than regional analysis.

    It focuses on:
    <ul>
        <li>Total stock value distribution by zone</li>
        <li>Stockout rates by city — identifying high-risk urban markets</li>
        <li>Overstock vs understock exposure by zone</li>
        <li>Fill rate comparison across store types</li>
    </ul><br>

    <b>Why this matters:</b>

    Regional averages can mask city-level or zone-level inventory crises.
    A region with healthy average fill rates may still contain cities
    with chronic stockout problems.<br>

    <b>Key insights users get:</b>
    <ul>
        <li>City-level stockout hotspots requiring urgent attention</li>
        <li>Zone-level excess inventory available for redistribution</li>
        <li>Store-type specific fill rate benchmarks for policy setting</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    GREEN_BG   = "#00D05E"
    GRID_GREEN = "#3B3B3B"
    BAR_BLUE   = "#001F5C"

    col_zone      = "zone"
    col_city      = "city"
    col_store_type = "store_type"
    col_stockval  = "stock_value"
    col_stockout  = "stockout_pct"
    col_fill_rate = "fill_rate_pct"
    col_overstock = "overstock_qty"
    col_understock = "understock_qty"

    TOP_CITIES = 15

    def blue_title_zone(title):
        st.markdown(
            f"""
            <div style="background-color:#2F75B5;padding:14px;border-radius:8px;
            font-size:16px;color:white;margin-bottom:8px;text-align:center;font-weight:600;">
                {title}
            </div>
            """,
            unsafe_allow_html=True
        )

    col1, col2 = st.columns(2)

    with col1:
        blue_title_zone("Stock Value by Zone")
        zone_sv = df.groupby(col_zone, observed=True)[col_stockval].sum().sort_values(ascending=False)
        chart_zsv = (
            alt.Chart(zone_sv.reset_index())
            .mark_bar(color=BAR_BLUE, cornerRadiusEnd=6)
            .encode(
                x=alt.X(f"{col_zone}:O", title="Zone"),
                y=alt.Y(f"{col_stockval}:Q", title="Total Stock Value (₹)", scale=alt.Scale(padding=10)),
                tooltip=[col_zone, col_stockval]
            )
            .properties(height=340, background=GREEN_BG,
                        padding={"top":10,"left":10,"right":10,"bottom":10})
            .configure_view(fill=GREEN_BG, strokeOpacity=0)
            .configure_axis(labelColor="#000000", titleColor="#000000",
                            gridColor="rgba(0,0,0,0.2)", domainColor="rgba(0,0,0,0.3)")
        )
        st.altair_chart(chart_zsv, use_container_width=True)

    with col2:
        blue_title_zone(f"Stockout Rate by City (Top {TOP_CITIES})")
        city_so = df.groupby(col_city)[col_stockout].mean().sort_values(ascending=False).head(TOP_CITIES)
        fig_cso, ax_cso = plt.subplots(figsize=(7, 4))
        fig_cso.patch.set_facecolor(GREEN_BG)
        ax_cso.set_facecolor(GREEN_BG)
        fig_cso.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.32)
        ax_cso.bar(city_so.index.astype(str), city_so.values, color="#EF4444")
        ax_cso.set_xlabel("City")
        ax_cso.set_ylabel("Avg Stockout Rate (%)")
        ax_cso.tick_params(axis="x", rotation=45)
        ax_cso.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax_cso.spines["top"].set_visible(False)
        ax_cso.spines["right"].set_visible(False)
        st.pyplot(fig_cso)
        plt.close(fig_cso)

    col3, col4 = st.columns(2)

    with col3:
        blue_title_zone("Zone Overstock vs Understock")
        zone_ov = df.groupby(col_zone, observed=True).agg(
            total_overstock=(col_overstock, "sum"),
            total_understock=(col_understock, "sum")
        ).sort_values("total_overstock", ascending=False)
        x_zo = np.arange(len(zone_ov))
        w_zo = 0.35
        fig_zo, ax_zo = plt.subplots(figsize=(7, 4))
        fig_zo.patch.set_facecolor(GREEN_BG)
        ax_zo.set_facecolor(GREEN_BG)
        fig_zo.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.17)
        ax_zo.bar(x_zo - w_zo/2, zone_ov["total_overstock"], w_zo, label="Overstock", color=BAR_BLUE)
        ax_zo.bar(x_zo + w_zo/2, zone_ov["total_understock"], w_zo, label="Understock", color="#EF4444")
        ax_zo.set_xticks(x_zo)
        ax_zo.set_xticklabels(zone_ov.index.astype(str), rotation=45, ha="right")
        ax_zo.set_xlabel("Zone")
        ax_zo.set_ylabel("Quantity")
        ax_zo.legend()
        ax_zo.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax_zo.spines["top"].set_visible(False)
        ax_zo.spines["right"].set_visible(False)
        st.pyplot(fig_zo)
        plt.close(fig_zo)

    with col4:
        blue_title_zone("Fill Rate by Store Type")
        stype_fill = df.groupby(col_store_type, observed=True)[col_fill_rate].mean().sort_values(ascending=False)
        chart_stf = (
            alt.Chart(stype_fill.reset_index())
            .mark_bar(color="#00897B", cornerRadiusEnd=6)
            .encode(
                x=alt.X(f"{col_store_type}:O", title="Store Type"),
                y=alt.Y(f"{col_fill_rate}:Q", title="Avg Fill Rate (%)", scale=alt.Scale(padding=10)),
                tooltip=[col_store_type, col_fill_rate]
            )
            .properties(height=300, background=GREEN_BG,
                        padding={"top":10,"left":10,"right":10,"bottom":10})
            .configure_view(fill=GREEN_BG, strokeOpacity=0)
            .configure_axis(labelColor="#000000", titleColor="#000000",
                            gridColor="rgba(0,0,0,0.2)", domainColor="rgba(0,0,0,0.3)")
        )
        st.altair_chart(chart_stf, width='stretch')


# ============================================================
# SECTION D: DEMAND INDEX & MODEL CONFIDENCE CORRELATION
# ============================================================

if eda_option in [
    "Cluster Transfer Analysis",
    "Product-Level Analysis",
    "Supplier Analysis"
]:

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="
        background-color:#0B2C5D;
        padding:18px 25px;
        border-radius:10px;
        color:white;
        margin-top:20px;
        margin-bottom:12px;
    ">
        <h3 style="margin:0;">Demand Index & Model Confidence Correlation Analysis</h3>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="
        background-color:#2F75B5;
        padding:24px;
        border-radius:12px;
        color:white;
        font-size:16px;
        line-height:1.7;
        margin-bottom:20px;
    ">
    <b>What this section does:</b><br>
    This analyzes how <b>demand index signals and model confidence scores</b>
    correlate with inventory turnover and overstock patterns — providing
    a cross-dimensional view of optimization readiness.

    It focuses on:
    <ul>
        <li>Demand index distribution by product category</li>
        <li>Model confidence scores across cluster model versions</li>
        <li>Demand index vs inventory turnover relationship</li>
        <li>Overstock index by region — identifying demand-supply misalignment</li>
    </ul><br>

    <b>Why this matters:</b>

    High demand index with low inventory turnover indicates a replenishment timing problem.
    High model confidence with low service level gain indicates a cluster assignment issue.
    This analysis identifies these <b>optimization gaps systematically</b>.<br>

    <b>Key insights users get:</b>
    <ul>
        <li>Which categories have misaligned demand signals vs actual turnover</li>
        <li>Which model versions deliver the highest confidence for transfer decisions</li>
        <li>Regional overstock index hotspots that contradict demand signals</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    GREEN_BG   = "#00D05E"
    GRID_GREEN = "#3B3B3B"
    BAR_BLUE   = "#001F5C"

    col_category       = "category"
    col_demand_index   = "demand_index"
    col_model_version  = "model_version"
    col_confidence     = "model_confidence_score"
    col_turnover       = "inventory_turnover"
    col_overstock_idx  = "overstock_index"
    col_region         = "region"

    def blue_title_di(title):
        st.markdown(
            f"""
            <div style="background-color:#2F75B5;padding:14px;border-radius:8px;
            font-size:16px;color:white;margin-bottom:8px;text-align:center;font-weight:600;">
                {title}
            </div>
            """,
            unsafe_allow_html=True
        )

    col1, col2 = st.columns(2)

    with col1:
        blue_title_di("Avg Demand Index by Product Category")
        cat_di = df.groupby(col_category)[col_demand_index].mean().sort_values(ascending=False)
        chart_di = (
            alt.Chart(cat_di.reset_index())
            .mark_bar(color=BAR_BLUE, cornerRadiusEnd=6)
            .encode(
                x=alt.X(f"{col_category}:O", title="Category"),
                y=alt.Y(f"{col_demand_index}:Q", title="Avg Demand Index", scale=alt.Scale(padding=10)),
                tooltip=[col_category, col_demand_index]
            )
            .properties(height=340, background=GREEN_BG,
                        padding={"top":10,"left":10,"right":10,"bottom":10})
            .configure_view(fill=GREEN_BG, strokeOpacity=0)
            .configure_axis(labelColor="#000000", titleColor="#000000",
                            gridColor="rgba(0,0,0,0.2)", domainColor="rgba(0,0,0,0.3)")
        )
        st.altair_chart(chart_di, use_container_width=True)

    with col2:
        blue_title_di("Model Confidence Score by Model Version")
        mv_conf = df.groupby(col_model_version)[col_confidence].mean().sort_values(ascending=False)
        chart_mvc = (
            alt.Chart(mv_conf.reset_index())
            .mark_bar(color="#00897B", cornerRadiusEnd=6)
            .encode(
                x=alt.X(f"{col_model_version}:O", title="Model Version"),
                y=alt.Y(f"{col_confidence}:Q", title="Avg Confidence Score", scale=alt.Scale(padding=10)),
                tooltip=[col_model_version, col_confidence]
            )
            .properties(height=340, background=GREEN_BG,
                        padding={"top":10,"left":10,"right":10,"bottom":10})
            .configure_view(fill=GREEN_BG, strokeOpacity=0)
            .configure_axis(labelColor="#000000", titleColor="#000000",
                            gridColor="rgba(0,0,0,0.2)", domainColor="rgba(0,0,0,0.3)")
        )
        st.altair_chart(chart_mvc, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        blue_title_di("Demand Index vs Inventory Turnover (All Products)")
        fig_dit, ax_dit = plt.subplots(figsize=(7, 4))
        fig_dit.patch.set_facecolor(GREEN_BG)
        ax_dit.set_facecolor(GREEN_BG)
        fig_dit.subplots_adjust(left=0.10, right=0.98, top=0.92, bottom=0.13)
        ax_dit.scatter(
            df[col_demand_index],
            df[col_turnover],
            alpha=0.3,
            color=BAR_BLUE,
            s=15
        )
        ax_dit.set_xlabel("Demand Index")
        ax_dit.set_ylabel("Inventory Turnover")
        ax_dit.grid(True, linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax_dit.spines["top"].set_visible(False)
        ax_dit.spines["right"].set_visible(False)
        st.pyplot(fig_dit)
        plt.close(fig_dit)

    with col4:
        blue_title_di("Avg Overstock Index by Region")
        reg_oi = df.groupby(col_region, observed=False)[col_overstock_idx].mean().sort_values(ascending=False)
        chart_roi = (
            alt.Chart(reg_oi.reset_index())
            .mark_bar(color="#F59E0B", cornerRadiusEnd=6)
            .encode(
                x=alt.X(f"{col_region}:O", title="Region"),
                y=alt.Y(f"{col_overstock_idx}:Q", title="Avg Overstock Index", scale=alt.Scale(padding=10)),
                tooltip=[col_region, col_overstock_idx]
            )
            .properties(height=300, background=GREEN_BG,
                        padding={"top":10,"left":10,"right":10,"bottom":10})
            .configure_view(fill=GREEN_BG, strokeOpacity=0)
            .configure_axis(labelColor="#000000", titleColor="#000000",
                            gridColor="rgba(0,0,0,0.2)", domainColor="rgba(0,0,0,0.3)")
        )
        st.altair_chart(chart_roi, use_container_width=True)

# ============================================================
# SUPPLYSYNC ML IMPLEMENTATION
# ============================================================
# ML GATE – LOCKED UNTIL EDA IS DONE
if not st.session_state.eda_completed:
    st.warning("⚠️ Please complete at least one EDA step to unlock ML Implementation.")
    st.stop()
    
import xgboost as xgb
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

from sklearn.feature_selection import SelectKBest, f_regression, mutual_info_regression, RFE
from sklearn.preprocessing import StandardScaler
from sklearn.inspection import permutation_importance

from streamlit_option_menu import option_menu


st.markdown(
    """
    <div style="
        background-color:#0B2C5D;
        padding:18px 25px;
        border-radius:10px;
        color:white;
        margin-top:30px;
        margin-bottom:20px;
    ">
        <h3 style="margin:0;">
            ML Model Implementations 
        </h3>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:24px;
        border-radius:12px;
        color:white;
        font-size:16px;
        line-height:1.7;
        margin-bottom:25px;
    ">
    <b>Core Objective:</b> Predict + optimize + automate inventory movement decisions across the network
    
    <p>This architecture implements 10 layers of ML models to create a comprehensive supply chain intelligence system:</p>
    <ul>
        <li><b>Layer 1:</b> Demand & Supply Intelligence – Forecasting, stockout prediction, overstock risk</li>
        <li><b>Layer 2:</b> Smart Segmentation – Store, product, and supplier clustering</li>
        <li><b>Layer 3:</b> Redistribution Decision Engine – Supply-demand matching and transfer optimization</li>
        <li><b>Layer 4:</b> Logistics & Route Optimization – Route planning and delivery prediction</li>
        <li><b>Layer 5:</b> Inventory Policy Optimization – Dynamic reorder points and safety stock</li>
        <li><b>Layer 6:</b> Warehouse Intelligence – Load prediction and storage optimization</li>
        <li><b>Layer 7:</b> Supplier Intelligence – Lead time prediction and risk scoring</li>
        <li><b>Layer 8:</b> Reinforcement Learning – Self-learning inventory redistribution agent</li>
        <li><b>Layer 9:</b> Anomaly Detection – Outlier detection for data quality</li>
        <li><b>Layer 10:</b> Explainable AI – Model interpretability with SHAP/LIME</li>
    </ul>
    </div>
    """,
    unsafe_allow_html=True
)

# ================================================================
# LAYER 1: DEMAND & SUPPLY INTELLIGENCE LAYER
# ================================================================

st.markdown(
    """
    <div style="
        background-color:#00D05E;
        padding:20px;
        border-radius:12px;
        color:white;
        font-size:20px;
        font-weight:600;
        margin-top:30px;
        margin-bottom:20px;
    ">
    🚀 Layer 1: Demand & Supply Intelligence Layer
    </div>
    """,
    unsafe_allow_html=True
)

# ================================================================
# MODEL 1.1: DEMAND FORECASTING MODEL
# ================================================================

st.markdown(
    """
    <div style="
        background-color:#163A70;
        padding:18px;
        border-radius:10px;
        color:white;
        font-size:18px;
        font-weight:600;
        margin-top:25px;
        margin-bottom:15px;
    ">
    🔹 ML Implementation: Demand Forecasting Model
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:20px;
        border-radius:12px;
        color:white;
        font-size:15px;
        line-height:1.6;
        margin-bottom:20px;
    ">
    <b>Type:</b> Time Series + ML Hybrid<br>
    <b>Models:</b> XGBoost / LightGBM (tabular demand drivers), LSTM / Temporal Fusion Transformer (sequence learning)<br>
    <b>Output:</b> SKU × Store × Time demand prediction<br>
    <b>Uses:</b> Sales Analysis, Time & Seasonality Analysis, Product Analysis
    </div>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def demand_forecasting_feature_engineering(df):
    """Feature engineering for demand forecasting model"""
    try:
        df_feat = df.copy()
        
        # Time-based features
        if 'date' in df_feat.columns:
            df_feat['date'] = pd.to_datetime(df_feat['date'])
            df_feat['day_of_week'] = df_feat['date'].dt.dayofweek
            df_feat['day_of_month'] = df_feat['date'].dt.day
            df_feat['month'] = df_feat['date'].dt.month
            df_feat['quarter'] = df_feat['date'].dt.quarter
            df_feat['year'] = df_feat['date'].dt.year
            df_feat['is_month_end'] = df_feat['date'].dt.is_month_end.astype(int)
            df_feat['is_month_start'] = df_feat['date'].dt.is_month_start.astype(int)
        
        # Lag features for demand
        if 'on_hand_qty' in df_feat.columns:
            df_feat['demand_lag_1'] = df_feat.groupby('product_id')['on_hand_qty'].shift(1)
            df_feat['demand_lag_7'] = df_feat.groupby('product_id')['on_hand_qty'].shift(7)
            df_feat['demand_lag_30'] = df_feat.groupby('product_id')['on_hand_qty'].shift(30)
        
        # Rolling statistics
        if 'on_hand_qty' in df_feat.columns:
            df_feat['demand_rolling_mean_7'] = df_feat.groupby('product_id')['on_hand_qty'].transform(lambda x: x.rolling(7).mean())
            df_feat['demand_rolling_std_7'] = df_feat.groupby('product_id')['on_hand_qty'].transform(lambda x: x.rolling(7).std())
            df_feat['demand_rolling_mean_30'] = df_feat.groupby('product_id')['on_hand_qty'].transform(lambda x: x.rolling(30).mean())
        
        # Product-level features
        if 'category' in df_feat.columns:
            category_demand = df_feat.groupby('category')['on_hand_qty'].transform('mean')
            df_feat['category_avg_demand'] = category_demand
        
        if 'subcategory' in df_feat.columns:
            subcategory_demand = df_feat.groupby('subcategory')['on_hand_qty'].transform('mean')
            df_feat['subcategory_avg_demand'] = subcategory_demand
        
        # Store-level features
        if 'store_id' in df_feat.columns:
            store_demand = df_feat.groupby('store_id')['on_hand_qty'].transform('mean')
            df_feat['store_avg_demand'] = store_demand
        
        # Seasonality indicators
        if 'month' in df_feat.columns:
            df_feat['is_q4'] = (df_feat['month'].isin([10, 11, 12])).astype(int)
            df_feat['is_holiday_season'] = (df_feat['month'].isin([11, 12])).astype(int)
        
        # Price and margin features
        if 'unit_price' in df_feat.columns and 'cost_price' in df_feat.columns:
            df_feat['margin_pct'] = ((df_feat['unit_price'] - df_feat['cost_price']) / df_feat['unit_price']) * 100
        
        # Fill NaN values
        numeric_cols = df_feat.select_dtypes(include=[np.number]).columns
        df_feat[numeric_cols] = df_feat[numeric_cols].fillna(df_feat[numeric_cols].median())
        
        return df_feat
        
    except Exception as e:
        st.error(f"Error in demand forecasting feature engineering: {str(e)}")
        return df

@st.cache_data
def train_demand_forecasting_model(X_train, y_train, model_type='xgboost'):
    """Train demand forecasting model"""
    try:
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
        
        X_train_split, X_val, y_train_split, y_val = train_test_split(
            X_train, y_train, test_size=0.2, random_state=42
        )
        
        if model_type == 'xgboost':
            try:
                import xgboost as xgb
                model = xgb.XGBRegressor(
                    n_estimators=100,
                    max_depth=6,
                    learning_rate=0.1,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    random_state=42,
                    n_jobs=-1
                )
            except ImportError:
                from sklearn.ensemble import RandomForestRegressor
                model = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42,
                    n_jobs=-1
                )
        elif model_type == 'lightgbm':
            try:
                import lightgbm as lgb
                model = lgb.LGBMRegressor(
                    n_estimators=100,
                    max_depth=6,
                    learning_rate=0.1,
                    random_state=42,
                    n_jobs=-1
                )
            except ImportError:
                from sklearn.ensemble import RandomForestRegressor
                model = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42,
                    n_jobs=-1
                )
        else:
            from sklearn.ensemble import RandomForestRegressor
            model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
        
        model.fit(X_train_split, y_train_split)
        
        # Validation
        y_pred = model.predict(X_val)
        mae = mean_absolute_error(y_val, y_pred)
        rmse = np.sqrt(mean_squared_error(y_val, y_pred))
        r2 = r2_score(y_val, y_pred)
        
        metrics = {
            'MAE': mae,
            'RMSE': rmse,
            'R2': r2
        }
        
        return model, metrics
        
    except Exception as e:
        st.error(f"Error training demand forecasting model: {str(e)}")
        return None, None

if st.button("Train Demand Forecasting Model", key="demand_forecast_btn"):
    if df is not None and not df.empty:
        with st.spinner("Performing feature engineering for demand forecasting..."):
            df_demand_feat = demand_forecasting_feature_engineering(df)
            st.success("✅ Feature engineering completed")
        
        # Select features for demand forecasting
        demand_features = [
            'day_of_week', 'day_of_month', 'month', 'quarter', 'year',
            'is_month_end', 'is_month_start', 'demand_lag_1', 'demand_lag_7',
            'demand_lag_30', 'demand_rolling_mean_7', 'demand_rolling_std_7',
            'demand_rolling_mean_30', 'category_avg_demand', 'subcategory_avg_demand',
            'store_avg_demand', 'is_q4', 'is_holiday_season'
        ]
        
        available_demand_features = [f for f in demand_features if f in df_demand_feat.columns]
        
        if len(available_demand_features) > 0 and 'on_hand_qty' in df_demand_feat.columns:
            X_demand = df_demand_feat[available_demand_features].fillna(0)
            y_demand = df_demand_feat['on_hand_qty'].fillna(0)
            
            with st.spinner("Training demand forecasting model..."):
                demand_model, demand_metrics = train_demand_forecasting_model(X_demand, y_demand)
                
                if demand_model is not None:
                    st.success("✅ Demand forecasting model trained successfully")
                    
                    st.markdown("### Model Performance Metrics")
                    st.json(demand_metrics)
                    
                    st.session_state['demand_model'] = demand_model
                    st.session_state['demand_features'] = available_demand_features
        else:
            st.warning("⚠️ Insufficient features for demand forecasting model")

# ================================================================
# MODEL 1.2: STOCKOUT PROBABILITY MODEL
# ================================================================

st.markdown(
    """
    <div style="
        background-color:#163A70;
        padding:18px;
        border-radius:10px;
        color:white;
        font-size:18px;
        font-weight:600;
        margin-top:25px;
        margin-bottom:15px;
    ">
    🔹 ML Implementation: Stockout Probability Model
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:20px;
        border-radius:12px;
        color:white;
        font-size:15px;
        line-height:1.6;
        margin-bottom:20px;
    ">
    <b>Type:</b> Classification (Binary / Multi-class)<br>
    <b>Predicts:</b> Probability of stockout in next N days<br>
    <b>Inputs:</b> Current inventory, Demand forecast, Lead time (Supplier Analysis)<br>
    <b>Output:</b> "Risk Score" per SKU-store
    </div>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def stockout_feature_engineering(df):
    """Feature engineering for stockout probability model"""
    try:
        df_feat = df.copy()
        
        # Current inventory features
        if 'on_hand_qty' in df_feat.columns:
            df_feat['current_inventory'] = df_feat['on_hand_qty']
            df_feat['inventory_pressure'] = df_feat.groupby('store_id')['on_hand_qty'].transform(
                lambda x: x / x.mean()
            )
        
        # Demand-related features
        if 'demand_index' in df_feat.columns:
            df_feat['demand_pressure'] = df_feat['demand_index']
        
        # Lead time features
        if 'lead_time_days' in df_feat.columns:
            df_feat['lead_time_risk'] = df_feat['lead_time_days']
        
        # Stockout history
        if 'stockout_pct' in df_feat.columns:
            df_feat['historical_stockout_rate'] = df_feat['stockout_pct']
            df_feat['high_stockout_risk'] = (df_feat['stockout_pct'] > 20).astype(int)
        
        # Fill rate features
        if 'fill_rate_pct' in df_feat.columns:
            df_feat['fill_rate_risk'] = 100 - df_feat['fill_rate_pct']
        
        # Supplier reliability
        if 'supplier_rating' in df_feat.columns:
            df_feat['supplier_risk'] = 5 - df_feat['supplier_rating']
        
        # Time-based risk factors
        if 'is_holiday' in df_feat.columns:
            df_feat['holiday_risk'] = df_feat['is_holiday'].astype(int)
        
        if 'is_weekend' in df_feat.columns:
            df_feat['weekend_risk'] = df_feat['is_weekend'].astype(int)
        
        # Product-specific risk
        if 'shelf_life_days' in df_feat.columns:
            df_feat['short_shelf_life'] = (df_feat['shelf_life_days'] < 30).astype(int)
        
        # Store-specific risk
        if 'store_type' in df_feat.columns:
            store_stockout = df_feat.groupby('store_type')['stockout_pct'].transform('mean')
            df_feat['store_type_risk'] = store_stockout
        
        # Category-specific risk
        if 'category' in df_feat.columns:
            category_stockout = df_feat.groupby('category')['stockout_pct'].transform('mean')
            df_feat['category_risk'] = category_stockout
        
        # Create target variable (stockout in next period)
        if 'stockout_pct' in df_feat.columns:
            df_feat['stockout_target'] = (df_feat['stockout_pct'] > 15).astype(int)
        
        # Fill NaN values
        numeric_cols = df_feat.select_dtypes(include=[np.number]).columns
        df_feat[numeric_cols] = df_feat[numeric_cols].fillna(df_feat[numeric_cols].median())
        
        return df_feat
        
    except Exception as e:
        st.error(f"Error in stockout feature engineering: {str(e)}")
        return df

@st.cache_data
def train_stockout_model(X_train, y_train, model_type='random_forest'):
    """Train stockout probability model"""
    try:
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
        from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
        
        X_train_split, X_val, y_train_split, y_val = train_test_split(
            X_train, y_train, test_size=0.2, random_state=42, stratify=y_train
        )
        
        if model_type == 'gradient_boosting':
            model = GradientBoostingClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
        else:
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1,
                class_weight='balanced'
            )
        
        model.fit(X_train_split, y_train_split)
        
        # Validation
        y_pred = model.predict(X_val)
        y_pred_proba = model.predict_proba(X_val)[:, 1]
        
        metrics = {
            'Accuracy': accuracy_score(y_val, y_pred),
            'Precision': precision_score(y_val, y_pred, average='binary'),
            'Recall': recall_score(y_val, y_pred, average='binary'),
            'F1 Score': f1_score(y_val, y_pred, average='binary'),
            'ROC AUC': roc_auc_score(y_val, y_pred_proba)
        }
        
        return model, metrics
        
    except Exception as e:
        st.error(f"Error training stockout model: {str(e)}")
        return None, None

if st.button("Train Stockout Probability Model", key="stockout_btn"):
    if df is not None and not df.empty:
        with st.spinner("Performing feature engineering for stockout prediction..."):
            df_stockout_feat = stockout_feature_engineering(df)
            st.success("✅ Feature engineering completed")
        
        # Select features for stockout prediction
        stockout_features = [
            'current_inventory', 'inventory_pressure', 'demand_pressure',
            'lead_time_risk', 'historical_stockout_rate', 'high_stockout_risk',
            'fill_rate_risk', 'supplier_risk', 'holiday_risk', 'weekend_risk',
            'short_shelf_life', 'store_type_risk', 'category_risk'
        ]
        
        available_stockout_features = [f for f in stockout_features if f in df_stockout_feat.columns]
        
        if len(available_stockout_features) > 0 and 'stockout_target' in df_stockout_feat.columns:
            X_stockout = df_stockout_feat[available_stockout_features].fillna(0)
            y_stockout = df_stockout_feat['stockout_target'].fillna(0)
            
            with st.spinner("Training stockout probability model..."):
                stockout_model, stockout_metrics = train_stockout_model(X_stockout, y_stockout)
                
                if stockout_model is not None:
                    st.success("✅ Stockout probability model trained successfully")
                    
                    st.markdown("### Model Performance Metrics")
                    st.json(stockout_metrics)
                    
                    st.session_state['stockout_model'] = stockout_model
                    st.session_state['stockout_features'] = available_stockout_features
        else:
            st.warning("⚠️ Insufficient features for stockout prediction model")

# ================================================================
# MODEL 1.3: OVERSTOCK RISK MODEL
# ================================================================

st.markdown(
    """
    <div style="
        background-color:#163A70;
        padding:18px;
        border-radius:10px;
        color:white;
        font-size:18px;
        font-weight:600;
        margin-top:25px;
        margin-bottom:15px;
    ">
    🔹 ML Implementation: Overstock Risk Model
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:20px;
        border-radius:12px;
        color:white;
        font-size:15px;
        line-height:1.6;
        margin-bottom:20px;
    ">
    <b>Type:</b> Regression / Classification<br>
    <b>Predicts:</b> Excess inventory probability, Dead stock risk (based on shelf-life)<br>
    <b>Inputs:</b> Inventory turnover, Shelf life, Demand variance
    </div>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def overstock_feature_engineering(df):
    """Feature engineering for overstock risk model"""
    try:
        df_feat = df.copy()
        
        # Inventory turnover features
        if 'inventory_turnover' in df_feat.columns:
            df_feat['turnover_rate'] = df_feat['inventory_turnover']
            df_feat['low_turnover'] = (df_feat['inventory_turnover'] < 2).astype(int)
        
        # Overstock quantity features
        if 'overstock_qty' in df_feat.columns:
            df_feat['overstock_level'] = df_feat['overstock_qty']
            df_feat['overstock_ratio'] = df_feat['overstock_qty'] / (df_feat['on_hand_qty'] + 1)
        
        # Shelf life features
        if 'shelf_life_days' in df_feat.columns:
            df_feat['shelf_life_remaining'] = df_feat['shelf_life_days']
            df_feat['expiry_risk'] = (df_feat['shelf_life_days'] < 90).astype(int)
        
        # Demand variance
        if 'demand_index' in df_feat.columns:
            demand_std = df_feat.groupby('product_id')['demand_index'].transform('std')
            df_feat['demand_volatility'] = demand_std.fillna(0)
        
        # Stock value features
        if 'stock_value' in df_feat.columns:
            df_feat['inventory_value'] = df_feat['stock_value']
            df_feat['high_value_overstock'] = ((df_feat['overstock_qty'] * df_feat.get('unit_price', 1)) > 10000).astype(int)
        
        # Seasonality features
        if 'month' in df_feat.columns:
            df_feat['seasonal_overstock_risk'] = df_feat['month'].isin([1, 2, 11, 12]).astype(int)
        
        # Category-specific overstock patterns
        if 'category' in df_feat.columns:
            category_overstock = df_feat.groupby('category')['overstock_qty'].transform('mean')
            df_feat['category_overstock_tendency'] = category_overstock
        
        # Store-specific overstock patterns
        if 'store_id' in df_feat.columns:
            store_overstock = df_feat.groupby('store_id')['overstock_qty'].transform('mean')
            df_feat['store_overstock_tendency'] = store_overstock
        
        # Create target variable (overstock risk)
        if 'overstock_qty' in df_feat.columns and 'on_hand_qty' in df_feat.columns:
            df_feat['overstock_risk_target'] = ((df_feat['overstock_qty'] / df_feat['on_hand_qty']) > 0.3).astype(int)
        
        # Fill NaN values
        numeric_cols = df_feat.select_dtypes(include=[np.number]).columns
        df_feat[numeric_cols] = df_feat[numeric_cols].fillna(df_feat[numeric_cols].median())
        
        return df_feat
        
    except Exception as e:
        st.error(f"Error in overstock feature engineering: {str(e)}")
        return df

@st.cache_data
def train_overstock_model(X_train, y_train, model_type='random_forest'):
    """Train overstock risk model"""
    try:
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        from sklearn.ensemble import RandomForestClassifier
        
        X_train_split, X_val, y_train_split, y_val = train_test_split(
            X_train, y_train, test_size=0.2, random_state=42, stratify=y_train
        )
        
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1,
            class_weight='balanced'
        )
        
        model.fit(X_train_split, y_train_split)
        
        # Validation
        y_pred = model.predict(X_val)
        
        metrics = {
            'Accuracy': accuracy_score(y_val, y_pred),
            'Precision': precision_score(y_val, y_pred, average='binary'),
            'Recall': recall_score(y_val, y_pred, average='binary'),
            'F1 Score': f1_score(y_val, y_pred, average='binary')
        }
        
        return model, metrics
        
    except Exception as e:
        st.error(f"Error training overstock model: {str(e)}")
        return None, None

if st.button("Train Overstock Risk Model", key="overstock_btn"):
    if df is not None and not df.empty:
        with st.spinner("Performing feature engineering for overstock risk..."):
            df_overstock_feat = overstock_feature_engineering(df)
            st.success("✅ Feature engineering completed")
        
        # Select features for overstock prediction
        overstock_features = [
            'turnover_rate', 'low_turnover', 'overstock_level', 'overstock_ratio',
            'shelf_life_remaining', 'expiry_risk', 'demand_volatility',
            'inventory_value', 'high_value_overstock', 'seasonal_overstock_risk',
            'category_overstock_tendency', 'store_overstock_tendency'
        ]
        
        available_overstock_features = [f for f in overstock_features if f in df_overstock_feat.columns]
        
        if len(available_overstock_features) > 0 and 'overstock_risk_target' in df_overstock_feat.columns:
            X_overstock = df_overstock_feat[available_overstock_features].fillna(0)
            y_overstock = df_overstock_feat['overstock_risk_target'].fillna(0)
            
            with st.spinner("Training overstock risk model..."):
                overstock_model, overstock_metrics = train_overstock_model(X_overstock, y_overstock)
                
                if overstock_model is not None:
                    st.success("✅ Overstock risk model trained successfully")
                    
                    st.markdown("### Model Performance Metrics")
                    st.json(overstock_metrics)
                    
                    st.session_state['overstock_model'] = overstock_model
                    st.session_state['overstock_features'] = available_overstock_features
        else:
            st.warning("⚠️ Insufficient features for overstock risk model")


# ================================================================
# LAYER 2: SMART SEGMENTATION LAYER (CLUSTERING)
# ================================================================

st.markdown(
    """
    <div style="
        background-color:#00D05E;
        padding:20px;
        border-radius:12px;
        color:white;
        font-size:20px;
        font-weight:600;
        margin-top:30px;
        margin-bottom:20px;
    ">
    🚀 Layer 2: Smart Segmentation Layer (Clustering)
    </div>
    """,
    unsafe_allow_html=True
)

# ================================================================
# MODEL 2.1: STORE CLUSTERING
# ================================================================

st.markdown(
    """
    <div style="
        background-color:#163A70;
        padding:18px;
        border-radius:10px;
        color:white;
        font-size:18px;
        font-weight:600;
        margin-top:25px;
        margin-bottom:15px;
    ">
    🔹 ML Implementation: Store Clustering
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:20px;
        border-radius:12px;
        color:white;
        font-size:15px;
        line-height:1.6;
        margin-bottom:20px;
    ">
    <b>Algorithm:</b> KMeans / DBSCAN / Hierarchical<br>
    <b>Clusters stores based on:</b> Demand patterns, Geography, Fill rate behavior<br>
    <b>Output:</b> "Similar demand zones"
    </div>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def store_clustering_feature_engineering(df):
    """Feature engineering for store clustering"""
    try:
        df_feat = df.copy()
        
        # Demand pattern features
        if 'demand_index' in df_feat.columns:
            store_demand_mean = df_feat.groupby('store_id')['demand_index'].transform('mean')
            store_demand_std = df_feat.groupby('store_id')['demand_index'].transform('std')
            df_feat['store_demand_mean'] = store_demand_mean
            df_feat['store_demand_std'] = store_demand_std.fillna(0)
        
        # Fill rate features
        if 'fill_rate_pct' in df_feat.columns:
            store_fill_rate = df_feat.groupby('store_id')['fill_rate_pct'].transform('mean')
            df_feat['store_fill_rate'] = store_fill_rate
        
        # Stockout features
        if 'stockout_pct' in df_feat.columns:
            store_stockout = df_feat.groupby('store_id')['stockout_pct'].transform('mean')
            df_feat['store_stockout_rate'] = store_stockout
        
        # Geographic features
        if 'region' in df_feat.columns:
            region_dummies = pd.get_dummies(df_feat['region'], prefix='region')
            df_feat = pd.concat([df_feat, region_dummies], axis=1)
        
        if 'zone' in df_feat.columns:
            zone_dummies = pd.get_dummies(df_feat['zone'], prefix='zone')
            df_feat = pd.concat([df_feat, zone_dummies], axis=1)
        
        # Store type features
        if 'store_type' in df_feat.columns:
            store_type_dummies = pd.get_dummies(df_feat['store_type'], prefix='store_type')
            df_feat = pd.concat([df_feat, store_type_dummies], axis=1)
        
        # Inventory value features
        if 'stock_value' in df_feat.columns:
            store_stock_value = df_feat.groupby('store_id')['stock_value'].transform('mean')
            df_feat['store_avg_stock_value'] = store_stock_value
        
        # Turnover features
        if 'inventory_turnover' in df_feat.columns:
            store_turnover = df_feat.groupby('store_id')['inventory_turnover'].transform('mean')
            df_feat['store_avg_turnover'] = store_turnover
        
        # Fill NaN values
        numeric_cols = df_feat.select_dtypes(include=[np.number]).columns
        df_feat[numeric_cols] = df_feat[numeric_cols].fillna(df_feat[numeric_cols].median())
        
        return df_feat
        
    except Exception as e:
        st.error(f"Error in store clustering feature engineering: {str(e)}")
        return df

@st.cache_data
def train_store_clustering_model(X, n_clusters=5, algorithm='kmeans'):
    """Train store clustering model"""
    try:
        from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
        from sklearn.preprocessing import StandardScaler
        from sklearn.metrics import silhouette_score
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        if algorithm == 'kmeans':
            model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            labels = model.fit_predict(X_scaled)
            silhouette = silhouette_score(X_scaled, labels)
        elif algorithm == 'dbscan':
            model = DBSCAN(eps=0.5, min_samples=5)
            labels = model.fit_predict(X_scaled)
            if len(set(labels)) > 1:
                silhouette = silhouette_score(X_scaled, labels)
            else:
                silhouette = 0
        else:  # hierarchical
            model = AgglomerativeClustering(n_clusters=n_clusters)
            labels = model.fit_predict(X_scaled)
            silhouette = silhouette_score(X_scaled, labels)
        
        metrics = {
            'Silhouette Score': silhouette,
            'Number of Clusters': len(set(labels)),
            'Algorithm': algorithm
        }
        
        return model, labels, metrics, scaler
        
    except Exception as e:
        st.error(f"Error training store clustering model: {str(e)}")
        return None, None, None, None

if st.button("Train Store Clustering Model", key="store_cluster_btn"):
    if df is not None and not df.empty:
        with st.spinner("Performing feature engineering for store clustering..."):
            df_store_feat = store_clustering_feature_engineering(df)
            st.success("✅ Feature engineering completed")
        
        # Select numeric features for clustering
        store_cluster_features = [
            'store_demand_mean', 'store_demand_std', 'store_fill_rate',
            'store_stockout_rate', 'store_avg_stock_value', 'store_avg_turnover'
        ]
        
        # Add encoded categorical features
        for col in df_store_feat.columns:
            if col.startswith('region_') or col.startswith('zone_') or col.startswith('store_type_'):
                store_cluster_features.append(col)
        
        available_store_features = [f for f in store_cluster_features if f in df_store_feat.columns]
        
        if len(available_store_features) > 0:
            X_store = df_store_feat[available_store_features].fillna(0)
            
            # Get unique store-level data
            X_store_unique = X_store.groupby(df_store_feat['store_id']).mean()
            
            with st.spinner("Training store clustering model..."):
                store_cluster_model, store_labels, store_metrics, store_scaler = train_store_clustering_model(
                    X_store_unique, n_clusters=5, algorithm='kmeans'
                )
                
                if store_cluster_model is not None:
                    st.success("✅ Store clustering model trained successfully")
                    
                    st.markdown("### Clustering Performance Metrics")
                    st.json(store_metrics)
                    
                    st.session_state['store_cluster_model'] = store_cluster_model
                    st.session_state['store_cluster_features'] = available_store_features
                    st.session_state['store_cluster_scaler'] = store_scaler
        else:
            st.warning("⚠️ Insufficient features for store clustering model")

# ================================================================
# MODEL 2.2: PRODUCT CLUSTERING
# ================================================================

st.markdown(
    """
    <div style="
        background-color:#163A70;
        padding:18px;
        border-radius:10px;
        color:white;
        font-size:18px;
        font-weight:600;
        margin-top:25px;
        margin-bottom:15px;
    ">
    🔹 ML Implementation: Product Clustering
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:20px;
        border-radius:12px;
        color:white;
        font-size:15px;
        line-height:1.6;
        margin-bottom:20px;
    ">
    <b>Segments:</b> Fast-moving vs slow-moving vs seasonal<br>
    <b>Based on:</b> Demand index, Turnover, Margin
    </div>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def product_clustering_feature_engineering(df):
    """Feature engineering for product clustering"""
    try:
        df_feat = df.copy()
        
        # Demand index features
        if 'demand_index' in df_feat.columns:
            product_demand_mean = df_feat.groupby('product_id')['demand_index'].transform('mean')
            product_demand_std = df_feat.groupby('product_id')['demand_index'].transform('std')
            df_feat['product_demand_mean'] = product_demand_mean
            df_feat['product_demand_std'] = product_demand_std.fillna(0)
        
        # Turnover features
        if 'inventory_turnover' in df_feat.columns:
            product_turnover = df_feat.groupby('product_id')['inventory_turnover'].transform('mean')
            df_feat['product_turnover'] = product_turnover
        
        # Margin features
        if 'unit_price' in df_feat.columns and 'cost_price' in df_feat.columns:
            df_feat['product_margin'] = ((df_feat['unit_price'] - df_feat['cost_price']) / df_feat['unit_price']) * 100
            product_margin_mean = df_feat.groupby('product_id')['product_margin'].transform('mean')
            df_feat['product_avg_margin'] = product_margin_mean
        
        # Shelf life features
        if 'shelf_life_days' in df_feat.columns:
            product_shelf_life = df_feat.groupby('product_id')['shelf_life_days'].transform('mean')
            df_feat['product_shelf_life'] = product_shelf_life
        
        # Category features
        if 'category' in df_feat.columns:
            category_dummies = pd.get_dummies(df_feat['category'], prefix='category')
            df_feat = pd.concat([df_feat, category_dummies], axis=1)
        
        # Stock value features
        if 'stock_value' in df_feat.columns:
            product_stock_value = df_feat.groupby('product_id')['stock_value'].transform('mean')
            df_feat['product_avg_stock_value'] = product_stock_value
        
        # Fill NaN values
        numeric_cols = df_feat.select_dtypes(include=[np.number]).columns
        df_feat[numeric_cols] = df_feat[numeric_cols].fillna(df_feat[numeric_cols].median())
        
        return df_feat
        
    except Exception as e:
        st.error(f"Error in product clustering feature engineering: {str(e)}")
        return df

@st.cache_data
def train_product_clustering_model(X, n_clusters=4, algorithm='kmeans'):
    """Train product clustering model"""
    try:
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
        from sklearn.metrics import silhouette_score
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = model.fit_predict(X_scaled)
        silhouette = silhouette_score(X_scaled, labels)
        
        metrics = {
            'Silhouette Score': silhouette,
            'Number of Clusters': n_clusters,
            'Algorithm': algorithm
        }
        
        return model, labels, metrics, scaler
        
    except Exception as e:
        st.error(f"Error training product clustering model: {str(e)}")
        return None, None, None, None

if st.button("Train Product Clustering Model", key="product_cluster_btn"):
    if df is not None and not df.empty:
        with st.spinner("Performing feature engineering for product clustering..."):
            df_product_feat = product_clustering_feature_engineering(df)
            st.success("✅ Feature engineering completed")
        
        # Select features for product clustering
        product_cluster_features = [
            'product_demand_mean', 'product_demand_std', 'product_turnover',
            'product_avg_margin', 'product_shelf_life', 'product_avg_stock_value'
        ]
        
        # Add category dummies
        for col in df_product_feat.columns:
            if col.startswith('category_'):
                product_cluster_features.append(col)
        
        available_product_features = [f for f in product_cluster_features if f in df_product_feat.columns]
        
        if len(available_product_features) > 0:
            X_product = df_product_feat[available_product_features].fillna(0)
            
            # Get unique product-level data
            X_product_unique = X_product.groupby(df_product_feat['product_id']).mean()
            
            with st.spinner("Training product clustering model..."):
                product_cluster_model, product_labels, product_metrics, product_scaler = train_product_clustering_model(
                    X_product_unique, n_clusters=4, algorithm='kmeans'
                )
                
                if product_cluster_model is not None:
                    st.success("✅ Product clustering model trained successfully")
                    
                    st.markdown("### Clustering Performance Metrics")
                    st.json(product_metrics)
                    
                    st.session_state['product_cluster_model'] = product_cluster_model
                    st.session_state['product_cluster_features'] = available_product_features
                    st.session_state['product_cluster_scaler'] = product_scaler
        else:
            st.warning("⚠️ Insufficient features for product clustering model")

# ================================================================
# MODEL 2.3: SUPPLIER SEGMENTATION
# ================================================================

st.markdown(
    """
    <div style="
        background-color:#163A70;
        padding:18px;
        border-radius:10px;
        color:white;
        font-size:18px;
        font-weight:600;
        margin-top:25px;
        margin-bottom:15px;
    ">
    🔹 ML Implementation: Supplier Segmentation
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:20px;
        border-radius:12px;
        color:white;
        font-size:15px;
        line-height:1.6;
        margin-bottom:20px;
    ">
    <b>Segments:</b> High reliability vs risky suppliers<br>
    <b>Based on:</b> Lead time variability, Rating, Cost
    </div>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def supplier_segmentation_feature_engineering(df):
    """Feature engineering for supplier segmentation"""
    try:
        df_feat = df.copy()
        
        # Lead time features
        if 'lead_time_days' in df_feat.columns:
            supplier_lead_mean = df_feat.groupby('supplier_id')['lead_time_days'].transform('mean')
            supplier_lead_std = df_feat.groupby('supplier_id')['lead_time_days'].transform('std')
            df_feat['supplier_lead_mean'] = supplier_lead_mean
            df_feat['supplier_lead_std'] = supplier_lead_std.fillna(0)
            df_feat['supplier_lead_cv'] = supplier_lead_std / (supplier_lead_mean + 1)
        
        # Rating features
        if 'supplier_rating' in df_feat.columns:
            supplier_rating = df_feat.groupby('supplier_id')['supplier_rating'].transform('mean')
            df_feat['supplier_avg_rating'] = supplier_rating
        
        # Cost features
        if 'unit_price' in df_feat.columns:
            supplier_cost = df_feat.groupby('supplier_id')['unit_price'].transform('mean')
            df_feat['supplier_avg_cost'] = supplier_cost
        
        # Fill rate features
        if 'fill_rate_pct' in df_feat.columns:
            supplier_fill_rate = df_feat.groupby('supplier_id')['fill_rate_pct'].transform('mean')
            df_feat['supplier_fill_rate'] = supplier_fill_rate
        
        # Stockout impact
        if 'stockout_pct' in df_feat.columns:
            supplier_stockout = df_feat.groupby('supplier_id')['stockout_pct'].transform('mean')
            df_feat['supplier_stockout_impact'] = supplier_stockout
        
        # Fill NaN values
        numeric_cols = df_feat.select_dtypes(include=[np.number]).columns
        df_feat[numeric_cols] = df_feat[numeric_cols].fillna(df_feat[numeric_cols].median())
        
        return df_feat
        
    except Exception as e:
        st.error(f"Error in supplier segmentation feature engineering: {str(e)}")
        return df

@st.cache_data
def train_supplier_segmentation_model(X, n_clusters=3, algorithm='kmeans'):
    """Train supplier segmentation model"""
    try:
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
        from sklearn.metrics import silhouette_score
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = model.fit_predict(X_scaled)
        silhouette = silhouette_score(X_scaled, labels)
        
        metrics = {
            'Silhouette Score': silhouette,
            'Number of Clusters': n_clusters,
            'Algorithm': algorithm
        }
        
        return model, labels, metrics, scaler
        
    except Exception as e:
        st.error(f"Error training supplier segmentation model: {str(e)}")
        return None, None, None, None

if st.button("Train Supplier Segmentation Model", key="supplier_segment_btn"):
    if df is not None and not df.empty:
        with st.spinner("Performing feature engineering for supplier segmentation..."):
            df_supplier_feat = supplier_segmentation_feature_engineering(df)
            st.success("✅ Feature engineering completed")
        
        # Select features for supplier segmentation
        supplier_features = [
            'supplier_lead_mean', 'supplier_lead_std', 'supplier_lead_cv',
            'supplier_avg_rating', 'supplier_avg_cost', 'supplier_fill_rate',
            'supplier_stockout_impact'
        ]
        
        available_supplier_features = [f for f in supplier_features if f in df_supplier_feat.columns]
        
        if len(available_supplier_features) > 0:
            X_supplier = df_supplier_feat[available_supplier_features].fillna(0)
            
            # Get unique supplier-level data
            X_supplier_unique = X_supplier.groupby(df_supplier_feat['supplier_id']).mean()
            
            with st.spinner("Training supplier segmentation model..."):
                supplier_segment_model, supplier_labels, supplier_metrics, supplier_scaler = train_supplier_segmentation_model(
                    X_supplier_unique, n_clusters=3, algorithm='kmeans'
                )
                
                if supplier_segment_model is not None:
                    st.success("✅ Supplier segmentation model trained successfully")
                    
                    st.markdown("### Segmentation Performance Metrics")
                    st.json(supplier_metrics)
                    
                    st.session_state['supplier_segment_model'] = supplier_segment_model
                    st.session_state['supplier_segment_features'] = available_supplier_features
                    st.session_state['supplier_segment_scaler'] = supplier_scaler
        else:
            st.warning("⚠️ Insufficient features for supplier segmentation model")


# ================================================================
# LAYER 3: REDISTRIBUTION DECISION ENGINE (CORE)
# ================================================================

st.markdown(
    """
    <div style="
        background-color:#00D05E;
        padding:20px;
        border-radius:12px;
        color:white;
        font-size:20px;
        font-weight:600;
        margin-top:30px;
        margin-bottom:20px;
    ">
    🚀 Layer 3: Redistribution Decision Engine (CORE)
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:24px;
        border-radius:12px;
        color:white;
        font-size:16px;
        line-height:1.7;
        margin-bottom:25px;
    ">
    <b>This is the heart of SupplySync.AI</b><br>
    This layer implements optimization + ML hybrid models to automate inventory movement decisions.
    </div>
    """,
    unsafe_allow_html=True
)

# ================================================================
# MODEL 3.1: SUPPLY-DEMAND MATCHING MODEL
# ================================================================

st.markdown(
    """
    <div style="
        background-color:#163A70;
        padding:18px;
        border-radius:10px;
        color:white;
        font-size:18px;
        font-weight:600;
        margin-top:25px;
        margin-bottom:15px;
    ">
    🔹 ML Implementation: Supply-Demand Matching Model
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:20px;
        border-radius:12px;
        color:white;
        font-size:15px;
        line-height:1.6;
        margin-bottom:20px;
    ">
    <b>Type:</b> Optimization + ML hybrid<br>
    <b>Step 1 - Identify Candidates:</b> Overstock locations, Understock locations<br>
    <b>Step 2 - Matching Algorithm:</b> Linear Programming (LP), Network Flow Optimization, Hungarian Algorithm<br>
    <b>Objective:</b> Minimize transport cost, stockout penalty, expiry loss
    </div>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def supply_demand_matching_feature_engineering(df):
    """Feature engineering for supply-demand matching"""
    try:
        df_feat = df.copy()
        
        # Overstock identification
        if 'overstock_qty' in df_feat.columns:
            df_feat['is_overstock'] = (df_feat['overstock_qty'] > 0).astype(int)
            df_feat['overstock_severity'] = df_feat['overstock_qty'] / (df_feat['on_hand_qty'] + 1)
        
        # Understock identification
        if 'understock_qty' in df_feat.columns:
            df_feat['is_understock'] = (df_feat['understock_qty'] > 0).astype(int)
            df_feat['understock_severity'] = df_feat['understock_qty'] / (df_feat['on_hand_qty'] + 1)
        
        # Distance features
        if 'distance_km' in df_feat.columns:
            df_feat['transfer_distance'] = df_feat['distance_km']
        
        # Cost features
        if 'fuel_cost' in df_feat.columns:
            df_feat['transfer_cost'] = df_feat['fuel_cost']
        
        # Urgency features
        if 'stockout_pct' in df_feat.columns:
            df_feat['transfer_urgency'] = df_feat['stockout_pct']
        
        # Compatibility features
        if 'category' in df_feat.columns:
            df_feat['category_match'] = 1  # Will be computed during matching
        
        # Fill NaN values
        numeric_cols = df_feat.select_dtypes(include=[np.number]).columns
        df_feat[numeric_cols] = df_feat[numeric_cols].fillna(df_feat[numeric_cols].median())
        
        return df_feat
        
    except Exception as e:
        st.error(f"Error in supply-demand matching feature engineering: {str(e)}")
        return df

@st.cache_data
def optimize_supply_demand_matching(df, cost_weight=1.0, urgency_weight=1.5, expiry_weight=0.5):
    """Optimize supply-demand matching using linear programming"""
    try:
        from scipy.optimize import linear_sum_assignment
        
        # Identify overstock and understock locations
        overstock = df[df['is_overstock'] == 1].copy()
        understock = df[df['is_understock'] == 1].copy()
        
        if len(overstock) == 0 or len(understock) == 0:
            return None, {"message": "No overstock or understock locations found"}
        
        # Create cost matrix
        n_over = len(overstock)
        n_under = len(understock)
        cost_matrix = np.zeros((n_over, n_under))
        
        for i, (_, over_row) in enumerate(overstock.iterrows()):
            for j, (_, under_row) in enumerate(understock.iterrows()):
                # Calculate transfer cost
                distance = over_row.get('transfer_distance', 100)
                fuel_cost = over_row.get('transfer_cost', 50)
                urgency = under_row.get('transfer_urgency', 10)
                expiry_risk = over_row.get('expiry_risk', 0)
                
                total_cost = (
                    cost_weight * (distance + fuel_cost) +
                    urgency_weight * urgency +
                    expiry_weight * expiry_risk
                )
                cost_matrix[i, j] = total_cost
        
        # Apply Hungarian algorithm for optimal assignment
        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        
        # Create matching results
        matches = []
        total_cost = 0
        for i, j in zip(row_ind, col_ind):
            match = {
                'from_store': overstock.iloc[i]['store_id'],
                'to_store': understock.iloc[j]['store_id'],
                'from_product': overstock.iloc[i]['product_id'],
                'to_product': understock.iloc[j]['product_id'],
                'transfer_qty': min(overstock.iloc[i]['overstock_qty'], understock.iloc[j]['understock_qty']),
                'cost': cost_matrix[i, j]
            }
            matches.append(match)
            total_cost += match['cost']
        
        results_df = pd.DataFrame(matches)
        metrics = {
            'Total Matches': len(matches),
            'Total Cost': total_cost,
            'Average Cost per Match': total_cost / len(matches) if matches else 0
        }
        
        return results_df, metrics
        
    except Exception as e:
        st.error(f"Error in supply-demand matching optimization: {str(e)}")
        return None, None

if st.button("Run Supply-Demand Matching Optimization", key="supply_demand_btn"):
    if df is not None and not df.empty:
        with st.spinner("Performing feature engineering for supply-demand matching..."):
            df_matching_feat = supply_demand_matching_feature_engineering(df)
            st.success("✅ Feature engineering completed")
        
        with st.spinner("Running supply-demand matching optimization..."):
            matching_results, matching_metrics = optimize_supply_demand_matching(df_matching_feat)
            
            if matching_results is not None and not matching_results.empty:
                st.success("✅ Supply-demand matching optimization completed")
                
                st.markdown("### Optimization Metrics")
                st.json(matching_metrics)
                
                st.markdown("### Optimal Transfer Recommendations")
                render_html_table(matching_results.head(20), max_height=300)
                
                st.session_state['matching_results'] = matching_results
            else:
                st.info("ℹ️ No optimal matches found or insufficient data")
    else:
        st.warning("⚠️ Please load data first")

# ================================================================
# MODEL 3.2: TRANSFER QUANTITY PREDICTION
# ================================================================

st.markdown(
    """
    <div style="
        background-color:#163A70;
        padding:18px;
        border-radius:10px;
        color:white;
        font-size:18px;
        font-weight:600;
        margin-top:25px;
        margin-bottom:15px;
    ">
    🔹 ML Implementation: Transfer Quantity Prediction
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:20px;
        border-radius:12px;
        color:white;
        font-size:15px;
        line-height:1.6;
        margin-bottom:20px;
    ">
    <b>Type:</b> Regression<br>
    <b>Predicts:</b> "How much to transfer?"
    </div>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def transfer_quantity_feature_engineering(df):
    """Feature engineering for transfer quantity prediction"""
    try:
        df_feat = df.copy()
        
        # Overstock/understock balance
        if 'overstock_qty' in df_feat.columns and 'understock_qty' in df_feat.columns:
            df_feat['supply_demand_gap'] = df_feat['overstock_qty'] - df_feat['understock_qty']
        
        # Distance impact
        if 'distance_km' in df_feat.columns:
            df_feat['distance_impact'] = df_feat['distance_km']
        
        # Cost impact
        if 'fuel_cost' in df_feat.columns:
            df_feat['cost_impact'] = df_feat['fuel_cost']
        
        # Urgency impact
        if 'stockout_pct' in df_feat.columns:
            df_feat['urgency_impact'] = df_feat['stockout_pct']
        
        # Capacity constraints
        if 'on_hand_qty' in df_feat.columns:
            df_feat['available_capacity'] = df_feat['on_hand_qty']
        
        # Fill NaN values
        numeric_cols = df_feat.select_dtypes(include=[np.number]).columns
        df_feat[numeric_cols] = df_feat[numeric_cols].fillna(df_feat[numeric_cols].median())
        
        return df_feat
        
    except Exception as e:
        st.error(f"Error in transfer quantity feature engineering: {str(e)}")
        return df

@st.cache_data
def train_transfer_quantity_model(X_train, y_train):
    """Train transfer quantity prediction model"""
    try:
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
        from sklearn.ensemble import RandomForestRegressor
        
        X_train_split, X_val, y_train_split, y_val = train_test_split(
            X_train, y_train, test_size=0.2, random_state=42
        )
        
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(X_train_split, y_train_split)
        
        # Validation
        y_pred = model.predict(X_val)
        mae = mean_absolute_error(y_val, y_pred)
        rmse = np.sqrt(mean_squared_error(y_val, y_pred))
        r2 = r2_score(y_val, y_pred)
        
        metrics = {
            'MAE': mae,
            'RMSE': rmse,
            'R2': r2
        }
        
        return model, metrics
        
    except Exception as e:
        st.error(f"Error training transfer quantity model: {str(e)}")
        return None, None

if st.button("Train Transfer Quantity Prediction Model", key="transfer_qty_btn"):
    if df is not None and not df.empty:
        with st.spinner("Performing feature engineering for transfer quantity prediction..."):
            df_transfer_feat = transfer_quantity_feature_engineering(df)
            st.success("✅ Feature engineering completed")
        
        # Select features for transfer quantity prediction
        transfer_features = [
            'supply_demand_gap', 'distance_impact', 'cost_impact',
            'urgency_impact', 'available_capacity'
        ]
        
        available_transfer_features = [f for f in transfer_features if f in df_transfer_feat.columns]
        
        if len(available_transfer_features) > 0 and 'transfer_qty' in df_transfer_feat.columns:
            X_transfer = df_transfer_feat[available_transfer_features].fillna(0)
            y_transfer = df_transfer_feat['transfer_qty'].fillna(0)
            
            with st.spinner("Training transfer quantity prediction model..."):
                transfer_model, transfer_metrics = train_transfer_quantity_model(X_transfer, y_transfer)
                
                if transfer_model is not None:
                    st.success("✅ Transfer quantity prediction model trained successfully")
                    
                    st.markdown("### Model Performance Metrics")
                    st.json(transfer_metrics)
                    
                    st.session_state['transfer_quantity_model'] = transfer_model
                    st.session_state['transfer_quantity_features'] = available_transfer_features
        else:
            st.warning("⚠️ Insufficient features for transfer quantity prediction model")

# ================================================================
# MODEL 3.3: TRANSFER TIMING MODEL
# ================================================================

st.markdown(
    """
    <div style="
        background-color:#163A70;
        padding:18px;
        border-radius:10px;
        color:white;
        font-size:18px;
        font-weight:600;
        margin-top:25px;
        margin-bottom:15px;
    ">
    🔹 ML Implementation: Transfer Timing Model
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:20px;
        border-radius:12px;
        color:white;
        font-size:15px;
        line-height:1.6;
        margin-bottom:20px;
    ">
    <b>Type:</b> Time-to-event / forecasting<br>
    <b>Predicts:</b> "When to move inventory?"
    </div>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def transfer_timing_feature_engineering(df):
    """Feature engineering for transfer timing prediction"""
    try:
        df_feat = df.copy()
        
        # Urgency features
        if 'stockout_pct' in df_feat.columns:
            df_feat['stockout_urgency'] = df_feat['stockout_pct']
        
        # Lead time features
        if 'lead_time_days' in df_feat.columns:
            df_feat['lead_time'] = df_feat['lead_time_days']
        
        # Seasonal timing
        if 'month' in df_feat.columns:
            df_feat['is_peak_season'] = df_feat['month'].isin([11, 12, 1]).astype(int)
        
        # Day of week
        if 'day_of_week' in df_feat.columns:
            df_feat['is_weekend'] = df_feat['day_of_week'].isin([5, 6]).astype(int)
        
        # Fill NaN values
        numeric_cols = df_feat.select_dtypes(include=[np.number]).columns
        df_feat[numeric_cols] = df_feat[numeric_cols].fillna(df_feat[numeric_cols].median())
        
        return df_feat
        
    except Exception as e:
        st.error(f"Error in transfer timing feature engineering: {str(e)}")
        return df

@st.cache_data
def train_transfer_timing_model(X_train, y_train):
    """Train transfer timing model"""
    try:
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import mean_absolute_error, mean_squared_error
        from sklearn.ensemble import RandomForestRegressor
        
        X_train_split, X_val, y_train_split, y_val = train_test_split(
            X_train, y_train, test_size=0.2, random_state=42
        )
        
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(X_train_split, y_train_split)
        
        # Validation
        y_pred = model.predict(X_val)
        mae = mean_absolute_error(y_val, y_pred)
        rmse = np.sqrt(mean_squared_error(y_val, y_pred))
        
        metrics = {
            'MAE (days)': mae,
            'RMSE (days)': rmse
        }
        
        return model, metrics
        
    except Exception as e:
        st.error(f"Error training transfer timing model: {str(e)}")
        return None, None

if st.button("Train Transfer Timing Model", key="transfer_timing_btn"):
    if df is not None and not df.empty:
        with st.spinner("Performing feature engineering for transfer timing..."):
            df_timing_feat = transfer_timing_feature_engineering(df)
            st.success("✅ Feature engineering completed")
        
        # Select features for transfer timing prediction
        timing_features = [
            'stockout_urgency', 'lead_time', 'is_peak_season', 'is_weekend'
        ]
        
        available_timing_features = [f for f in timing_features if f in df_timing_feat.columns]
        
        if len(available_timing_features) > 0 and 'delivery_time_mins' in df_timing_feat.columns:
            X_timing = df_timing_feat[available_timing_features].fillna(0)
            y_timing = df_timing_feat['delivery_time_mins'].fillna(0) / 1440  # Convert to days
            
            with st.spinner("Training transfer timing model..."):
                timing_model, timing_metrics = train_transfer_timing_model(X_timing, y_timing)
                
                if timing_model is not None:
                    st.success("✅ Transfer timing model trained successfully")
                    
                    st.markdown("### Model Performance Metrics")
                    st.json(timing_metrics)
                    
                    st.session_state['transfer_timing_model'] = timing_model
                    st.session_state['transfer_timing_features'] = available_timing_features
        else:
            st.warning("⚠️ Insufficient features for transfer timing model")


# ================================================================
# LAYER 4: LOGISTICS & ROUTE OPTIMIZATION LAYER
# ================================================================

st.markdown(
    """
    <div style="
        background-color:#00D05E;
        padding:20px;
        border-radius:12px;
        color:white;
        font-size:20px;
        font-weight:600;
        margin-top:30px;
        margin-bottom:20px;
    ">
    🚀 Layer 4: Logistics & Route Optimization Layer
    </div>
    """,
    unsafe_allow_html=True
)

# ================================================================
# MODEL 4.1: ROUTE OPTIMIZATION ENGINE
# ================================================================

st.markdown(
    """
    <div style="
        background-color:#163A70;
        padding:18px;
        border-radius:10px;
        color:white;
        font-size:18px;
        font-weight:600;
        margin-top:25px;
        margin-bottom:15px;
    ">
    🔹 ML Implementation: Route Optimization Engine
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:20px;
        border-radius:12px;
        color:white;
        font-size:15px;
        line-height:1.6;
        margin-bottom:20px;
    ">
    <b>Type:</b> Optimization (Graph-based)<br>
    <b>Algorithms:</b> Dijkstra / A*, Vehicle Routing Problem (VRP)<br>
    <b>Inputs:</b> Transport Route Analysis, Logistics Analysis<br>
    <b>Output:</b> Optimal route + cost
    </div>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def route_optimization_feature_engineering(df):
    """Feature engineering for route optimization"""
    try:
        df_feat = df.copy()
        
        # Distance features
        if 'distance_km' in df_feat.columns:
            df_feat['route_distance'] = df_feat['distance_km']
        
        # Cost features
        if 'fuel_cost' in df_feat.columns:
            df_feat['route_cost'] = df_feat['fuel_cost']
        
        # Efficiency features
        if 'route_efficiency_score' in df_feat.columns:
            df_feat['efficiency'] = df_feat['route_efficiency_score']
        
        # Delivery time features
        if 'delivery_time_mins' in df_feat.columns:
            df_feat['delivery_time'] = df_feat['delivery_time_mins']
        
        # Fill NaN values
        numeric_cols = df_feat.select_dtypes(include=[np.number]).columns
        df_feat[numeric_cols] = df_feat[numeric_cols].fillna(df_feat[numeric_cols].median())
        
        return df_feat
        
    except Exception as e:
        st.error(f"Error in route optimization feature engineering: {str(e)}")
        return df

@st.cache_data
def optimize_routes(df, max_stops=10):
    """Optimize delivery routes using graph-based algorithms"""
    try:
        import networkx as nx
        
        # Create graph from route data
        G = nx.Graph()
        
        # Add nodes (stores/locations)
        if 'store_id' in df.columns:
            unique_stores = df['store_id'].unique()
            for store in unique_stores:
                G.add_node(store)
        
        # Add edges with weights (distance/cost)
        if 'route_id' in df.columns and 'distance_km' in df.columns:
            for _, row in df.iterrows():
                if 'from_store' in df.columns and 'to_store' in df.columns:
                    weight = row.get('distance_km', row.get('fuel_cost', 1))
                    G.add_edge(row['from_store'], row['to_store'], weight=weight)
        
        # Find optimal routes using Dijkstra
        optimal_routes = []
        total_cost = 0
        
        if len(G.nodes) > 1:
            nodes = list(G.nodes)
            for i in range(min(len(nodes), max_stops)):
                for j in range(i+1, min(len(nodes), max_stops)):
                    try:
                        path = nx.shortest_path(G, source=nodes[i], target=nodes[j], weight='weight')
                        cost = nx.shortest_path_length(G, source=nodes[i], target=nodes[j], weight='weight')
                        optimal_routes.append({
                            'route': ' -> '.join(path),
                            'cost': cost,
                            'stops': len(path)
                        })
                        total_cost += cost
                    except:
                        pass
        
        results_df = pd.DataFrame(optimal_routes)
        metrics = {
            'Total Routes': len(optimal_routes),
            'Total Cost': total_cost,
            'Average Cost per Route': total_cost / len(optimal_routes) if optimal_routes else 0
        }
        
        return results_df, metrics
        
    except Exception as e:
        st.error(f"Error in route optimization: {str(e)}")
        return None, None

if st.button("Run Route Optimization", key="route_opt_btn"):
    if df is not None and not df.empty:
        with st.spinner("Performing feature engineering for route optimization..."):
            df_route_feat = route_optimization_feature_engineering(df)
            st.success("✅ Feature engineering completed")
        
        with st.spinner("Running route optimization..."):
            route_results, route_metrics = optimize_routes(df_route_feat)
            
            if route_results is not None and not route_results.empty:
                st.success("✅ Route optimization completed")
                
                st.markdown("### Optimization Metrics")
                st.json(route_metrics)
                
                st.markdown("### Optimal Routes")
                render_html_table(route_results.head(20), max_height=300)
                
                st.session_state['route_results'] = route_results
            else:
                st.info("ℹ️ No optimal routes found or insufficient data")
    else:
        st.warning("⚠️ Please load data first")

# ================================================================
# MODEL 4.2: DELIVERY TIME PREDICTION
# ================================================================

st.markdown(
    """
    <div style="
        background-color:#163A70;
        padding:18px;
        border-radius:10px;
        color:white;
        font-size:18px;
        font-weight:600;
        margin-top:25px;
        margin-bottom:15px;
    ">
    🔹 ML Implementation: Delivery Time Prediction
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:20px;
        border-radius:12px;
        color:white;
        font-size:15px;
        line-height:1.6;
        margin-bottom:20px;
    ">
    <b>Type:</b> Regression<br>
    <b>Predicts:</b> Delivery ETA
    </div>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def delivery_time_feature_engineering(df):
    """Feature engineering for delivery time prediction"""
    try:
        df_feat = df.copy()
        
        # Distance features
        if 'distance_km' in df_feat.columns:
            df_feat['distance'] = df_feat['distance_km']
        
        # Route efficiency
        if 'route_efficiency_score' in df_feat.columns:
            df_feat['efficiency'] = df_feat['route_efficiency_score']
        
        # Vehicle features
        if 'vehicle_id' in df_feat.columns:
            vehicle_avg_time = df_feat.groupby('vehicle_id')['delivery_time_mins'].transform('mean')
            df_feat['vehicle_avg_delivery'] = vehicle_avg_time
        
        # Time features
        if 'is_holiday' in df_feat.columns:
            df_feat['holiday_delay'] = df_feat['is_holiday'].astype(int)
        
        # Fill NaN values
        numeric_cols = df_feat.select_dtypes(include=[np.number]).columns
        df_feat[numeric_cols] = df_feat[numeric_cols].fillna(df_feat[numeric_cols].median())
        
        return df_feat
        
    except Exception as e:
        st.error(f"Error in delivery time feature engineering: {str(e)}")
        return df

@st.cache_data
def train_delivery_time_model(X_train, y_train):
    """Train delivery time prediction model"""
    try:
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
        from sklearn.ensemble import RandomForestRegressor
        
        X_train_split, X_val, y_train_split, y_val = train_test_split(
            X_train, y_train, test_size=0.2, random_state=42
        )
        
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(X_train_split, y_train_split)
        
        # Validation
        y_pred = model.predict(X_val)
        mae = mean_absolute_error(y_val, y_pred)
        rmse = np.sqrt(mean_squared_error(y_val, y_pred))
        r2 = r2_score(y_val, y_pred)
        
        metrics = {
            'MAE (mins)': mae,
            'RMSE (mins)': rmse,
            'R2': r2
        }
        
        return model, metrics
        
    except Exception as e:
        st.error(f"Error training delivery time model: {str(e)}")
        return None, None

if st.button("Train Delivery Time Prediction Model", key="delivery_time_btn"):
    if df is not None and not df.empty:
        with st.spinner("Performing feature engineering for delivery time prediction..."):
            df_delivery_feat = delivery_time_feature_engineering(df)
            st.success("✅ Feature engineering completed")
        
        # Select features for delivery time prediction
        delivery_features = [
            'distance', 'efficiency', 'vehicle_avg_delivery', 'holiday_delay'
        ]
        
        available_delivery_features = [f for f in delivery_features if f in df_delivery_feat.columns]
        
        if len(available_delivery_features) > 0 and 'delivery_time_mins' in df_delivery_feat.columns:
            X_delivery = df_delivery_feat[available_delivery_features].fillna(0)
            y_delivery = df_delivery_feat['delivery_time_mins'].fillna(0)
            
            with st.spinner("Training delivery time prediction model..."):
                delivery_model, delivery_metrics = train_delivery_time_model(X_delivery, y_delivery)
                
                if delivery_model is not None:
                    st.success("✅ Delivery time prediction model trained successfully")
                    
                    st.markdown("### Model Performance Metrics")
                    st.json(delivery_metrics)
                    
                    st.session_state['delivery_time_model'] = delivery_model
                    st.session_state['delivery_time_features'] = available_delivery_features
        else:
            st.warning("⚠️ Insufficient features for delivery time prediction model")

# ================================================================
# MODEL 4.3: TRANSPORT COST PREDICTION
# ================================================================

st.markdown(
    """
    <div style="
        background-color:#163A70;
        padding:18px;
        border-radius:10px;
        color:white;
        font-size:18px;
        font-weight:600;
        margin-top:25px;
        margin-bottom:15px;
    ">
    🔹 ML Implementation: Transport Cost Prediction
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:20px;
        border-radius:12px;
        color:white;
        font-size:15px;
        line-height:1.6;
        margin-bottom:20px;
    ">
    <b>Predicts:</b> Fuel, distance, load-based cost prediction
    </div>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def transport_cost_feature_engineering(df):
    """Feature engineering for transport cost prediction"""
    try:
        df_feat = df.copy()
        
        # Distance features
        if 'distance_km' in df_feat.columns:
            df_feat['distance'] = df_feat['distance_km']
        
        # Load features
        if 'on_hand_qty' in df_feat.columns:
            df_feat['load_size'] = df_feat['on_hand_qty']
        
        # Vehicle features
        if 'vehicle_id' in df_feat.columns:
            vehicle_avg_cost = df_feat.groupby('vehicle_id')['fuel_cost'].transform('mean')
            df_feat['vehicle_avg_cost'] = vehicle_avg_cost
        
        # Route features
        if 'route_efficiency_score' in df_feat.columns:
            df_feat['route_efficiency'] = df_feat['route_efficiency_score']
        
        # Fill NaN values
        numeric_cols = df_feat.select_dtypes(include=[np.number]).columns
        df_feat[numeric_cols] = df_feat[numeric_cols].fillna(df_feat[numeric_cols].median())
        
        return df_feat
        
    except Exception as e:
        st.error(f"Error in transport cost feature engineering: {str(e)}")
        return df

@st.cache_data
def train_transport_cost_model(X_train, y_train):
    """Train transport cost prediction model"""
    try:
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
        from sklearn.ensemble import RandomForestRegressor
        
        X_train_split, X_val, y_train_split, y_val = train_test_split(
            X_train, y_train, test_size=0.2, random_state=42
        )
        
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(X_train_split, y_train_split)
        
        # Validation
        y_pred = model.predict(X_val)
        mae = mean_absolute_error(y_val, y_pred)
        rmse = np.sqrt(mean_squared_error(y_val, y_pred))
        r2 = r2_score(y_val, y_pred)
        
        metrics = {
            'MAE': mae,
            'RMSE': rmse,
            'R2': r2
        }
        
        return model, metrics
        
    except Exception as e:
        st.error(f"Error training transport cost model: {str(e)}")
        return None, None

if st.button("Train Transport Cost Prediction Model", key="transport_cost_btn"):
    if df is not None and not df.empty:
        with st.spinner("Performing feature engineering for transport cost prediction..."):
            df_cost_feat = transport_cost_feature_engineering(df)
            st.success("✅ Feature engineering completed")
        
        # Select features for transport cost prediction
        cost_features = [
            'distance', 'load_size', 'vehicle_avg_cost', 'route_efficiency'
        ]
        
        available_cost_features = [f for f in cost_features if f in df_cost_feat.columns]
        
        if len(available_cost_features) > 0 and 'fuel_cost' in df_cost_feat.columns:
            X_cost = df_cost_feat[available_cost_features].fillna(0)
            y_cost = df_cost_feat['fuel_cost'].fillna(0)
            
            with st.spinner("Training transport cost prediction model..."):
                cost_model, cost_metrics = train_transport_cost_model(X_cost, y_cost)
                
                if cost_model is not None:
                    st.success("✅ Transport cost prediction model trained successfully")
                    
                    st.markdown("### Model Performance Metrics")
                    st.json(cost_metrics)
                    
                    st.session_state['transport_cost_model'] = cost_model
                    st.session_state['transport_cost_features'] = available_cost_features
        else:
            st.warning("⚠️ Insufficient features for transport cost prediction model")


# ================================================================
# LAYER 5: INVENTORY POLICY OPTIMIZATION
# ================================================================

st.markdown(
    """
    <div style="
        background-color:#00D05E;
        padding:20px;
        border-radius:12px;
        color:white;
        font-size:20px;
        font-weight:600;
        margin-top:30px;
        margin-bottom:20px;
    ">
    🚀 Layer 5: Inventory Policy Optimization
    </div>
    """,
    unsafe_allow_html=True
)

# ================================================================
# MODEL 5.1: DYNAMIC REORDER POINT MODEL
# ================================================================

st.markdown(
    """
    <div style="
        background-color:#163A70;
        padding:18px;
        border-radius:10px;
        color:white;
        font-size:18px;
        font-weight:600;
        margin-top:25px;
        margin-bottom:15px;
    ">
    🔹 ML Implementation: Dynamic Reorder Point Model
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:20px;
        border-radius:12px;
        color:white;
        font-size:15px;
        line-height:1.6;
        margin-bottom:20px;
    ">
    <b>Type:</b> Probabilistic / Simulation<br>
    <b>Uses:</b> Demand forecast, Lead time uncertainty<br>
    <b>Output:</b> Optimal reorder point per SKU-store
    </div>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def reorder_point_feature_engineering(df):
    """Feature engineering for dynamic reorder point model"""
    try:
        df_feat = df.copy()
        
        # Demand features
        if 'demand_index' in df_feat.columns:
            df_feat['demand_rate'] = df_feat['demand_index']
        
        # Lead time features
        if 'lead_time_days' in df_feat.columns:
            df_feat['lead_time'] = df_feat['lead_time_days']
            lead_time_std = df_feat.groupby('product_id')['lead_time_days'].transform('std')
            df_feat['lead_time_uncertainty'] = lead_time_std.fillna(0)
        
        # Service level features
        if 'fill_rate_pct' in df_feat.columns:
            df_feat['service_level'] = df_feat['fill_rate_pct'] / 100
        
        # Demand variability
        if 'demand_index' in df_feat.columns:
            demand_std = df_feat.groupby('product_id')['demand_index'].transform('std')
            df_feat['demand_variability'] = demand_std.fillna(0)
        
        # Fill NaN values
        numeric_cols = df_feat.select_dtypes(include=[np.number]).columns
        df_feat[numeric_cols] = df_feat[numeric_cols].fillna(df_feat[numeric_cols].median())
        
        return df_feat
        
    except Exception as e:
        st.error(f"Error in reorder point feature engineering: {str(e)}")
        return df

@st.cache_data
def calculate_dynamic_reorder_point(df, service_level=0.95):
    """Calculate dynamic reorder points using probabilistic model"""
    try:
        from scipy.stats import norm
        
        results = []
        
        # Group by product and store
        if 'product_id' in df.columns and 'store_id' in df.columns:
            grouped = df.groupby(['product_id', 'store_id'])
            
            for (product, store), group in grouped:
                demand_rate = group['demand_rate'].mean() if 'demand_rate' in group.columns else 10
                lead_time = group['lead_time'].mean() if 'lead_time' in group.columns else 7
                lead_time_uncertainty = group['lead_time_uncertainty'].mean() if 'lead_time_uncertainty' in group.columns else 1
                demand_variability = group['demand_variability'].mean() if 'demand_variability' in group.columns else 2
                
                # Calculate safety stock using service level
                z_score = norm.ppf(service_level)
                safety_stock = z_score * np.sqrt((lead_time * demand_variability**2) + (demand_rate**2 * lead_time_uncertainty**2))
                
                # Calculate reorder point
                reorder_point = (demand_rate * lead_time) + safety_stock
                
                results.append({
                    'product_id': product,
                    'store_id': store,
                    'demand_rate': demand_rate,
                    'lead_time': lead_time,
                    'safety_stock': safety_stock,
                    'reorder_point': reorder_point,
                    'service_level': service_level
                })
        
        results_df = pd.DataFrame(results)
        metrics = {
            'Total SKU-Store Combinations': len(results_df),
            'Average Reorder Point': results_df['reorder_point'].mean() if not results_df.empty else 0,
            'Average Safety Stock': results_df['safety_stock'].mean() if not results_df.empty else 0
        }
        
        return results_df, metrics
        
    except Exception as e:
        st.error(f"Error calculating dynamic reorder points: {str(e)}")
        return None, None

if st.button("Calculate Dynamic Reorder Points", key="reorder_point_btn"):
    if df is not None and not df.empty:
        with st.spinner("Performing feature engineering for reorder point calculation..."):
            df_reorder_feat = reorder_point_feature_engineering(df)
            st.success("✅ Feature engineering completed")
        
        service_level = st.slider("Target Service Level", 0.80, 0.99, 0.95, 0.01)
        
        with st.spinner("Calculating dynamic reorder points..."):
            reorder_results, reorder_metrics = calculate_dynamic_reorder_point(df_reorder_feat, service_level)
            
            if reorder_results is not None and not reorder_results.empty:
                st.success("✅ Dynamic reorder points calculated successfully")
                
                st.markdown("### Reorder Point Metrics")
                st.json(reorder_metrics)
                
                st.markdown("### Reorder Point Recommendations")
                render_html_table(reorder_results.head(20), max_height=300)
                
                st.session_state['reorder_point_results'] = reorder_results
            else:
                st.info("ℹ️ Could not calculate reorder points")
    else:
        st.warning("⚠️ Please load data first")

# ================================================================
# MODEL 5.2: SAFETY STOCK OPTIMIZATION
# ================================================================

st.markdown(
    """
    <div style="
        background-color:#163A70;
        padding:18px;
        border-radius:10px;
        color:white;
        font-size:18px;
        font-weight:600;
        margin-top:25px;
        margin-bottom:15px;
    ">
    🔹 ML Implementation: Safety Stock Optimization
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:20px;
        border-radius:12px;
        color:white;
        font-size:15px;
        line-height:1.6;
        margin-bottom:20px;
    ">
    <b>Based on:</b> Demand variability, Service level targets
    </div>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def safety_stock_feature_engineering(df):
    """Feature engineering for safety stock optimization"""
    try:
        df_feat = df.copy()
        
        # Demand variability
        if 'demand_index' in df_feat.columns:
            demand_std = df_feat.groupby('product_id')['demand_index'].transform('std')
            demand_mean = df_feat.groupby('product_id')['demand_index'].transform('mean')
            df_feat['demand_cv'] = demand_std / (demand_mean + 1)
        
        # Lead time variability
        if 'lead_time_days' in df_feat.columns:
            lead_std = df_feat.groupby('product_id')['lead_time_days'].transform('std')
            lead_mean = df_feat.groupby('product_id')['lead_time_days'].transform('mean')
            df_feat['lead_cv'] = lead_std / (lead_mean + 1)
        
        # Fill rate target
        if 'fill_rate_pct' in df_feat.columns:
            df_feat['target_fill_rate'] = df_feat['fill_rate_pct']
        
        # Fill NaN values
        numeric_cols = df_feat.select_dtypes(include=[np.number]).columns
        df_feat[numeric_cols] = df_feat[numeric_cols].fillna(df_feat[numeric_cols].median())
        
        return df_feat
        
    except Exception as e:
        st.error(f"Error in safety stock feature engineering: {str(e)}")
        return df

@st.cache_data
def optimize_safety_stock(df, service_level=0.95):
    """Optimize safety stock levels"""
    try:
        from scipy.stats import norm
        
        results = []
        
        # Group by product
        if 'product_id' in df.columns:
            grouped = df.groupby('product_id')
            
            for product, group in grouped:
                demand_cv = group['demand_cv'].mean() if 'demand_cv' in group.columns else 0.2
                lead_cv = group['lead_cv'].mean() if 'lead_cv' in group.columns else 0.1
                avg_demand = group['demand_index'].mean() if 'demand_index' in group.columns else 10
                avg_lead = group['lead_time_days'].mean() if 'lead_time_days' in group.columns else 7
                
                # Calculate optimal safety stock
                z_score = norm.ppf(service_level)
                safety_stock = z_score * avg_demand * np.sqrt(demand_cv**2 + lead_cv**2)
                
                results.append({
                    'product_id': product,
                    'avg_demand': avg_demand,
                    'avg_lead_time': avg_lead,
                    'demand_cv': demand_cv,
                    'lead_cv': lead_cv,
                    'optimal_safety_stock': safety_stock,
                    'service_level': service_level
                })
        
        results_df = pd.DataFrame(results)
        metrics = {
            'Total Products': len(results_df),
            'Average Safety Stock': results_df['optimal_safety_stock'].mean() if not results_df.empty else 0
        }
        
        return results_df, metrics
        
    except Exception as e:
        st.error(f"Error optimizing safety stock: {str(e)}")
        return None, None

if st.button("Optimize Safety Stock Levels", key="safety_stock_btn"):
    if df is not None and not df.empty:
        with st.spinner("Performing feature engineering for safety stock optimization..."):
            df_safety_feat = safety_stock_feature_engineering(df)
            st.success("✅ Feature engineering completed")
        
        service_level = st.slider("Target Service Level", 0.80, 0.99, 0.95, 0.01, key="safety_sl")
        
        with st.spinner("Optimizing safety stock levels..."):
            safety_results, safety_metrics = optimize_safety_stock(df_safety_feat, service_level)
            
            if safety_results is not None and not safety_results.empty:
                st.success("✅ Safety stock optimization completed")
                
                st.markdown("### Safety Stock Metrics")
                st.json(safety_metrics)
                
                st.markdown("### Safety Stock Recommendations")
                render_html_table(safety_results.head(20), max_height=300)
                
                st.session_state['safety_stock_results'] = safety_results
            else:
                st.info("ℹ️ Could not optimize safety stock")
    else:
        st.warning("⚠️ Please load data first")


# ================================================================
# LAYER 6: WAREHOUSE INTELLIGENCE LAYER
# ================================================================

st.markdown(
    """
    <div style="
        background-color:#00D05E;
        padding:20px;
        border-radius:12px;
        color:white;
        font-size:20px;
        font-weight:600;
        margin-top:30px;
        margin-bottom:20px;
    ">
    🚀 Layer 6: Warehouse Intelligence Layer
    </div>
    """,
    unsafe_allow_html=True
)

# ================================================================
# MODEL 6.1: WAREHOUSE LOAD PREDICTION
# ================================================================

st.markdown(
    """
    <div style="
        background-color:#163A70;
        padding:18px;
        border-radius:10px;
        color:white;
        font-size:18px;
        font-weight:600;
        margin-top:25px;
        margin-bottom:15px;
    ">
    🔹 ML Implementation: Warehouse Load Prediction
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:20px;
        border-radius:12px;
        color:white;
        font-size:15px;
        line-height:1.6;
        margin-bottom:20px;
    ">
    <b>Predicts:</b> Incoming + outgoing load
    </div>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def warehouse_load_feature_engineering(df):
    """Feature engineering for warehouse load prediction"""
    try:
        df_feat = df.copy()
        
        # Incoming load features
        if 'on_hand_qty' in df_feat.columns:
            df_feat['incoming_load'] = df_feat['on_hand_qty']
        
        # Outgoing load features
        if 'demand_index' in df_feat.columns:
            df_feat['outgoing_load'] = df_feat['demand_index']
        
        # Seasonal features
        if 'month' in df_feat.columns:
            df_feat['is_peak_month'] = df_feat['month'].isin([11, 12, 1]).astype(int)
        
        # Fill NaN values
        numeric_cols = df_feat.select_dtypes(include=[np.number]).columns
        df_feat[numeric_cols] = df_feat[numeric_cols].fillna(df_feat[numeric_cols].median())
        
        return df_feat
        
    except Exception as e:
        st.error(f"Error in warehouse load feature engineering: {str(e)}")
        return df

@st.cache_data
def train_warehouse_load_model(X_train, y_train):
    """Train warehouse load prediction model"""
    try:
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import mean_absolute_error, mean_squared_error
        from sklearn.ensemble import RandomForestRegressor
        
        X_train_split, X_val, y_train_split, y_val = train_test_split(
            X_train, y_train, test_size=0.2, random_state=42
        )
        
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(X_train_split, y_train_split)
        
        # Validation
        y_pred = model.predict(X_val)
        mae = mean_absolute_error(y_val, y_pred)
        rmse = np.sqrt(mean_squared_error(y_val, y_pred))
        
        metrics = {
            'MAE': mae,
            'RMSE': rmse
        }
        
        return model, metrics
        
    except Exception as e:
        st.error(f"Error training warehouse load model: {str(e)}")
        return None, None

if st.button("Train Warehouse Load Prediction Model", key="warehouse_load_btn"):
    if df is not None and not df.empty:
        with st.spinner("Performing feature engineering for warehouse load prediction..."):
            df_warehouse_feat = warehouse_load_feature_engineering(df)
            st.success("✅ Feature engineering completed")
        
        # Select features for warehouse load prediction
        warehouse_features = [
            'incoming_load', 'outgoing_load', 'is_peak_month'
        ]
        
        available_warehouse_features = [f for f in warehouse_features if f in df_warehouse_feat.columns]
        
        if len(available_warehouse_features) > 0 and 'on_hand_qty' in df_warehouse_feat.columns:
            X_warehouse = df_warehouse_feat[available_warehouse_features].fillna(0)
            y_warehouse = df_warehouse_feat['on_hand_qty'].fillna(0)
            
            with st.spinner("Training warehouse load prediction model..."):
                warehouse_model, warehouse_metrics = train_warehouse_load_model(X_warehouse, y_warehouse)
                
                if warehouse_model is not None:
                    st.success("✅ Warehouse load prediction model trained successfully")
                    
                    st.markdown("### Model Performance Metrics")
                    st.json(warehouse_metrics)
                    
                    st.session_state['warehouse_load_model'] = warehouse_model
                    st.session_state['warehouse_load_features'] = available_warehouse_features
        else:
            st.warning("⚠️ Insufficient features for warehouse load prediction model")

# ================================================================
# MODEL 6.2: STORAGE OPTIMIZATION MODEL
# ================================================================

st.markdown(
    """
    <div style="
        background-color:#163A70;
        padding:18px;
        border-radius:10px;
        color:white;
        font-size:18px;
        font-weight:600;
        margin-top:25px;
        margin-bottom:15px;
    ">
    🔹 ML Implementation: Storage Optimization Model
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:20px;
        border-radius:12px;
        color:white;
        font-size:15px;
        line-height:1.6;
        margin-bottom:20px;
    ">
    <b>Method:</b> Slotting optimization using clustering + heuristics
    </div>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def storage_optimization_feature_engineering(df):
    """Feature engineering for storage optimization"""
    try:
        df_feat = df.copy()
        
        # Product size features
        if 'stock_value' in df_feat.columns:
            df_feat['product_value'] = df_feat['stock_value']
        
        # Demand frequency
        if 'demand_index' in df_feat.columns:
            df_feat['demand_frequency'] = df_feat['demand_index']
        
        # Turnover features
        if 'inventory_turnover' in df_feat.columns:
            df_feat['turnover'] = df_feat['inventory_turnover']
        
        # Fill NaN values
        numeric_cols = df_feat.select_dtypes(include=[np.number]).columns
        df_feat[numeric_cols] = df_feat[numeric_cols].fillna(df_feat[numeric_cols].median())
        
        return df_feat
        
    except Exception as e:
        st.error(f"Error in storage optimization feature engineering: {str(e)}")
        return df

@st.cache_data
def optimize_storage_layout(df, n_zones=5):
    """Optimize storage layout using clustering"""
    try:
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
        
        # Select features for clustering
        storage_features = ['product_value', 'demand_frequency', 'turnover']
        available_features = [f for f in storage_features if f in df.columns]
        
        if len(available_features) < 2:
            return None, {"message": "Insufficient features for storage optimization"}
        
        # Get unique product data
        product_data = df.groupby('product_id')[available_features].mean()
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(product_data)
        
        # Cluster products
        kmeans = KMeans(n_clusters=n_zones, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X_scaled)
        
        # Create storage zone assignments
        product_data['storage_zone'] = clusters
        product_data['storage_zone'] = product_data['storage_zone'].apply(lambda x: f"Zone_{x+1}")
        
        metrics = {
            'Total Products': len(product_data),
            'Number of Storage Zones': n_zones,
            'Algorithm': 'KMeans Clustering'
        }
        
        return product_data.reset_index(), metrics
        
    except Exception as e:
        st.error(f"Error optimizing storage layout: {str(e)}")
        return None, None

if st.button("Optimize Storage Layout", key="storage_opt_btn"):
    if df is not None and not df.empty:
        with st.spinner("Performing feature engineering for storage optimization..."):
            df_storage_feat = storage_optimization_feature_engineering(df)
            st.success("✅ Feature engineering completed")
        
        n_zones = st.slider("Number of Storage Zones", 3, 10, 5)
        
        with st.spinner("Optimizing storage layout..."):
            storage_results, storage_metrics = optimize_storage_layout(df_storage_feat, n_zones)
            
            if storage_results is not None and not storage_results.empty:
                st.success("✅ Storage layout optimization completed")
                
                st.markdown("### Storage Optimization Metrics")
                st.json(storage_metrics)
                
                st.markdown("### Storage Zone Assignments")
                render_html_table(storage_results.head(20), max_height=300)
                
                st.session_state['storage_results'] = storage_results
            else:
                st.info("ℹ️ Could not optimize storage layout")
    else:
        st.warning("⚠️ Please load data first")


# ================================================================
# LAYER 7: SUPPLIER INTELLIGENCE MODELS
# ================================================================

st.markdown(
    """
    <div style="
        background-color:#00D05E;
        padding:20px;
        border-radius:12px;
        color:white;
        font-size:20px;
        font-weight:600;
        margin-top:30px;
        margin-bottom:20px;
    ">
    🚀 Layer 7: Supplier Intelligence Models
    </div>
    """,
    unsafe_allow_html=True
)

# ================================================================
# MODEL 7.1: LEAD TIME PREDICTION
# ================================================================

st.markdown(
    """
    <div style="
        background-color:#163A70;
        padding:18px;
        border-radius:10px;
        color:white;
        font-size:18px;
        font-weight:600;
        margin-top:25px;
        margin-bottom:15px;
    ">
    🔹 ML Implementation: Lead Time Prediction
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:20px;
        border-radius:12px;
        color:white;
        font-size:15px;
        line-height:1.6;
        margin-bottom:20px;
    ">
    <b>Type:</b> Regression model
    </div>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def lead_time_feature_engineering(df):
    """Feature engineering for lead time prediction"""
    try:
        df_feat = df.copy()
        
        # Supplier features
        if 'supplier_rating' in df_feat.columns:
            supplier_rating = df_feat.groupby('supplier_id')['supplier_rating'].transform('mean')
            df_feat['supplier_avg_rating'] = supplier_rating
        
        # Distance features
        if 'distance_km' in df_feat.columns:
            df_feat['distance'] = df_feat['distance_km']
        
        # Order size features
        if 'on_hand_qty' in df_feat.columns:
            df_feat['order_size'] = df_feat['on_hand_qty']
        
        # Seasonal features
        if 'month' in df_feat.columns:
            df_feat['is_peak_season'] = df_feat['month'].isin([11, 12, 1]).astype(int)
        
        # Fill NaN values
        numeric_cols = df_feat.select_dtypes(include=[np.number]).columns
        df_feat[numeric_cols] = df_feat[numeric_cols].fillna(df_feat[numeric_cols].median())
        
        return df_feat
        
    except Exception as e:
        st.error(f"Error in lead time feature engineering: {str(e)}")
        return df

@st.cache_data
def train_lead_time_model(X_train, y_train):
    """Train lead time prediction model"""
    try:
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import mean_absolute_error, mean_squared_error
        from sklearn.ensemble import RandomForestRegressor
        
        X_train_split, X_val, y_train_split, y_val = train_test_split(
            X_train, y_train, test_size=0.2, random_state=42
        )
        
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(X_train_split, y_train_split)
        
        # Validation
        y_pred = model.predict(X_val)
        mae = mean_absolute_error(y_val, y_pred)
        rmse = np.sqrt(mean_squared_error(y_val, y_pred))
        
        metrics = {
            'MAE (days)': mae,
            'RMSE (days)': rmse
        }
        
        return model, metrics
        
    except Exception as e:
        st.error(f"Error training lead time model: {str(e)}")
        return None, None

if st.button("Train Lead Time Prediction Model", key="lead_time_btn"):
    if df is not None and not df.empty:
        with st.spinner("Performing feature engineering for lead time prediction..."):
            df_lead_feat = lead_time_feature_engineering(df)
            st.success("✅ Feature engineering completed")
        
        # Select features for lead time prediction
        lead_features = [
            'supplier_avg_rating', 'distance', 'order_size', 'is_peak_season'
        ]
        
        available_lead_features = [f for f in lead_features if f in df_lead_feat.columns]
        
        if len(available_lead_features) > 0 and 'lead_time_days' in df_lead_feat.columns:
            X_lead = df_lead_feat[available_lead_features].fillna(0)
            y_lead = df_lead_feat['lead_time_days'].fillna(0)
            
            with st.spinner("Training lead time prediction model..."):
                lead_model, lead_metrics = train_lead_time_model(X_lead, y_lead)
                
                if lead_model is not None:
                    st.success("✅ Lead time prediction model trained successfully")
                    
                    st.markdown("### Model Performance Metrics")
                    st.json(lead_metrics)
                    
                    st.session_state['lead_time_model'] = lead_model
                    st.session_state['lead_time_features'] = available_lead_features
        else:
            st.warning("⚠️ Insufficient features for lead time prediction model")

# ================================================================
# MODEL 7.2: SUPPLIER RISK SCORING
# ================================================================

st.markdown(
    """
    <div style="
        background-color:#163A70;
        padding:18px;
        border-radius:10px;
        color:white;
        font-size:18px;
        font-weight:600;
        margin-top:25px;
        margin-bottom:15px;
    ">
    🔹 ML Implementation: Supplier Risk Scoring
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:20px;
        border-radius:12px;
        color:white;
        font-size:15px;
        line-height:1.6;
        margin-bottom:20px;
    ">
    <b>Type:</b> Classification model<br>
    <b>Predicts:</b> On-time vs delayed supplier
    </div>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def supplier_risk_feature_engineering(df):
    """Feature engineering for supplier risk scoring"""
    try:
        df_feat = df.copy()
        
        # Lead time variability
        if 'lead_time_days' in df_feat.columns:
            lead_std = df_feat.groupby('supplier_id')['lead_time_days'].transform('std')
            lead_mean = df_feat.groupby('supplier_id')['lead_time_days'].transform('mean')
            df_feat['lead_cv'] = lead_std / (lead_mean + 1)
        
        # Rating features
        if 'supplier_rating' in df_feat.columns:
            df_feat['rating'] = df_feat['supplier_rating']
        
        # Cost features
        if 'unit_price' in df_feat.columns:
            supplier_cost = df_feat.groupby('supplier_id')['unit_price'].transform('mean')
            df_feat['avg_cost'] = supplier_cost
        
        # Fill rate features
        if 'fill_rate_pct' in df_feat.columns:
            supplier_fill = df_feat.groupby('supplier_id')['fill_rate_pct'].transform('mean')
            df_feat['avg_fill_rate'] = supplier_fill
        
        # Create target variable (delayed vs on-time)
        if 'lead_time_days' in df_feat.columns:
            avg_lead = df_feat['lead_time_days'].mean()
            df_feat['is_delayed'] = (df_feat['lead_time_days'] > avg_lead * 1.5).astype(int)
        
        # Fill NaN values
        numeric_cols = df_feat.select_dtypes(include=[np.number]).columns
        df_feat[numeric_cols] = df_feat[numeric_cols].fillna(df_feat[numeric_cols].median())
        
        return df_feat
        
    except Exception as e:
        st.error(f"Error in supplier risk feature engineering: {str(e)}")
        return df

@st.cache_data
def train_supplier_risk_model(X_train, y_train):
    """Train supplier risk scoring model"""
    try:
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        from sklearn.ensemble import RandomForestClassifier
        
        X_train_split, X_val, y_train_split, y_val = train_test_split(
            X_train, y_train, test_size=0.2, random_state=42, stratify=y_train
        )
        
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1,
            class_weight='balanced'
        )
        
        model.fit(X_train_split, y_train_split)
        
        # Validation
        y_pred = model.predict(X_val)
        
        metrics = {
            'Accuracy': accuracy_score(y_val, y_pred),
            'Precision': precision_score(y_val, y_pred, average='binary'),
            'Recall': recall_score(y_val, y_pred, average='binary'),
            'F1 Score': f1_score(y_val, y_pred, average='binary')
        }
        
        return model, metrics
        
    except Exception as e:
        st.error(f"Error training supplier risk model: {str(e)}")
        return None, None

if st.button("Train Supplier Risk Scoring Model", key="supplier_risk_btn"):
    if df is not None and not df.empty:
        with st.spinner("Performing feature engineering for supplier risk scoring..."):
            df_risk_feat = supplier_risk_feature_engineering(df)
            st.success("✅ Feature engineering completed")
        
        # Select features for supplier risk scoring
        risk_features = [
            'lead_cv', 'rating', 'avg_cost', 'avg_fill_rate'
        ]
        
        available_risk_features = [f for f in risk_features if f in df_risk_feat.columns]
        
        if len(available_risk_features) > 0 and 'is_delayed' in df_risk_feat.columns:
            X_risk = df_risk_feat[available_risk_features].fillna(0)
            y_risk = df_risk_feat['is_delayed'].fillna(0)
            
            with st.spinner("Training supplier risk scoring model..."):
                risk_model, risk_metrics = train_supplier_risk_model(X_risk, y_risk)
                
                if risk_model is not None:
                    st.success("✅ Supplier risk scoring model trained successfully")
                    
                    st.markdown("### Model Performance Metrics")
                    st.json(risk_metrics)
                    
                    st.session_state['supplier_risk_model'] = risk_model
                    st.session_state['supplier_risk_features'] = available_risk_features
        else:
            st.warning("⚠️ Insufficient features for supplier risk scoring model")


# ================================================================
# LAYER 8: REINFORCEMENT LEARNING (ADVANCED)
# ================================================================

st.markdown(
    """
    <div style="
        background-color:#00D05E;
        padding:20px;
        border-radius:12px;
        color:white;
        font-size:20px;
        font-weight:600;
        margin-top:30px;
        margin-bottom:20px;
    ">
    🚀 Layer 8: Reinforcement Learning (Advanced – Differentiator)
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:24px;
        border-radius:12px;
        color:white;
        font-size:16px;
        line-height:1.7;
        margin-bottom:25px;
    ">
    <b>This is where your product becomes next-gen AI.</b><br>
    This layer implements a self-learning supply chain system using reinforcement learning.
    </div>
    """,
    unsafe_allow_html=True
)

# ================================================================
# MODEL 8.1: RL-BASED INVENTORY REDISTRIBUTION AGENT
# ================================================================

st.markdown(
    """
    <div style="
        background-color:#163A70;
        padding:18px;
        border-radius:10px;
        color:white;
        font-size:18px;
        font-weight:600;
        margin-top:25px;
        margin-bottom:15px;
    ">
    🔹 ML Implementation: RL-Based Inventory Redistribution Agent
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:20px;
        border-radius:12px;
        color:white;
        font-size:15px;
        line-height:1.6;
        margin-bottom:20px;
    ">
    <b>Agent Goal:</b> Minimize total cost, Maximize fill rate<br>
    <b>State:</b> Inventory levels, Demand forecast, Transport cost<br>
    <b>Action:</b> Move SKU X from Store A - Store B<br>
    <b>Reward:</b> Reduced stockout, Reduced overstock, Lower logistics cost<br>
    <b>This creates:</b> Self-learning supply chain system
    </div>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def rl_agent_feature_engineering(df):
    """Feature engineering for RL agent"""
    try:
        df_feat = df.copy()
        
        # State features
        if 'on_hand_qty' in df_feat.columns:
            df_feat['inventory_level'] = df_feat['on_hand_qty']
        
        if 'demand_index' in df_feat.columns:
            df_feat['demand_forecast'] = df_feat['demand_index']
        
        if 'fuel_cost' in df_feat.columns:
            df_feat['transport_cost'] = df_feat['fuel_cost']
        
        # Reward calculation features
        if 'stockout_pct' in df_feat.columns:
            df_feat['stockout_reduction_potential'] = df_feat['stockout_pct']
        
        if 'overstock_qty' in df_feat.columns:
            df_feat['overstock_reduction_potential'] = df_feat['overstock_qty']
        
        # Fill NaN values
        numeric_cols = df_feat.select_dtypes(include=[np.number]).columns
        df_feat[numeric_cols] = df_feat[numeric_cols].fillna(df_feat[numeric_cols].median())
        
        return df_feat
        
    except Exception as e:
        st.error(f"Error in RL agent feature engineering: {str(e)}")
        return df

@st.cache_data
def train_rl_agent(df, n_episodes=100):
    """Train a simple Q-learning agent for inventory redistribution"""
    try:
        import numpy as np
        
        # Simplified Q-learning implementation
        # State: (inventory_level, demand_forecast, transport_cost)
        # Action: transfer quantities
        
        results = []
        
        # Discretize state space
        inventory_bins = np.linspace(df['inventory_level'].min(), df['inventory_level'].max(), 10)
        demand_bins = np.linspace(df['demand_forecast'].min(), df['demand_forecast'].max(), 10)
        cost_bins = np.linspace(df['transport_cost'].min(), df['transport_cost'].max(), 5)
        
        # Initialize Q-table
        q_table = np.zeros((len(inventory_bins), len(demand_bins), len(cost_bins), 5))  # 5 actions
        
        # Training loop
        for episode in range(n_episodes):
            # Sample a random state
            sample = df.sample(1).iloc[0]
            
            # Discretize state
            inv_state = np.digitize(sample['inventory_level'], inventory_bins) - 1
            dem_state = np.digitize(sample['demand_forecast'], demand_bins) - 1
            cost_state = np.digitize(sample['transport_cost'], cost_bins) - 1
            
            # Choose action (epsilon-greedy)
            epsilon = max(0.1, 1.0 - episode / n_episodes)
            if np.random.random() < epsilon:
                action = np.random.randint(5)
            else:
                action = np.argmax(q_table[inv_state, dem_state, cost_state])
            
            # Calculate reward
            reward = -sample['transport_cost'] - sample['stockout_reduction_potential'] + sample['overstock_reduction_potential'] * 0.5
            
            # Update Q-value
            q_table[inv_state, dem_state, cost_state, action] += 0.1 * (reward - q_table[inv_state, dem_state, cost_state, action])
            
            if episode % 10 == 0:
                results.append({
                    'episode': episode,
                    'total_reward': reward,
                    'epsilon': epsilon
                })
        
        results_df = pd.DataFrame(results)
        metrics = {
            'Total Episodes': n_episodes,
            'Final Epsilon': epsilon,
            'Q-Table Shape': q_table.shape
        }
        
        return q_table, results_df, metrics
        
    except Exception as e:
        st.error(f"Error training RL agent: {str(e)}")
        return None, None, None

if st.button("Train RL Redistribution Agent", key="rl_agent_btn"):
    if df is not None and not df.empty:
        with st.spinner("Performing feature engineering for RL agent..."):
            df_rl_feat = rl_agent_feature_engineering(df)
            st.success("✅ Feature engineering completed")
        
        n_episodes = st.slider("Number of Training Episodes", 50, 500, 100, 10)
        
        with st.spinner("Training RL agent..."):
            q_table, rl_results, rl_metrics = train_rl_agent(df_rl_feat, n_episodes)
            
            if q_table is not None:
                st.success("✅ RL agent trained successfully")
                
                st.markdown("### RL Training Metrics")
                st.json(rl_metrics)
                
                if rl_results is not None and not rl_results.empty:
                    st.markdown("### Training Progress")
                    render_html_table(rl_results, max_height=300)
                
                st.session_state['rl_q_table'] = q_table
                st.session_state['rl_results'] = rl_results
            else:
                st.info("ℹ️ Could not train RL agent")
    else:
        st.warning("⚠️ Please load data first")


# ================================================================
# LAYER 9: ANOMALY DETECTION LAYER
# ================================================================

st.markdown(
    """
    <div style="
        background-color:#00D05E;
        padding:20px;
        border-radius:12px;
        color:white;
        font-size:20px;
        font-weight:600;
        margin-top:30px;
        margin-bottom:20px;
    ">
    🚀 Layer 9: Anomaly Detection Layer
    </div>
    """,
    unsafe_allow_html=True
)

# ================================================================
# MODEL 9.1: OUTLIER DETECTION
# ================================================================

st.markdown(
    """
    <div style="
        background-color:#163A70;
        padding:18px;
        border-radius:10px;
        color:white;
        font-size:18px;
        font-weight:600;
        margin-top:25px;
        margin-bottom:15px;
    ">
    🔹 ML Implementation: Outlier Detection
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:20px;
        border-radius:12px;
        color:white;
        font-size:15px;
        line-height:1.6;
        margin-bottom:20px;
    ">
    <b>Algorithms:</b> Isolation Forest / Autoencoders<br>
    <b>Detects:</b> Sudden demand spikes, Data quality issues
    </div>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def anomaly_detection_feature_engineering(df):
    """Feature engineering for anomaly detection"""
    try:
        df_feat = df.copy()
        
        # Select numeric features for anomaly detection
        numeric_cols = df_feat.select_dtypes(include=[np.number]).columns.tolist()
        
        # Remove ID columns
        id_cols = [col for col in numeric_cols if 'id' in col.lower()]
        feature_cols = [col for col in numeric_cols if col not in id_cols]
        
        # Fill NaN values
        df_feat[feature_cols] = df_feat[feature_cols].fillna(df_feat[feature_cols].median())
        
        return df_feat, feature_cols
        
    except Exception as e:
        st.error(f"Error in anomaly detection feature engineering: {str(e)}")
        return df, []

@st.cache_data
def detect_anomalies_isolation_forest(X, contamination=0.05):
    """Detect anomalies using Isolation Forest"""
    try:
        from sklearn.ensemble import IsolationForest
        
        model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_jobs=-1
        )
        
        anomalies = model.fit_predict(X)
        anomaly_scores = model.decision_function(X)
        
        # -1 indicates anomaly, 1 indicates normal
        is_anomaly = anomalies == -1
        
        metrics = {
            'Total Samples': len(X),
            'Anomalies Detected': sum(is_anomaly),
            'Anomaly Rate': f"{sum(is_anomaly) / len(X) * 100:.2f}%"
        }
        
        return is_anomaly, anomaly_scores, metrics, model
        
    except Exception as e:
        st.error(f"Error in anomaly detection: {str(e)}")
        return None, None, None, None

if st.button("Run Anomaly Detection", key="anomaly_btn"):
    if df is not None and not df.empty:
        with st.spinner("Performing feature engineering for anomaly detection..."):
            df_anomaly_feat, anomaly_features = anomaly_detection_feature_engineering(df)
            st.success("✅ Feature engineering completed")
        
        contamination = st.slider("Expected Anomaly Rate", 0.01, 0.20, 0.05, 0.01)
        
        if len(anomaly_features) > 0:
            X_anomaly = df_anomaly_feat[anomaly_features]
            
            with st.spinner("Running anomaly detection..."):
                is_anomaly, anomaly_scores, anomaly_metrics, anomaly_model = detect_anomalies_isolation_forest(
                    X_anomaly, contamination
                )
                
                if is_anomaly is not None:
                    st.success("✅ Anomaly detection completed")
                    
                    st.markdown("### Anomaly Detection Metrics")
                    st.json(anomaly_metrics)
                    
                    # Add anomaly results to dataframe
                    df_anomaly_result = df_anomaly_feat.copy()
                    df_anomaly_result['is_anomaly'] = is_anomaly
                    df_anomaly_result['anomaly_score'] = anomaly_scores
                    
                    # Show anomalies
                    anomalies_df = df_anomaly_result[df_anomaly_result['is_anomaly'] == True]
                    
                    if not anomalies_df.empty:
                        st.markdown("### Detected Anomalies")
                        render_html_table(anomalies_df.head(20), max_height=300)
                    else:
                        st.info("ℹ️ No anomalies detected")
                    
                    st.session_state['anomaly_results'] = df_anomaly_result
                    st.session_state['anomaly_model'] = anomaly_model
        else:
            st.warning("⚠️ Insufficient features for anomaly detection")
    else:
        st.warning("⚠️ Please load data first")


# ================================================================
# LAYER 10: EXPLAINABLE AI LAYER
# ================================================================

st.markdown(
    """
    <div style="
        background-color:#00D05E;
        padding:20px;
        border-radius:12px;
        color:white;
        font-size:20px;
        font-weight:600;
        margin-top:30px;
        margin-bottom:20px;
    ">
    🚀 Layer 10: Explainable AI Layer (Very Important for Adoption)
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:24px;
        border-radius:12px;
        color:white;
        font-size:16px;
        line-height:1.7;
        margin-bottom:25px;
    ">
    This layer provides model interpretability to build trust and enable adoption.
    </div>
    """,
    unsafe_allow_html=True
)

# ================================================================
# MODEL 10.1: EXPLAINABILITY ENGINE
# ================================================================

st.markdown(
    """
    <div style="
        background-color:#163A70;
        padding:18px;
        border-radius:10px;
        color:white;
        font-size:18px;
        font-weight:600;
        margin-top:25px;
        margin-bottom:15px;
    ">
    🔹 ML Implementation: Explainability Engine
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        background-color:#2F75B5;
        padding:20px;
        border-radius:12px;
        color:white;
        font-size:15px;
        line-height:1.6;
        margin-bottom:20px;
    >
    <b>Tools:</b> SHAP / LIME<br>
    <b>Answers:</b> Why this transfer was recommended? Why this store is high risk?
    </div>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def generate_shap_explanations(model, X, background_samples=100):
    """Generate SHAP explanations for model predictions"""
    try:
        import shap
        
        # Create explainer
        explainer = shap.Explainer(model, X[:background_samples])
        
        # Calculate SHAP values
        shap_values = explainer(X)
        
        # Get feature importance
        feature_importance = np.abs(shap_values.values).mean(axis=0)
        
        # Create importance dataframe
        importance_df = pd.DataFrame({
            'feature': X.columns,
            'importance': feature_importance
        }).sort_values('importance', ascending=False)
        
        metrics = {
            'Total Features': len(X.columns),
            'Top Feature': importance_df.iloc[0]['feature'] if not importance_df.empty else 'N/A',
            'Method': 'SHAP'
        }
        
        return shap_values, importance_df, metrics
        
    except ImportError:
        st.warning("⚠️ SHAP library not installed. Using permutation importance instead.")
        from sklearn.inspection import permutation_importance
        
        # Use permutation importance as fallback
        perm_importance = permutation_importance(model, X, n_repeats=10, random_state=42)
        importance_df = pd.DataFrame({
            'feature': X.columns,
            'importance': perm_importance.importances_mean
        }).sort_values('importance', ascending=False)
        
        metrics = {
            'Total Features': len(X.columns),
            'Top Feature': importance_df.iloc[0]['feature'] if not importance_df.empty else 'N/A',
            'Method': 'Permutation Importance (Fallback)'
        }
        
        return None, importance_df, metrics
        
    except Exception as e:
        st.error(f"Error generating SHAP explanations: {str(e)}")
        return None, None, None

if st.button("Generate Model Explanations", key="explainability_btn"):
    # Check if any model is trained
    trained_models = {
        'demand_model': 'Demand Forecasting Model',
        'stockout_model': 'Stockout Probability Model',
        'overstock_model': 'Overstock Risk Model',
        'transfer_quantity_model': 'Transfer Quantity Model',
        'delivery_time_model': 'Delivery Time Model',
        'transport_cost_model': 'Transport Cost Model'
    }
    
    available_models = {k: v for k, v in trained_models.items() if k in st.session_state}
    
    if not available_models:
        st.warning("⚠️ No trained models found. Please train a model first.")
    else:
        selected_model = st.selectbox(
            "Select Model to Explain",
            options=list(available_models.keys()),
            format_func=lambda x: available_models[x]
        )
        
        if selected_model in st.session_state:
            model = st.session_state[selected_model]
            
            # Get corresponding features
            feature_key = selected_model.replace('_model', '_features')
            if feature_key in st.session_state:
                features = st.session_state[feature_key]
                
                if df is not None and not df.empty:
                    X_explain = df[features].fillna(0).head(100)
                    
                    with st.spinner("Generating model explanations..."):
                        shap_values, importance_df, explain_metrics = generate_shap_explanations(
                            model, X_explain
                        )
                        
                        if importance_df is not None and not importance_df.empty:
                            st.success("✅ Model explanations generated successfully")
                            
                            st.markdown("### Explainability Metrics")
                            st.json(explain_metrics)
                            
                            st.markdown("### Feature Importance")
                            render_html_table(importance_df.head(20), max_height=300)
                            
                            st.session_state['feature_importance'] = importance_df
                        else:
                            st.info("ℹ️ Could not generate explanations")
                else:
                    st.warning("⚠️ Please load data first")
            else:
                st.warning("⚠️ Model features not found in session state")


# ============================================================
# FOOTER
# ============================================================

st.markdown("""
    <br><br>
    <div style="
        background-color:#2E86C1;
        padding:12px;
        text-align:center;
        color:white;
        border-radius:6px;
        font-size:14px;">
        © 2025 SupplySyncAI – Inventory Intelligence & Analytics Platform
    </div>
""", unsafe_allow_html=True)
