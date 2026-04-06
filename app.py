import streamlit as st
import pandas as pd
from engines import KnowledgeEngine, DataEngine, StratOS_Orchestrator, ReportEngine

st.set_page_config(page_title="StratOS AI", page_icon="🏛️", layout="wide")

st.title("🏛️ StratOS v10: Strategy & Business Analysis")
st.markdown("Automated Consulting Intelligence using MBB Frameworks")

# Initialize engines in session state
if 'kb' not in st.session_state:
    st.session_state.kb = KnowledgeEngine()

# Sidebar
# Sidebar
with st.sidebar:
    st.header("1. Configuration")
    # Check for secret key first, then fall back to input box
    api_key = st.secrets.get("GOOGLE_API_KEY") or st.text_input("Enter Google API Key", type="password")
    
    st.header("2. Knowledge Ingestion")
    uploaded_pdf = st.file_uploader("Upload Market Reports (PDF)", type="pdf")
    if uploaded_pdf and st.button("Index PDF"):
        count = st.session_state.kb.ingest_pdf(uploaded_pdf)
        st.success(f"Indexed {count} fragments.")

# Main Body
st.header("3. Strategic Analysis")
uploaded_csv = st.file_uploader("Upload Client Dataset (CSV)", type="csv")
problem = st.text_area("What is the Business Challenge?", height=150)

if st.button("Generate Strategy Report"):
    if not api_key or not uploaded_csv or not problem:
        st.error("Missing API Key, CSV, or Business Problem!")
    else:
        with st.spinner("Analyzing data and generating strategy..."):
            # Load Data
            df = pd.read_csv(uploaded_csv)
            
            # Run Engines
            de = DataEngine()
            stats, charts = de.analyze_and_plot(df)
            
            orch = StratOS_Orchestrator(st.session_state.kb, api_key)
            final_output = orch.run_loop(problem, stats)
            
            re = ReportEngine()
            ppt_path = re.create_deck(final_output, charts)
            
            # Display Result
            st.subheader("Executive Synthesis")
            st.markdown(final_output)
            
            with open(ppt_path, "rb") as f:
                st.download_button("📥 Download Executive PPTX", f, file_name="Strategy_Report.pptx")
