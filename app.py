import streamlit as st
import pandas as pd
import numpy as np
import google.generativeai as genai
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

# =========================================================
# THE ENGINE: STRATOS v11 (With Knowledge Context)
# =========================================================
class StratOS11:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.knowledge_context = ""

    def ingest_pdf(self, uploaded_file):
        """Processes PDF and stores text for context."""
        try:
            with open("temp_report.pdf", "wb") as f:
                f.write(uploaded_file.getbuffer())
            loader = PyPDFLoader("temp_report.pdf")
            pages = loader.load()
            # Extract text from first 5 pages to keep context window clean
            self.knowledge_context = " ".join([p.page_content for p in pages[:5]])
            os.remove("temp_report.pdf")
            return True
        except Exception as e:
            st.error(f"Ingestion Error: {e}")
            return False

    def run_agent_debate(self, stats, industry):
        agents = {
            "Growth": "Visionary scaling and top-line expansion.",
            "Risk": "Margin protection and structural failure points.",
            "Ops": "Execution efficiency and lean scalability."
        }
        debate = {}
        # Inject Knowledge Context if available
        context_prompt = f"Context from Market Reports: {self.knowledge_context[:2000]}" if self.knowledge_context else ""
        
        for name, persona in agents.items():
            prompt = f"Role: {name} Agent. Persona: {persona}. Industry: {industry}. {context_prompt}. Data: {stats}. Give 2 tactical moves."
            debate[name] = self.model.generate_content(prompt).text
        return debate

    def synthesize(self, debate):
        prompt = f"Synthesize this 3-agent debate into a Lancia Strategy Mandate: {debate}"
        return self.model.generate_content(prompt).text

    def results365_audit(self, strategy):
        prompt = f"Lancia Results365 Health Check. Rate confidence (0-100%) and 3 risks for: {strategy}"
        return self.model.generate_content(prompt).text

# =========================================================
# THE INTERFACE (Matching Screenshot)
# =========================================================
st.set_page_config(page_title="StratOS v11", layout="wide")

with st.sidebar:
    st.image("https://lancia-consult.com/wp-content/uploads/2021/05/Lancia-Consult-Logo-Standard-RGB.png", width=200)
    
    st.header("Scenario Modeling")
    st.slider("Target Margin Improvement (%)", 0, 50, 15)
    
    # --- THE KNOWLEDGE INGESTION SECTION ---
    st.header("Knowledge Ingestion")
    st.write("Upload Market Reports (PDF)")
    pdf_file = st.file_uploader("Upload", type=['pdf'], key="knowledge_upload", label_visibility="collapsed")
    
    st.header("Client Data")
    st.write("Upload Telemetry (CSV/XLSX)")
    data_file = st.file_uploader("Upload", type=['csv', 'xlsx'], key="data_upload", label_visibility="collapsed")
    
    st.divider()
    api_key = st.text_input("Gemini API Key", type="password")

if api_key:
    engine = StratOS11(api_key)
    st.title("🏛️ StratOS v11: Executive Strategy Suite")
    st.caption("Lancia Consulting Methodology: AI Realise (Audit) & Results365 (Health)")

    # THE CORE TABS
    tab_audit, tab_engine, tab_health = st.tabs([
        "🛡️ AI Realise (Data Audit)", 
        "🚀 Strategy Engine", 
        "📊 Results365 (Project Health)"
    ])

    # Handle PDF Ingestion
    if pdf_file:
        if engine.ingest_pdf(pdf_file):
            st.sidebar.success("Knowledge Ingested Successfully")

    if data_file:
        df = pd.read_csv(data_file)
        
        with tab_audit:
            st.subheader("Results: AI Realise Data Maturity")
            score = round((1 - df.isnull().mean().mean()) * 100, 1)
            st.metric("Data Maturity", f"{score}%", "READY")
            st.dataframe(df.head(10), use_container_width=True)

        with tab_engine:
            if st.button("EXECUTE STRATEGY ENGINE"):
                with st.spinner("Orchestrating Agents..."):
                    stats = df.describe().to_string()
                    # Run the debate using both Data and Knowledge
                    st.session_state['debate'] = engine.run_agent_debate(stats, "Corporate")
                    st.session_state['strat'] = engine.synthesize(st.session_state['debate'])

            if 'strat' in st.session_state:
                st.subheader("3-Agent Strategic Debate")
                c1, c2, c3 = st.columns(3)
                c1.info(f"**Growth**\n\n{st.session_state['debate']['Growth']}")
                c2.warning(f"**Risk**\n\n{st.session_state['debate']['Risk']}")
                c3.success(f"**Ops**\n\n{st.session_state['debate']['Ops']}")
                
                st.divider()
                st.subheader("Executive Mandate")
                st.markdown(st.session_state['strat'])

        with tab_health:
            st.subheader("Results365: Transformation Health-Check")
            if 'strat' in st.session_state:
                health = engine.results365_audit(st.session_state['strat'])
                st.success(health)
            else:
                st.info("Please generate a strategy in the 'Strategy Engine' tab first.")
else:
    st.warning("Please enter your API Key in the sidebar.")
