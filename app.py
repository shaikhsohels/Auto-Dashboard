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
    page_title="Advanced Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# =====================================================
# HEADER
# =====================================================
st.markdown("""
<h1 style="text-align:center;color:#1f77b4;">📊 Advanced Analytics Dashboard</h1>
<p style="text-align:center;">Power BI / Tableau–like Auto Dashboard</p>
""", unsafe_allow_html=True)

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
# SIDEBAR – DATA INPUT
# =====================================================
with st.sidebar:
    st.header("📂 Data Source")
    file = st.file_uploader(
        "Upload CSV / Excel / JSON / Parquet",
        type=["csv", "xlsx", "xls", "json", "parquet"]
    )

if not file:
    st.info("Upload a dataset to start analysis")
    st.stop()

df = load_file(file)
if df is None:
    st.error("Unsupported file")
    st.stop()

numeric_cols, categorical_cols, datetime_cols = detect_columns(df)

# =====================================================
# SIDEBAR – FILTERS (SLICERS)
# =====================================================
with st.sidebar:
    st.header("🎛 Filters")

    filtered_df = df.copy()

    # Categorical filters
    for col in categorical_cols[:3]:
        values = st.multiselect(
            f"{col}",
            options=filtered_df[col].dropna().unique(),
            default=None
        )
        if values:
            filtered_df = filtered_df[filtered_df[col].isin(values)]

    # Numeric filters
    for col in numeric_cols[:2]:
        min_val, max_val = float(filtered_df[col].min()), float(filtered_df[col].max())
        selected = st.slider(
            f"{col} range",
            min_val,
            max_val,
            (min_val, max_val)
        )
        filtered_df = filtered_df[
            (filtered_df[col] >= selected[0]) &
            (filtered_df[col] <= selected[1])
        ]

# =====================================================
# KPI SECTION
# =====================================================
st.subheader("📌 Key Metrics")

kpi_cols = st.columns(min(4, len(numeric_cols)))

for i, col in enumerate(numeric_cols[:4]):
    kpi_cols[i].metric(
        label=col,
        value=round(filtered_df[col].sum(), 2)
    )

# =====================================================
# CHART BUILDER
# =====================================================
st.divider()
st.subheader("📈 Chart Builder")

chart_type = st.selectbox(
    "Select Chart Type",
    ["Bar", "Line", "Pie", "Scatter", "Histogram"]
)

col1, col2, col3 = st.columns(3)

with col1:
    x_col = st.selectbox("X-axis", categorical_cols + numeric_cols + datetime_cols)

with col2:
    y_col = st.selectbox("Y-axis / Value", numeric_cols)

with col3:
    color_col = st.selectbox(
        "Color (optional)",
        [None] + categorical_cols
    )

# =====================================================
# CHART RENDER
# =====================================================
fig = None

if chart_type == "Bar":
    agg = filtered_df.groupby(x_col, as_index=False)[y_col].sum()
    fig = px.bar(agg, x=x_col, y=y_col, color=color_col)

elif chart_type == "Pie":
    agg = filtered_df.groupby(x_col, as_index=False)[y_col].sum()
    fig = px.pie(agg, names=x_col, values=y_col)

elif chart_type == "Line":
    temp = filtered_df.copy()
    if x_col in datetime_cols:
        temp[x_col] = pd.to_datetime(temp[x_col], errors="coerce")
        temp = temp.sort_values(x_col)
    fig = px.line(temp, x=x_col, y=y_col, color=color_col)

elif chart_type == "Scatter":
    fig = px.scatter(filtered_df, x=x_col, y=y_col, color=color_col)

elif chart_type == "Histogram":
    fig = px.histogram(filtered_df, x=y_col)

# =====================================================
# DISPLAY CHART
# =====================================================
if fig:
    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# DATA VIEW
# =====================================================
with st.expander("📄 View Filtered Data"):
    st.dataframe(filtered_df.head(100), use_container_width=True)
