import streamlit as st
import pandas as pd
from pygwalker.api.streamlit import StreamlitRenderer

# --- App Configuration ---
st.set_page_config(
    page_title="Enterprise AI Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom Styling for a "Corporate BI" look
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    stApp { border-top: 5px solid #0078d4; } /* Power BI Blue */
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Enterprise Auto-BI Engine")
st.write("Upload any dataset to launch a full Tableau-style workspace.")

# --- Sidebar Management ---
with st.sidebar:
    st.header("📂 Data Connectivity")
    source = st.radio("Select Source", ["Local File", "SQL Database", "Sample Data"])
    
    df = None

    if source == "Local File":
        uploaded_file = st.file_uploader("Upload CSV, Excel, or JSON", type=["csv", "xlsx", "json"])
        if uploaded_file:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file)
            else:
                df = pd.read_json(uploaded_file)

    elif source == "SQL Database":
        db_url = st.text_input("Connection String", "sqlite:///demo.db")
        query = st.text_area("SQL Query", "SELECT * FROM table")
        if st.button("Connect"):
            from sqlalchemy import create_engine
            engine = create_engine(db_url)
            df = pd.read_sql(query, engine)

    elif source == "Sample Data":
        # Load a default dataset for instant demo
        df = pd.read_csv("https://raw.githubusercontent.com/mwaskom/seaborn-data/master/penguins.csv")

# --- Dashboard Engine ---
if df is not None:
    # 1. KPI Ribbon (Like Power BI top bar)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Rows", f"{df.shape[0]:,}")
    col2.metric("Columns", len(df.columns))
    col3.metric("Missing Values", df.isna().sum().sum())
    col4.metric("Data Size", f"{df.memory_usage().sum() / 1024:.1f} KB")

    # 2. Tableau-style Workspace
    st.divider()
    
    # We use StreamlitRenderer to keep the "State" (your charts) saved 
    # as you work. 'spec' saves your dashboard configuration.
    renderer = StreamlitRenderer(df, spec="./dw_config.json", spec_io_mode="rw")
    
    st.subheader("🎨 Visual Workspace")
    renderer.explorer()
    
else:
    st.info("👋 Welcome! Please upload a file in the sidebar to start building your dashboard.")
    # Show a professional placeholder image or instructions
