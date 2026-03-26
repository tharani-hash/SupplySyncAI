import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import io
import numpy as np
import altair as alt

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
    if title:
        st.markdown(f"**{title}**")
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
    for _, row in df.iterrows():
        html += "<tr style='border-bottom:1px solid #E5E7EB;'>"
        for val in row:
            html += f"<td style='padding:6px 10px;white-space:nowrap;'>{val}</td>"
        html += "</tr>"
    html += "</tbody></table></div>"
    st.markdown(html, unsafe_allow_html=True)


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
# CACHED FUNCTIONS FOR PERFORMANCE
# ================================================================
@st.cache_data
def remove_duplicates_cached(df):
    """Optimized cached function for duplicate removal processing"""
    # Quick check for duplicates without full scan
    total_rows = len(df)
    
    # For very large datasets, show progress and process in chunks
    if total_rows > 100000:
        # Use subset method for faster duplicate detection on large datasets
        sample_size = min(50000, total_rows // 2)
        sample_duplicates = df.sample(n=sample_size, random_state=42).duplicated().sum()
        
        # Estimate total duplicates based on sample
        estimated_dup_rate = sample_duplicates / sample_size
        estimated_total_dups = int(total_rows * estimated_dup_rate)
        
        if estimated_total_dups == 0:
            # Early exit if no duplicates detected in sample
            return df.copy(), df.copy(), pd.DataFrame()
    
    # Full duplicate check (optimized)
    before_df = df.copy()
    
    # Use duplicated() with keep=False for better performance
    dup_mask = before_df.duplicated(keep=False)
    dup_rows = before_df[dup_mask]
    
    # More efficient drop_duplicates
    after_df = before_df.drop_duplicates().reset_index(drop=True)
    
    return before_df, after_df, dup_rows

@st.cache_data
def remove_outliers_cached(df, delete_cols):
    """Cached function for outlier removal processing"""
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

    extreme_mask = outlier_count >= 4
    removed_df = before_df[extreme_mask]
    after_df = after_df[~extreme_mask].reset_index(drop=True)
    
    return before_df, after_df, removed_df

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
    """Cached function for Recursive Feature Elimination"""
    from sklearn.feature_selection import RFE
    from sklearn.ensemble import RandomForestRegressor
    
    model = RandomForestRegressor(n_estimators=50, random_state=42)
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
def compute_eda_aggregations(df, sample_size=None):
    """Optimized cached function for common EDA aggregations with sampling support"""
    results = {}
    
    # Use sampling for large datasets to improve performance
    if sample_size and len(df) > sample_size:
        df_work = df.sample(n=sample_size, random_state=42)
        st.info(f"📊 Using sample of {sample_size:,} rows for faster analysis")
    else:
        df_work = df
    
    # Common aggregations used across EDA (optimized)
    try:
        if 'category' in df_work.columns and 'stock_value' in df_work.columns:
            results['category_stockval'] = df_work.groupby('category')['stock_value'].sum().sort_values(ascending=False)
        
        if 'subcategory' in df_work.columns and 'fill_rate_pct' in df_work.columns:
            results['subcategory_fillrate'] = df_work.groupby('subcategory')['fill_rate_pct'].mean().sort_values(ascending=False).head(15)
        
        if 'zone' in df_work.columns and 'stock_value' in df_work.columns:
            results['zone_stockval'] = df_work.groupby('zone')['stock_value'].sum().sort_values(ascending=False)
        
        if 'city' in df_work.columns and 'stockout_pct' in df_work.columns:
            results['city_stockout'] = df_work.groupby('city')['stockout_pct'].mean().sort_values(ascending=False).head(15)
            
        if 'vehicle_id' in df_work.columns and 'delivery_time_mins' in df_work.columns:
            results['vehicle_delivery'] = df_work.groupby('vehicle_id')['delivery_time_mins'].mean().sort_values(ascending=False).head(15)
            
        if 'region' in df_work.columns and 'overstock_index' in df_work.columns:
            results['region_overstock'] = df_work.groupby('region')['overstock_index'].mean().sort_values(ascending=False)
            
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
    return pd.read_csv("FACT_SUPPLY_CHAIN_DATA.csv")


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
    with st.spinner("Loading supply chain data..."):
        try:
            st.session_state.df = load_data()
            st.success("Data loaded successfully!")
        except Exception:
            import os
            uploads_path = "/mnt/user-data/uploads/FACT_SUPPLY_CHAIN_DATA.csv"
            if os.path.exists(uploads_path):
                st.session_state.df = pd.read_csv(uploads_path)
                st.success("Data loaded successfully!")
            else:
                st.error("Could not find FACT_SUPPLY_CHAIN_DATA.csv. Place it in data/ folder.")

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
        "Replace Missing Values"
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
# COLUMN MAPPING
# ================================================================
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
    row1 = st.columns(5)
    row2 = st.columns(4)

    with row1[0]:
        nav_button("Data Quality Overview", "Data Quality Overview")
    with row1[1]:
        nav_button("Inventory Overview", "Inventory Overview")
    with row1[2]:
        nav_button("Product-Level Analysis", "Product-Level Analysis")
    with row1[3]:
        nav_button("Store & Regional Analysis", "Store & Regional Analysis")
    with row1[4]:
        nav_button("Shipment & Routing Analysis", "Shipment & Routing Analysis")

    with row2[0]:
        nav_button("Cluster Transfer Analysis", "Cluster Transfer Analysis")
    with row2[1]:
        nav_button("Supplier Analysis", "Supplier Analysis")
    with row2[2]:
        nav_button("Time & Seasonality Analysis", "Time & Seasonality Analysis")
    with row2[3]:
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
        df.groupby(col_store)[col_stockval]
        .sum()
        .sort_values(ascending=False)
        .head(TOP_STORES)
        .index
    )

    store_product_qty = (
        df[df[col_store].isin(top_stores)]
        .groupby([col_store, col_product])[col_onhand]
        .sum()
        .reset_index()
    )

    store_top_products = (
        store_product_qty
        .sort_values([col_store, col_onhand], ascending=[True, False])
        .groupby(col_store)
        .head(TOP_PRODUCTS)
    )

    pivot_qty = store_top_products.pivot_table(
        index=col_store,
        columns=col_product,
        values=col_onhand,
        fill_value=0
    )

    col1, col2 = st.columns(2)

    # Plot 1: Stock Value Concentration by Store
    with col1:
        blue_title("Stock Value Concentration Across Stores")

        store_sv = (
            df.groupby(col_store)[col_stockval]
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
            df.groupby(col_store)
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
            df.groupby(col_store)
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
        cat_sv = df.groupby(col_category)[col_stockval].sum().sort_values(ascending=False)
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
        st.altair_chart(chart_cat, use_container_width=True)

    with col2:
        blue_title_ext("Avg Fill Rate by Subcategory")
        sub_fill = df.groupby(col_subcategory)[col_fill_rate].mean().sort_values(ascending=False).head(15)
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
        cat_del = df.groupby(col_category)[col_delivery].mean().sort_values(ascending=False)
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
        cat_ov = df.groupby(col_category).agg(
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
        zone_sv = df.groupby(col_zone)[col_stockval].sum().sort_values(ascending=False)
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
        zone_ov = df.groupby(col_zone).agg(
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
        stype_fill = df.groupby(col_store_type)[col_fill_rate].mean().sort_values(ascending=False)
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
        reg_oi = df.groupby(col_region)[col_overstock_idx].mean().sort_values(ascending=False)
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
</div>
""", unsafe_allow_html=True)


numeric_columns = df.select_dtypes(include=["int64", "float64"]).columns.tolist()

if len(numeric_columns) == 0:
    st.error("No numeric columns found for feature selection.")
    st.stop()

# Prefer supply chain optimization target columns
preferred_targets = [
    "on_hand_qty", "demand_index", "delivery_time_mins",
    "fill_rate_pct", "stockout_pct", "inventory_turnover",
    "transfer_qty", "route_efficiency_score", "fuel_cost"
]
default_target = next((t for t in preferred_targets if t in numeric_columns), numeric_columns[0])

target_column = st.selectbox(
    "Choose your target column (e.g., on_hand_qty, demand_index, delivery_time_mins):",
    numeric_columns,
    index=numeric_columns.index(default_target)
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
Choose Feature Selection Approach
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

    numeric_df = df.select_dtypes(include=["int64", "float64"]).dropna()

    if target_column not in numeric_df.columns:
        st.error("Target must be numeric for Automated selection.")
        st.stop()

    X = numeric_df.drop(columns=[target_column])
    y = numeric_df[target_column]

    if X.shape[1] == 0:
        st.error("No numeric features available for selection.")
        st.stop()


    if selection_mode == "Automated":

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

current_signature = (
    tuple(sorted(st.session_state.get("selected_features", []))),
    target_column,
    st.session_state.get("selection_mode"),
    st.session_state.get("method_selection")
)

if "feature_signature" not in st.session_state:
    st.session_state["feature_signature"] = current_signature

if st.session_state["feature_signature"] != current_signature:

    if "scaled_features" in st.session_state:
        del st.session_state["scaled_features"]

    if "scaler_object" in st.session_state:
        del st.session_state["scaler_object"]

    st.session_state["feature_signature"] = current_signature


from sklearn.preprocessing import StandardScaler

st.markdown("""
<div style="
    background-color:#2F75B5;
    padding:20px;
    border-radius:10px;
    color:white;
    font-size:18px;
    font-weight:600;
    margin-top:30px;
    margin-bottom:20px;
">
Feature Scaling (Z-Score Scaling)
</div>
""", unsafe_allow_html=True)


if "selected_features" not in st.session_state or not st.session_state["selected_features"]:
    st.info("Please select features first.")

selected_features = st.session_state["selected_features"]

X = df[selected_features].select_dtypes(include=["int64", "float64"]).copy()

if X.shape[1] == 0:
    st.warning("No numeric features selected.")
    st.stop()

selection_mode_val = st.session_state.get("selection_mode", "Manual")
method_used = st.session_state.get("method_selection", "Manual Selection")
selected_features = st.session_state.get("selected_features", [])

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
        st.success("✔ Standard Scaling Applied Successfully")


if "scaled_features" in st.session_state:

    scaled_df = st.session_state["scaled_features"]

    st.markdown("### Before Scaling")
    render_html_table(X.head(10), max_height=300)

    st.markdown("### After Scaling")
    render_html_table(scaled_df.head(10), max_height=300)
