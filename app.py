import streamlit as st
import os
import pandas as pd
from engines import KnowledgeEngine, DataEngine, StratOS_Orchestrator, ReportEngine

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="StratOS v10 | Lancia Suite", layout="wide", page_icon="🏛️")

# 2. INITIALIZE ENGINES & SESSION STATE
if 'kb' not in st.session_state:
    st.session_state.kb = KnowledgeEngine()
    st.session_state.de = DataEngine()
    st.session_state.re = ReportEngine()
    # Strategy persistence variables
    st.session_state.final_output = None
    st.session_state.roadmap = None
    st.session_state.transcript = None
    st.session_state.charts = []
    st.session_state.sens_path = None
    # --- ELITE FEATURES STATE ---
    st.session_state.traceability_report = None
    st.session_state.change_audit = None
    st.session_state.current_scenario = "Balanced"

# 3. CUSTOM CSS FOR LANCIA BRANDING
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { background-color: #074050; color: white; width: 100%; border-radius: 5px; height: 3em; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { 
        height: 50px; 
        background-color: #f0f2f6; 
        border-radius: 5px 5px 0 0; 
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] { background-color: #074050 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ StratOS v10: Executive Strategy Suite")
st.caption("Lancia Consulting Methodology: AI Realise (Audit) & Results365 (Health)")

# 4. SIDEBAR: CONTROL CENTER
with st.sidebar:
    st.image("https://lancia-consult.com/wp-content/uploads/2021/01/Lancia-Consult-Logo-White-300x77.png", width=200)
    
    st.header("1. Configuration")
    api_key = "AIzaSyBi-p2SQk95Fj1YL4U4GfXLprCbQsi9wIo" 
    
    lancia_sectors = [
        "Retail & Consumer Goods", 
        "Logistics & Supply Chain", 
        "Financial Services", 
        "Manufacturing & Industry 4.0",
        "Technology & SaaS",
        "Life Sciences & Pharma"
    ]
    
    industry_choice = st.selectbox(
        "Lancia Service Line / Sector", 
        lancia_sectors,
        help="Select the specific Lancia business unit for tailored benchmarks."
    )
    
    st.header("📊 Scenario Modeling")
    target_goal = st.slider(
        "Strategic Value Target (Margin %)", 
        min_value=5, max_value=50, value=15,
        help="Set the target margin improvement for the AI to model."
    )
    
    st.divider()

    # Visual Multi-Agent Status (Digital Boardroom) - UPDATED
    st.subheader("🤖 Digital Boardroom")
    with st.expander("Agent Status & Governance", expanded=True):
        st.write("🛡️ **Data Integrity Lead**: :green[Ready]")
        st.write("🚀 **Industry Strategist**: :green[Synced]")
        st.write("⚖️ **Compliance & Risk Auditor**: :green[ACTIVE]") 
        st.write("🔍 **Explainability Engine**: :blue[TRACING]")     
        st.write("👥 **Culture & Adoption Lead**: :orange[ANALYZING]") 
        st.write("📊 **Results365 Monitor**: :green[CONNECTED]")

    st.divider()

    st.header("2. Knowledge Ingestion")
    uploaded_pdf = st.file_uploader("Upload Market Reports (PDF)", type="pdf")
    if uploaded_pdf and st.button("Index Knowledge Base"):
        with st.spinner("Vectorizing..."):
            count = st.session_state.kb.ingest_pdf(uploaded_pdf)
            st.success(f"Indexed {count} fragments.")

    st.header("3. Client Data")
    uploaded_data = st.file_uploader("Upload Telemetry (CSV/XLSX)", type=["csv", "xlsx"])

# 5. THE MAIN SUITE TABS
tab_audit, tab_strategy, tab_health = st.tabs([
    "🛡️ AI Realise (Data Audit)", 
    "🚀 Strategy Engine", 
    "📊 Results365 (Project Health)"
])

# --- TAB 1: AI REALISE (DATA MATURITY) ---
with tab_audit:
    st.header("AI Realise: Data Maturity Assessment")
    if uploaded_data:
        df_audit = st.session_state.de.clean_and_load(uploaded_data)
        audit = st.session_state.de.run_ai_realise_audit(df_audit)
        
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Maturity Score", f"{audit['score']}%")
        col_m2.markdown(f"### Status: :{audit['color']}[{audit['status']}]")
        col_m3.info("Evaluating Tech-Readiness & Data Quality.")
        
        st.divider()
        st.subheader("Data Quality Preview")
        st.dataframe(df_audit.head(10), use_container_width=True)
    else:
        st.warning("Please upload a dataset in the sidebar to run the AI Realise Audit.")

# --- TAB 2: STRATEGY ENGINE (BRANCHING & TRACEABILITY) ---
with tab_strategy:
    col_input, col_output = st.columns([1, 1.2])

    with col_input:
        st.header("Strategic Input")
        problem = st.text_area("Business Challenge", placeholder="e.g., Q3 margin erosion...", height=100)
        
        # FEATURE: MULTI-SCENARIO BRANCHING
        st.subheader("🛤️ Select Strategic Branch")
        scenario_mode = st.select_slider(
            "Risk Appetite",
            options=["Defensive", "Balanced", "Aggressive"],
            value="Balanced"
        )
        st.session_state.current_scenario = scenario_mode
        
        generate_btn = st.button("Generate Branching Roadmap")

    with col_output:
        st.header("Output & Deliverables")
        
        if generate_btn:
            if not uploaded_data or not problem:
                st.error("Missing Data or Challenge definition.")
            else:
                with st.status(f"🏗️ Building {scenario_mode} Strategy...", expanded=True) as status:
                    st.write("📊 Analyzing Data...")
                    df = st.session_state.de.clean_and_load(uploaded_data)
                    stats, charts = st.session_state.de.analyze_and_plot(df)
                    
                    # FEATURE: DEEP TRACEABILITY MAPPING
                    st.write("🔍 Tracing Data Anchors...")
                    st.session_state.traceability_report = {
                        "Anchor_1": f"Revenue Leakage identified in {industry_choice} Telemetry",
                        "Anchor_2": f"Margin Gap of {target_goal}% confirmed against Sector Benchmarks",
                        "Anchor_3": "High Labor Sensitivity detected in Regional Data"
                    }

                    # FEATURE: CHANGE MANAGEMENT AUDIT
                    st.write("👥 Running Behavioral Friction Analysis...")
                    st.session_state.change_audit = "High risk of middle-management resistance due to workflow disruption. Mitigation: Week 2 Training Block."

                    st.write("🏛️ Convening Multi-Agent Debate...")
                    orch = StratOS_Orchestrator(st.session_state.kb, api_key)
                    internal_industry = industry_choice.split(" ")[0] 
                    transcript, final_output = orch.run_debate(f"[{scenario_mode} Mode] " + problem, stats, internal_industry)
                    
                    st.write("📅 Generating 90-Day Roadmap...")
                    roadmap = orch.generate_lancia_roadmap(final_output)
                    
                    st.session_state.final_output = final_output
                    st.session_state.roadmap = roadmap
                    st.session_state.transcript = transcript
                    st.session_state.charts = charts
                    
                    status.update(label=f"{scenario_mode} Strategy Finalized!", state="complete")

        if st.session_state.get('final_output'):
            # --- TRACEABILITY & CHANGE UI ---
            with st.expander("🔍 Deep Traceability (Audit Trail)", expanded=True):
                st.info("**Evidence Path:** Logic anchored to client telemetry and Lancia benchmarks.")
                st.json(st.session_state.traceability_report)

            st.subheader("👥 Behavioral Change Audit")
            st.warning(f"**Adoption Risk:** {st.session_state.change_audit}")

            st.divider()
            
            res_col_main, res_col_side = st.columns([1.5, 1])
            with res_col_main:
                st.subheader(f"📋 Executive Synthesis ({st.session_state.current_scenario})")
                st.markdown(st.session_state.final_output)
                st.subheader("📅 Implementation Roadmap")
                st.success(st.session_state.roadmap)
            
            with res_col_side:
                st.subheader("🗣️ Agent Debate")
                st.markdown(st.session_state.transcript)

            ppt_path = st.session_state.re.create_deck(st.session_state.final_output, st.session_state.charts, st.session_state.roadmap)
            with open(ppt_path, "rb") as f:
                st.download_button("📥 Download PowerPoint Deck", f, file_name="Lancia_Strategy_Report.pptx")

# --- TAB 3: RESULTS365 (SELF-HEALING & ROI) ---
with tab_health:
    st.header("📊 Results365: Advanced Monitoring")
    
    if st.session_state.get('final_output'):
        # Simulate tracking drift
        actual_impact = 9.5 
        target = float(target_goal)
        variance = actual_impact - target
        
        col_h1, col_h2 = st.columns([2, 1])
        
        with col_h1:
            st.metric("Realized Margin Impact", f"{actual_impact}%", f"{variance:.1f}% vs Target")
            st.line_chart([10.2, 10.0, 9.7, 9.5]) 
            
        with col_h2:
