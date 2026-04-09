import streamlit as st
import pandas as pd
import numpy as np
import google.generativeai as genai

# =========================================================
# THE STRATOS v11 ENGINE
# =========================================================
class StratOS11_Engine:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def run_debate(self, stats, industry):
        agents = {
            "Growth Agent": "Focus on expansion and top-line revenue.",
            "Risk Agent": "Focus on margin protection and failure points.",
            "Ops Agent": "Focus on lean execution and efficiency."
        }
        debate = {}
        for name, persona in agents.items():
            prompt = f"Role: {name}. {persona} Industry: {industry}. Data: {stats}. 2 tactical moves."
            debate[name] = self.model.generate_content(prompt).text
        return debate

    def synthesize(self, debate):
        prompt = f"Synthesize this 3-agent debate into a Lancia Strategy Mandate: {debate}"
        return self.model.generate_content(prompt).text

    def results365_audit(self, strategy):
        prompt = f"Results365 Audit: Rate delivery confidence (0-100%) and 3 execution risks: {strategy}"
        return self.model.generate_content(prompt).text

# =========================================================
# THE INTERFACE (Matching your 'Important' Screenshot)
# =========================================================
st.set_page_config(page_title="Lancia StratOS v11", layout="wide")

# Sidebar - Branding & Setup
with st.sidebar:
    st.image("https://lancia-consult.com/wp-content/uploads/2021/05/Lancia-Consult-Logo-Standard-RGB.png", width=200)
    st.header("Scenario Modeling")
    target_margin = st.slider("Target Margin Improvement (%)", 0, 50, 15)
    
    st.header("Knowledge Ingestion")
    st.file_uploader("Upload Market Reports (PDF)", type=['pdf'])
    
    st.header("Client Data")
    data_file = st.file_uploader("Upload Telemetry (CSV/XLSX)", type=['csv', 'xlsx'])
    
    st.divider()
    api_key = st.text_input("Gemini API Key", type="password")

if api_key:
    engine = StratOS11_Engine(api_key)
    st.title("🏛️ StratOS v11: Executive Strategy Suite")
    st.caption("Lancia Consulting Methodology: AI Realise (Audit) & Results365 (Health)")

    # THE TABBED INTERFACE FROM YOUR SCREENSHOT
    tab_audit, tab_engine, tab_health = st.tabs([
        "🛡️ AI Realise (Data Audit)", 
        "🚀 Strategy Engine", 
        "📊 Results365 (Project Health)"
    ])

    if data_file:
        df = pd.read_csv(data_file)
        
        with tab_audit:
            st.subheader("Results: AI Realise Data Maturity")
            score = round((1 - df.isnull().mean().mean()) * 100, 1)
            st.metric("Data Maturity", f"{score}%")
            st.write("---")
            st.dataframe(df.head(10))

        with tab_engine:
            if st.button("RUN STRATEGY ENGINE"):
                with st.spinner("Engaging Multi-Agent Debate..."):
                    stats = df.describe().to_string()
                    debate = engine.run_debate(stats, "Retail")
                    strategy = engine.synthesize(str(debate))
                    
                    # Store in session state for the Health tab
                    st.session_state['current_strat'] = strategy
                    st.session_state['current_debate'] = debate

            if 'current_strat' in st.session_state:
                st.subheader("3-Agent Strategic Debate")
                c1, c2, c3 = st.columns(3)
                c1.info(f"**Growth**\n\n{st.session_state['current_debate']['Growth Agent']}")
                c2.warning(f"**Risk**\n\n{st.session_state['current_debate']['Risk Agent']}")
                c3.success(f"**Ops**\n\n{st.session_state['current_debate']['Ops Agent']}")
                
                st.divider()
                st.subheader("Executive Mandate")
                st.markdown(st.session_state['current_strat'])

        with tab_health:
            st.subheader("Results365: Transformation Health-Check")
            if 'current_strat' in st.session_state:
                health = engine.results365_audit(st.session_state['current_strat'])
                st.success(health)
            else:
                st.info("Please generate a strategy in the 'Strategy Engine' tab to view health diagnostics.")
    
    st.divider()
    st.caption("StratOS v11 | Proprietary Lancia Consult Framework Integration")
else:
    st.warning("Please enter your API Key in the sidebar.")
