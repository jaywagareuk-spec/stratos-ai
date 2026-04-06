import os
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
            
            df.columns = df.columns.astype(str).str.strip()
            df = df.dropna(how='all', axis=0).dropna(how='all', axis=1)
            
            for col in df.columns:
                if df[col].dtype == 'object':
                    try:
                        df[col] = df[col].replace(r'[\$,%]', '', regex=True).astype(float)
                    except:
                        pass 
            return df
        except Exception as e:
            return None

    # --- NEW FEATURE: AI REALISE (Data Readiness Audit) ---
    def run_ai_realise_audit(self, df):
        """Lancia Methodology: Audits data maturity for AI implementation"""
        if df is None or df.empty:
            return {"score": 0, "status": "NO DATA", "color": "red"}
        
        null_pct = df.isnull().sum().mean() / len(df) if len(df) > 0 else 1
        completeness_score = (1 - null_pct) * 100
        
        # Check for numeric density (Lancia likes quantitative depth)
        numeric_cols = len(df.select_dtypes(include=[np.number]).columns)
        total_cols = len(df.columns)
        density_score = (numeric_cols / total_cols) * 100 if total_cols > 0 else 0
        
        maturity_score = (completeness_score + density_score) / 2
        
        if maturity_score > 80:
            return {"score": round(maturity_score, 1), "status": "AI READY", "color": "green"}
        elif maturity_score > 50:
            return {"score": round(maturity_score, 1), "status": "NEEDS STEWARDSHIP", "color": "orange"}
        else:
            return {"score": round(maturity_score, 1), "status": "UNSTRUCTURED / UNREADY", "color": "red"}

    def analyze_and_plot(self, df):
        numeric = df.select_dtypes(include=[np.number])
        if numeric.empty:
            return {"Status": "No numeric trends found."}, []
        
        stats = {}
        charts = []
        sns.set_theme(style="whitegrid")
        
        for col in numeric.columns[:3]:
            vals = numeric[col].dropna()
            if len(vals) > 1:
                trend = np.polyfit(range(len(vals)), vals, 1)[0]
                stats[col] = {"mean": round(vals.mean(), 2), "trend": round(trend, 4)}
                
                plt.figure(figsize=(6, 4))
                sns.lineplot(data=vals, color='#074050', linewidth=2, marker='o')
                plt.title(f"Client Data Analysis: {col}")
                path = f"{col.replace(' ', '_')}_viz.png"
                plt.savefig(path, bbox_inches='tight')
                plt.close()
                charts.append(path)
        return stats, charts

    def generate_sensitivity(self, target_gain):
        x = np.linspace(0, target_gain * 1.5, 20)
        y = 15 + (x * 0.82) 
        
        plt.figure(figsize=(8, 4))
        plt.plot(x, y, color='#074050', linewidth=3, label="Profit Trajectory")
        plt.axvline(target_gain, color='#d9534f', linestyle='--', label=f"Target: {target_gain}%")
        plt.fill_between(x, y-2, y+2, alpha=0.1, color='#074050')
        plt.title("Strategic Sensitivity: Efficiency vs. Projected Margin", fontsize=10)
        plt.xlabel("OpEx Efficiency Gain (%)")
        plt.ylabel("Projected Net Margin (%)")
        plt.legend()
        plt.grid(alpha=0.3)
        
        path = "sensitivity_plot.png"
        plt.savefig(path, bbox_inches='tight')
        plt.close()
        return path

class StratOS_Orchestrator:
    def __init__(self, kb, api_key):
        genai.configure(api_key=api_key)
        self.kb = kb
        self.model_stack = ['gemini-2.0-flash', 'models/gemini-2.0-flash', 'gemini-1.5-flash']

    # --- UPDATED: LANCIA PERSONA DATABASE ---
    def get_persona_database(self):
        return {
            "Logistics": "Supply Chain Architect. Focus: Lead times, fuel volatility, and port congestion.",
            "Utilities": "Regulatory Strategist. Focus: Grid stability, ESG compliance, and CAPEX.",
            "Retail": "Consumer Behavioral Analyst. Focus: Inventory churn and
