import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import warnings

warnings.filterwarnings("ignore")

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Advanced Auto Dashboard",
    page_icon="📊",
    layout="wide"
)

# =====================================================
# STYLE
# =====================================================
st.markdown("""
<style>
.kpi {
    background:#f5f7fb;
    padding:20px;
    border-radius:15px;
    text-align:center;
    box-shadow:0 0 10px rgba(0,0,0,0.05);
}
.title {
    font-size:2.6rem;
    font-weight:800;
    color:#1f77b4;
    text-align:center;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">📊 Advanced Auto Analytics Dashboard</div>',
            unsafe_allow_html=True)

# =====================================================
# LOAD DATA
# =====================================================
@st.cache_data
def load_file(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    elif file.name.endswith((".xlsx", ".xls")):
        return pd.read_excel(file)
    elif file.name.endswith(".json"):
        return pd.read_json(file)
    elif file.name.endswith(".parquet"):
        return pd.read_parquet(file)
    return None


# =====================================================
# COLUMN DETECTION
# =====================================================
def detect_columns(df):
    numeric = df.select_dtypes(include=np.number).columns.tolist()
    categorical = df.select_dtypes(include=["object", "category"]).columns.tolist()
    datetime = []

    for col in categorical.copy():
        parsed = pd.to_datetime(df[col], errors="coerce")
        if parsed.notna().mean() > 0.8:
            datetime.append(col)
            categorical.remove(col)

    return numeric, categorical, datetime


# =====================================================
# SIDEBAR
# =====================================================
with st.sidebar:
    st.header("📁 Upload Data")
    file = st.file_uploader(
        "CSV | Excel | JSON | Parquet",
        type=["csv", "xlsx", "xls", "json", "parquet"]
    )

    if not file:
        st.stop()

df = load_file(file)

numeric_cols, categorical_cols, datetime_cols = detect_columns(df)

# =====================================================
# FILTERS
# =====================================================
st.sidebar.header("🔎 Filters")

filtered_df = df.copy()

if categorical_cols:
    cat_filter = st.sidebar.multiselect(
        "Filter Category",
        df[categorical_cols[0]].unique()
    )
    if cat_filter:
        filtered_df = filtered_df[
            filtered_df[categorical_cols[0]].isin(cat_filter)
        ]

if datetime_cols:
    filtered_df[datetime_cols[0]] = pd.to_datetime(
        filtered_df[datetime_cols[0]], errors="coerce"
    )

    date_range = st.sidebar.date_input(
        "Date Range",
        [filtered_df[datetime_cols[0]].min(),
         filtered_df[datetime_cols[0]].max()]
    )

    if len(date_range) == 2:
        filtered_df = filtered_df[
            (filtered_df[datetime_cols[0]] >= pd.to_datetime(date_range[0])) &
            (filtered_df[datetime_cols[0]] <= pd.to_datetime(date_range[1]))
        ]

# =====================================================
# KPI CARDS
# =====================================================
st.subheader("📌 Key Metrics")

kpi_cols = st.columns(min(4, len(numeric_cols)))

for i, col in enumerate(numeric_cols[:4]):
    kpi_cols[i].markdown(
        f"""
        <div class="kpi">
            <h2>{round(filtered_df[col].sum(),2)}</h2>
            <p>{col} (Total)</p>
        </div>
