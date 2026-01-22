import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Auto Dashboard", layout="wide")

st.title("📊 Automated Data Dashboard")

uploaded_file = st.file_uploader(
    "Upload CSV or Excel file",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.subheader("Preview of Data")
    st.dataframe(df.head())

    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns
    categorical_cols = df.select_dtypes(include=["object"]).columns

    st.sidebar.header("Dashboard Controls")

    if len(categorical_cols) > 0 and len(numeric_cols) > 0:
        x_axis = st.sidebar.selectbox("Select Category", categorical_cols)
        y_axis = st.sidebar.selectbox("Select Value", numeric_cols)

        chart_type = st.sidebar.radio(
            "Select Chart Type",
            ["Bar Chart", "Line Chart", "Pie Chart"]
        )

        if chart_type == "Bar Chart":
            fig = px.bar(df, x=x_axis, y=y_axis)
        elif chart_type == "Line Chart":
            fig = px.line(df, x=x_axis, y=y_axis)
        else:
            fig = px.pie(df, names=x_axis, values=y_axis)

        st.plotly_chart(fig, use_container_width=True)

    st.success("Dashboard created successfully ✅")

