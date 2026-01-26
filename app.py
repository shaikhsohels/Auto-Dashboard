import streamlit as st
import pandas as pd

# Set page config FIRST
st.set_page_config(page_title="Power BI Clone", layout="wide")

try:
    from pygwalker.api.streamlit import StreamlitRenderer
except ImportError:
    st.error("PyGWalker not found. Please ensure it is in requirements.txt")

# Title and Styling
st.title("📊 Enterprise BI Dashboard")
st.markdown("---")

# --- Sidebar ---
with st.sidebar:
    st.header("1. Data Upload")
    file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])
    
    st.header("2. Settings")
    theme = st.selectbox("Theme", ["light", "dark"])

# --- Main Logic ---
if file is not None:
    try:
        # Load Data
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

        # Show KPIs
        col1, col2, col3 = st.columns(3)
        col1.metric("Rows", df.shape[0])
        col2.metric("Columns", df.shape[1])
        col3.metric("Duplicates", df.duplicated().sum())

        # The Tableau/PowerBI Workspace
        st.subheader("🛠️ Build Your Dashboard")
        
        # Initialize the renderer
        # This creates the Drag-and-Drop interface
        renderer = StreamlitRenderer(df, spec_io_mode="rw")
        renderer.explorer(theme=theme)

    except Exception as e:
        st.error(f"Analysis Error: {e}")
else:
    st.info("💡 Please upload a CSV or Excel file to begin.")
    # Show a placeholder for better UI
    st.image("https://streamlit.io/images/brand/streamlit-mark-color.png", width=100)
