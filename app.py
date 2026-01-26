import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import warnings

warnings.filterwarnings("ignore")

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(
    page_title="Auto Dashboard App",
    page_icon="📊",
    layout="wide"
)

# ---------------- STYLING ---------------- #
st.markdown("""
<style>
.main-header {
    font-size: 3rem;
    font-weight: bold;
    text-align: center;
    color: #1f77b4;
}
.stButton>button {
    width:100%;
    background-color:#1f77b4;
    color:white;
    font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

# ---------------- DATA LOADER ---------------- #
@st.cache_data
def load_data(uploaded_file):
    try:
        if uploaded_file.name.endswith(".csv"):
            return pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith((".xlsx", ".xls")):
            return pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith(".json"):
            return pd.read_json(uploaded_file)
        elif uploaded_file.name.endswith(".parquet"):
            return pd.read_parquet(uploaded_file)
        else:
            st.error("Unsupported file format")
            return None
    except Exception as e:
        st.error(str(e))
        return None


# ---------------- COLUMN TYPE DETECTION ---------------- #
def detect_column_types(df):
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    datetime_cols = []

    for col in categorical_cols.copy():
        converted = pd.to_datetime(df[col], errors="coerce")
        if converted.notna().sum() > 0.8 * len(df):
            datetime_cols.append(col)
            categorical_cols.remove(col)

    return numeric_cols, categorical_cols, datetime_cols


# ---------------- CHART FUNCTIONS ---------------- #
def aggregate(df, cat, val, top=15):
    agg = df.groupby(cat)[val].sum().reset_index()
    return agg.sort_values(val, ascending=False).head(top)


def pie(df, v, c):
    df = aggregate(df, c, v)
    return px.pie(df, values=v, names=c, title=f"{c} by {v}")


def donut(df, v, c):
    df = aggregate(df, c, v)
    return px.pie(df, values=v, names=c, hole=0.4, title=f"{c} by {v}")


def bar(df, x, y, orient="v"):
    return px.bar(df, x=x, y=y, orientation=orient, title=f"{y} by {x}")


def scatter(df, x, y, color=None):
    return px.scatter(df, x=x, y=y, color=color)


def bubble(df, x, y, size, color=None):
    return px.scatter(df, x=x, y=y, size=size, color=color, size_max=60)


def histogram(df, col, bins):
    return px.histogram(df, x=col, nbins=bins)


def radial(df, cat, val):
    df = aggregate(df, cat, val, 10)
    df[cat] = df[cat].astype(str)

    fig = go.Figure(
        go.Barpolar(
            r=df[val],
            theta=df[cat],
            marker_color="skyblue"
        )
    )

    fig.update_layout(
        title=f"{val} by {cat}",
        polar=dict(radialaxis=dict(visible=True))
    )

    return fig


# ---------------- MAIN APP ---------------- #
def main():
    st.markdown('<div class="main-header">📊 Auto Dashboard App</div>', unsafe_allow_html=True)

    with st.sidebar:
        st.header("📁 Upload File")
        file = st.file_uploader(
            "Upload CSV / Excel / JSON / Parquet",
            type=["csv", "xlsx", "xls", "json", "parquet"]
        )

    if not file:
        st.info("Upload a file to begin")
        return

    df = load_data(file)

    if df is None:
        return

    numeric_cols, categorical_cols, datetime_cols = detect_column_types(df)

    # ---------------- METRICS ---------------- #
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", len(df))
    c2.metric("Columns", len(df.columns))
    c3.metric("Numeric", len(numeric_cols))
    c4.metric("Categorical", len(categorical_cols))

    with st.expander("Preview Data"):
        st.dataframe(df.head(20), use_container_width=True)

    # ---------------- AUTO DASHBOARD ---------------- #
    st.header("📈 Auto Generated Dashboard")

    charts = []

    if categorical_cols and numeric_cols:
        charts.append(pie(df, numeric_cols[0], categorical_cols[0]))
        charts.append(donut(df, numeric_cols[0], categorical_cols[0]))
        charts.append(bar(aggregate(df, categorical_cols[0], numeric_cols[0]),
                          categorical_cols[0], numeric_cols[0]))

    if len(numeric_cols) >= 2:
        charts.append(scatter(df, numeric_cols[0], numeric_cols[1],
                               categorical_cols[0] if categorical_cols else None))

    if len(numeric_cols) >= 3:
        charts.append(bubble(df, numeric_cols[0], numeric_cols[1],
                              numeric_cols[2],
                              categorical_cols[0] if categorical_cols else None))

    for col in numeric_cols[:2]:
        charts.append(histogram(df, col, 30))

    if categorical_cols and numeric_cols:
        charts.append(radial(df, categorical_cols[0], numeric_cols[0]))

    for i in range(0, len(charts), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(charts):
                cols[j].plotly_chart(charts[i + j], use_container_width=True)


if __name__ == "__main__":
    main()
