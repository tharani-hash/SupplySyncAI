import streamlit as st
import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt
import io
import numpy as np


st.set_page_config(page_title="SupplySyncAI – MLOps UI", layout="wide")

st.markdown("""
    <div style="
        background-color:#2E86C1;
        padding:20px;
        text-align:center;
        color:white;
        border-radius:6px;
        font-size:28px;
        font-weight:600;">
        SupplySyncAI 
        <div style="font-size:14px; font-weight:normal; margin-top:4px;">
            Autonomous Inventory Intelligence Platform
        </div>
    </div>
""", unsafe_allow_html=True)

st.write("")  

@st.cache_data
@st.cache_data
def load_data():
    return pd.read_csv("data/fact_consolidated.csv")


# CENTERED SMALL PLOT FUNCTION
def show_small_plot(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    buf.seek(0)

    st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
    st.image(buf, width=480)  # Half screen
    st.markdown("</div>", unsafe_allow_html=True)




# STEP 1 – LOAD DATA 


st.markdown("## 📥 Load Dataset")

# Make sure session key exists
if "df" not in st.session_state:
    st.session_state.df = None

# Load Button
if st.button("Load Data"):
    st.session_state.df = load_data()
    st.success("✔ Dataset loaded successfully!")


# Show preview if loaded
df = st.session_state.df

if df is not None:
    st.markdown("### 🔍 Data Preview")
    st.dataframe(df.head(20), use_container_width=True)
    st.info(f"**Shape:** {df.shape[0]} rows × {df.shape[1]} columns")
else:
    st.info("Click the button above to load the dataset.")


# STEP 2 – PREPROCESSING
st.markdown("Data Cleaning & Preprocessing")

if df is None:
    st.warning("⚠ Load data first.")
else:

    remove_duplicates = st.checkbox("Remove Duplicate Rows")
    remove_nulls = st.checkbox("Remove Rows with NULL Values")
    replace_nulls = st.checkbox("Replace NULL Values with 'Unknown'")
    convert_numeric = st.checkbox("Convert Columns to Numeric (Safe Columns Only)")

    processed_df = df.copy()
    status_logs = []

    # Remove duplicates
    if remove_duplicates:
        before = processed_df.shape[0]
        processed_df = processed_df.drop_duplicates()
        status_logs.append(f"✔ Removed **{before - processed_df.shape[0]} duplicate rows**")

    # Remove NULL rows
    if remove_nulls:
        before = processed_df.shape[0]
        processed_df = processed_df.dropna()
        status_logs.append(f"✔ Removed **{before - processed_df.shape[0]} NULL rows**")

    # Replace NULL with Unknown
    if replace_nulls:
        processed_df = processed_df.fillna("Unknown")
        status_logs.append("✔ Replaced all NULL values with `'Unknown'`")

    # Convert numeric safely
    if convert_numeric:
        safe_cols = processed_df.select_dtypes(include=["object"]).columns
        exclude = [
            "transaction_id","product_id","store_id","customer_id",
            "sales_channel_id","promo_id","event_id","customer_time_id",
            "promo_time_id","reorder_time_id","stock_time_id",
            "forecast_time_id","returns_return_id"
        ]
        safe_cols = [c for c in safe_cols if c not in exclude]

        converted = 0
        for col in safe_cols:
            before = processed_df[col].dtype
            processed_df[col] = pd.to_numeric(processed_df[col], errors="ignore")
            after = processed_df[col].dtype
            if before != after:
                converted += 1
        status_logs.append(f"✔ Converted **{converted} columns** to numeric")

    st.session_state.df = processed_df

    if status_logs:
        st.success("### Changes Made:")
        for s in status_logs:
            st.markdown(s)

    st.dataframe(processed_df.head(20), use_container_width=True)

# STEP 3 – FULL ADAPTIVE EDA 


df = st.session_state.get("df", None)

if df is None:
    st.warning("⚠ No dataset loaded. Please load data first.")
    st.stop()

st.markdown("## 📊 Step 3 — Exploratory Data Analysis (EDA)")
st.info(f"Dataset Loaded: **{df.shape[0]} rows × {df.shape[1]} columns**")


# COLUMN MAPPING 


def map_col(candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None

col_rev     = map_col(["total_sales_amount"])
col_qty     = map_col(["quantity_sold"])
col_price   = map_col(["unit_price"])
col_date    = map_col(["date"])
col_product = map_col(["product_id"])
col_store   = map_col(["store_id"])
col_channel = map_col(["sales_channel_id"])
col_event   = map_col(["event_id"])
col_promo   = map_col(["promo_id"])

num_df = df.select_dtypes(include=np.number)


# 1. DATA QUALITY OVERVIEW


with st.expander("1. Data Quality Overview"):

    st.subheader("Dataset Shape")
    st.write(f"Rows: **{df.shape[0]}**, Columns: **{df.shape[1]}**")

    st.subheader("Missing Value Analysis (%)")
    mv = (df.isnull().mean() * 100).sort_values(ascending=False)
    st.dataframe(mv.to_frame("missing_%"))

    st.subheader("Duplicate Analysis")
    st.write(f"Total duplicate rows: **{df.duplicated().sum()}**")

    st.subheader("Data Types Summary")
    st.dataframe(df.dtypes.value_counts().to_frame("count"))


# 2. SALES METRICS OVERVIEW


with st.expander("2. Sales Overview"):

    if col_rev:
        st.metric("Total Revenue", f"{df[col_rev].sum():,.2f}")
        st.metric("Average Order Value", f"{df[col_rev].mean():,.2f}")
        st.metric("Max Order Value", f"{df[col_rev].max():,.2f}")

    if col_qty:
        st.metric("Total Units Sold", f"{df[col_qty].sum():,}")
        st.metric("Average Units per Transaction", f"{df[col_qty].mean():.2f}")


# 3. PRODUCT ANALYSIS 


with st.expander("3. Product-Level Analysis"):

    if col_product:
        st.subheader("Top Products by Transaction Count")
        st.dataframe(df[col_product].value_counts().head(10))

    if col_product and col_rev:
        st.subheader("Top Products by Revenue")
        st.dataframe(
            df.groupby(col_product)[col_rev]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )


# 4. STORE ANALYSIS


with st.expander("4. Store-Level Analysis"):

    if col_store:
        st.subheader("Transactions per Store")
        st.dataframe(df[col_store].value_counts().head(10))

    if col_store and col_rev:
        st.subheader("Revenue Contribution by Store")
        st.dataframe(
            df.groupby(col_store)[col_rev]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )


# 5. SALES CHANNEL ANALYSIS


with st.expander("5. Sales Channel Analysis"):

    if col_channel:
        st.subheader("Transaction Distribution by Channel")
        st.dataframe(df[col_channel].value_counts())

    if col_channel and col_rev:
        st.subheader("Revenue by Channel")
        st.dataframe(df.groupby(col_channel)[col_rev].sum())


# 6. PROMOTION ANALYSIS


with st.expander("6. Promotion Effectiveness"):

    if col_promo:
        st.subheader("Transactions under Promotions")
        st.dataframe(df[col_promo].value_counts().head(10))

    if col_promo and col_rev:
        st.subheader("Revenue under Promotions")
        st.dataframe(
            df.groupby(col_promo)[col_rev]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )


# 7. EVENT IMPACT ANALYSIS


with st.expander("7. Event Impact Analysis"):

    if col_event:
        st.subheader("Transactions per Event")
        st.dataframe(df[col_event].value_counts().head(10))

    if col_event and col_rev:
        st.subheader("Revenue Impact by Event")
        st.dataframe(
            df.groupby(col_event)[col_rev]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )

# 7. Correlation  ANALYSIS

with st.expander("Top Correlated Features "):

    # 1. Select numeric columns
    num_df = df.select_dtypes(include=np.number)

    if num_df.shape[1] < 2:
        st.info("Not enough numeric columns for correlation.")
    else:
        # 2. Correlation
        corr = num_df.corr()

        corr_abs = corr.abs()
        np.fill_diagonal(corr_abs.values, np.nan)

        # 4. Get top correlated pairs
        top_pairs = (
            corr_abs.unstack()
            .dropna()
            .sort_values(ascending=False)
            .head(8)   
        )

        # 5. Extract involved features
        top_features = sorted(
            set([f for pair in top_pairs.index for f in pair])
        )

        # 6. Focused correlation matrix
        focused_corr = corr.loc[top_features, top_features]

        # 7. Plot FULL GRID heatmap
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.heatmap(
            focused_corr,
            annot=True,
            fmt=".2f",
            cmap="coolwarm",
            linewidths=0.5,
            cbar=True,
            ax=ax
        )

        ax.set_title("Top Correlated Numeric Features ")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0)

        plt.tight_layout()
        st.pyplot(fig)




# 10. SUMMARY REPORT (INSIGHTS)


with st.expander("10. Summary Report"):

    summary = {
        "Rows": df.shape[0],
        "Columns": df.shape[1],
        "Numeric Columns": num_df.shape[1],
        "Total Revenue": df[col_rev].sum() if col_rev else None,
        "Total Units Sold": int(df["quantity_sold"].fillna(0).sum()),
        
    }

    st.json(summary)
    st.success("EDA Summary Generated ✔")


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
