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
# THE ENGINES (Strategic Logic & Data Processing)
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
            return f"Error indexing PDF: {str(e)}"

    def query(self, text):
        try:
            results = self.collection.query(query_texts=[text], n_results=3)
            return " ".join(results['documents'][0]) if results['documents'] else ""
        except:
            return ""

class DataEngine:
    def clean_and_load(self, file_object):
        """Fixes the 'USD' mismatch by renaming columns automatically."""
        try:
            if file_object.name.endswith('.csv'):
                df = pd.read_csv(file_object)
            else:
                df = pd.read_excel(file_object)
            
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
        except:
            return None

    def run_ai_realise_audit(self, df):
        if df is None or df.empty:
            return {"score": 0, "status": "NO DATA", "color": "red"}
        score = round(((1 - df.isnull().mean().mean()) * 100 + (len(df.select_dtypes(include=[np.number]).columns) / len(df.columns)) * 100) / 2, 1)
        status = "STRATEGICALLY READY" if score > 85 else "DATA REMEDIATION ADVISED" if score > 60 else "CRITICAL DATA GAPS"
        return {"score": score, "status": status}

    def analyze_and_plot(self, df):
        numeric = df.select_dtypes(include=[np.number])
        if numeric.empty: return {"Status": "No numeric trends found."}, []
        stats, charts = {}, []
        sns.set_theme(style="whitegrid")
        for col in numeric.columns[:3]:
            vals = numeric[col].dropna()
            if len(vals) > 1:
                trend = np.polyfit(range(len(vals)), vals, 1)[0]
                stats[col] = {"mean": round(vals.mean(), 2), "trend": round(trend, 4)}
                plt.figure(figsize=(6, 4))
                sns.lineplot(data=vals, color='#074050', linewidth=2, marker='o')
                plt.title(f"Client Data Analysis: {col}")
                path = f"{col}_viz.png"
                plt.savefig(path, bbox_inches='tight')
                plt.close()
                charts.append(path)
        return stats, charts

class StratOS_Orchestrator:
    def __init__(self, kb, api_key):
        genai.configure(api_key=api_key)
        self.kb = kb
        self.model_stack = ['gemini-1.5-flash', 'gemini-1.5-pro']

    def run_debate(self, problem, stats, industry):
        agents = {"Visionary": "Scale focus.", "Risk": "Margin focus.", "Ops": "Lean focus."}
        transcript = ""
        context = self.kb.query(problem)
        for name, persona in agents.items():
            prompt = f"Role: {name}. {persona}\nIndustry: {industry}\nData: {stats}\nTask: 2-sentence solution for {problem}"
            response = self.call_gemini(prompt)
            transcript += f"### {name}\n{response}\n\n"
        synth = self.call_gemini(f"Synthesize this into a strategy:\n{transcript}")
        return transcript, synth

    def call_gemini(self, prompt):
        for model_name in self.model_stack:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                if response.text: return response.text
            except: continue
        return "ERROR: Strategy Engine Offline."

class ReportEngine:
    def create_deck(self, summary, charts):
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.shapes.title.text = "Lancia Executive Mandate"
        slide.shapes.placeholders[1].text = summary[:1500]
        path = "Lancia_Report.pptx"
        prs.save(path)
        return path

# =========================================================
# THE UI (Streamlit Frontend)
# =========================================================

st.set_page_config(page_title="Lancia StratOS", layout="wide")

if "kb" not in st.session_state: st.session_state.kb = KnowledgeEngine()
if "de" not in st.session_state: st.session_state.de = DataEngine()
if "re" not in st.session_state: st.session_state.re = ReportEngine()

with st.sidebar:
    st.image("https://lancia-consult.com/wp-content/uploads/2021/05/Lancia-Consult-Logo-Standard-RGB.png", width=200)
    api_key = st.text_input("Gemini API Key", type="password")
    industry = st.selectbox("Industry", ["Retail", "Manufacturing", "Logistics"])
    data_file = st.file_uploader("Upload CSV", type=['csv'])

if api_key:
    orch = StratOS_Orchestrator(st.session_state.kb, api_key)
    st.title("Lancia StratOS AI")
    if data_file:
        df = st.session_state.de.clean_and_load(data_file)
        if df is not None:
            audit = st.session_state.de.run_ai_realise_audit(df)
            st.metric("AI Realise Score", f"{audit['score']}%", audit['status'])
            if st.button("RUN STRATEGY"):
                stats, charts = st.session_state.de.analyze_and_plot(df)
                _, synthesis = orch.run_debate("Analyze margins", stats, industry)
                st.subheader("Strategy Synthesis")
                st.markdown(synthesis)
                for c in charts: st.image(c)
                path = st.session_state.re.create_deck(synthesis, charts)
                with open(path, "rb") as f:
                    st.download_button("Download Report", f, file_name="Lancia_Strategy.pptx")
else:
    st.warning("Please enter your API Key.")
