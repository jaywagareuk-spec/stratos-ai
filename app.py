import os
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import google.generativeai as genai
import chromadb
import time
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pptx import Presentation
from pptx.util import Inches

# =========================================================
# THE ENGINES (Lancia Strategic Core)
# =========================================================

class KnowledgeEngine:
    def __init__(self):
        self.chroma_client = chromadb.Client()
        try:
            self.collection = self.chroma_client.create_collection(name="strat_vault")
        except:
            self.collection = self.chroma_client.get_collection(name="strat_vault")
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

    def ingest_pdf(self, file_object):
        try:
            with open("temp.pdf", "wb") as f:
                f.write(file_object.getbuffer())
            loader = PyPDFLoader("temp.pdf")
            pages = loader.load()
            chunks = self.text_splitter.split_documents(pages)
            for i, chunk in enumerate(chunks):
                self.collection.add(documents=[chunk.page_content], ids=[f"id_{os.urandom(4).hex()}"])
            os.remove("temp.pdf")
            return len(chunks)
        except Exception as e:
            return f"Vault Error: {str(e)}"

    def query(self, text):
        try:
            results = self.collection.query(query_texts=[text], n_results=3)
            return " ".join(results['documents'][0]) if results['documents'] else ""
        except:
            return ""

class DataEngine:
    def clean_and_load(self, file_object):
        """Fixes 'USD' data mismatch automatically."""
        try:
            df = pd.read_csv(file_object) if file_object.name.endswith('.csv') else pd.read_excel(file_object)
            df.columns = (df.columns.astype(str)
                          .str.replace('_USD', '', case=False)
                          .str.replace('_Units', '', case=False)
                          .str.replace(' ', '_')
                          .str.strip())
            df = df.dropna(how='all', axis=0).dropna(how='all', axis=1)
            for col in df.columns:
                if df[col].dtype == 'object':
                    try:
                        df[col] = df[col].replace(r'[\$,%]', '', regex=True).astype(float)
                    except: pass 
            return df
        except: return None

    def run_ai_realise_audit(self, df):
        """Lancia AI Realise: Maturity Diagnostic."""
        if df is None or df.empty: return {"score": 0, "status": "NO DATA"}
        score = round(((1 - df.isnull().mean().mean()) * 100 + (len(df.select_dtypes(include=[np.number]).columns) / len(df.columns)) * 100) / 2, 1)
        status = "STRATEGICALLY READY" if score > 85 else "REMEDIATION ADVISED" if score > 60 else "CRITICAL GAPS"
        return {"score": score, "status": status}

    def analyze_and_plot(self, df):
        numeric = df.select_dtypes(include=[np.number])
        if numeric.empty: return {}, []
        stats, charts = {}, []
        sns.set_theme(style="whitegrid")
        for col in numeric.columns[:3]:
            vals = numeric[col].dropna()
            if len(vals) > 1:
                stats[col] = {"mean": round(vals.mean(), 2), "trend": round(np.polyfit(range(len(vals)), vals, 1)[0], 4)}
                plt.figure(figsize=(6, 4))
                sns.lineplot(data=vals, color='#074050', linewidth=2, marker='o')
                plt.title(f"Lancia Analysis: {col}")
                path = f"{col}_viz.png"
                plt.savefig(path, bbox_inches='tight')
                plt.close()
                charts.append(path)
        return stats, charts

class StratOS_Orchestrator:
    def __init__(self, kb, api_key):
        genai.configure(api_key=api_key)
        self.kb = kb

    def run_strat_engine(self, problem, stats, industry):
        context = self.kb.query(problem)
        prompt = f"Act as Lancia StratOS. Solve {problem} for {industry} industry. Data stats: {stats}. Context: {context}. Use Pyramid Principle."
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text if response.text else "Engine Error."
        except: return "Engine Offline."

class ReportEngine:
    def run_results365_check(self, strategy_output, orch):
        """Lancia Results365: Performance Health Diagnostic."""
        prompt = f"Audit this strategy using the Lancia Results365 framework. Rate confidence 0-100% and identify risks: {strategy_output}"
        return orch.run_strat_engine(prompt, "N/A", "Consulting")

# =========================================================
# THE UI (Lancia Experience)
# =========================================================

st.set_page_config(page_title="Lancia StratOS AI", layout="wide")

if "kb" not in st.session_state: st.session_state.kb = KnowledgeEngine()
if "de" not in st.session_state: st.session_state.de = DataEngine()
if "re" not in st.session_state: st.session_state.re = ReportEngine()

with st.sidebar:
    st.image("https://lancia-consult.com/wp-content/uploads/2021/05/Lancia-Consult-Logo-Standard-RGB.png", width=200)
    api_key = st.text_input("Gemini API Key", type="password")
    industry = st.selectbox("Industry Focus", ["Retail", "Manufacturing", "Logistics", "Utilities"])
    data_file = st.file_uploader("Upload Client Telemetry (CSV)", type=['csv'])

if api_key:
    orch = StratOS_Orchestrator(st.session_state.kb, api_key)
    st.title("Lancia StratOS AI")
    
    if data_file:
        df = st.session_state.de.clean_and_load(data_file)
        if df is not None:
            # 1. AI Realise Audit
            st.subheader("📊 Lancia AI Realise Audit")
            audit = st.session_state.de.run_ai_realise_audit(df)
            c1, c2 = st.columns(2)
            c1.metric("Data Maturity Score", f"{audit['score']}%")
            c2.info(f"Maturity Status: {audit['status']}")
            
            if st.button("EXECUTE STRATOS ENGINE"):
                with st.spinner("Orchestrating Strategic Logic..."):
                    stats, charts = st.session_state.de.analyze_and_plot(df)
                    synthesis = orch.run_strat_engine("Diagnose profit/revenue trends", stats, industry)
                    health = st.session_state.re.run_results365_check(synthesis, orch)
                    
                    # 2. Results365 Display
                    st.divider()
                    st.subheader("✅ Results365 Delivery Health")
                    st.success(health)
                    
                    # 3. Strategy Synthesis
                    st.divider()
                    st.subheader("Strategic Synthesis")
                    st.markdown(synthesis)
                    for c in charts: st.image(c)
    else:
        st.info("👈 Please upload a CSV file in the sidebar to begin.")
else:
    st.warning("Please enter your API Key to initialize the StratOS Engines.")
