import streamlit as st
import os
from engines import KnowledgeEngine, DataEngine, StratOS_Orchestrator, ReportEngine

# Page Config
st.set_page_config(page_title="StratOS v10 | Lancia Suite", layout="wide")

# --- INITIALIZE SESSION STATE ---
# This ensures data persists across tab switches and button clicks
if 'kb' not in st.session_state:
    st.session_state.kb = KnowledgeEngine()
    st.session_state.de = DataEngine()
    st.session_state.re = ReportEngine()
    # Storage for generated outputs
    st.session_state.final_output = None
    st.session_state.roadmap = None
    st.session_state.transcript = None
    st.session_state.charts = []

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { background-color: #074050; color: white; width: 100%; border-radius: 5px; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #f0f2f6; border-radius: 5px 5px 0 0; }
    .stTabs [aria-selected="true"] { background-color: #074050 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ StratOS v10: Executive Strategy Suite")
st.caption("Powered by Lancia Consulting Methodology: AI Realise & Results365")

# Sidebar Configuration
with st.sidebar:
    st.header("1. Configuration")
    # API Key - Ensure this is valid
    api_key = "AIzaSyBi-p2SQk95Fj1YL4U4GfXLprCbQsi9wIo" 
    
    # Initialize Orchestrator to get industries
    orch_init = StratOS_Orchestrator(st.session_state.kb, api_key)
    industry_choice = st.selectbox(
        "Lancia Service Line / Sector", 
        list(orch_init.get_persona_database().keys())
    )
    
    st.header("📊 Scenario Modeling")
    target_goal = st.slider("Target Margin Improvement (%)", 5, 50, 15)
    
    st.header("2. Knowledge Ingestion")
    uploaded_pdf = st.file_uploader("Upload Market Reports (PDF)", type="pdf")
    if uploaded_pdf and st.button("Index Knowledge Base"):
        with st.spinner("Vectorizing..."):
            count = st.session_state.kb.ingest_pdf(uploaded_pdf)
            st.success(f"Indexed {count} fragments.")

    st.divider()
    st.header("3. Client Data")
    uploaded_data = st.file_uploader("Upload Telemetry (CSV/XLSX)", type=["csv", "xlsx"])

# --- MAIN INTERFACE: THE LANCIA TABS ---
tab_audit, tab_strategy, tab_health = st.tabs([
    "🛡️ AI Realise (Data Audit)", 
    "🚀 Strategy Engine", 
    "📊 Results365 (Project Health)"
])

# --- TAB 1: AI REALISE ---
with tab_audit:
    st.header("AI Realise: Data Maturity Assessment")
    if uploaded_data:
        df_audit = st.session_state.de.clean_and_load(uploaded_data)
        audit = st.session_state.de.run_ai_realise_audit(df_audit)
        
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Maturity Score", f"{audit['score']}%")
        col_m2.markdown(f"### Status: :{audit['color']}[{audit['status']}]")
        col_m3.info("Lancia AI Realise evaluates tech-readiness and data integrity.")
        
        st.divider()
        st.subheader("Data Quality Preview")
        st.dataframe(df_audit.head(10), use_container_width=True)
    else:
        st.warning("Please upload a dataset in the sidebar to run the AI Realise Audit.")

# --- TAB 2: STRATEGY ENGINE ---
with tab_strategy:
    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.header("Strategic Input")
        problem = st.text_area("Business Challenge", placeholder="Define the problem...", height=150)
        generate_btn = st.button("Generate Executive Mandate")

    with col2:
        st.header("Output & Deliverables")
        
        if generate_btn:
            if not uploaded_data or not problem:
                st.error("Missing Data or Challenge definition.")
            else:
                with st.status("🗺️ Executing Strategy Cycle...", expanded=True) as status:
                    st.write("📊 Analyzing Data...")
                    df = st.session_state.de.clean_and_load(uploaded_data)
                    stats, charts = st.session_state.de.analyze_and_plot(df)
                    
                    st.write("🏛️ Convening Multi-Agent Debate...")
                    orch = StratOS_Orchestrator(st.session_state.kb, api_key)
                    transcript, final_output = orch.run_debate(problem, stats, industry_choice)
                    
                    st.write("📅 Generating 90-Day Roadmap...")
                    roadmap = orch.generate_lancia_roadmap(final_output)
                    
                    st.write("📈 Modeling Profit Sensitivity...")
                    sens_path = st.session_state.de.generate_sensitivity(target_goal)
                    charts.append(sens_path)
                    
                    # Store in session state so Tab 3 can see it
                    st.session_state.final_output = final_output
                    st.session_state.roadmap = roadmap
                    st.session_state.transcript = transcript
                    st.session_state.charts = charts
                    st.session_state.sens_path = sens_path
                    
                    status.update(label="Strategy & Roadmap Finalized!", state="complete")

        # Persistent Display (Shows data if it exists in session state)
        if st.session_state.final_output:
            res_col1, res_col2 = st.columns([1.5, 1])
            with res_col1:
                st.subheader("📋 Executive Synthesis")
                st.markdown(st.session_state.final_output)
                
                st.subheader("📅 Lancia 90-Day Implementation Roadmap")
                st.success(st.session_state.roadmap)
                
                st.image(st.session_state.sens_path, caption="Strategic Sensitivity Graph")

            with res_col2:
                st.subheader("🗣️ Agent Debate")
                st.markdown(st.session_state.transcript)
                
                with st.expander("🛡️ View Red Team Risk Audit"):
                    risk_audit = orch_init.run_red_team_audit(st.session_state.final_output)
                    st.warning(risk_audit)

            # PPTX Generation
            ppt_path = st.session_state.re.create_deck(
                st.session_state.final_output, 
                st.session_state.charts, 
                st.session_state.roadmap
            )
            with open(ppt_path, "rb") as f:
                st.download_button("📥 Download PowerPoint Deck", f, file_name="Lancia_Strategy_Report.pptx")

# --- TAB 3: RESULTS365 ---
with tab_health:
    st.header("Results365: Transformation Health-Check")
    st.write("Ensuring long-term value realization and project stability.")
    
    if st.session_state.final_output:
        if st.button("Run Health-Check Audit"):
            with st.spinner("Analyzing for delivery risks..."):
                orch = StratOS_Orchestrator(st.session_state.kb, api_key)
                health_prompt = st.session_state.re.run_results365_check(st.session_state.final_output)
                health_results = orch.call_gemini(health_prompt)
                st.markdown("### Results365 Findings")
                st.info(health_results)
    else:
        st.info("Please generate a strategy in the 'Strategy Engine' tab to view health diagnostics.")

st.markdown("---")
st.caption("StratOS v10 | Lancia Consult Framework Integration")
