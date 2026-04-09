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
from pptx import Presentation

# =========================================================
# THE ENGINES (Core Lancia Logic)
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
            return f"Error: {str(e)}"

    def query(self, text):
        try:
            results = self.collection.query(query_texts=[text], n_results=3)
            return " ".join(results['documents'][0]) if results['documents'] else ""
        except:
            return ""

class DataEngine:
    def clean_and_load(self, file_object):
        """Original Data Ingestion Logic."""
        try:
            df = pd.read_csv(file_object) if file_object.name.endswith('.csv') else pd.read_excel(file_object)
            df.columns = df.columns.astype(str).str.strip().str.replace(' ', '_')
            return df.dropna(how='all', axis=0).dropna(how='all', axis=1)
        except:
            return None

    def run_ai_realise_audit(self, df):
        """Standard Lancia AI Realise Framework."""
        if df is None or df.empty: return {"score": 0, "status": "No Data"}
        score = round(((1 - df.isnull().mean().mean()) * 50) + (min(len(df.columns)/10, 1) * 50), 1)
        status = "MATURE" if score > 80 else "DEVELOPING" if score > 50 else "CRITICAL"
        return {"score": score, "status": status}

    def analyze_trends(self, df):
        numeric = df.select_dtypes(include=[np.number])
        stats, charts = {}, []
        for col in numeric.columns[:2]:
            plt.figure(figsize=(6, 3))
            sns.lineplot(data=df[col], color='#074050')
            plt.title(f"Trend Analysis: {col}")
            path = f"{col}_chart.png"
            plt.savefig(path, bbox_inches='tight')
            plt.close()
            charts.append(path)
            stats[col] = df[col].mean()
        return stats, charts

class StratOS_Orchestrator:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate_strategy(self, prompt, context=""):
        response = self.model.generate_content(f"Context: {context}\n\nTask: {prompt}")
        return response.text if response else "Engine Error."

class ReportEngine:
    def run_results365_check(self, strategy, orch):
        """Standard Results365 Performance Diagnostic."""
        return orch.generate_strategy(f"Audit this strategy using the Results365 framework: {strategy}")

# =========================================================
# THE UI (Main App)
# =========================================================

st.set_page_config(page_title="Lancia StratOS AI", layout="wide")

if "kb" not in st.session_state: st.session_state.kb = KnowledgeEngine()
if "de" not in st.session_state: st.session_state.de = DataEngine()

with st.sidebar:
    st.image("https://lancia-consult.com/wp-content/uploads/2021/05/Lancia-Consult-Logo-Standard-RGB.png", width=180)
    api_key = st.text_input("Gemini API Key", type="password")
    uploaded_file = st.file_uploader("Upload Client CSV", type=['csv'])

if api_key:
    orch = StratOS_Orchestrator(api_key)
    re = ReportEngine()
    st.title("Lancia StratOS AI")

    if uploaded_file:
        df = st.session_state.de.clean_and_load(uploaded_file)
        if df is not None:
            audit = st.session_state.de.run_ai_realise_audit(df)
            st.metric("AI Realise Maturity", f"{audit['score']}%", audit['status'])
            
            if st.button("Generate Lancia Strategy"):
                stats, charts = st.session_state.de.analyze_trends(df)
                strat = orch.generate_strategy(f"Analyze these stats: {stats}")
                
                st.subheader("Results365 Performance Health")
                st.info(re.run_results365_check(strat, orch))
                
                st.subheader("Core Strategy")
                st.markdown(strat)
                for c in charts: st.image(c)
else:
    st.warning("Please provide an API Key.")
