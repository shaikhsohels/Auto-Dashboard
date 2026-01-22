import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import json

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Advanced Auto Dashboard",
    layout="wide"
)

st.title("🚀 Advanced Auto Dashboard Creator")

# -----------------------------
# File Upload
# -----------------------------
file = st.file_uploader(
    "Upload CSV, Excel, JSON or SQLite DB",
    type=["csv", "xlsx", "json", "db"]
)

df = None

if file:

    # CSV file
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)

    # Excel file
    elif file.name.endswith(".xlsx"):
        df = pd.read_excel(file)

    # JSON file
    elif file.name.endswith(".json"):
        data = json.load(file)
        df = pd.DataFrame(data)

    # SQLite database
    elif file.name.endswith(".db"):
        conn = sqlite3.connect(file)
        tables = pd.read_sql(
            "SELECT name FROM sqlite_master WHERE type='table';",
            conn
        )
        table_name = st.selectbox(
            "Select SQL Table",
            tables["name"]
        )
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)

# -----------------------------
# Dashboard Section
# -----------------------------
if df is not None:

    st.success("✅ Data loaded successfully")

    # -----------------------------
    # Data Preview with Slider
    # -----------------------------
    st.subheader("📄 Data Preview")

    rows = st.slider(
        "Select number of rows to preview",
        min_value=5,
        max_value=100,
        value=10
    )

    st.dataframe(df.head(rows))

    # -----------------------------
    # Column Detection
    # -----------------------------
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns
    categorical_cols = df.select_dtypes(include=["object"]).columns

    # -----------------------------
    # Sidebar Controls
    # -----------------------------
    st.sidebar.header("📊 Dashboard Controls")

    chart_type = st.sidebar.selectbox(
        "Select Chart Type",
        [
            "Bar Chart",
            "Column Chart",
            "Line Chart",
            "Scatter Plot",
            "Pie Chart",
            "Histogram",
            "Treemap",
            "Radial Bar Chart"
        ]
    )

    x_col = st.sidebar.selectbox(
        "Select X-axis",
        df.columns
    )

    y_col = st.sidebar.selectbox(
        "Select Y-axis",
        numeric_cols
    )

    # -----------------------------
    # Chart Generator
    # -----------------------------
    if chart_type == "Bar Chart":
        fig = px.bar(df, x=x_col, y=y_col)

    elif chart_type == "Column Chart":
        fig = px.bar(df, x=x_col, y=y_col)

    elif chart_type == "Line Chart":
        fig = px.line(df, x=x_col, y=y_col)

    elif chart_type == "Scatter Plot":
        fig = px.scatter(df, x=x_col, y=y_col)

    elif chart_type == "Pie Chart":
        fig = px.pie(df, names=x_col, values=y_col)

    elif chart_type == "Histogram":
        fig = px.histogram(df, x=y_col)

    elif chart_type == "Treemap":
        fig = px.treemap(df, path=[x_col], values=y_col)

    elif chart_type == "Radial Bar Chart":
        fig = px.pie(
            df,
            names=x_col,
            values=y_col,
            hole=0.55
        )

    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # KPI Section
    # -----------------------------
    st.subheader("📈 Key Metrics")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Rows", df.shape[0])
    col2.metric("Total Columns", df.shape[1])
    col3.metric("Missing Values", df.isnull().sum().sum())
