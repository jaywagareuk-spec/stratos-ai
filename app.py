import os
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import google.generativeai as genai
import chromadb
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# =========================================================
# THE ENGINES
# =========================================================

class LanciaEngines:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.chroma_client = chromadb.Client()
        try:
            self.collection = self.chroma_client.create_collection(name="strat_vault")
        except:
            self.collection = self.chroma_client.get_collection(name="strat_vault")

    def ai_realise_audit(self, df):
        """Lancia AI Realise: Data Maturity Diagnostic."""
        score = round(((1 - df.isnull().mean().mean()) * 100 + (len(df.select_dtypes(include=[np.number]).columns) / len(df.columns)) * 100) / 2, 1)
        status = "STRATEGICALLY READY" if score > 80 else "DATA REMEDIATION ADVISED"
        return score, status

    def results365_check(self, strategy):
        """Lancia Results365: Delivery Health Audit."""
        prompt = f"Audit this strategy using the Lancia Results365 framework. Identify 3 execution risks: {strategy}"
        return self.model.generate_content(prompt).text

    def red_team_audit(self, strategy):
        """Red Team Stress-Test: Breaking the strategy."""
        prompt = f"Act as a Red Team Auditor. Find 3 failure points and 3 mitigations for: {strategy}"
        return self.model.generate_content(prompt).text

    def generate_strategy(self, data_summary, industry):
        prompt = f"Create a 3-pillar strategy for the {industry} industry based on this data: {data_summary}. Use the Pyramid Principle."
        return self.model.generate_content(prompt).text

# =========================================================
# THE UI
# =========================================================

st.set_page_config(page_title="Lancia StratOS AI", layout="wide")

with st.sidebar:
    st.image("https://lancia-consult.com/wp-content/uploads/2021/05/Lancia-Consult-Logo-Standard-RGB.png", width=200)
    api_key = st.text_input("Gemini API Key", type="password")
    industry = st.selectbox("Industry Focus", ["Retail", "Manufacturing", "Logistics", "Energy"])
    data_file = st.file_uploader("Upload Client Telemetry (CSV)", type=['csv'])

if api_key:
    engine = LanciaEngines(api_key)
    st.title("Lancia StratOS AI")
    st.caption("Strategic Intelligence & Performance Orchestration")

    if data_file:
        # Load and clean
        df = pd.read_csv(data_file)
        df.columns = df.columns.astype(str).str.replace('_USD', '').str.replace(' ', '_')
        
        # 1. AI Realise Audit (Always Visible)
        st.subheader("📊 Lancia AI Realise Audit")
        score, status = engine.ai_realise_audit(df)
        c1, c2 = st.columns(2)
        c1.metric("Data Maturity", f"{score}%")
        c2.info(f"Audit Status: {status}")

        if st.button("RUN FULL ORCHESTRATION"):
            with st.spinner("Engaging Strategic Engines..."):
                # Run Logic
                data_summary = df.describe().to_string()
                strategy = engine.generate_strategy(data_summary, industry)
                health = engine.results365_check(strategy)
                red_team = engine.red_team_audit(strategy)

                # Display Results in Tabs for Professionalism
                tab1, tab2, tab3 = st.tabs(["Strategy Synthesis", "Results365 Health", "🛡️ Red Team Audit"])
                
                with tab1:
                    st.markdown(strategy)
                    # Simple Plot
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    if not numeric_cols.empty:
                        st.line_chart(df[numeric_cols[0]])
                
                with tab2:
                    st.info(health)
                
                with tab3:
                    st.error("RED TEAM CRITICAL FINDINGS")
                    st.markdown(red_team)
else:
    st.warning("Please enter your API Key to initialize.")
