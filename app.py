import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import google.generativeai as genai
import os

# =========================================================
# THE LANCIA CORE ENGINES
# =========================================================

class LanciaStratOS:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def ai_realise_audit(self, df):
        """Lancia AI Realise Framework: Diagnostic for Data Maturity."""
        completeness = (1 - df.isnull().mean().mean()) * 100
        numeric_density = (len(df.select_dtypes(include=[np.number]).columns) / len(df.columns)) * 100
        score = round((completeness + numeric_density) / 2, 1)
        status = "STRATEGICALLY READY" if score > 85 else "REMEDIATION ADVISED"
        return score, status

    def results365_diagnostic(self, strategy):
        """Lancia Results365: Performance and Execution Health Check."""
        prompt = f"Audit this strategy using the Lancia Results365 framework. Rate delivery confidence (0-100%) and identify 3 execution risks: {strategy}"
        return self.model.generate_content(prompt).text

    def red_team_audit(self, strategy):
        """Red Team Stress-Test: Rigorous Risk Mitigation."""
        prompt = f"Act as a Red Team Auditor. Identify 3 structural failure points in this strategy and provide specific mitigations: {strategy}"
        return self.model.generate_content(prompt).text

    def synthesize_strategy(self, data_summary, industry):
        prompt = f"Act as a Lancia Consultant. Based on this data: {data_summary}, develop a 3-pillar strategy for the {industry} sector using the Pyramid Principle."
        return self.model.generate_content(prompt).text

# =========================================================
# THE INTERFACE
# =========================================================

st.set_page_config(page_title="Lancia StratOS AI", layout="wide")

# Sidebar - Branding & Inputs
with st.sidebar:
    st.image("https://lancia-consult.com/wp-content/uploads/2021/05/Lancia-Consult-Logo-Standard-RGB.png", width=200)
    st.divider()
    api_key = st.text_input("Gemini API Key", type="password")
    industry = st.selectbox("Industry Focus", ["Retail", "Manufacturing", "Logistics", "Energy"])
    data_file = st.file_uploader("Upload Client Telemetry (CSV)", type=['csv'])

if api_key:
    engine = LanciaStratOS(api_key)
    st.title("Lancia StratOS AI")
    st.caption("Proprietary Strategic Intelligence Platform")

    if data_file:
        # Data Cleaning (The USD Fix)
        df = pd.read_csv(data_file)
        df.columns = df.columns.astype(str).str.replace('_USD', '', case=False).str.replace(' ', '_')
        
        # --- SECTION 1: AI REALISE AUDIT ---
        st.subheader("📊 Lancia AI Realise: Data Maturity")
        score, status = engine.ai_realise_audit(df)
        c1, c2 = st.columns(2)
        c1.metric("Maturity Score", f"{score}%")
        c2.info(f"Audit Status: {status}")

        if st.button("EXECUTE FULL STRATEGIC ORCHESTRATION"):
            with st.spinner("Processing through Lancia Frameworks..."):
                # Run Logic
                data_summary = df.describe().to_string()
                strategy = engine.synthesize_strategy(data_summary, industry)
                health = engine.results365_diagnostic(strategy)
                red_team = engine.red_team_audit(strategy)

                # --- DISPLAY OUTPUTS ---
                tab1, tab2, tab3 = st.tabs(["Strategic Synthesis", "Results365 Diagnostic", "🛡️ Red Team Stress-Test"])
                
                with tab1:
                    st.markdown("### Executive Strategy Synthesis")
                    st.markdown(strategy)
                    # Visual Trend
                    num_cols = df.select_dtypes(include=[np.number]).columns
                    if not num_cols.empty:
                        st.line_chart(df[num_cols[0]])
                
                with tab2:
                    st.markdown("### Results365 Execution Audit")
                    st.info(health)
                
                with tab3:
                    st.markdown("### Red Team Failure Analysis")
                    st.error("CRITICAL VULNERABILITIES IDENTIFIED")
                    st.markdown(red_team)
else:
    st.warning("Please provide your API Key in the sidebar to initialize the StratOS Engines.")
