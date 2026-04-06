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
    api_key = "AIzaSyBi-p2SQk95Fj1YL4U4GfXLprCbQsi9wIo" 
    
    st.header("🏢 Industry Context")
    industry_choice = st.selectbox(
        "Target Industry Benchmark", 
        ["Retail", "SaaS", "Manufacturing"]
    )
    
    st.header("📊 Scenario Modeling")
    target_goal = st.slider("Target Margin Improvement (%)", 5, 50, 15)
    
    st.header("2. Knowledge Ingestion")
    st.info("Upload market reports or competitor PDFs to 'prime' the AI's memory.")
    uploaded_pdf = st.file_uploader("Upload PDF Reports", type="pdf")
    if uploaded_pdf and st.button("Index PDF"):
        with st.spinner("Vectorizing Knowledge..."):
            count = st.session_state.kb.ingest_pdf(uploaded_pdf)
            st.success(f"Indexed {count} text fragments.")

# Main Dashboard Area
col1, col2 = st.columns([1, 1.2]) # Slightly wider right column for debate view

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
            # --- NEW FEATURE: LOGIC MAPPING (Visual Chain of Thought) ---
            with st.status("🗺️ Mapping Strategic Logic...", expanded=True) as status:
                st.write("📊 Analyzing historical data telemetry...")
                de = DataEngine()
                df = de.clean_and_load(uploaded_data)
                
                if df is not None:
                    stats, charts = de.analyze_and_plot(df)
                    
                    st.write("🏛️ Convening Multi-Agent Consensus Debate...")
                    orch = StratOS_Orchestrator(st.session_state.kb, api_key)
                    # Use the new run_debate function
                    debate_transcript, final_output = orch.run_debate(problem, stats, industry_choice)
                    
                    st.write("📈 Modeling Profit Sensitivity Curves...")
                    # Pass the slider value to the math engine
                    sens_path = de.generate_sensitivity(target_goal)
                    charts.append(sens_path) # Include in PPTX
                    
                    status.update(label="Strategic Logic Mapped!", state="complete", expanded=False)

                    # --- DISPLAY SECTION ---
                    # Left sub-column for Main Output, Right sub-column for Debate
                    res_col1, res_col2 = st.columns([1.5, 1])
                    
                    with res_col1:
                        st.subheader("📋 Executive Synthesis")
                        st.markdown(final_output)
                        
                        st.image(sens_path, caption="Strategic Sensitivity: Efficiency vs. Margin")
                        
                        st.info(f"💡 **Scenario Analysis:** To achieve a **{target_goal}%** boost, "
                                f"StratOS identifies a required efficiency gain of ~**{target_goal * 0.82:.1f}%** "
                                f"relative to current OpEx.")

                    with res_col2:
                        st.subheader("🗣️ Agent Debate")
                        st.markdown(debate_transcript)
                        
                        with st.expander("🛡️ View Red Team Risk Audit"):
                            st.write("Auditing strategy for execution blindspots...")
                            risk_audit = orch.run_red_team_audit(final_output)
                            st.warning(risk_audit)
                    
                    # 5. Generate PPTX
                    re = ReportEngine()
                    ppt_path = re.create_deck(final_output, charts)
                    
                    with open(ppt_path, "rb") as f:
                        st.download_button(
                            label="📥 Download PowerPoint Strategy Deck",
                            data=f,
                            file_name="StratOS_Executive_Report.pptx",
                            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                        )
                    
                    with st.expander("View Sanitized Data Preview"):
                        st.dataframe(df.head())
                else:
                    st.error("Critical Error: Could not read data file.")

st.markdown("---")
st.caption("StratOS v10 | Proprietary Augmented Consulting Framework")
