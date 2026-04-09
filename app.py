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

# ==========================================
# STEP 1: DEFINE THE ENGINES (The "Brain")
# These MUST come before the UI code.
# ==========================================

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
            return f"Error indexing PDF: {str(e)}"

    def query(self, text):
        try:
            results = self.collection.query(query_texts=[text], n_results=3)
            return " ".join(results['documents'][0]) if results['documents'] else ""
        except:
            return ""

class DataEngine:
    def clean_and_load(self, file_object):
        try:
            if file_object.name.endswith('.csv'):
                df = pd.read_csv(file_object)
            else:
                df = pd.read_excel(file_object)
            # FIX: Renames USD columns to standard names
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
                    except:
                        pass 
            return df
        except: return None

    def run_ai_realise_audit(self, df):
        if df is None or df.empty: return {"score": 0, "status": "NO DATA", "color": "red"}
        score = round(((1 - df.isnull().mean().mean()) * 100 + (len(df.select_dtypes(include=[np.number]).columns) / len(df.columns)) * 100) / 2, 1)
        status = "STRATEGICALLY READY" if score > 85 else "DATA REMEDIATION ADVISED" if score > 60 else "CRITICAL DATA GAPS"
        color = "green" if score > 85 else "orange" if score > 60 else "red"
        return {"score": score, "status": status, "color": color}

    def analyze_and_plot(self, df):
        numeric = df.select_dtypes(include=[np.number])
        if numeric.empty: return {"Status": "No numeric trends found."}, []
        stats, charts = {}, []
        for col in numeric.columns[:3]:
            vals = numeric[col].dropna()
            if len(vals) > 1:
                stats[col] = {"mean": round(vals.mean(), 2), "trend": round(np.polyfit(range(len(vals)), vals, 1)[0], 4)}
                plt.figure(figsize=(6, 4))
                sns.lineplot(data=vals, color='#074050')
                path = f"{col}_viz.png"
                plt.savefig(path)
                plt.close()
                charts.append(path)
        return stats, charts

class StratOS_Orchestrator:
    def __init__(self, kb, api_key):
        genai.configure(api_key=api_key)
        self.kb = kb
        self.model_stack = ['gemini-1.5-flash', 'gemini-1.5-pro']

    def call_gemini(self, prompt):
        for model_name in self.model_stack:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                if response.text: return response.text
            except: continue
        return "CRITICAL ERROR: Strategy Engine unavailable."

# ==========================================
# STEP 2: STREAMLIT UI (The "Body")
# This runs ONLY after the Engines are ready.
# ==========================================

st.set_page_config(page_title="StratOS AI", layout="wide")

# Initialize Session State
if "kb" not in st.session_state:
    st.session_state.kb = KnowledgeEngine()
if "de" not in st.session_state:
    st.session_state.de = DataEngine()

st.title("Lancia StratOS AI")
st.write("Expert Strategy Orchestration")

# ... (The rest of your app.py UI code goes here) ...
