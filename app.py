import streamlit as st
import pandas as pd
import numpy as np
import google.generativeai as genai
import os

# =========================================================
# THE ORIGINAL STRATOS 11 ENGINE (Matched Logic)
# =========================================================

class StratOS11_Original:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def run_multi_agent_debate(self, stats_summary, industry):
        """Original 3-Agent Logic: Growth, Risk, and Ops Perspectives."""
        agents = {
            "Growth Agent": "Focus on visionary scaling and revenue expansion.",
            "Risk Agent": "Focus on margin protection and cost leakage.",
            "Ops Agent": "Focus on lean execution and supply chain stability."
        }
        debate_log = {}
        for name, persona in agents.items():
            prompt = f"Role: {name}. Persona: {persona}. Industry: {industry}. Data: {stats_summary}. Give 2 tactical moves."
            debate_log[name] = self.model.generate_content(prompt).text
        return debate_log

    def synthesize_mandate(self, debate_log):
        """Synthesizes the debate into the Executive Mandate."""
        prompt = f"Synthesize this 3-agent debate into a Lancia Strategy Mandate using the Pyramid Principle: {debate_log}"
        return self.model.generate_content(prompt).text

    def results365_audit(self, strategy):
        """Lancia Results365: Execution Confidence Check."""
        prompt = f"Audit this via Lancia Results365. Rate delivery confidence (0-100%) and identify 3 execution risks: {strategy}"
        return self.model.generate_content(prompt).text

    def red_team_stress_test(self, strategy):
        """Red Team Auditor: Finding Failure Points."""
        prompt = f"Act as a Red Team Auditor. Identify 3 critical failure points and mitigations for: {strategy}"
        return self.model.generate_content(prompt).text

# =========================================================
# THE ORIGINAL INTERFACE (Stable Build)
# =========================================================

st.set_page_config(page_title="Lancia StratOS 11", layout="wide")

with st.sidebar:
    st.image("https://lancia-consult.com/wp-content/uploads/2021/05/Lancia-Consult-Logo-Standard-RGB.png", width=200)
    st.divider()
    api_key = st.text_input("Gemini API Key", type="password")
    industry = st.selectbox("Industry Focus", ["Retail", "Manufacturing", "Logistics", "Energy"])
    data_file = st.file_uploader("Upload Client CSV", type=['csv'])

if api_key:
    orch = StratOS11_Original(api_key)
    st.title("Lancia StratOS 11")
    st.caption("Proprietary Multi-Agent Strategic Intelligence")

    if data_file:
        # The 'USD' Fix - restored original stable cleaning
        df = pd.read_csv(data_file)
        df.columns = df.columns.astype(str).str.replace('_USD', '', case=False).str.replace(' ', '_')
        
        # 📊 AI Realise Audit (The version that worked yesterday)
        st.subheader("📊 Lancia AI Realise Audit")
        maturity_score = round((1 - df.isnull().mean().mean()) * 100, 1)
        st.metric("Data Maturity", f"{maturity_score}%", "READY" if maturity_score > 85 else "REMEDIATE")

        if st.button("RUN STRATOS 11 ORCHESTRATION"):
            with st.spinner("Engaging Multi-Agent Debate..."):
                stats = df.describe().to_string()
                
                # 1. Run the Debate
                debate = orch.run_multi_agent_debate(stats, industry)
                
                # 2. Synthesize & Audit
                strategy = orch.synthesize_mandate(str(debate))
                results365 = orch.results365_audit(strategy)
                red_team = orch.red_team_stress_test(strategy)

                # --- UI DISPLAY: THE ORIGINAL 3-COLUMN DEBATE ---
                st.divider()
                st.subheader("🕵️ The Strategic Debate")
                c1, c2, c3 = st.columns(3)
                c1.info(f"**Growth**\n\n{debate['Growth Agent']}")
                c2.warning(f"**Risk**\n\n{debate['Risk Agent']}")
                c3.success(f"**Ops**\n\n{debate['Ops Agent']}")

                # --- UI DISPLAY: THE FINAL MANDATE & AUDITS ---
                st.divider()
                tab1, tab2, tab3 = st.tabs(["Strategy Mandate", "✅ Results365 Health", "🛡️ Red Team Audit"])
                
                with tab1:
                    st.markdown(strategy)
                    st.line_chart(df.select_dtypes(include=[np.number]).iloc[:, 0])
                
                with tab2:
                    st.info(results365)
                
                with tab3:
                    st.error("RED TEAM CRITICAL FINDINGS")
                    st.markdown(red_team)
else:
    st.warning("Please enter your API Key in the sidebar.")
