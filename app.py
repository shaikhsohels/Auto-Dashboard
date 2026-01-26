import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import warnings

warnings.filterwarnings("ignore")

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Interactive Auto Dashboard",
    page_icon="📊",
    layout="wide"
)

# --------------------------------------------------
# TITLE
# --------------------------------------------------
st.markdown(
    "<h1 style='text-align:center;color:#1f77b4;'>📊 Interactive Auto Dashboard</h1>",
    unsafe_allow_html=True
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
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


# --------------------------------------------------
# COLUMN DETECTION
# --------------------------------------------------
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


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
with st.sidebar:
    st.header("Upload File")
    uploaded_file = st.file_uploader(
        "CSV | Excel | JSON | Parquet",
        type=["csv", "xlsx", "xls", "json", "parquet"]
    )

if not uploaded_file:
    st.info("Upload a file to start")
    st.stop()

df = load_file(uploaded_file)

if df is None:
    st.error("Unsupported file")
    st.stop()

numeric_cols, categorical_cols, datetime_cols = detect_columns(df)

# --------------------------------------------------
# PREVIEW
# --------------------------------------------------
st.subheader("Dataset Preview")
st.dataframe(df.head(30), use_container_width=True)

# --------------------------------------------------
# CHART SELECTION
# --------------------------------------------------
st.sidebar.header("Chart Options")

chart_type = st.sidebar.selectbox(
    "Select Chart Type",
    [
        "Pie Chart",
        "Bar Chart",
        "Line Chart",
        "Scatter Plot",
        "Histogram"
    ]
)

# --------------------------------------------------
# PIE CHART
# --------------------------------------------------
if chart_type == "Pie Chart":

    cat = st.selectbox("Select Category Column", categorical_cols)
    num = st.selectbox("Select Numeric Column", numeric_cols)

    agg = df.groupby(cat, as_index=False)[num].sum()

    fig = px.pie(
        agg,
        names=cat,
        values=num,
        title=f"{num} by {cat}"
    )

    st.plotly_chart(fig, use_container_width=True)


# --------------------------------------------------
# BAR CHART
# --------------------------------------------------
elif chart_type == "Bar Chart":

    cat = st.selectbox("Select Category Column", categorical_cols)
    num = st.selectbox("Select Numeric Column", numeric_cols)

    agg = df.groupby(cat, as_index=False)[num].sum()

    fig = px.bar(
        agg,
        x=cat,
        y=num,
        title=f"{num} by {cat}"
    )

    st.plotly_chart(fig, use_container_width=True)


# --------------------------------------------------
# LINE CHART
# --------------------------------------------------
elif chart_type == "Line Chart":

    date_col = st.selectbox("Select Date Column", datetime_cols)
    num = st.selectbox("Select Numeric Column", numeric_cols)

    temp = df.copy()
    temp[date_col] = pd.to_datetime(temp[date_col], errors="coerce")

    fig = px.line(
        temp.sort_values(date_col),
        x=date_col,
        y=num,
        title=f"{num} over Time"
    )

    st.plotly_chart(fig, use_container_width=True)


# --------------------------------------------------
# SCATTER
# --------------------------------------------------
elif chart_type == "Scatter Plot":

    x = st.selectbox("X-axis", numeric_cols)
    y = st.selectbox("Y-axis", numeric_cols)

    fig = px.scatter(
        df,
        x=x,
        y=y,
        title=f"{y} vs {x}"
    )

    st.plotly_chart(fig, use_container_width=True)


# --------------------------------------------------
# HISTOGRAM
# --------------------------------------------------
elif chart_type == "Histogram":

    col = st.selectbox("Select Numeric Column", numeric_cols)

    fig = px.histogram(
        df,
        x=col,
        nbins=30,
        title=f"Distribution of {col}"
    )

    st.plotly_chart(fig, use_container_width=True)
