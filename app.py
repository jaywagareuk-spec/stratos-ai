import streamlit as st
import os
from engines import KnowledgeEngine, DataEngine, StratOS_Orchestrator, ReportEngine

# 1. Page Config
st.set_page_config(page_title="Lancia StratOS AI", layout="wide")

# 2. Initialize Engines in Session State
if "kb" not in st.session_state:
    st.session_state.kb = KnowledgeEngine()
if "de" not in st.session_state:
    st.session_state.de = DataEngine()
if "re" not in st.session_state:
    st.session_state.re = ReportEngine()

# 3. Sidebar
with st.sidebar:
    st.title("Settings")
    api_key = st.text_input("Gemini API Key", type="password")
    industry = st.selectbox("Industry", ["Retail", "Logistics", "Manufacturing", "Utilities"])
    uploaded_file = st.file_uploader("Upload CSV", type=['csv'])

# 4. Main App Logic
if api_key:
    orch = StratOS_Orchestrator(st.session_state.kb, api_key)
    st.title("Lancia StratOS AI")

    if uploaded_file:
        df = st.session_state.de.clean_and_load(uploaded_file)
        if df is not None:
            # Audit Logic
            audit = st.session_state.de.run_ai_realise_audit(df)
            st.metric("Data Maturity", f"{audit['score']}%", audit['status'])
            
            if st.button("Generate Strategy"):
                with st.spinner("Analyzing data trends..."):
                    stats, charts = st.session_state.de.analyze_and_plot(df)
                    transcript, synthesis = orch.run_debate("Diagnose profit/loss", stats, industry)
                    
                    st.subheader("Executive Synthesis")
                    st.markdown(synthesis)
                    
                    for chart in charts:
                        st.image(chart)
                        
                    report_path = st.session_state.re.create_deck(synthesis, charts)
                    with open(report_path, "rb") as f:
                        st.download_button("Download PPTX Report", f, "Lancia_Report.pptx")
else:
    st.warning("Please enter your API Key to start the StratOS Engines.")
