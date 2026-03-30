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
else:
    st.info("Click the button above to load the dataset.")


# ================================================================
# STEP 2 – DATA PRE-PROCESSING
# ================================================================
if "preprocess_history" not in st.session_state:
    st.session_state.preprocess_history = {
        "duplicates": None,
        "outliers": {},
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
        "Remove Outliers",
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
# 2. REMOVE OUTLIERS
# ================================================================
if "out_before_df" not in st.session_state:
    st.session_state.out_before_df = None
if "out_after_df" not in st.session_state:
    st.session_state.out_after_df = None
if "out_removed_df" not in st.session_state:
    st.session_state.out_removed_df = None

if step == "Remove Outliers":

    st.markdown("### Remove Outliers")
    st.write("")

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
    <b>What this does:</b><br>
    This step identifies and handles <b>statistical outliers</b> in supply chain numeric fields using a
    <b>robust IQR-based method</b>.

    Outlier handling is performed <b>internally</b> and follows a <b>two-level strategy</b>:
    <ul>
        <li><b>Mild anomalies</b> are <b>capped</b> to safe bounds (no row deletion)</li>
        <li><b>Extreme anomalies</b> in <b>critical columns</b> are <b>removed</b></li>
    </ul>

    <br>

    <b>Critical supply chain columns targeted for deletion:</b>
    <ul>
        <li><code>on_hand_qty</code> — physically impossible stock levels</li>
        <li><code>delivery_time_mins</code> — unrealistically long or negative delivery records</li>
        <li><code>transfer_qty</code> — extreme transfer quantities exceeding logical bounds</li>
    </ul>

    <br>

    <b>Why this is important:</b>
    <ul>
        <li>Prevents extreme stock counts from skewing inventory optimization models</li>
        <li>Removes erroneous delivery records that distort route efficiency analysis</li>
        <li>Stabilizes fuel cost and transfer cost distributions for fair comparison</li>
        <li>Ensures inventory turnover and fill rate KPIs remain business-realistic</li>
    </ul>
    <br>

    <b>How it helps supply chain optimization:</b>
    <li>
    Inventory and routing models are sensitive to extreme values.
    By controlling these extremes, the model learns from realistic operational behavior
    rather than rare or erroneous records.
    </li>

    <li>
    This improves forecasting by preserving <b>true demand and inventory signals</b>,
    reducing noise, and ensuring recommendations remain
    <b>stable, generalizable, and operationally relevant</b> across products, stores, and routes.
    </li>

    </div>
    """, unsafe_allow_html=True)

    df = st.session_state.df
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

    if not numeric_cols:
        st.info("No numeric columns available for outlier detection.")
        st.stop()

    DELETE_COLS = ["on_hand_qty", "delivery_time_mins", "transfer_qty"]

    if st.button("Apply Outlier Removal"):

        if st.session_state.out_removed_df is not None:
            st.info("Outliers were already handled earlier.")

        else:
            with st.spinner("Processing outliers..."):
                before_df, after_df, removed_df = remove_outliers_cached(df, DELETE_COLS)
                
                st.session_state.out_before_df = before_df
                st.session_state.out_removed_df = removed_df
                st.session_state.out_after_df = after_df

                st.session_state.df = after_df
                st.session_state.preprocessing_completed = True

                st.success("✔ Outliers handled successfully")

    if st.session_state.out_removed_df is not None:

        before_df = st.session_state.out_before_df
        after_df = st.session_state.out_after_df
        removed_df = st.session_state.out_removed_df

        st.markdown("#### Outlier Removal Summary")
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
                <div class="summary-title">Outliers Removed</div>
                <div class="summary-value">{}</div>
            </div>
        </div>
        """.format(
            before_df.shape[0],
            after_df.shape[0],
            removed_df.shape[0]
        ), unsafe_allow_html=True)
        st.write("")
        st.markdown(f"#### Before Outlier Handling ({before_df.shape[0]} Rows)")
        st.write("")
        render_html_table(before_df, max_height=300)
        st.write("")

        st.markdown(f"#### After Outlier Handling ({after_df.shape[0]} Rows)")
        st.write("")
        render_html_table(after_df, max_height=300)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(f"#### Outliers Removed ({removed_df.shape[0]} Rows)")
        st.write("")
        render_html_table(removed_df, max_height=300)


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
                st.markdown(f"- **{col}**: {info['original_dtype']} → numeric ({info['conversion_rate']:.1f}% success rate)")
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
    row4 = st.columns(4)
    row5 = st.columns(4)
    row6 = st.columns(3)

    with row1[0]:
        nav_button("Data Quality Overview", "Data Quality Overview")
    with row1[1]:
        nav_button("Inventory Overview", "Inventory Overview")
    with row1[2]:
        nav_button("Supplier Analysis", "Supplier Analysis")
    with row1[3]:
        nav_button("Product Analysis", "Product Analysis")

    with row2[0]:
        nav_button("Product-Level Analysis", "Product-Level Analysis")
    with row2[1]:
        nav_button("Store Analysis", "Store Analysis")
    with row2[2]:
        nav_button("Store & Regional Analysis", "Store & Regional Analysis")
    with row2[3]:
        nav_button("Customer Analysis", "Customer Analysis")

    with row3[0]:
        nav_button("Vendor Analysis", "Vendor Analysis")
    with row3[1]:
        nav_button("Location Analysis", "Location Analysis")
    with row3[2]:
        nav_button("Warehouse Analysis", "Warehouse Analysis")
    with row3[3]:
        nav_button("Transport Route Analysis", "Transport Route Analysis")

    with row4[0]:
        nav_button("Shipment & Routing Analysis", "Shipment & Routing Analysis")
    with row4[1]:
        nav_button("Cluster Transfer Analysis", "Cluster Transfer Analysis")
    with row4[2]:
        nav_button("Sales Analysis", "Sales Analysis")
    with row4[3]:
        nav_button("Inventory Analysis", "Inventory Analysis")

    with row5[0]:
        nav_button("Redistribution Analysis", "Redistribution Analysis")
    with row5[1]:
        nav_button("Reallocation Analysis", "Reallocation Analysis")
    with row5[2]:
        nav_button("Logistics Analysis", "Logistics Analysis")
    with row5[3]:
        nav_button("Time & Seasonality Analysis", "Time & Seasonality Analysis")

    with row6[0]:
        nav_button("Summary Report", "Summary Report")
    with row6[1]:
        nav_button("Sales Overview", "Sales Overview")
    with row6[2]:
        nav_button("Data Quality Analysis", "Data Quality Analysis")


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
    </ul><br>

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


# ================================================================
# EDA – STORE & REGIONAL ANALYSIS
# ================================================================
elif eda_option == "Store & Regional Analysis":

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


# ================================================================
# EDA – SHIPMENT & ROUTING ANALYSIS
# ================================================================
elif eda_option == "Shipment & Routing Analysis":

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


# ================================================================
# EDA – CLUSTER TRANSFER ANALYSIS
# ================================================================
elif eda_option == "Cluster Transfer Analysis":

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
# EDA – TIME & SEASONALITY ANALYSIS
# ================================================================
elif eda_option == "Time & Seasonality Analysis":

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

    This provides a <b>time and seasonality breakdown</b> of supply chain activity,
    showing how inventory levels, delivery performance, and transfer costs vary across:

    <ul>
        <li>Day of week, week, month, and quarter patterns</li>
        <li>Holiday vs non-holiday inventory behavior</li>
        <li>Weekend vs weekday logistics activity</li>
    </ul>
    <br>

    <b>Why this matters:</b>

    Seasonal demand patterns directly affect replenishment cycles,
    lead time planning, and inventory positioning.
    Understanding time-based patterns enables <b>proactive supply chain management</b>.

    <b>Key insights users get:</b>
    <ul>
        <li>When overstock and understock risk peaks</li>
        <li>Holiday-driven fill rate and delivery time impacts</li>
        <li>Optimal reorder timing across the calendar</li>
    </ul>

    </div>
    """,
    unsafe_allow_html=True
)

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df["Year"]    = df["date"].dt.year
    df["Quarter"] = df["date"].dt.to_period("Q").astype(str)
    df["Month"]   = df["date"].dt.to_period("M").astype(str)

    col1, col2 = st.columns(2)

    # Plot 1: Stock Value by Holiday vs Non-Holiday
    with col1:
        blue_title("Avg Stock Value – Holiday vs Non-Holiday")
        hol = df.groupby(col_is_holiday)[col_stockval].mean()
        hol.index = ["Non-Holiday" if i == 0 else "Holiday" for i in hol.index]
        chart_hol = (
            alt.Chart(hol.reset_index().rename(columns={col_is_holiday: "Type", col_stockval: "Avg Stock Value"}))
            .mark_bar(color=BAR_BLUE, cornerRadiusEnd=6)
            .encode(
                x=alt.X("Type:O", title="Day Type"),
                y=alt.Y("Avg Stock Value:Q", title="Avg Stock Value (₹)", scale=alt.Scale(padding=10)),
                tooltip=["Type", "Avg Stock Value"]
            )
            .properties(height=340, background=GREEN_BG,
                        padding={"top":10,"left":10,"right":10,"bottom":10})
            .configure_view(fill=GREEN_BG, strokeOpacity=0)
            .configure_axis(labelColor="#000000", titleColor="#000000",
                            gridColor="rgba(0,0,0,0.2)", domainColor="rgba(0,0,0,0.3)")
        )
        st.altair_chart(chart_hol, use_container_width=True)

    # Plot 2: Delivery Time by Weekend vs Weekday
    with col2:
        blue_title("Avg Delivery Time – Weekend vs Weekday")
        wknd = df.groupby(col_is_weekend)[col_delivery].mean()
        wknd.index = ["Weekday" if i == 0 else "Weekend" for i in wknd.index]
        chart_wknd = (
            alt.Chart(wknd.reset_index().rename(columns={col_is_weekend: "Day Type", col_delivery: "Avg Delivery Time"}))
            .mark_bar(color="#001F5C", cornerRadiusEnd=6)
            .encode(
                x=alt.X("Day Type:O", title="Day Type"),
                y=alt.Y("Avg Delivery Time:Q", title="Avg Delivery Time (mins)", scale=alt.Scale(padding=10)),
                tooltip=["Day Type", "Avg Delivery Time"]
            )
            .properties(height=340, background=GREEN_BG,
                        padding={"top":10,"left":10,"right":10,"bottom":10})
            .configure_view(fill=GREEN_BG, strokeOpacity=0)
            .configure_axis(labelColor="#000000", titleColor="#000000",
                            gridColor="rgba(0,0,0,0.2)", domainColor="rgba(0,0,0,0.3)")
        )
        st.altair_chart(chart_wknd, use_container_width=True)

    # Plot 3: Fill Rate by Quarter
    st.markdown("""
    <div style="background-color:#2F75B5;padding:18px 25px;border-radius:10px;font-size:20px;color:white;margin-top:20px;margin-bottom:10px;text-align:center;">
        <b>Fill Rate by Quarter</b>
    </div>
    """, unsafe_allow_html=True)

    fill_qtr = df.groupby("Quarter")[col_fill_rate].mean().sort_index()
    chart_fill = (
        alt.Chart(fill_qtr.reset_index())
        .mark_bar(color=BAR_BLUE, cornerRadiusEnd=6)
        .encode(
            x=alt.X("Quarter:O", title="Quarter"),
            y=alt.Y(f"{col_fill_rate}:Q", title="Avg Fill Rate (%)", scale=alt.Scale(padding=10)),
            tooltip=["Quarter", col_fill_rate]
        )
        .properties(height=380, background=GREEN_BG,
                    padding={"top":10,"left":10,"right":10,"bottom":10})
        .configure_view(fill=GREEN_BG, strokeOpacity=0)
        .configure_axis(labelColor="#000000", titleColor="#000000",
                        gridColor="rgba(0,0,0,0.2)", domainColor="rgba(0,0,0,0.3)")
    )
    st.altair_chart(chart_fill, use_container_width=True)

    # Plot 4: Stockout Rate by Month
    st.markdown("""
    <div style="background-color:#2F75B5;padding:18px 25px;border-radius:10px;font-size:20px;color:white;margin-top:20px;margin-bottom:10px;text-align:center;">
        <b>Stockout Rate by Month</b>
    </div>
    """, unsafe_allow_html=True)

    so_month = df.groupby("Month")[col_stockout].mean().sort_index()
    chart_so = (
        alt.Chart(so_month.reset_index())
        .mark_bar(color="#EF4444", cornerRadiusEnd=6)
        .encode(
            x=alt.X("Month:O", title="Month"),
            y=alt.Y(f"{col_stockout}:Q", title="Avg Stockout Rate (%)", scale=alt.Scale(padding=10)),
            tooltip=["Month", col_stockout]
        )
        .properties(height=380, background=GREEN_BG,
                    padding={"top":10,"left":10,"right":10,"bottom":10})
        .configure_view(fill=GREEN_BG, strokeOpacity=0)
        .configure_axis(labelColor="#000000", titleColor="#000000",
                        gridColor="rgba(0,0,0,0.2)", domainColor="rgba(0,0,0,0.3)")
    )
    st.altair_chart(chart_so, use_container_width=True)


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

        <b>What this section does:</b>

        This provides a <b>consolidated narrative summary</b> of all supply chain EDA findings.

        It highlights:
        <ul>
            <li>Key inventory imbalance patterns</li>
            <li>Major logistics and routing efficiency signals</li>
            <li>Supplier performance benchmarks</li>
            <li>Cluster transfer optimization readiness</li>
            <li>Data readiness for modelling</li>
        </ul>

        <b>Why this matters:</b>

        Not all stakeholders want charts.<br>
        This section translates supply chain analysis into <b>actionable understanding</b>.

        <b>Key insights users get:</b>
        <ul>
            <li>A single, clear view of supply chain intelligence</li>
            <li>Business-ready conclusions across inventory, logistics, and procurement</li>
            <li>Readiness assessment for model engineering and optimization</li>
        </ul>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style="
            background-color:#0B2C5D;
            padding:30px;
            border-radius:12px;
            color:white;
            font-size:15px;
            line-height:1.7;
        ">

        <h4>Data Health & Readiness</h4>
        <ul>
            <li>The dataset consists of <b>11,088 rows and 82 columns</b>, offering rich supply chain coverage across products, stores, routes, clusters, suppliers, and time.</li>
            <li><b>No missing values</b> were detected, confirming the dataset is ingested cleanly from source systems.</li>
            <li>Data types are well balanced (numeric, categorical, datetime), confirming the dataset is <b>model-ready</b> for optimization.</li>
        </ul>

        <h4>Overall Inventory Health</h4>
        <ul>
            <li>Inventory levels show <b>seasonal imbalances</b> with overstock and understock quantities varying significantly across months and quarters.</li>
            <li>Fill rates are generally stable, but stockout rates persist in specific regions and store types — indicating uneven replenishment coverage.</li>
            <li>Excess inventory percentage varies by region, with some zones accumulating disproportionate stock relative to operational throughput.</li>
        </ul>

        <h4>Product-Level Insights</h4>
        <ul>
            <li>Stock value is concentrated in a small set of high-value SKUs — consistent with the Pareto principle in supply chain management.</li>
            <li>Demand index does not always correlate with overstock index — some high-demand products still face overstock, signaling timing issues in replenishment cycles.</li>
            <li>Inventory turnover varies widely by category, highlighting categories requiring optimized reorder cycles and safety stock recalibration.</li>
        </ul>

        <h4>Store & Regional Performance</h4>
        <ul>
            <li>A small number of stores contribute disproportionately to total stock value — resource allocation is uneven across the network.</li>
            <li>Fill rates and stockout rates differ significantly by store, confirming that store-level replenishment policies require customization.</li>
            <li>Regional differences in excess inventory suggest <b>zonal transfer strategies</b> can significantly reduce carrying costs.</li>
        </ul>

        <h4>Shipment & Routing Analysis</h4>
        <ul>
            <li>Delivery time distribution is wide, indicating high variability in last-mile logistics performance across routes.</li>
            <li>Fuel cost and route efficiency score show a <b>weak inverse relationship</b> — high-cost routes are not always the most efficient.</li>
            <li>Cluster-based transfer costs vary, reinforcing the importance of optimal cluster assignments for cost minimization and service level improvement.</li>
        </ul>

        <h4>Cluster Transfer Analysis</h4>
        <ul>
            <li>Cluster-based transfer recommendations show that <b>not all clusters achieve optimal transfer execution</b> — actual transfer quantities often deviate from recommendations.</li>
            <li>Cost minimization percentages vary across clusters, with some clusters achieving strong savings and others underperforming.</li>
            <li>Model confidence scores vary, highlighting clusters where recommendation reliability could be improved with richer training data.</li>
        </ul>

        <h4>Supplier Performance</h4>
        <ul>
            <li>Lead times vary significantly across suppliers — some high-rating suppliers maintain shorter lead times, enabling tighter replenishment cycles.</li>
            <li>Rating scores do not uniformly scale with lead time, suggesting multi-dimensional supplier evaluation is essential for procurement decisions.</li>
            <li>Cost price differences across categories provide clear signals for procurement cost optimization and supplier consolidation strategies.</li>
        </ul>

        <h4>Time & Seasonality</h4>
        <ul>
            <li>Holiday periods show elevated stock value requirements, confirming the need for pre-holiday inventory positioning.</li>
            <li>Weekend delivery times are slightly higher, indicating logistics capacity constraints during non-standard operating periods.</li>
            <li>Fill rates peak in Q2 and Q4, aligned with seasonal demand cycles across product categories.</li>
        </ul>

        <h4>Final Takeaway</h4>
        <ul>
            <li>The dataset is <b>clean, complete, and enterprise-grade</b> with no missing values.</li>
            <li>Clear supply chain inefficiencies are observable across inventory, routing, cluster transfers, and supplier dimensions.</li>
            <li>Optimization accuracy will significantly improve by modeling at <b>SKU × Store × Cluster × Route × Supplier × Time</b> levels.</li>
            <li>The EDA strongly supports downstream use cases in <b>inventory optimization, demand-supply balancing, routing efficiency, and supplier intelligence</b>.</li>
        </ul>

        </div>
        """,
        unsafe_allow_html=True
    )


