import streamlit as st
import os
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
    
    # Updated Sector List to match Lancia's Service Lines
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
        min_value=5, 
        max_value=50, 
        value=15,
        help="Set the target margin improvement for the AI to model."
    )
    
    st.divider()
    
    # Visual Multi-Agent Status (Digital Boardroom)
    st.subheader("🤖 Active Agents")
    with st.expander("View Agent Status", expanded=True):
        st.write("🛡️ **Data Integrity Lead**: *Ready*")
        st.write("🚀 **Industry Strategist**: *Synced*")
        st.write("🛡️ **Red Team Auditor**: *Standby*")
        st.write("🏗️ **Implementation Lead**: *Ready*")
        st.write("📊 **Results365 Monitor**: *Active*")

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
        audit = st.session_state.de.run_ai_realise_audit
