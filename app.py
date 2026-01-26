import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import warnings

warnings.filterwarnings("ignore")

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Auto Dashboard App",
    page_icon="📊",
    layout="wide"
)

# -------------------------------------------------
# STYLE
# -------------------------------------------------
st.markdown("""
<style>
.main-header {
    font-size: 2.8rem;
    font-weight: 800;
    text-align: center;
    color: #1f77b4;
}
.stButton>button {
    width:100%;
    background:#1f77b4;
    color:white;
    font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
@st.cache_data
def load_data(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    elif file.name.endswith((".xlsx", ".xls")):
        return pd.read_excel(file)
    elif file.name.endswith(".json"):
        return pd.read_json(file)
    elif file.name.endswith(".parquet"):
        return pd.read_parquet(file)
    return None


# -------------------------------------------------
# COLUMN DETECTION
# -------------------------------------------------
def detect_columns(df):
    numeric = df.select_dtypes(include=np.number).columns.tolist()
    categorical = df.select_dtypes(include=["object", "category"]).columns.tolist()
    datetime = []

    for col in categorical.copy():
        parsed = pd.to_datetime(df[col], errors="coerce")
        if parsed.notna().sum() > 0.8 * len(df):
            datetime.append(col)
            categorical.remove(col)

    return numeric, categorical, datetime


# -------------------------------------------------
# SAFE AGGREGATION
# -------------------------------------------------
def aggregate(df, cat, val, top=15):
    df = df.copy()
    df[cat] = df[cat].astype(str)
    return (
        df.groupby(cat)[val]
        .sum()
        .reset_index()
        .sort_values(val, ascending=False)
        .head(top)
    )


# -------------------------------------------------
# CHARTS (SAFE)
# -------------------------------------------------
def pie(df, v, c):
    d = aggregate(df, c, v)
    return px.pie(d, values=v, names=c, hole=0.3)


def bar(df, x, y, orient="v"):
    return px.bar(df, x=x, y=y, orientation=orient)


def histogram(df, col):
    return px.histogram(df, x=col, nbins=30)


def scatter(df, x, y, color=None):
    df = df.copy()
    if color and df[color].nunique() < len(df):
        df[color] = df[color].astype(str)
    else:
        color = None

    return px.scatter(df, x=x, y=y, color=color)


def bubble(df, x, y, size, color=None):
    df = df.copy()

    if color and df[color].nunique() < len(df):
        df[color] = df[color].astype(str)
    else:
        color = None

    return px.scatter(
        df,
        x=x,
        y=y,
        size=size,
        color=color,
        size_max=60
    )


def radial(df, cat, val):
    d = aggregate(df, cat, val, 10)
    fig = go.Figure(
        go.Barpolar(
            r=d[val],
            theta=d[cat],
            marker_color="skyblue"
        )
    )
    fig.update_layout(polar=dict(radialaxis=dict(visible=True)))
    return fig


# -------------------------------------------------
# MAIN APP
# -------------------------------------------------
def main():
    st.markdown('<div class="main-header">📊 Auto Generated Dashboard</div>',
                unsafe_allow_html=True)

    with st.sidebar:
        st.header("Upload File")
        file = st.file_uploader(
            "CSV | Excel | JSON | Parquet",
            type=["csv", "xlsx", "xls", "json", "parquet"]
        )

    if not file:
        st.info("Upload a file to start")
        return

    df = load_data(file)
    if df is None:
        st.error("File not supported")
        return

    numeric, categorical, datetime = detect_columns(df)

    # METRICS
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", len(df))
    c2.metric("Columns", len(df.columns))
    c3.metric("Numeric", len(numeric))
    c4.metric("Categorical", len(categorical))

    with st.expander("Preview Data"):
        st.dataframe(df.head(50), use_container_width=True)

    st.header("📈 Auto Dashboard")

    charts = []

    if categorical and numeric:
        charts.append(pie(df, numeric[0], categorical[0]))
        charts.append(bar(aggregate(df, categorical[0], numeric[0]),
                          categorical[0], numeric[0]))

    if len(numeric) >= 2:
        charts.append(scatter(
            df, numeric[0], numeric[1],
            categorical[0] if categorical else None
        ))

    if len(numeric) >= 3:
        charts.append(bubble(
            df, numeric[0], numeric[1], numeric[2],
            categorical[0] if categorical else None
        ))

    for col in numeric[:2]:
        charts.append(histogram(df, col))

    if categorical and numeric:
        charts.append(radial(df, categorical[0], numeric[0]))

    for i in range(0, len(charts), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(charts):
                cols[j].plotly_chart(charts[i + j], use_container_width=True)


if __name__ == "__main__":
    main()
