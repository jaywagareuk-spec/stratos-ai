import streamlit as st
from engines import KnowledgeEngine, DataEngine, StratOS_Orchestrator, ReportEngine

# Page Config
st.set_page_config(page_title="StratOS v10 | Strategy Engine", layout="wide")

# Initialize Session State for the Knowledge Base
if 'kb' not in st.session_state:
    st.session_state.kb = KnowledgeEngine()

# Custom CSS for a professional "Consulting" look
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { background-color: #074050; color: white; width: 100%; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ StratOS v10: Executive Strategy Mandate")
st.markdown("---")

# Sidebar Configuration
with st.sidebar:
    st.header("1. Configuration")
    # Secret Key check or Manual Input
    api_key = api_key = "AIzaSyBamfqYWmB72jcqpDPmqKRVEOd9_0TJ37s"
    
    st.header("2. Knowledge Ingestion")
    st.info("Upload market reports or competitor PDFs to 'prime' the AI's memory.")
    uploaded_pdf = st.file_uploader("Upload PDF Reports", type="pdf")
    if uploaded_pdf and st.button("Index PDF"):
        with st.spinner("Vectorizing Knowledge..."):
            count = st.session_state.kb.ingest_pdf(uploaded_pdf)
            st.success(f"Indexed {count} text fragments.")

# Main Dashboard Area
col1, col2 = st.columns([1, 1])

with col1:
    st.header("3. Strategic Input")
    uploaded_data = st.file_uploader("Upload Client Dataset (CSV or Excel)", type=["csv", "xlsx"])
    problem = st.text_area("What is the Business Challenge?", 
                          placeholder="Example: Analyze our Q3 margin erosion and suggest a 3-step recovery plan.",
                          height=150)
    
    generate_btn = st.button("Generate Strategy Report")

with col2:
    st.header("4. Output & Deliverables")
    
    if generate_btn:
        if not api_key:
            st.error("Missing API Key. Please provide one in the sidebar.")
        elif not uploaded_data:
            st.error("Please upload a CSV or Excel file to analyze.")
        elif not problem:
            st.error("Please define the business challenge.")
        else:
            with st.spinner("Orchestrating Strategy... (Analyzing Data + PDF Context)"):
                # 1. Process Data
                de = DataEngine()
                df = de.clean_and_load(uploaded_data)
                
                if df is None:
                    st.error("Critical Error: Could not read data file. Check formatting.")
                else:
                    # 2. Run Analytics
                    stats, charts = de.analyze_and_plot(df)
                    
                    # 3. Run AI Orchestrator
                    orch = StratOS_Orchestrator(st.session_state.kb, api_key)
                    final_output = orch.run_loop(problem, stats)
                    
                    # 4. Generate PPTX
                    re = ReportEngine()
                    ppt_path = re.create_deck(final_output, charts)
                    
                    # 5. Display Results
                    st.subheader("Executive Synthesis")
                    st.markdown(final_output)
                    
                    with open(ppt_path, "rb") as f:
                        st.download_button(
                            label="📥 Download PowerPoint Strategy Deck",
                            data=f,
                            file_name="StratOS_Executive_Report.pptx",
                            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                        )
                    
                    # Show data preview for transparency
                    with st.expander("View Sanitized Data Preview"):
                        st.dataframe(df.head())

st.markdown("---")
st.caption("StratOS v10 | Proprietary Augmented Consulting Framework")