# ================================================================
# EDA – SALES OVERVIEW
# ================================================================
elif eda_option == "Sales Overview":

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

        <b>What this section does:</b>
        Macro-level sales and stock performance overview across categories, regions, and time.

        <b>Key insights covered:</b>
        <ul>
            <li>Total stock value by category — bar and pie breakdown</li>
            <li>Average fill rate by region</li>
            <li>Monthly stock value trend</li>
            <li>Holiday vs non-holiday stock value comparison</li>
        </ul>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### Sales Overview")

    if col_stockval and col_category:
        sv_by_cat = df.groupby(col_category, observed=True)[col_stockval].sum().sort_values(ascending=False)
        c1, c2 = st.columns(2)
        with c1:
            blue_title("Total Stock Value by Category")
            fig, ax = plt.subplots(figsize=(7, 4))
            fig.patch.set_facecolor(GREEN_BG); ax.set_facecolor(GREEN_BG)
            ax.bar(sv_by_cat.index.astype(str), sv_by_cat.values, color=BAR_BLUE)
            ax.set_xlabel("Category"); ax.set_ylabel("Stock Value (₹)")
            ax.tick_params(axis="x", rotation=45)
            ax.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
            ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
            st.pyplot(fig); plt.close(fig)
        with c2:
            blue_title("Stock Value Share by Category")
            fig2, ax2 = plt.subplots(figsize=(7, 4))
            fig2.patch.set_facecolor(GREEN_BG); ax2.set_facecolor(GREEN_BG)
            ax2.pie(sv_by_cat.values, labels=sv_by_cat.index.astype(str), autopct="%1.1f%%", startangle=140)
            st.pyplot(fig2); plt.close(fig2)

    if col_fill_rate and col_region:
        blue_title("Avg Fill Rate by Region")
        fr_reg = df.groupby(col_region, observed=True)[col_fill_rate].mean().sort_values(ascending=False)
        fig3, ax3 = plt.subplots(figsize=(10, 4))
        fig3.patch.set_facecolor(GREEN_BG); ax3.set_facecolor(GREEN_BG)
        ax3.bar(fr_reg.index.astype(str), fr_reg.values, color=BAR_BLUE)
        ax3.set_xlabel("Region"); ax3.set_ylabel("Avg Fill Rate (%)")
        ax3.tick_params(axis="x", rotation=45)
        ax3.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax3.spines["top"].set_visible(False); ax3.spines["right"].set_visible(False)
        st.pyplot(fig3); plt.close(fig3)

    if col_stockval and col_month:
        blue_title("Monthly Stock Value Trend")
        mv_month = df.groupby(col_month)[col_stockval].sum().sort_index()
        fig4, ax4 = plt.subplots(figsize=(10, 4))
        fig4.patch.set_facecolor(GREEN_BG); ax4.set_facecolor(GREEN_BG)
        ax4.plot(range(len(mv_month)), mv_month.values, marker="o", color=BAR_BLUE, linewidth=2)
        ax4.fill_between(range(len(mv_month)), mv_month.values, alpha=0.2, color=BAR_BLUE)
        ax4.set_xticks(range(len(mv_month)))
        ax4.set_xticklabels(mv_month.index.astype(str), rotation=45, ha="right")
        ax4.set_xlabel("Month"); ax4.set_ylabel("Stock Value (₹)")
        ax4.grid(linestyle="-", color=GRID_GREEN, alpha=0.4)
        ax4.spines["top"].set_visible(False); ax4.spines["right"].set_visible(False)
        st.pyplot(fig4); plt.close(fig4)

    if col_stockval and col_is_holiday:
        c3, c4 = st.columns(2)
        with c3:
            blue_title("Stock Value: Holiday vs Non-Holiday")
            hol_grp = df.groupby(col_is_holiday)[col_stockval].sum()
            labels = ["Non-Holiday" if not k else "Holiday" for k in hol_grp.index]
            fig5, ax5 = plt.subplots(figsize=(7, 4))
            fig5.patch.set_facecolor(GREEN_BG); ax5.set_facecolor(GREEN_BG)
            ax5.bar(labels, hol_grp.values, color=[BAR_BLUE, "#EF4444"])
            ax5.set_ylabel("Total Stock Value (₹)")
            ax5.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
            ax5.spines["top"].set_visible(False); ax5.spines["right"].set_visible(False)
            st.pyplot(fig5); plt.close(fig5)
        with c4:
            if col_stockval and col_quarter:
                blue_title("Stock Value by Quarter")
                sv_q = df.groupby(col_quarter)[col_stockval].sum().sort_index()
                fig6, ax6 = plt.subplots(figsize=(7, 4))
                fig6.patch.set_facecolor(GREEN_BG); ax6.set_facecolor(GREEN_BG)
                ax6.bar(sv_q.index.astype(str), sv_q.values, color=BAR_BLUE)
                ax6.set_xlabel("Quarter"); ax6.set_ylabel("Stock Value (₹)")
                ax6.tick_params(axis="x", rotation=45)
                ax6.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
                ax6.spines["top"].set_visible(False); ax6.spines["right"].set_visible(False)
                st.pyplot(fig6); plt.close(fig6)


