import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import google.generativeai as genai
import chromadb
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pptx import Presentation
from pptx.util import Inches

class KnowledgeEngine:
    def __init__(self):
        self.chroma_client = chromadb.Client()
        try:
            self.collection = self.chroma_client.create_collection(name="strat_vault")
        except:
            self.collection = self.chroma_client.get_collection(name="strat_vault")
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=70)

    def ingest_pdf(self, file_object):
        # Temporary save for PyPDFLoader
        with open("temp.pdf", "wb") as f:
            f.write(file_object.getbuffer())
        loader = PyPDFLoader("temp.pdf")
        pages = loader.load()
        chunks = self.text_splitter.split_documents(pages)
        for i, chunk in enumerate(chunks):
            self.collection.add(documents=[chunk.page_content], ids=[f"id_{i}"])
        os.remove("temp.pdf")
        return len(chunks)

    def query(self, text):
        results = self.collection.query(query_texts=[text], n_results=2)
        return " ".join(results['documents'][0]) if results['documents'] else ""

class DataEngine:
    def analyze_and_plot(self, df):
        numeric = df.select_dtypes(include=[np.number])
        stats = {}
        charts = []
        sns.set_theme(style="whitegrid")
        for col in numeric.columns[:2]:
            vals = numeric[col].dropna()
            trend = np.polyfit(range(len(vals)), vals, 1)[0]
            stats[col] = {"mean": round(vals.mean(), 2), "trend": round(trend, 4)}
            plt.figure(figsize=(6, 4))
            sns.lineplot(data=vals, color='#074050', linewidth=2)
            plt.title(f"Trend: {col}")
            path = f"{col}_viz.png"
            plt.savefig(path, dpi=150)
            plt.close()
            charts.append(path)
        return stats, charts

class StratOS_Orchestrator:
    def __init__(self, kb, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.kb = kb

    def run_loop(self, problem, stats):
        context = self.kb.query(problem)
        p1 = f"System: Junior Analyst. Context: {context}. Stats: {stats}. Problem: {problem}. 3 Hypotheses?"
        analysis = self.model.generate_content(p1).text
        p2 = f"System: Senior Partner. Critique this: {analysis}"
        critique = self.model.generate_content(p2).text
        p3 = f"System: Manager. Pyramid Principle Strategy for: {problem}. Consider: {critique}"
        return self.model.generate_content(p3).text

class ReportEngine:
    def create_deck(self, summary, charts):
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.shapes.title.text = "Executive Strategy Mandate"
        slide.shapes.placeholders[1].text = summary
        for img in charts:
            slide = prs.slides.add_slide(prs.slide_layouts[6])
            slide.shapes.add_picture(img, Inches(1), Inches(1), width=Inches(8))
        path = "StratOS_Strategy_Deck.pptx"
        prs.save(path)
        return path