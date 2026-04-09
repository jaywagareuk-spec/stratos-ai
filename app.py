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
# PART 1: THE ENGINES (Strategic Logic)
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
                plt.savefig(path, bbox_inches='tight') # Fixed the Syntax Here
                plt.close()
                charts.append(path)
        return stats, charts

    def generate_sensitivity(self, target_gain):
        x = np.linspace(0, 20, 20)
        y = 15 + (x * 0.82) 
        plt.figure(figsize=(8, 4))
        plt.plot(x, y, color='#074050', linewidth=3)
        plt.title("Lancia Strategic Sensitivity: Efficiency vs. Projected Margin")
        path = "sensitivity_plot.png"
        plt.savefig(path, bbox_inches='tight')
        plt.close()
        return path

class StratOS_Orchestrator:
    def __init__(self, kb, api_key):
        genai.configure(api_key=api_key)
        self.kb = kb
        self.model_stack = ['gemini-1.5-flash', 'gemini-1.5-pro']

    def run_debate(self, problem, stats, industry):
        agents = {"Growth": "Visionary scale.", "Risk": "Margin protection.", "Ops": "Execution."}
        transcript = ""
        context = self.kb.query(problem)
        for name, persona in agents.items():
            prompt = f"Role: {name}. {persona}\nIndustry: {industry}\nData: {stats}\nContext: {context}\nTask: 2-sentence solution for: {problem}"
            response = self.call_gemini(prompt)
            transcript += f"### {name}\n{response}\n\n"
        synthesis = f"Synthesize into a 3-pillar strategy for {industry} using the Pyramid Principle:\n{transcript}"
        return transcript, self.call_gemini(synthesis)

    def generate_lancia_roadmap(self, strategy_text):
        return self.call_gemini(f"Create a 90-day roadmap for: {strategy_text}")

    def run_red_team_audit(self, strategy):
        return self.call_gemini(f"Red Team Auditor: Find 3 structural failure points and mitigations for: {strategy}")

    def call_gemini(self, prompt):
        for model_name in self.model_stack:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                if response and response.text: return response.text
            except: continue
        return "CRITICAL ERROR: Strategy Engine unavailable."

class ReportEngine:
    def run_results365_check(self, strategy_output, orch):
        return orch.call_gemini(f"Results365 Audit: Rate delivery confidence (0-100%) and 3 risks for: {strategy_output}")

    def create_deck(self, summary, charts, roadmap=""):
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.shapes.title.text = "Lancia Executive Strategy Mandate"
        slide.