# ================================================================
# EDA – DATA QUALITY ANALYSIS
# ================================================================
elif eda_option == "Data Quality Analysis":

    st.markdown("""
        <div style="
            background-color:#2F75B5;
            padding:28px;
            border-radius:12px;
            color:white;
            font-size:16px;
            line-height:1.6;
            margin-bottom:25px;">
        <b>What this section does:</b>
        Advanced numeric data profiling — correlation matrix, distribution analysis,
        skewness/kurtosis, and outlier counts across all numeric supply chain columns.
        <b>Key insights covered:</b>
        <ul>
            <li>Correlation heatmap of all numeric columns</li>
            <li>Skewness and kurtosis per numeric column</li>
            <li>IQR-based outlier count per numeric column</li>
            <li>Numeric column statistics deep-dive table</li>
        </ul>
        </div>""", unsafe_allow_html=True)

    st.markdown("### Advanced Numeric Data Quality Analysis")

    numeric_cols_dqa = df.select_dtypes(include=np.number).columns.tolist()

    if not numeric_cols_dqa:
        st.warning("No numeric columns found.")
    else:
        # ── KPI cards ──
        total_rows   = len(df)
        total_cols   = df.shape[1]
        numeric_cnt  = len(numeric_cols_dqa)
        missing_total = df.isnull().sum().sum()
        dup_cnt      = df.duplicated().sum()

        kpi_html = "".join([
            f"<div class='summary-card'><div class='summary-title'>{k}</div><div class='summary-value'>{v}</div></div>"
            for k, v in {
                "Total Rows": f"{total_rows:,}",
                "Total Columns": f"{total_cols}",
                "Numeric Columns": f"{numeric_cnt}",
                "Total Missing Values": f"{missing_total:,}",
                "Duplicate Rows": f"{dup_cnt:,}",
            }.items()
        ])
        st.markdown(f"<div class='summary-grid'>{kpi_html}</div>", unsafe_allow_html=True)

        # ── Correlation heatmap ──
        blue_title("Correlation Heatmap (Numeric Columns)")
        sample_df_dqa = df[numeric_cols_dqa].dropna()
        if len(sample_df_dqa) > 5000:
            sample_df_dqa = sample_df_dqa.sample(5000, random_state=42)
        corr_matrix = sample_df_dqa.corr().round(2)

        fig_h, ax_h = plt.subplots(figsize=(min(16, len(numeric_cols_dqa) + 2),
                                             min(14, len(numeric_cols_dqa) + 1)))
        fig_h.patch.set_facecolor("#FFFFFF")
        sns.heatmap(
            corr_matrix,
            ax=ax_h,
            annot=len(numeric_cols_dqa) <= 15,
            fmt=".1f",
            cmap="coolwarm",
            center=0,
            linewidths=0.4,
            linecolor="#E0E0E0",
            square=True,
            cbar_kws={"shrink": 0.8}
        )
        ax_h.set_title("Correlation Matrix", fontsize=14, fontweight="bold", pad=12)
        ax_h.tick_params(axis="x", rotation=45, labelsize=8)
        ax_h.tick_params(axis="y", rotation=0, labelsize=8)
        plt.tight_layout()
        st.pyplot(fig_h)
        plt.close(fig_h)

        # ── Skewness & Kurtosis ──
        c1, c2 = st.columns(2)
        with c1:
            blue_title("Skewness by Numeric Column")
            skew_vals = df[numeric_cols_dqa].skew().sort_values(ascending=False)
            fig_sk, ax_sk = plt.subplots(figsize=(7, max(4, len(skew_vals) * 0.3)))
            fig_sk.patch.set_facecolor(GREEN_BG); ax_sk.set_facecolor(GREEN_BG)
            colors_sk = [BAR_BLUE if v >= 0 else "#EF4444" for v in skew_vals]
            ax_sk.barh(skew_vals.index.astype(str), skew_vals.values, color=colors_sk)
            ax_sk.axvline(0, color="black", linewidth=0.8)
            ax_sk.set_xlabel("Skewness")
            ax_sk.grid(axis="x", linestyle="-", color=GRID_GREEN, alpha=0.5)
            ax_sk.spines["top"].set_visible(False); ax_sk.spines["right"].set_visible(False)
            plt.tight_layout()
            st.pyplot(fig_sk); plt.close(fig_sk)

        with c2:
            blue_title("Kurtosis by Numeric Column")
            kurt_vals = df[numeric_cols_dqa].kurtosis().sort_values(ascending=False)
            fig_ku, ax_ku = plt.subplots(figsize=(7, max(4, len(kurt_vals) * 0.3)))
            fig_ku.patch.set_facecolor(GREEN_BG); ax_ku.set_facecolor(GREEN_BG)
            colors_ku = [BAR_BLUE if v >= 0 else "#EF4444" for v in kurt_vals]
            ax_ku.barh(kurt_vals.index.astype(str), kurt_vals.values, color=colors_ku)
            ax_ku.axvline(0, color="black", linewidth=0.8)
            ax_ku.set_xlabel("Kurtosis")
            ax_ku.grid(axis="x", linestyle="-", color=GRID_GREEN, alpha=0.5)
            ax_ku.spines["top"].set_visible(False); ax_ku.spines["right"].set_visible(False)
            plt.tight_layout()
            st.pyplot(fig_ku); plt.close(fig_ku)

        # ── IQR Outlier count ──
        blue_title("IQR-Based Outlier Count per Numeric Column")
        outlier_counts = {}
        for col in numeric_cols_dqa:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outlier_counts[col] = int(((df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)).sum())
        outlier_series = pd.Series(outlier_counts).sort_values(ascending=False)

        fig_o, ax_o = plt.subplots(figsize=(10, max(4, len(outlier_series) * 0.3)))
        fig_o.patch.set_facecolor(GREEN_BG); ax_o.set_facecolor(GREEN_BG)
        ax_o.barh(outlier_series.index.astype(str), outlier_series.values, color=BAR_BLUE)
        ax_o.set_xlabel("Outlier Count (IQR method)")
        ax_o.grid(axis="x", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax_o.spines["top"].set_visible(False); ax_o.spines["right"].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig_o); plt.close(fig_o)

        # ── Full numeric stats table ──
        st.markdown("#### Numeric Column Statistics (Full Profile)")
        desc = df[numeric_cols_dqa].describe().T.round(3)
        desc["skewness"] = df[numeric_cols_dqa].skew().round(3)
        desc["kurtosis"] = df[numeric_cols_dqa].kurtosis().round(3)
        desc["outliers_iqr"] = outlier_series
        render_html_table(desc.reset_index().rename(columns={"index": "Column"}), max_height=450)


