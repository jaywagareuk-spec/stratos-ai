import streamlit as st
import os
from engines import KnowledgeEngine, DataEngine, StratOS_Orchestrator, ReportEngine

# UI Configuration
st.set_page_config(page_title="Lancia StratOS AI", layout="wide", initial_sidebar_state="expanded")

# Initialize Session State
if "kb" not in st.session_state: st.session_state.kb = KnowledgeEngine()
if "de" not in st.session_state: st.session_state.de = DataEngine()
if "re" not in st.session_state: st.session_state.re = ReportEngine()

# Sidebar Setup
with st.sidebar:
    st.image("https://lancia-consult.com/wp-content/uploads/2021/05/Lancia-Consult-Logo-Standard-RGB.png", width=200)
    st.title("Control Tower")
    api_key = st.text_input("Gemini API Key", type="password")
    industry = st.selectbox("Industry Focus", ["Retail", "Manufacturing", "Logistics", "Utilities"])
    
    st.divider()
    pdf_file = st.file_uploader("Upload Strat Vault (PDF)", type=['pdf'])
    if pdf_file:
        count = st.session_state.kb.ingest_pdf(pdf_file)
        st.success(f"Vault Updated: {count} chunks indexed.")
    
    st.divider()
    data_file = st.file_uploader("Client Telemetry (CSV/Excel)", type=['csv', 'xlsx'])

# Main Application
if api_key:
    orch = StratOS_Orchestrator(st.session_state.kb, api_key)
    st.title("Lancia StratOS AI")
    st.caption("Strategic Intelligence & Performance Orchestration")

    if data_file:
        df = st.session_state.de.clean_and_load(data_file)
        if df is not None:
            # AI Realise Audit
            audit = st.session_state.de.run_ai_realise_audit(df)
            col1, col2 = st.columns([1, 3])
            with col1:
                st.metric("AI Realise Score", f"{audit['score']}%", audit['status'])
            with col2:
                st.progress(audit['score']/100)

            # Execution Tabs
            tab1, tab2, tab3 = st.tabs(["Strategy Synthesis", "Risk & Roadmap", "Results365 Audit"])

            if st.button("RUN STRATEGOS ENGINE"):
                with st.spinner("Orchestrating Strategic Agents..."):
                    stats, charts = st.session_state.de.analyze_and_plot(df)
                    transcript, synthesis = orch.run_debate("Analyze negative margin vs inventory collapse", stats, industry)
                    roadmap = orch.generate_lancia_roadmap(synthesis)
                    red_team = orch.run_red_team_audit(synthesis)
                    health_check = st.session_state.re.run_results365_check(synthesis, orch)
                    sens_plot = st.session_state.de.generate_sensitivity(15)

                    with tab1:
                        st.subheader("Executive Synthesis (Balanced)")
                        st.markdown(synthesis)
                        for chart in charts: st.image(chart)
                        st.image(sens_plot)

                    with tab2:
                        st.subheader("90-Day Implementation Roadmap")
                        st.markdown(roadmap)
                        st.divider()
                        st.subheader("Red Team Audit (Stress Test)")
                        st.error(red_team)

                    with tab3:
                        st.subheader("Results365 Health Diagnostic")
                        st.info(health_check)
                        
                        report_path = st.session_state.re.create_deck(synthesis, charts, roadmap)
                        with open(report_path, "rb") as f:
                            st.download_button("Export Lancia Strategy Deck", f, file_name="Strategy_Mandate.pptx")
else:
    st.warning("StratOS requires an authorized API Key to initialize.")
