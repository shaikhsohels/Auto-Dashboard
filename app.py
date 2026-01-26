import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import warnings

warnings.filterwarnings("ignore")

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="Auto Dashboard Generator",
    page_icon="📊",
    layout="wide"
)

# ======================================================
# STYLE
# ======================================================
st.markdown("""
<style>
.main-title {
    font-size: 2.8rem;
    font-weight: 800;
    text-align: center;
    color: #1f77b4;
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# LOAD DATA
# ======================================================
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


# ======================================================
# COLUMN DETECTION
# ======================================================
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


# ======================================================
# SAFE AGGREGATION
# ======================================================
def safe_group(df, cat, num, top=15):
    df = df.copy()

    for c in ["index", "level_0"]:
        if c in df.columns:
            df.drop(columns=c, inplace=True)

    df[cat] = df[cat].astype(str)

    agg = (
        df.groupby(cat, as_index=False)[num]
        .sum()
        .sort_values(num, ascending=False)
        .head(top)
    )
    return agg


# ======================================================
# CHART BUILDERS (100% SAFE)
# ======================================================
def auto_charts(df):
    charts = []

    numeric, categorical, datetime = detect_columns(df)

    # ---------- KPI ----------
    if numeric:
        kpi_cols = st.columns(len(numeric[:4]))
        for i, col in enumerate(numeric[:4]):
            kpi_cols[i].metric(col, round(df[col].sum(), 2))

    # ---------- PIE / BAR ----------
    if numeric and categorical:
        agg = safe_group(df, categorical[0], numeric[0])

        charts.append(px.pie(
            agg,
            names=categorical[0],
            values=numeric[0],
            title=f"{numeric[0]} by {categorical[0]}"
        ))

        charts.append(px.bar(
            agg,
            x=categorical[0],
            y=numeric[0],
            title=f"{numeric[0]} by {categorical[0]}"
        ))

    # ---------- SCATTER ----------
    if len(numeric) >= 2:
        charts.append(px.scatter(
            df,
            x=numeric[0],
            y=numeric[1],
            title=f"{numeric[1]} vs {numeric[0]}"
        ))

    # ---------- HISTOGRAM ----------
    for col in numeric[:2]:
        charts.append(px.histogram(df, x=col, title=f"Distribution of {col}"))

    # ---------- TIME SERIES ----------
    if datetime and numeric:
        temp = df.copy()
        temp[datetime[0]] = pd.to_datetime(temp[datetime[0]], errors="coerce")

        charts.append(px.line(
            temp.sort_values(datetime[0]),
            x=datetime[0],
            y=numeric[0],
            title=f"{numeric[0]} over time"
        ))

    return charts


# ======================================================
# MAIN APP
# ======================================================
def main():
    st.markdown('<div class="main-title">📊 Auto Dashboard Generator</div>',
                unsafe_allow_html=True)

    with st.sidebar:
        st.header("Upload Data File")
        file = st.file_uploader(
            "CSV | Excel | JSON | Parquet",
            type=["csv", "xlsx", "xls", "json", "parquet"]
        )

    if not file:
        st.info("Upload a file to generate dashboard")
        return

    df = load_file(file)

    if df is None:
        st.error("Unsupported file format")
        return

    st.subheader("Dataset Preview")
    st.dataframe(df.head(50), use_container_width=True)

    st.divider()

    st.subheader("📈 Auto Generated Dashboard")

    charts = auto_charts(df)

    for i in range(0, len(charts), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(charts):
                cols[j].plotly_chart(charts[i + j], use_container_width=True)


# ======================================================
if __name__ == "__main__":
    main()