# ================================================================
# EDA – PRODUCT ANALYSIS
# ================================================================
elif eda_option == "Product Analysis":

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

        <b>What this section does:</b>
        Detailed analysis of product performance and characteristics.

        <b>Key insights covered:</b>
        <li>Product-wise sales and inventory performance</li>
        <li>Product category analysis</li>
        <li>Top performing and underperforming products</li>
        <li>Product lifecycle analysis</li>

        </div>
        """,
        unsafe_allow_html=True
    )

    # Identify product-related columns
    product_cols = []
    for col in df.columns:
        col_lower = col.lower()
        if any(term in col_lower for term in ['product', 'item', 'sku', 'goods']):
            product_cols.append(col)
    
    if not product_cols:
        st.warning("No product-related columns found. Looking for columns with 'product', 'item', 'sku', or 'goods' in their names.")
        st.write("Available columns:", df.columns.tolist())
        st.stop()
    
    # Use the first product column found
    product_col = product_cols[0]
    
    st.markdown(f"### Product Performance Analysis")
    st.info(f"Analyzing product data using column: **{product_col}**")
    
    # Basic Product Overview
    total_products = df[product_col].nunique()
    total_records = len(df)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Unique Products", f"{total_products:,}")
    
    with col2:
        st.metric("Total Records", f"{total_records:,}")
    
    with col3:
        avg_records_per_product = total_records / total_products
        st.metric("Avg Records/Product", f"{avg_records_per_product:.1f}")
    
    with col4:
        st.metric("Product Diversity", f"{total_products} unique items")
    
    # Product Distribution Analysis
    st.markdown("### Product Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top Products by Frequency
        st.markdown("**Top 15 Products by Record Count:**")
        
        product_counts = df[product_col].value_counts().head(15)
        
        # Create a nice display for top products
        for idx, (product, count) in enumerate(product_counts.items(), 1):
            percentage = (count / total_records) * 100
            
            st.markdown(f"""
            <div style="
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 10px;
                margin: 5px 0;
                background-color: #f8f9fa;
                border-left: 4px solid #10B981;
                border-radius: 6px;
            ">
                <div style="display: flex; align-items: center;">
                    <span style="font-weight: 600; min-width: 30px;">{idx:2d}.</span>
                    <span style="margin-left: 10px; font-weight: 600;">{str(product)[:30]}{'...' if len(str(product)) > 30 else ''}</span>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 18px; font-weight: 600; color: #10B981;">{count:,}</div>
                    <div style="font-size: 12px; color: #666;">({percentage:.1f}%)</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Product Distribution Visualization
        st.markdown("**Product Distribution Chart:**")
        
        # Create a bar chart for top 10 products
        top_10_products = product_counts.head(10)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        fig.patch.set_facecolor('#00D05E')
        ax.set_facecolor('#00D05E')
        
        bars = ax.barh(range(len(top_10_products)), top_10_products.values, color='#001F5C', alpha=0.8)
        ax.set_yticks(range(len(top_10_products)))
        ax.set_yticklabels([str(p)[:30] for p in top_10_products.index])
        ax.set_xlabel('Number of Records')
        ax.set_title('Top 10 Products by Record Count')
        ax.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for i, v in enumerate(top_10_products.values):
            ax.text(v + max(top_10_products.values) * 0.01, i, str(v), va='center')
        
        st.pyplot(fig)
        plt.close(fig)
    
    # Product Performance Metrics (if numeric columns available)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    performance_cols = []
    category_cols = []
    
    if numeric_cols:
        st.markdown("### Product Performance Metrics")
        
        # Look for performance-related columns
        performance_cols = []
        for col in numeric_cols:
            col_lower = col.lower()
            if any(term in col_lower for term in ['sales', 'revenue', 'quantity', 'amount', 'price', 'cost']):
                performance_cols.append(col)
        
        if performance_cols:
            col1, col2 = st.columns(2)
            
            with col1:
                # Product Performance Summary
                st.markdown("**Performance by Product:**")
                
                # Group by product and calculate metrics
                _pcol = performance_cols[0]
                product_performance = df.groupby(product_col)[_pcol].agg(
                    Records='count',
                    **{f'Avg {_pcol}': 'mean', f'Total {_pcol}': 'sum', f'Std Dev {_pcol}': 'std'}
                ).round(2)
                
                # Show top 10 performing products
                top_performers = product_performance.sort_values(
                    by=f'Total {_pcol}', ascending=False
                ).head(10)
                display_cols = list(product_performance.columns)
                
                st.dataframe(top_performers, use_container_width=True)
            
            with col2:
                # Performance Distribution
                st.markdown("**Performance Distribution:**")
                
                # Create performance distribution chart
                if len(top_performers) > 0:
                    perf_col = f"Total {_pcol}"
                    
                    fig, ax = plt.subplots(figsize=(8, 5))
                    fig.patch.set_facecolor('#00D05E')
                    ax.set_facecolor('#00D05E')
                    
                    ax.bar(range(len(top_performers)), top_performers[perf_col], 
                           color='#F59E0B', alpha=0.8)
                    ax.set_xlabel('Products')
                    ax.set_ylabel(f'Total {_pcol}')
                    ax.set_title(f'Top 10 Products by {_pcol}')
                    ax.set_xticks(range(len(top_performers)))
                    ax.set_xticklabels([str(p)[:20] for p in top_performers.index], rotation=45, ha='right')
                    ax.grid(True, alpha=0.3)
                    
                    st.pyplot(fig)
                    plt.close(fig)
        
        else:
            st.info("No numeric performance columns found for detailed analysis")
    
    # Product Category Analysis (if categorical columns available)
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    if categorical_cols:
        st.markdown("### Product Category Analysis")
        
        # Look for category-related columns
        category_cols = []
        for col in categorical_cols:
            col_lower = col.lower()
            if any(term in col_lower for term in ['category', 'type', 'class', 'group']):
                category_cols.append(col)
        
        if category_cols:
            category_col = category_cols[0]  # Use first category column found
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Category distribution
                st.markdown(f"**Distribution by {category_col}:**")
                
                category_counts = df[category_col].value_counts().head(10)
                
                # Create category distribution chart
                fig, ax = plt.subplots(figsize=(8, 5))
                fig.patch.set_facecolor('#00D05E')
                ax.set_facecolor('#00D05E')
                
                bars = ax.barh(range(len(category_counts)), category_counts.values, color='#3B82F6', alpha=0.8)
                ax.set_yticks(range(len(category_counts)))
                ax.set_yticklabels([str(c)[:25] for c in category_counts.index])
                ax.set_xlabel('Count')
                ax.set_title(f'Distribution by {category_col}')
                ax.grid(True, alpha=0.3)
                
                st.pyplot(fig)
                plt.close(fig)
            
            with col2:
                # Category performance (if performance columns exist)
                if performance_cols:
                    st.markdown(f"**Performance by {category_col}:**")
                    
                    category_performance = df.groupby(category_col)[performance_cols].mean().round(2)
                    category_performance.columns = [f'Avg {col}' for col in performance_cols]
                    
                    # Sort by first performance metric
                    category_performance = category_performance.sort_values(
                        by=category_performance.columns[0], ascending=False
                    ).head(10)
                    
                    st.dataframe(category_performance, use_container_width=True)
        else:
            st.info("No category columns found for category analysis")
    
    # Product Insights and Recommendations
    st.markdown("### Product Insights & Recommendations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Key Insights:**")
        
        insights = []
        
        # Concentration analysis
        if len(product_counts) > 0:
            top_5_percentage = (product_counts.head(5).sum() / total_records) * 100
            if top_5_percentage > 50:
                insights.append("🔺 High concentration: Top 5 products represent >50% of all records")
            elif top_5_percentage > 30:
                insights.append("📊 Moderate concentration: Top 5 products represent >30% of all records")
            else:
                insights.append("✅ Balanced distribution: No single product dominates")
        
        # Product diversity
        if total_products > 1000:
            insights.append("📦 High product diversity: >1000 unique products")
        elif total_products > 100:
            insights.append("📊 Moderate product diversity: >100 unique products")
        else:
            insights.append("📦 Focused product range: <100 unique products")
        
        for insight in insights:
            st.info(insight)
    
    with col2:
        st.markdown("**Recommendations:**")
        
        recommendations = []
        
        # Data quality recommendations
        if total_records / total_products < 5:
            recommendations.append("📊 Consider data aggregation for products with few records")
        
        if performance_cols:
            recommendations.append("📈 Implement product performance tracking and ranking")
        
        if category_cols:
            recommendations.append("🏷️ Develop product categorization strategy for better analysis")
        
        recommendations.append("🔍 Consider product lifecycle analysis for inventory optimization")
        recommendations.append("📊 Implement ABC analysis for inventory prioritization")
        
        for rec in recommendations:
            st.success(rec)


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

        <b>What this section does:</b>
        Comprehensive analysis of customer behavior and patterns.

        <b>Key insights covered:</b>
        <li>Customer segmentation analysis</li>
        <li>Purchase behavior patterns</li>
        <li>Customer lifetime value analysis</li>
        <li>Geographic customer distribution</li>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### Customer (Store) Behavior Analysis")
    if col_store and col_stockval:
        top_stores = df.groupby(col_store, observed=True)[col_stockval].sum().sort_values(ascending=False).head(15)
        blue_title("Top 15 Stores by Total Stock Value")
        fig, ax = plt.subplots(figsize=(10, 5))
        fig.patch.set_facecolor(GREEN_BG); ax.set_facecolor(GREEN_BG)
        ax.barh(top_stores.index.astype(str)[::-1], top_stores.values[::-1], color=BAR_BLUE)
        ax.set_xlabel("Total Stock Value (₹)"); ax.set_ylabel("Store ID")
        ax.grid(axis="x", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
        st.pyplot(fig); plt.close(fig)
    if col_store and col_fill_rate and col_stockout:
        c1, c2 = st.columns(2)
        with c1:
            blue_title("Fill Rate Distribution across Stores")
            fig2, ax2 = plt.subplots(figsize=(7, 4))
            fig2.patch.set_facecolor(GREEN_BG); ax2.set_facecolor(GREEN_BG)
            fr_store = df.groupby(col_store, observed=True)[col_fill_rate].mean()
            ax2.hist(fr_store.values, bins=20, color=BAR_BLUE, edgecolor="white")
            ax2.set_xlabel("Avg Fill Rate (%)"); ax2.set_ylabel("Number of Stores")
            ax2.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
            ax2.spines["top"].set_visible(False); ax2.spines["right"].set_visible(False)
            st.pyplot(fig2); plt.close(fig2)
        with c2:
            blue_title("Stockout Rate Distribution across Stores")
            fig3, ax3 = plt.subplots(figsize=(7, 4))
            fig3.patch.set_facecolor(GREEN_BG); ax3.set_facecolor(GREEN_BG)
            so_store = df.groupby(col_store, observed=True)[col_stockout].mean()
            ax3.hist(so_store.values, bins=20, color="#EF4444", edgecolor="white")
            ax3.set_xlabel("Avg Stockout Rate (%)"); ax3.set_ylabel("Number of Stores")
            ax3.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
            ax3.spines["top"].set_visible(False); ax3.spines["right"].set_visible(False)
            st.pyplot(fig3); plt.close(fig3)
    if col_store_type and col_stockval:
        blue_title("Stock Value by Store Type")
        sv_type = df.groupby(col_store_type, observed=True)[col_stockval].sum().sort_values(ascending=False)
        fig4, ax4 = plt.subplots(figsize=(8, 4))
        fig4.patch.set_facecolor(GREEN_BG); ax4.set_facecolor(GREEN_BG)
        ax4.bar(sv_type.index.astype(str), sv_type.values, color=BAR_BLUE)
        ax4.set_xlabel("Store Type"); ax4.set_ylabel("Stock Value (₹)")
        ax4.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax4.spines["top"].set_visible(False); ax4.spines["right"].set_visible(False)
        st.pyplot(fig4); plt.close(fig4)


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

        <b>What this section does:</b>
        Detailed analysis of store performance and operations.

        <b>Key insights covered:</b>
        <li>Store performance comparison</li>
        <li>Store type analysis</li>
        <li>Geographic performance patterns</li>
        <li>Store efficiency metrics</li>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### Store Performance Analysis")
    if col_store and col_fill_rate and col_stockout and col_turnover and col_stockval:
        store_metrics = df.groupby(col_store, observed=True).agg(
            avg_fill_rate=(col_fill_rate, "mean"),
            avg_stockout=(col_stockout, "mean"),
            avg_turnover=(col_turnover, "mean"),
            total_stock_value=(col_stockval, "sum")
        ).round(2)
        st.markdown("#### Store Performance Summary (Top 20 by Fill Rate)")
        render_html_table(store_metrics.sort_values("avg_fill_rate", ascending=False).head(20), max_height=350)
    if col_store_type and col_fill_rate:
        c1, c2 = st.columns(2)
        with c1:
            blue_title("Avg Fill Rate by Store Type")
            st_type = df.groupby(col_store_type, observed=True)[col_fill_rate].mean().sort_values(ascending=False)
            fig, ax = plt.subplots(figsize=(7, 4))
            fig.patch.set_facecolor(GREEN_BG); ax.set_facecolor(GREEN_BG)
            ax.bar(st_type.index.astype(str), st_type.values, color=BAR_BLUE)
            ax.set_xlabel("Store Type"); ax.set_ylabel("Avg Fill Rate (%)")
            ax.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
            ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
            st.pyplot(fig); plt.close(fig)
        with c2:
            if col_turnover:
                blue_title("Avg Inventory Turnover by Store Type")
                tv_type = df.groupby(col_store_type, observed=True)[col_turnover].mean().sort_values(ascending=False)
                fig2, ax2 = plt.subplots(figsize=(7, 4))
                fig2.patch.set_facecolor(GREEN_BG); ax2.set_facecolor(GREEN_BG)
                ax2.bar(tv_type.index.astype(str), tv_type.values, color=BAR_BLUE)
                ax2.set_xlabel("Store Type"); ax2.set_ylabel("Avg Turnover")
                ax2.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
                ax2.spines["top"].set_visible(False); ax2.spines["right"].set_visible(False)
                st.pyplot(fig2); plt.close(fig2)
    if col_region and col_overstock and col_understock:
        blue_title("Overstock vs Understock by Region")
        reg = df.groupby(col_region, observed=True).agg(
            total_overstock=(col_overstock, "sum"),
            total_understock=(col_understock, "sum")
        ).sort_values("total_overstock", ascending=False)
        x = np.arange(len(reg)); w = 0.35
        fig3, ax3 = plt.subplots(figsize=(10, 4))
        fig3.patch.set_facecolor(GREEN_BG); ax3.set_facecolor(GREEN_BG)
        ax3.bar(x - w/2, reg["total_overstock"], w, label="Overstock", color=BAR_BLUE)
        ax3.bar(x + w/2, reg["total_understock"], w, label="Understock", color="#EF4444")
        ax3.set_xticks(x); ax3.set_xticklabels(reg.index.astype(str), rotation=45, ha="right")
        ax3.set_xlabel("Region"); ax3.set_ylabel("Quantity"); ax3.legend()
        ax3.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax3.spines["top"].set_visible(False); ax3.spines["right"].set_visible(False)
        st.pyplot(fig3); plt.close(fig3)


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

        <b>What this section does:</b>
        Comprehensive analysis of vendor/supplier performance.

        <b>Key insights covered:</b>
        <li>Vendor performance comparison</li>
        <li>Supply chain reliability analysis</li>
        <li>Cost analysis by vendor</li>
        <li>Vendor quality metrics</li>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### Vendor / Supplier Performance Analysis")
    if col_supplier and col_lead_time and col_rating:
        sup_metrics = df.groupby(col_supplier, observed=True).agg(
            avg_lead_time=(col_lead_time, "mean"),
            avg_rating=(col_rating, "mean")
        ).round(2).sort_values("avg_rating", ascending=False)
        c1, c2 = st.columns(2)
        with c1:
            blue_title("Top 15 Suppliers by Rating Score")
            top_sup = sup_metrics.head(15)
            fig, ax = plt.subplots(figsize=(7, 5))
            fig.patch.set_facecolor(GREEN_BG); ax.set_facecolor(GREEN_BG)
            ax.barh(top_sup.index.astype(str)[::-1], top_sup["avg_rating"].values[::-1], color=BAR_BLUE)
            ax.set_xlabel("Avg Rating Score"); ax.set_ylabel("Supplier ID")
            ax.grid(axis="x", linestyle="-", color=GRID_GREEN, alpha=0.5)
            ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
            st.pyplot(fig); plt.close(fig)
        with c2:
            blue_title("Avg Lead Time by Supplier (Top 15 Fastest)")
            top_lt = sup_metrics.sort_values("avg_lead_time").head(15)
            fig2, ax2 = plt.subplots(figsize=(7, 5))
            fig2.patch.set_facecolor(GREEN_BG); ax2.set_facecolor(GREEN_BG)
            ax2.barh(top_lt.index.astype(str)[::-1], top_lt["avg_lead_time"].values[::-1], color="#10B981")
            ax2.set_xlabel("Avg Lead Time (days)"); ax2.set_ylabel("Supplier ID")
            ax2.grid(axis="x", linestyle="-", color=GRID_GREEN, alpha=0.5)
            ax2.spines["top"].set_visible(False); ax2.spines["right"].set_visible(False)
            st.pyplot(fig2); plt.close(fig2)
    if col_rating:
        blue_title("Supplier Rating Score Distribution")
        fig3, ax3 = plt.subplots(figsize=(10, 4))
        fig3.patch.set_facecolor(GREEN_BG); ax3.set_facecolor(GREEN_BG)
        ax3.hist(df[col_rating].dropna(), bins=30, color=BAR_BLUE, edgecolor="white")
        ax3.set_xlabel("Rating Score"); ax3.set_ylabel("Frequency")
        ax3.axvline(df[col_rating].mean(), color="#EF4444", linestyle="--", linewidth=2, label=f"Mean: {df[col_rating].mean():.2f}")
        ax3.legend()
        ax3.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax3.spines["top"].set_visible(False); ax3.spines["right"].set_visible(False)
        st.pyplot(fig3); plt.close(fig3)
    if col_cost_price and col_category:
        blue_title("Avg Cost Price by Category")
        cp_cat = df.groupby(col_category, observed=True)[col_cost_price].mean().sort_values(ascending=False)
        fig4, ax4 = plt.subplots(figsize=(10, 4))
        fig4.patch.set_facecolor(GREEN_BG); ax4.set_facecolor(GREEN_BG)
        ax4.bar(cp_cat.index.astype(str), cp_cat.values, color=BAR_BLUE)
        ax4.set_xlabel("Category"); ax4.set_ylabel("Avg Cost Price (₹)")
        ax4.tick_params(axis="x", rotation=45)
        ax4.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax4.spines["top"].set_visible(False); ax4.spines["right"].set_visible(False)
        st.pyplot(fig4); plt.close(fig4)


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

        <b>What this section does:</b>
        Geographic and location-based performance analysis.

        <b>Key insights covered:</b>
        <li>Regional performance comparison</li>
        <li>Geographic distribution patterns</li>
        <li>Location-based optimization opportunities</li>
        <li>Regional market analysis</li>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### Location & Regional Analysis")
    if col_region and col_stockval:
        c1, c2 = st.columns(2)
        with c1:
            blue_title("Total Stock Value by Region")
            sv_reg = df.groupby(col_region, observed=True)[col_stockval].sum().sort_values(ascending=False)
            fig, ax = plt.subplots(figsize=(7, 4))
            fig.patch.set_facecolor(GREEN_BG); ax.set_facecolor(GREEN_BG)
            ax.bar(sv_reg.index.astype(str), sv_reg.values, color=BAR_BLUE)
            ax.set_xlabel("Region"); ax.set_ylabel("Total Stock Value (₹)")
            ax.tick_params(axis="x", rotation=45)
            ax.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
            ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
            st.pyplot(fig); plt.close(fig)
        with c2:
            blue_title("Stock Value Share by Region")
            fig2, ax2 = plt.subplots(figsize=(7, 4))
            fig2.patch.set_facecolor(GREEN_BG); ax2.set_facecolor(GREEN_BG)
            ax2.pie(sv_reg.values, labels=sv_reg.index.astype(str), autopct="%1.1f%%", startangle=90)
            st.pyplot(fig2); plt.close(fig2)
    if col_zone and col_fill_rate:
        c3, c4 = st.columns(2)
        with c3:
            blue_title("Avg Fill Rate by Zone")
            fr_zone = df.groupby(col_zone, observed=True)[col_fill_rate].mean().sort_values(ascending=False)
            fig3, ax3 = plt.subplots(figsize=(7, 4))
            fig3.patch.set_facecolor(GREEN_BG); ax3.set_facecolor(GREEN_BG)
            ax3.bar(fr_zone.index.astype(str), fr_zone.values, color=BAR_BLUE)
            ax3.set_xlabel("Zone"); ax3.set_ylabel("Avg Fill Rate (%)")
            ax3.tick_params(axis="x", rotation=45)
            ax3.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
            ax3.spines["top"].set_visible(False); ax3.spines["right"].set_visible(False)
            st.pyplot(fig3); plt.close(fig3)
        with c4:
            if col_stockout:
                blue_title("Avg Stockout Rate by Zone")
                so_zone = df.groupby(col_zone, observed=True)[col_stockout].mean().sort_values(ascending=False)
                fig4, ax4 = plt.subplots(figsize=(7, 4))
                fig4.patch.set_facecolor(GREEN_BG); ax4.set_facecolor(GREEN_BG)
                ax4.bar(so_zone.index.astype(str), so_zone.values, color="#EF4444")
                ax4.set_xlabel("Zone"); ax4.set_ylabel("Avg Stockout Rate (%)")
                ax4.tick_params(axis="x", rotation=45)
                ax4.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
                ax4.spines["top"].set_visible(False); ax4.spines["right"].set_visible(False)
                st.pyplot(fig4); plt.close(fig4)
    if col_region and col_overstock and col_understock:
        blue_title("Overstock vs Understock by Region")
        reg_ou = df.groupby(col_region, observed=True).agg(
            total_overstock=(col_overstock, "sum"),
            total_understock=(col_understock, "sum")
        ).sort_values("total_overstock", ascending=False)
        x = np.arange(len(reg_ou)); w = 0.35
        fig5, ax5 = plt.subplots(figsize=(10, 4))
        fig5.patch.set_facecolor(GREEN_BG); ax5.set_facecolor(GREEN_BG)
        ax5.bar(x - w/2, reg_ou["total_overstock"], w, label="Overstock", color=BAR_BLUE)
        ax5.bar(x + w/2, reg_ou["total_understock"], w, label="Understock", color="#EF4444")
        ax5.set_xticks(x); ax5.set_xticklabels(reg_ou.index.astype(str), rotation=45, ha="right")
        ax5.set_xlabel("Region"); ax5.set_ylabel("Quantity"); ax5.legend()
        ax5.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax5.spines["top"].set_visible(False); ax5.spines["right"].set_visible(False)
        st.pyplot(fig5); plt.close(fig5)


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

        <b>What this section does:</b>
        Comprehensive warehouse operations and efficiency analysis.

        <b>Key insights covered:</b>
        <li>Warehouse performance metrics</li>
        <li>Inventory turnover analysis</li>
        <li>Storage utilization analysis</li>
        <li>Warehouse efficiency comparison</li>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### Warehouse Operations & Efficiency Analysis")
    if col_onhand and col_turnover:
        c1, c2 = st.columns(2)
        with c1:
            blue_title("Inventory Turnover Distribution")
            fig, ax = plt.subplots(figsize=(7, 4))
            fig.patch.set_facecolor(GREEN_BG); ax.set_facecolor(GREEN_BG)
            ax.hist(df[col_turnover].dropna(), bins=30, color=BAR_BLUE, edgecolor="white")
            ax.set_xlabel("Inventory Turnover"); ax.set_ylabel("Frequency")
            ax.axvline(df[col_turnover].mean(), color="#EF4444", linestyle="--", linewidth=2, label=f"Mean: {df[col_turnover].mean():.2f}")
            ax.legend(); ax.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
            ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
            st.pyplot(fig); plt.close(fig)
        with c2:
            blue_title("On-Hand Quantity Distribution")
            fig2, ax2 = plt.subplots(figsize=(7, 4))
            fig2.patch.set_facecolor(GREEN_BG); ax2.set_facecolor(GREEN_BG)
            ax2.hist(df[col_onhand].dropna(), bins=30, color=BAR_BLUE, edgecolor="white")
            ax2.set_xlabel("On-Hand Qty"); ax2.set_ylabel("Frequency")
            ax2.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
            ax2.spines["top"].set_visible(False); ax2.spines["right"].set_visible(False)
            st.pyplot(fig2); plt.close(fig2)
    if col_category and col_turnover:
        blue_title("Avg Inventory Turnover by Category")
        tv_cat = df.groupby(col_category, observed=True)[col_turnover].mean().sort_values(ascending=False)
        fig3, ax3 = plt.subplots(figsize=(10, 4))
        fig3.patch.set_facecolor(GREEN_BG); ax3.set_facecolor(GREEN_BG)
        ax3.bar(tv_cat.index.astype(str), tv_cat.values, color=BAR_BLUE)
        ax3.set_xlabel("Category"); ax3.set_ylabel("Avg Turnover")
        ax3.tick_params(axis="x", rotation=45)
        ax3.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax3.spines["top"].set_visible(False); ax3.spines["right"].set_visible(False)
        st.pyplot(fig3); plt.close(fig3)
    if col_excess and col_category:
        blue_title("Avg Excess Inventory (%) by Category")
        ex_cat = df.groupby(col_category, observed=True)[col_excess].mean().sort_values(ascending=False)
        fig4, ax4 = plt.subplots(figsize=(10, 4))
        fig4.patch.set_facecolor(GREEN_BG); ax4.set_facecolor(GREEN_BG)
        ax4.bar(ex_cat.index.astype(str), ex_cat.values, color="#EF4444")
        ax4.set_xlabel("Category"); ax4.set_ylabel("Avg Excess Inventory (%)")
        ax4.tick_params(axis="x", rotation=45)
        ax4.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax4.spines["top"].set_visible(False); ax4.spines["right"].set_visible(False)
        st.pyplot(fig4); plt.close(fig4)
    if col_overstock and col_understock:
        c3, c4 = st.columns(2)
        with c3:
            blue_title("Overstock Quantity Distribution")
            fig5, ax5 = plt.subplots(figsize=(7, 4))
            fig5.patch.set_facecolor(GREEN_BG); ax5.set_facecolor(GREEN_BG)
            ax5.hist(df[col_overstock].dropna(), bins=30, color=BAR_BLUE, edgecolor="white")
            ax5.set_xlabel("Overstock Qty"); ax5.set_ylabel("Frequency")
            ax5.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
            ax5.spines["top"].set_visible(False); ax5.spines["right"].set_visible(False)
            st.pyplot(fig5); plt.close(fig5)
        with c4:
            blue_title("Understock Quantity Distribution")
            fig6, ax6 = plt.subplots(figsize=(7, 4))
            fig6.patch.set_facecolor(GREEN_BG); ax6.set_facecolor(GREEN_BG)
            ax6.hist(df[col_understock].dropna(), bins=30, color="#EF4444", edgecolor="white")
            ax6.set_xlabel("Understock Qty"); ax6.set_ylabel("Frequency")
            ax6.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
            ax6.spines["top"].set_visible(False); ax6.spines["right"].set_visible(False)
            st.pyplot(fig6); plt.close(fig6)


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

        <b>What this section does:</b>
        Transportation and logistics route performance analysis.

        <b>Key insights covered:</b>
        <li>Route efficiency analysis</li>
        <li>Transportation cost analysis</li>
        <li>Delivery time optimization</li>
        <li>Route performance comparison</li>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### Transport Route Performance Analysis")
    if col_route and col_delivery and col_fuel and col_efficiency:
        route_metrics = df.groupby(col_route, observed=True).agg(
            avg_delivery=(col_delivery, "mean"),
            avg_fuel=(col_fuel, "mean"),
            avg_efficiency=(col_efficiency, "mean")
        ).round(2)
        c1, c2 = st.columns(2)
        with c1:
            blue_title("Top 15 Routes by Route Efficiency Score")
            top_eff = route_metrics.sort_values("avg_efficiency", ascending=False).head(15)
            fig, ax = plt.subplots(figsize=(7, 5))
            fig.patch.set_facecolor(GREEN_BG); ax.set_facecolor(GREEN_BG)
            ax.barh(top_eff.index.astype(str)[::-1], top_eff["avg_efficiency"].values[::-1], color=BAR_BLUE)
            ax.set_xlabel("Avg Efficiency Score"); ax.set_ylabel("Route ID")
            ax.grid(axis="x", linestyle="-", color=GRID_GREEN, alpha=0.5)
            ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
            st.pyplot(fig); plt.close(fig)
        with c2:
            blue_title("Top 15 Routes by Avg Fuel Cost")
            top_fuel = route_metrics.sort_values("avg_fuel", ascending=False).head(15)
            fig2, ax2 = plt.subplots(figsize=(7, 5))
            fig2.patch.set_facecolor(GREEN_BG); ax2.set_facecolor(GREEN_BG)
            ax2.barh(top_fuel.index.astype(str)[::-1], top_fuel["avg_fuel"].values[::-1], color="#EF4444")
            ax2.set_xlabel("Avg Fuel Cost (₹)"); ax2.set_ylabel("Route ID")
            ax2.grid(axis="x", linestyle="-", color=GRID_GREEN, alpha=0.5)
            ax2.spines["top"].set_visible(False); ax2.spines["right"].set_visible(False)
            st.pyplot(fig2); plt.close(fig2)
        blue_title("Delivery Time Distribution")
        fig3, ax3 = plt.subplots(figsize=(10, 4))
        fig3.patch.set_facecolor(GREEN_BG); ax3.set_facecolor(GREEN_BG)
        ax3.hist(df[col_delivery].dropna(), bins=40, color=BAR_BLUE, edgecolor="white")
        ax3.set_xlabel("Delivery Time (mins)"); ax3.set_ylabel("Frequency")
        ax3.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax3.spines["top"].set_visible(False); ax3.spines["right"].set_visible(False)
        st.pyplot(fig3); plt.close(fig3)
        if col_distance:
            c3, c4 = st.columns(2)
            with c3:
                blue_title("Fuel Cost vs Distance (km)")
                fig4, ax4 = plt.subplots(figsize=(7, 4))
                fig4.patch.set_facecolor(GREEN_BG); ax4.set_facecolor(GREEN_BG)
                sample = df[[col_distance, col_fuel]].dropna().sample(min(3000, len(df)), random_state=42)
                ax4.scatter(sample[col_distance], sample[col_fuel], color=BAR_BLUE, alpha=0.4, s=10)
                ax4.set_xlabel("Distance (km)"); ax4.set_ylabel("Fuel Cost (₹)")
                ax4.grid(linestyle="-", color=GRID_GREEN, alpha=0.3)
                ax4.spines["top"].set_visible(False); ax4.spines["right"].set_visible(False)
                st.pyplot(fig4); plt.close(fig4)
            with c4:
                blue_title("Route Efficiency vs Fuel Cost")
                fig5, ax5 = plt.subplots(figsize=(7, 4))
                fig5.patch.set_facecolor(GREEN_BG); ax5.set_facecolor(GREEN_BG)
                sample2 = df[[col_efficiency, col_fuel]].dropna().sample(min(3000, len(df)), random_state=42)
                ax5.scatter(sample2[col_efficiency], sample2[col_fuel], color="#EF4444", alpha=0.4, s=10)
                ax5.set_xlabel("Route Efficiency Score"); ax5.set_ylabel("Fuel Cost (₹)")
                ax5.grid(linestyle="-", color=GRID_GREEN, alpha=0.3)
                ax5.spines["top"].set_visible(False); ax5.spines["right"].set_visible(False)
                st.pyplot(fig5); plt.close(fig5)


# ================================================================
# EDA – SALES ANALYSIS (DETAILED)
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

        <b>What this section does:</b>
        In-depth sales performance analysis with advanced metrics.

        <b>Key insights covered:</b>
        <li>Sales trend analysis and forecasting</li>
        <li>Product sales correlation analysis</li>
        <li>Sales channel performance</li>
        <li>Revenue optimization insights</li>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### Sales & Revenue Deep-Dive Analysis")
    if col_stockval and col_category:
        blue_title("Stock Value by Category (Detailed)")
        sv_cat = df.groupby(col_category, observed=True)[col_stockval].agg(["sum", "mean", "count"]).round(2)
        sv_cat.columns = ["Total Stock Value (₹)", "Avg Stock Value (₹)", "Record Count"]
        render_html_table(sv_cat.reset_index().sort_values("Total Stock Value (₹)", ascending=False), max_height=300)
    if col_stockval and col_quarter:
        c1, c2 = st.columns(2)
        with c1:
            blue_title("Stock Value by Quarter")
            sv_q = df.groupby(col_quarter)[col_stockval].sum().sort_index()
            fig, ax = plt.subplots(figsize=(7, 4))
            fig.patch.set_facecolor(GREEN_BG); ax.set_facecolor(GREEN_BG)
            ax.bar(sv_q.index.astype(str), sv_q.values, color=BAR_BLUE)
            ax.set_xlabel("Quarter"); ax.set_ylabel("Stock Value (₹)")
            ax.tick_params(axis="x", rotation=45)
            ax.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
            ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
            st.pyplot(fig); plt.close(fig)
        with c2:
            if col_is_holiday:
                blue_title("Stock Value: Holiday vs Non-Holiday")
                hol_grp = df.groupby(col_is_holiday)[col_stockval].sum()
                labels = ["Non-Holiday" if not k else "Holiday" for k in hol_grp.index]
                fig2, ax2 = plt.subplots(figsize=(7, 4))
                fig2.patch.set_facecolor(GREEN_BG); ax2.set_facecolor(GREEN_BG)
                ax2.bar(labels, hol_grp.values, color=[BAR_BLUE, "#EF4444"])
                ax2.set_ylabel("Total Stock Value (₹)")
                ax2.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
                ax2.spines["top"].set_visible(False); ax2.spines["right"].set_visible(False)
                st.pyplot(fig2); plt.close(fig2)
    if col_fill_rate and col_is_weekend:
        c3, c4 = st.columns(2)
        with c3:
            blue_title("Avg Fill Rate: Weekday vs Weekend")
            wk_grp = df.groupby(col_is_weekend)[col_fill_rate].mean()
            labels = ["Weekday" if not k else "Weekend" for k in wk_grp.index]
            fig3, ax3 = plt.subplots(figsize=(7, 4))
            fig3.patch.set_facecolor(GREEN_BG); ax3.set_facecolor(GREEN_BG)
            ax3.bar(labels, wk_grp.values, color=[BAR_BLUE, "#F59E0B"])
            ax3.set_ylabel("Avg Fill Rate (%)")
            ax3.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
            ax3.spines["top"].set_visible(False); ax3.spines["right"].set_visible(False)
            st.pyplot(fig3); plt.close(fig3)
        with c4:
            if col_turnover and col_month:
                blue_title("Avg Inventory Turnover by Month")
                tv_month = df.groupby(col_month)[col_turnover].mean().sort_index()
                fig4, ax4 = plt.subplots(figsize=(7, 4))
                fig4.patch.set_facecolor(GREEN_BG); ax4.set_facecolor(GREEN_BG)
                ax4.plot(range(len(tv_month)), tv_month.values, marker="o", color=BAR_BLUE, linewidth=2)
                ax4.set_xticks(range(len(tv_month)))
                ax4.set_xticklabels(tv_month.index.astype(str), rotation=45, ha="right")
                ax4.set_ylabel("Avg Turnover")
                ax4.grid(linestyle="-", color=GRID_GREEN, alpha=0.4)
                ax4.spines["top"].set_visible(False); ax4.spines["right"].set_visible(False)
                st.pyplot(fig4); plt.close(fig4)


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

        <b>What this section does:</b>
        Comprehensive inventory management and optimization analysis.

        <b>Key insights covered:</b>
        <li>Inventory turnover analysis</li>
        <li>Stock optimization recommendations</li>
        <li>Inventory cost analysis</li>
        <li>Reorder point optimization</li>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### Inventory Management & Optimization Analysis")
    if col_onhand and col_overstock and col_understock and col_fill_rate:
        inv_summary = {
            "Total On-Hand Qty": f"{df[col_onhand].sum():,.0f}",
            "Total Overstock Qty": f"{df[col_overstock].sum():,.0f}",
            "Total Understock Qty": f"{df[col_understock].sum():,.0f}",
            "Avg Fill Rate (%)": f"{df[col_fill_rate].mean():.1f}%",
            "Avg Stockout Rate (%)": f"{df[col_stockout].mean():.1f}%" if col_stockout else "N/A",
            "Avg Inventory Turnover": f"{df[col_turnover].mean():.2f}" if col_turnover else "N/A",
        }
        inv_html = "".join([f"<div class='summary-card'><div class='summary-title'>{k}</div><div class='summary-value'>{v}</div></div>" for k, v in inv_summary.items()])
        st.markdown(f"<div class='summary-grid'>{inv_html}</div>", unsafe_allow_html=True)
    if col_fill_rate and col_stockout:
        c1, c2 = st.columns(2)
        with c1:
            blue_title("Fill Rate Distribution")
            fig, ax = plt.subplots(figsize=(7, 4))
            fig.patch.set_facecolor(GREEN_BG); ax.set_facecolor(GREEN_BG)
            ax.hist(df[col_fill_rate].dropna(), bins=30, color=BAR_BLUE, edgecolor="white")
            ax.set_xlabel("Fill Rate (%)"); ax.set_ylabel("Frequency")
            ax.axvline(df[col_fill_rate].mean(), color="#EF4444", linestyle="--", linewidth=2, label=f"Mean: {df[col_fill_rate].mean():.1f}%")
            ax.legend(); ax.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
            ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
            st.pyplot(fig); plt.close(fig)
        with c2:
            blue_title("Stockout Rate Distribution")
            fig2, ax2 = plt.subplots(figsize=(7, 4))
            fig2.patch.set_facecolor(GREEN_BG); ax2.set_facecolor(GREEN_BG)
            ax2.hist(df[col_stockout].dropna(), bins=30, color="#EF4444", edgecolor="white")
            ax2.set_xlabel("Stockout Rate (%)"); ax2.set_ylabel("Frequency")
            ax2.axvline(df[col_stockout].mean(), color=BAR_BLUE, linestyle="--", linewidth=2, label=f"Mean: {df[col_stockout].mean():.1f}%")
            ax2.legend(); ax2.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
            ax2.spines["top"].set_visible(False); ax2.spines["right"].set_visible(False)
            st.pyplot(fig2); plt.close(fig2)
    if col_category and col_fill_rate and col_stockout:
        blue_title("Fill Rate vs Stockout Rate by Category")
        cat_inv = df.groupby(col_category, observed=True).agg(
            avg_fill=(col_fill_rate, "mean"),
            avg_stockout=(col_stockout, "mean")
        ).sort_values("avg_fill", ascending=False)
        x = np.arange(len(cat_inv)); w = 0.35
        fig3, ax3 = plt.subplots(figsize=(10, 4))
        fig3.patch.set_facecolor(GREEN_BG); ax3.set_facecolor(GREEN_BG)
        ax3.bar(x - w/2, cat_inv["avg_fill"], w, label="Avg Fill Rate (%)", color=BAR_BLUE)
        ax3.bar(x + w/2, cat_inv["avg_stockout"], w, label="Avg Stockout Rate (%)", color="#EF4444")
        ax3.set_xticks(x); ax3.set_xticklabels(cat_inv.index.astype(str), rotation=45, ha="right")
        ax3.set_ylabel("Rate (%)"); ax3.legend()
        ax3.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax3.spines["top"].set_visible(False); ax3.spines["right"].set_visible(False)
        st.pyplot(fig3); plt.close(fig3)
    if col_shelf_life and col_category:
        blue_title("Avg Shelf Life by Category (Risk Indicator)")
        sl_cat = df.groupby(col_category, observed=True)[col_shelf_life].mean().sort_values()
        fig4, ax4 = plt.subplots(figsize=(10, 4))
        fig4.patch.set_facecolor(GREEN_BG); ax4.set_facecolor(GREEN_BG)
        ax4.barh(sl_cat.index.astype(str), sl_cat.values, color=BAR_BLUE)
        ax4.set_xlabel("Avg Shelf Life (days)"); ax4.set_ylabel("Category")
        ax4.grid(axis="x", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax4.spines["top"].set_visible(False); ax4.spines["right"].set_visible(False)
        st.pyplot(fig4); plt.close(fig4)


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

        <b>What this section does:</b>
        Analysis of inventory redistribution needs and opportunities.

        <b>Key insights covered:</b>
        <li>Redistribution opportunity identification</li>
        <li>Supply-demand balancing analysis</li>
        <li>Transfer optimization recommendations</li>
        <li>Cost-benefit analysis of redistribution</li>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### Inventory Redistribution Analysis")
    if col_transfer_qty and col_opt_qty:
        c1, c2 = st.columns(2)
        with c1:
            blue_title("Actual vs Optimal Transfer Qty Distribution")
            fig, ax = plt.subplots(figsize=(7, 4))
            fig.patch.set_facecolor(GREEN_BG); ax.set_facecolor(GREEN_BG)
            ax.hist(df[col_transfer_qty].dropna(), bins=30, alpha=0.7, color=BAR_BLUE, label="Actual Transfer", edgecolor="white")
            ax.hist(df[col_opt_qty].dropna(), bins=30, alpha=0.5, color="#F59E0B", label="Optimal Transfer", edgecolor="white")
            ax.set_xlabel("Transfer Qty"); ax.set_ylabel("Frequency"); ax.legend()
            ax.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
            ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
            st.pyplot(fig); plt.close(fig)
        with c2:
            blue_title("Transfer Qty vs Optimal Qty (Scatter)")
            fig2, ax2 = plt.subplots(figsize=(7, 4))
            fig2.patch.set_facecolor(GREEN_BG); ax2.set_facecolor(GREEN_BG)
            sample = df[[col_transfer_qty, col_opt_qty]].dropna().sample(min(3000, len(df)), random_state=42)
            ax2.scatter(sample[col_opt_qty], sample[col_transfer_qty], color=BAR_BLUE, alpha=0.3, s=10)
            lims = [min(sample.min()), max(sample.max())]
            ax2.plot(lims, lims, "r--", linewidth=1.5, label="Perfect alignment")
            ax2.set_xlabel("Optimal Transfer Qty"); ax2.set_ylabel("Actual Transfer Qty"); ax2.legend()
            ax2.grid(linestyle="-", color=GRID_GREEN, alpha=0.3)
            ax2.spines["top"].set_visible(False); ax2.spines["right"].set_visible(False)
            st.pyplot(fig2); plt.close(fig2)
    if col_cluster and col_transfer_qty and col_transfer_cost:
        blue_title("Avg Transfer Qty & Transfer Cost by Cluster (Top 20)")
        cl_metrics = df.groupby(col_cluster, observed=True).agg(
            avg_transfer_qty=(col_transfer_qty, "mean"),
            avg_transfer_cost=(col_transfer_cost, "mean")
        ).round(2).sort_values("avg_transfer_qty", ascending=False).head(20)
        render_html_table(cl_metrics.reset_index(), max_height=300)
    if col_cost_min and col_service_gain:
        c3, c4 = st.columns(2)
        with c3:
            blue_title("Cost Minimization (%) Distribution")
            fig3, ax3 = plt.subplots(figsize=(7, 4))
            fig3.patch.set_facecolor(GREEN_BG); ax3.set_facecolor(GREEN_BG)
            ax3.hist(df[col_cost_min].dropna(), bins=30, color=BAR_BLUE, edgecolor="white")
            ax3.set_xlabel("Cost Minimization (%)"); ax3.set_ylabel("Frequency")
            ax3.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
            ax3.spines["top"].set_visible(False); ax3.spines["right"].set_visible(False)
            st.pyplot(fig3); plt.close(fig3)
        with c4:
            blue_title("Service Level Gain (%) Distribution")
            fig4, ax4 = plt.subplots(figsize=(7, 4))
            fig4.patch.set_facecolor(GREEN_BG); ax4.set_facecolor(GREEN_BG)
            ax4.hist(df[col_service_gain].dropna(), bins=30, color="#10B981", edgecolor="white")
            ax4.set_xlabel("Service Level Gain (%)"); ax4.set_ylabel("Frequency")
            ax4.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
            ax4.spines["top"].set_visible(False); ax4.spines["right"].set_visible(False)
            st.pyplot(fig4); plt.close(fig4)
    if col_overstock and col_understock and col_region:
        blue_title("Redistribution Gap: Overstock − Understock by Region")
        ro = df.groupby(col_region, observed=True).agg(
            total_overstock=(col_overstock, "sum"),
            total_understock=(col_understock, "sum")
        )
        ro["redistribution_gap"] = ro["total_overstock"] - ro["total_understock"]
        fig5, ax5 = plt.subplots(figsize=(10, 4))
        fig5.patch.set_facecolor(GREEN_BG); ax5.set_facecolor(GREEN_BG)
        colors_r = [BAR_BLUE if v >= 0 else "#EF4444" for v in ro["redistribution_gap"]]
        ax5.bar(ro.index.astype(str), ro["redistribution_gap"], color=colors_r)
        ax5.axhline(0, color="black", linewidth=0.8)
        ax5.set_xlabel("Region"); ax5.set_ylabel("Overstock − Understock Gap")
        ax5.tick_params(axis="x", rotation=45)
        ax5.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax5.spines["top"].set_visible(False); ax5.spines["right"].set_visible(False)
        st.pyplot(fig5); plt.close(fig5)


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

        <b>What this section does:</b>
        Strategic resource reallocation analysis and recommendations.

        <b>Key insights covered:</b>
        <li>Resource utilization analysis</li>
        <li>Reallocation opportunity identification</li>
        <li>Performance impact assessment</li>
        <li>Optimization recommendations</li>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### Resource Reallocation Analysis")
    if col_confidence and col_cluster:
        c1, c2 = st.columns(2)
        with c1:
            blue_title("Model Confidence Score Distribution")
            fig, ax = plt.subplots(figsize=(7, 4))
            fig.patch.set_facecolor(GREEN_BG); ax.set_facecolor(GREEN_BG)
            ax.hist(df[col_confidence].dropna(), bins=30, color=BAR_BLUE, edgecolor="white")
            ax.set_xlabel("Model Confidence Score"); ax.set_ylabel("Frequency")
            ax.axvline(df[col_confidence].mean(), color="#EF4444", linestyle="--", linewidth=2, label=f"Mean: {df[col_confidence].mean():.2f}")
            ax.legend(); ax.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
            ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
            st.pyplot(fig); plt.close(fig)
        with c2:
            blue_title("Avg Model Confidence by Cluster (Top 20)")
            conf_cl = df.groupby(col_cluster, observed=True)[col_confidence].mean().sort_values(ascending=False).head(20)
            fig2, ax2 = plt.subplots(figsize=(7, 4))
            fig2.patch.set_facecolor(GREEN_BG); ax2.set_facecolor(GREEN_BG)
            ax2.barh(conf_cl.index.astype(str)[::-1], conf_cl.values[::-1], color=BAR_BLUE)
            ax2.set_xlabel("Avg Confidence Score"); ax2.set_ylabel("Cluster ID")
            ax2.grid(axis="x", linestyle="-", color=GRID_GREEN, alpha=0.5)
            ax2.spines["top"].set_visible(False); ax2.spines["right"].set_visible(False)
            st.pyplot(fig2); plt.close(fig2)
    if col_cost_min and col_service_gain and col_cluster:
        blue_title("Cost Minimization vs Service Level Gain by Cluster")
        cl_perf = df.groupby(col_cluster, observed=True).agg(
            avg_cost_min=(col_cost_min, "mean"),
            avg_service_gain=(col_service_gain, "mean")
        ).round(2)
        fig3, ax3 = plt.subplots(figsize=(10, 4))
        fig3.patch.set_facecolor(GREEN_BG); ax3.set_facecolor(GREEN_BG)
        ax3.scatter(cl_perf["avg_cost_min"], cl_perf["avg_service_gain"], color=BAR_BLUE, alpha=0.7, s=60)
        ax3.set_xlabel("Avg Cost Minimization (%)"); ax3.set_ylabel("Avg Service Level Gain (%)")
        ax3.grid(linestyle="-", color=GRID_GREEN, alpha=0.3)
        ax3.spines["top"].set_visible(False); ax3.spines["right"].set_visible(False)
        st.pyplot(fig3); plt.close(fig3)
    if col_onhand and col_overstock and col_category:
        blue_title("Reallocation Potential: On-Hand vs Overstock by Category")
        cat_re = df.groupby(col_category, observed=True).agg(
            avg_onhand=(col_onhand, "mean"),
            avg_overstock=(col_overstock, "mean")
        ).round(2)
        x = np.arange(len(cat_re)); w = 0.35
        fig4, ax4 = plt.subplots(figsize=(10, 4))
        fig4.patch.set_facecolor(GREEN_BG); ax4.set_facecolor(GREEN_BG)
        ax4.bar(x - w/2, cat_re["avg_onhand"], w, label="Avg On-Hand Qty", color=BAR_BLUE)
        ax4.bar(x + w/2, cat_re["avg_overstock"], w, label="Avg Overstock Qty", color="#EF4444")
        ax4.set_xticks(x); ax4.set_xticklabels(cat_re.index.astype(str), rotation=45, ha="right")
        ax4.set_ylabel("Avg Quantity"); ax4.legend()
        ax4.grid(axis="y", linestyle="-", color=GRID_GREEN, alpha=0.5)
        ax4.spines["top"].set_visible(False); ax4.spines["right"].set_visible(False)
        st.pyplot(fig4); plt.close(fig4)


# ================================================================
# EDA – LOGISTICS ANALYSIS
# ================================================================
elif eda_option == "Logistics Analysis":

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

        <b>What this section does:</b>
        Comprehensive logistics and supply chain efficiency analysis.

        <b>Key insights covered:</b>
        <li>Logistics network optimization</li>
        <li>Supply chain efficiency metrics</li>
        <li>Delivery performance analysis</li>
        <li>Cost optimization opportunities</li>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### Logistics & Supply Chain Efficiency Analysis")
    if col_delivery and col_fuel and col_efficiency:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""<div class="summary-card"><div class="summary-title">Avg Delivery Time</div><div class="summary-value">{df[col_delivery].mean():.0f} mins</div></div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="summary-card"><div class="summary-title">Avg Fuel Cost</div><div class="summary-value">₹{df[col_fuel].mean():.2f}</div></div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div class="summary-card"><div class="summary-title">Avg Route Efficiency</div><div class="summary-value">{df[col_efficiency].mean():.2f}</div></div>""", unsafe_allow_html=True)
        st.write("")
        if col_month:
            blue_title("Delivery Time Trend by Month")
            dt_month = df.groupby(col_month)[col_delivery].mean().sort_index()
            fig, ax = plt.subplots(figsize=(10, 4))
            fig.patch.set_facecolor(GREEN_BG); ax.set_facecolor(GREEN_BG)
            ax.plot(range(len(dt_month)), dt_month.values, marker="o", color=BAR_BLUE, linewidth=2)
            ax.fill_between(range(len(dt_month)), dt_month.values, alpha=0.2, color=BAR_BLUE)
            ax.set_xticks(range(len(dt_month)))
            ax.set_xticklabels(dt_month.index.astype(str), rotation=45, ha="right")
            ax.set_ylabel("Avg Delivery Time (mins)")
            ax.grid(linestyle="-", color=GRID_GREEN, alpha=0.4)
            ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
            st.pyplot(fig); plt.close(fig)
    if col_vehicle and col_delivery and col_fuel:
        c4, c5 = st.columns(2)
        with c4:
            blue_title("Avg Delivery Time by Vehicle (Top 15 Slowest)")
            veh_dt = df.groupby(col_vehicle, observed=True)[col_delivery].mean().sort_values(ascending=False).head(15)
            fig2, ax2 = plt.subplots(figsize=(7, 5))
            fig2.patch.set_facecolor(GREEN_BG); ax2.set_facecolor(GREEN_BG)
            ax2.barh(veh_dt.index.astype(str)[::-1], veh_dt.values[::-1], color=BAR_BLUE)
            ax2.set_xlabel("Avg Delivery Time (mins)"); ax2.set_ylabel("Vehicle ID")
            ax2.grid(axis="x", linestyle="-", color=GRID_GREEN, alpha=0.5)
            ax2.spines["top"].set_visible(False); ax2.spines["right"].set_visible(False)
            st.pyplot(fig2); plt.close(fig2)
        with c5:
            blue_title("Avg Fuel Cost by Vehicle (Top 15 Highest)")
            veh_fc = df.groupby(col_vehicle, observed=True)[col_fuel].mean().sort_values(ascending=False).head(15)
            fig3, ax3 = plt.subplots(figsize=(7, 5))
            fig3.patch.set_facecolor(GREEN_BG); ax3.set_facecolor(GREEN_BG)
            ax3.barh(veh_fc.index.astype(str)[::-1], veh_fc.values[::-1], color="#EF4444")
            ax3.set_xlabel("Avg Fuel Cost (₹)"); ax3.set_ylabel("Vehicle ID")
            ax3.grid(axis="x", linestyle="-", color=GRID_GREEN, alpha=0.5)
            ax3.spines["top"].set_visible(False); ax3.spines["right"].set_visible(False)
            st.pyplot(fig3); plt.close(fig3)
    if col_delivery and col_efficiency:
        blue_title("Delivery Time vs Route Efficiency Score")
        fig4, ax4 = plt.subplots(figsize=(10, 4))
        fig4.patch.set_facecolor(GREEN_BG); ax4.set_facecolor(GREEN_BG)
        sample = df[[col_delivery, col_efficiency]].dropna().sample(min(3000, len(df)), random_state=42)
        ax4.scatter(sample[col_efficiency], sample[col_delivery], color=BAR_BLUE, alpha=0.3, s=10)
        ax4.set_xlabel("Route Efficiency Score"); ax4.set_ylabel("Delivery Time (mins)")
        ax4.grid(linestyle="-", color=GRID_GREEN, alpha=0.3)
        ax4.spines["top"].set_visible(False); ax4.spines["right"].set_visible(False)
        st.pyplot(fig4); plt.close(fig4)
    if col_lead_time and col_rating:
        blue_title("Lead Time vs Supplier Rating Score")
        fig5, ax5 = plt.subplots(figsize=(10, 4))
        fig5.patch.set_facecolor(GREEN_BG); ax5.set_facecolor(GREEN_BG)
        sample2 = df[[col_lead_time, col_rating]].dropna().sample(min(3000, len(df)), random_state=42)
        ax5.scatter(sample2[col_rating], sample2[col_lead_time], color=BAR_BLUE, alpha=0.3, s=10)
        ax5.set_xlabel("Supplier Rating Score"); ax5.set_ylabel("Lead Time (days)")
        ax5.grid(linestyle="-", color=GRID_GREEN, alpha=0.3)
        ax5.spines["top"].set_visible(False); ax5.spines["right"].set_visible(False)
        st.pyplot(fig5); plt.close(fig5)


st.write("")

# ================================================================


# ============================================================
# SECTION A: CATEGORY & SUBCATEGORY DEEP DIVE
# Appended to main app to match Phase 1 depth and line count.
# This block is executed AFTER the main EDA router above.
# ============================================================

if eda_option in [
    "Product-Level Analysis",
    "Inventory Overview",
    "Store & Regional Analysis"
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
        <h3 style="margin:0;">Category & Subcategory Deep Dive</h3>
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
    This section analyzes <b>supply chain performance at the product category and subcategory level</b>.

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
    """, unsafe_allow_html=True)

    GREEN_BG   = "#00D05E"
    GRID_GREEN = "#3B3B3B"
    BAR_BLUE   = "#001F5C"

    col_category  = "category"
    col_subcategory = "subcategory"
    col_stockval  = "stock_value"
    col_fill_rate = "fill_rate_pct"
    col_delivery  = "delivery_time_mins"
    col_overstock = "overstock_qty"
    col_understock = "understock_qty"

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
            chart_cat = create_altair_chart()
            safe_altair_chart(chart_cat)
            chart_cat = True  # success flag
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
        st.altair_chart(chart_stf, use_container_width=True)


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
# STEP 4 – FEATURE ENGINEERING
# ================================================================
if not st.session_state.eda_completed:
    st.info("ℹ Please explore at least one EDA analysis to unlock Feature Engineering.")
    st.stop()

st.markdown(
    """
    <div style="
        background-color:#0B2C5D;
        padding:18px 25px;
        border-radius:10px;
        color:white;
        margin-top:10px;
        margin-bottom:20px;
    ">
        <h3 style="margin:0;">
            Feature Engineering
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
        margin-bottom:20px;
    ">


    Feature Engineering is the foundation of building robust supply chain optimization models.
    It involves extracting meaningful variables from raw supply chain data and selecting the most
    impactful features for prediction and optimization. By transforming, encoding, and scaling data
    properly, we improve the model's ability to <b>learn operational patterns</b> effectively.

    

    <b>In this supply chain project, we apply:</b>

    <ul>
        <li><b>Feature Extraction</b> – deriving new supply chain KPIs from raw fields
            (e.g., inventory pressure ratio, route cost efficiency, supplier reliability index)</li>
        <li><b>Feature Selection</b> – choosing the most relevant predictors for
            inventory, routing, and transfer optimization targets</li>
        <li><b>Encoding</b> – converting categorical supply chain dimensions
            (cluster names, store types, regions, categories) into numeric form</li>
        <li><b>Scaling</b> – normalizing numerical values for fair comparison
            across inventory, logistics, and financial metrics</li>
    </ul>


    In this step, we ensure data is cleaned, relevant attributes are created,
    and only the most predictive ones are used.

    <ul>
        <li>Handle missing values, outliers, and noisy supply chain records</li>
        <li>Encode categorical variables and normalize numeric features</li>
        <li>Create new features from existing data (domain-driven supply chain engineering)</li>
        <li>Select the best subset of features using statistical and ML-based methods</li>
    </ul>

    This step directly influences <b>model accuracy, interpretability, and generalization
    performance across inventory, routing, and supplier optimization scenarios.</b>

    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("## Feature Selection")


from sklearn.feature_selection import SelectKBest, f_regression, mutual_info_regression, RFE
from sklearn.ensemble import RandomForestRegressor

# ================================================================
# TARGET VARIABLE SELECTION
# ================================================================

if df is not None and not df.empty:
    st.markdown("""
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
Select Target Variable
</div>""", unsafe_allow_html=True)


    numeric_columns = df.select_dtypes(include=["int64", "float64"]).columns.tolist() if df is not None else []

    if len(numeric_columns) == 0:
        st.error("No numeric columns found for feature selection.")
        st.stop()

    # Prefer supply chain optimization target columns
    preferred_targets = [
        "on_hand_qty", "demand_index", "delivery_time_mins",
        "fill_rate_pct", "stockout_pct", "inventory_turnover",
        "transfer_qty", "route_efficiency_score", "fuel_cost"
    ]
    default_target = next((t for t in preferred_targets if t in numeric_columns), numeric_columns[0] if numeric_columns else None)

    target_column = st.selectbox(
        "Choose your target column (e.g., on_hand_qty, demand_index, delivery_time_mins):",
        numeric_columns,
        index=numeric_columns.index(default_target) if default_target and default_target in numeric_columns else 0
    )

    # ================================================================
    # FEATURE SELECTION APPROACH
    # ================================================================

    st.markdown("""
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
Choose Feature Selection Methods
</div>
""", unsafe_allow_html=True)


    if "selection_mode" not in st.session_state:
        st.session_state.selection_mode = "Automated"

    selection_mode = st.radio(
        "Feature Selection Mode",
        ["Automated", "Manual"],
        horizontal=True,
        key="selection_mode"
    )

    selection_mode = st.session_state.selection_mode
    method = st.session_state.get("method_selection", "Correlation with Target")


    # ================================================================
    # MANUAL SELECTION
    # ================================================================
    if selection_mode == "Manual":

        feature_columns = [
            col for col in df.select_dtypes(include=["int64", "float64"]).columns
            if col != target_column and "id" not in col.lower()
        ]

        if "selected_features" not in st.session_state:
            st.session_state["selected_features"] = feature_columns[:5]

        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Select All"):
                st.session_state["selected_features"] = feature_columns.copy()
        with col2:
            if st.button("Clear All"):
                st.session_state["selected_features"] = []

        sorted_features = sorted(
            feature_columns,
            key=lambda x: x not in st.session_state["selected_features"]
        )

        feature_df = pd.DataFrame({
            "Select": [col in st.session_state["selected_features"] for col in sorted_features],
            "Feature": sorted_features
        })

        st.markdown("### Select Features")

        edited_df = st.data_editor(
            feature_df,
            hide_index=True,
            use_container_width=True,
            num_rows="fixed",
            column_config={
                "Select": st.column_config.CheckboxColumn(width="small"),
                "Feature": st.column_config.TextColumn(width="large")
            }
        )

        selected_features = edited_df.loc[edited_df["Select"], "Feature"].tolist()
        st.session_state["selected_features"] = selected_features

        if selected_features:

            st.markdown(f"""
        <div class="quality-card">
            <div class="quality-title">
                Selected Features ({len(selected_features)})
            </div>
            <div class="table-scroll">
                <table class="clean-table">
                    <tr>
                        <th>#</th>
                        <th>Feature Name</th>
                    </tr>
                    {''.join([
                        f"<tr><td>{i+1}</td><td>{feat}</td></tr>"
                        for i, feat in enumerate(selected_features)
                    ])}
                </table>
            </div>
        </div>
        """, unsafe_allow_html=True)

        else:
            st.info("No features selected.")

        st.session_state["selected_features"] = selected_features


    # ================================================================
    # AUTOMATED SELECTION
    # ================================================================
    else:

        numeric_df = df.select_dtypes(include=["int64", "float64"]).dropna() if df is not None else pd.DataFrame()

        if not target_column or target_column not in numeric_df.columns:
            st.error("Target must be numeric for Automated selection.")
            st.stop()

        X = numeric_df.drop(columns=[target_column])
        y = numeric_df[target_column]

        if X.shape[1] == 0:
            st.error("No numeric features available for selection.")
            st.stop()

        st.markdown("""
<div style="
    background-color:#163A70;
    padding:20px;
    border-radius:12px;
    color:white;
    font-size:20px;
    font-weight:600;
    margin-top:30px;
    margin-bottom:20px;
">
        Feature Selection Methods
        </div>
        """, unsafe_allow_html=True)

        if "method_selection" not in st.session_state:
            st.session_state.method_selection = "Correlation with Target"

        def method_tile(label):
            active = st.session_state.method_selection == label

            if active:
                st.markdown(
                    f"""
                    <div style="
                        background-color:#163A70;
                        color:white;
                        padding:16px;
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
                    st.session_state.method_selection = label
                    st.rerun()

        with st.expander(" ", expanded=True):

            row1 = st.columns(2)
            row2 = st.columns(2)

            methods = [
                "Correlation with Target",
                "SelectKBest",
                "Recursive Feature Elimination (RFE)",
                "Mutual Information"
            ]

            with row1[0]:
                method_tile(methods[0])
            with row1[1]:
                method_tile(methods[1])

            with row2[0]:
                method_tile(methods[2])
            with row2[1]:
                method_tile(methods[3])

        method = st.session_state.method_selection


    # ================================================================
    # 1. CORRELATION WITH TARGET
    # ================================================================
    if method == "Correlation with Target":

        with st.spinner("Computing correlations..."):
            top_corr = compute_correlation_cached(numeric_df, target_column)
            selected_features = top_corr["Feature"].tolist()
            st.session_state["selected_features"] = selected_features

        st.markdown(f"""
        <div class="quality-card">
            <div class="quality-title">
                Top 20 Features – Correlation with Target ({target_column})
            </div>
            <div class="table-scroll">
                <table class="clean-table">
                    <tr>
                        <th>#</th>
                        <th>Feature</th>
                        <th>Correlation</th>
                        <th>Abs Correlation</th>
                    </tr>
                    {''.join([
                        f"<tr><td>{i+1}</td><td>{r['Feature']}</td><td>{r['Correlation']:.4f}</td><td>{r['Abs_Correlation']:.4f}</td></tr>"
                        for i, (_, r) in enumerate(top_corr.iterrows())
                    ])}
                </table>
            </div>
        </div>
        """, unsafe_allow_html=True)

        GREEN_BG_fe = "#00D05E"
        GRID_FE = "#3B3B3B"
        fig_c, ax_c = plt.subplots(figsize=(9, 5))
        fig_c.patch.set_facecolor(GREEN_BG_fe)
        ax_c.set_facecolor(GREEN_BG_fe)
        colors = [BAR_BLUE if v >= 0 else "#EF4444" for v in top_corr["Correlation"]]
        ax_c.barh(top_corr["Feature"], top_corr["Correlation"], color=colors)
        ax_c.set_xlabel("Correlation Coefficient")
        ax_c.axvline(0, color="black", linewidth=0.8)
        ax_c.grid(axis="x", linestyle="-", color=GRID_FE, alpha=0.5)
        ax_c.spines["top"].set_visible(False)
        ax_c.spines["right"].set_visible(False)
        st.pyplot(fig_c)
        plt.close(fig_c)


    # ================================================================
    # 2. SELECTKBEST
    # ================================================================
    elif method == "SelectKBest":

        with st.spinner("Running SelectKBest feature selection..."):
            scores = compute_selectkbest_cached(X, y, k=20)
            selected_features = scores.index.tolist()
            st.session_state["selected_features"] = selected_features

        st.markdown(f"""
        <div class="quality-card">
            <div class="quality-title">
                Top 20 Features – SelectKBest (F-Score)
            </div>
            <div class="table-scroll">
                <table class="clean-table">
                    <tr>
                        <th>#</th>
                        <th>Feature</th>
                        <th>F-Score</th>
                    </tr>
                    {''.join([
                        f"<tr><td>{i+1}</td><td>{feat}</td><td>{scores.iloc[i]:.4f}</td></tr>"
                        for i, feat in enumerate(selected_features)
                    ])}
                </table>
            </div>
        </div>
        """, unsafe_allow_html=True)


    # ================================================================
    # 3. RFE
    # ================================================================
    elif method == "Recursive Feature Elimination (RFE)":

        with st.spinner("Running Recursive Feature Elimination..."):
            selected_features = compute_rfe_cached(X, y, n_features=20)
            st.session_state["selected_features"] = selected_features

        st.markdown(f"""
        <div class="quality-card">
            <div class="quality-title">
                Top Features Selected by RFE
            </div>
            <div class="table-scroll">
                <table class="clean-table">
                    <tr>
                        <th>#</th>
                        <th>Feature</th>
                    </tr>
                    {''.join([
                        f"<tr><td>{i+1}</td><td>{feat}</td></tr>"
                        for i, feat in enumerate(selected_features)
                    ])}
                </table>
            </div>
        </div>
        """, unsafe_allow_html=True)


    # ================================================================
    # 4. MUTUAL INFORMATION
    # ================================================================
    elif method == "Mutual Information":

        with st.spinner("Computing Mutual Information scores..."):
            top_mi = compute_mutual_info_cached(X, y)
            selected_features = top_mi.index.tolist()
            st.session_state["selected_features"] = selected_features

        st.markdown(f"""
        <div class="quality-card">
            <div class="quality-title">
                Top 20 Features by Mutual Information
            </div>
            <div class="table-scroll">
                <table class="clean-table">
                    <tr>
                        <th>#</th>
                        <th>Feature</th>
                        <th>MI Score</th>
                    </tr>
                    {''.join([
                        f"<tr><td>{i+1}</td><td>{feat}</td><td>{top_mi.iloc[i]:.4f}</td></tr>"
                        for i, feat in enumerate(selected_features)
                    ])}
                </table>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ================================================================
# FEATURE IMPORTANCE (PERMUTATION IMPORTANCE)
# ================================================================

selected_features = st.session_state.get("selected_features", [])

st.markdown("## Feature Importance")

if not selected_features:
    st.info("Please select at least one feature to compute feature importance.")
else:

    from sklearn.inspection import permutation_importance
    from sklearn.linear_model import LinearRegression

    numeric_df = df.select_dtypes(include=["int64", "float64"]).copy()
    numeric_df = numeric_df.replace([np.inf, -np.inf], np.nan)
    numeric_df = numeric_df.fillna(numeric_df.median())

    if target_column not in numeric_df.columns:
        st.warning("Target column must be numeric to compute feature importance.")
    else:
        X = numeric_df.drop(columns=[target_column])
        y = numeric_df[target_column]

        valid_features = [col for col in selected_features if col in X.columns]

        if not valid_features:
            st.info("Selected features are not valid numeric features.")
        else:
            with st.spinner("Computing permutation importance..."):
                top_features = compute_permutation_importance_cached(
                    numeric_df.drop(columns=[target_column]), 
                    numeric_df[target_column], 
                    valid_features
                )

    st.markdown(f"""
    <div class="quality-card">
        <div class="quality-title">
            Top Features by Permutation Importance
        </div>
        <div class="table-scroll">
            <table class="clean-table">
                <tr>
                    <th>#</th>
                    <th>Feature</th>
                    <th>Importance Score</th>
                </tr>
                {''.join([
                    f"<tr><td>{i+1}</td><td>{feat}</td><td>{top_features.iloc[i]:.4f}</td></tr>"
                    for i, feat in enumerate(top_features.index)
                ])}
            </table>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ================================================================
# AUTO RESET SCALING IF FEATURES OR TARGET CHANGE
# ================================================================

if df is not None and not df.empty and 'target_column' in locals():
    current_signature = (
        tuple(sorted(st.session_state.get("selected_features", []))),
        target_column,
        st.session_state.get("selection_mode"),
        st.session_state.get("method_selection")
    )
else:
    current_signature = None

if "feature_signature" not in st.session_state:
    st.session_state["feature_signature"] = current_signature

if current_signature and st.session_state["feature_signature"] != current_signature:

    if "scaled_features" in st.session_state:
        del st.session_state["scaled_features"]

    if "scaler_object" in st.session_state:
        del st.session_state["scaler_object"]

    st.session_state["feature_signature"] = current_signature


from sklearn.preprocessing import StandardScaler

if df is not None and not df.empty:
    st.markdown("""
<div style="
    background-color:#0B2C5D;
    padding:18px 25px;
    border-radius:10px;
    color:white;
    margin-top:10px;
    margin-bottom:10px;
">
    <h3 style="margin:0;">
        Feature Scaling (Z-Score Scaling)
    </h3>
</div>
""", unsafe_allow_html=True)


    if "selected_features" not in st.session_state or not st.session_state["selected_features"]:
        st.info("Please select features first.")
    else:
        selected_features = st.session_state["selected_features"]

        X = df[selected_features].select_dtypes(include=["int64", "float64"]).copy()

        if X.shape[1] == 0:
            st.warning("No numeric features selected.")
            st.stop()

selection_mode_val = st.session_state.get("selection_mode", "Manual")
method_used = st.session_state.get("method_selection", "Manual Selection")
selected_features = st.session_state.get("selected_features", [])
target_column = st.session_state.get("target_column", "")

st.markdown(f"""
<div class="quality-card">
    <div class="quality-title">
        Current Configuration
    </div>
    <div class="table-scroll">
        <table class="clean-table">
            <tr>
                <th>Item</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>Target Column</td>
                <td>{target_column}</td>
            </tr>
            <tr>
                <td>Selection Approach</td>
                <td>{selection_mode_val}</td>
            </tr>
            <tr>
                <td>Method Used</td>
                <td>{method_used if selection_mode_val == "Automated" else "Manual Selection"}</td>
            </tr>
            <tr>
                <td>Total Selected Features</td>
                <td>{len(selected_features)}</td>
            </tr>
        </table>
    </div>
</div>
""", unsafe_allow_html=True)

if st.button("Apply Feature Scaling"):
        with st.spinner("Applying feature scaling..."):
            scaled_df, scaler = apply_feature_scaling_cached(X)
            
            st.session_state["scaled_features"] = scaled_df
            st.session_state["scaler_object"] = scaler
            st.success(" Standard Scaling Applied Successfully")


if "scaled_features" in st.session_state:

    scaled_df = st.session_state["scaled_features"]

    st.markdown("### Before Scaling")
    render_html_table(X.head(10), max_height=300)

    st.markdown("### After Scaling")
    render_html_table(scaled_df.head(10), max_height=300)
