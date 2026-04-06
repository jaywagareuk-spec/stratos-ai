import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import google.generativeai as genai
import chromadb
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
        """Automatically detects file type and cleans data for the AI."""
        try:
            # Handle Excel or CSV
            if file_object.name.endswith('.csv'):
                df = pd.read_csv(file_object)
            else:
                df = pd.read_excel(file_object)
            
            # CLEANING: Strip spaces from headers, remove empty rows/columns
            df.columns = df.columns.astype(str).str.strip()
            df = df.dropna(how='all', axis=0).dropna(how='all', axis=1)
            
            # FORCE NUMERIC: Convert strings like '$50,000' to 50000 automatically
            for col in df.columns:
                if df[col].dtype == 'object':
                    try:
                        df[col] = df[col].replace(r'[\$,%]', '', regex=True).astype(float)
                    except:
                        pass # Keep as text if it's truly a category (like 'Month')
            return df
        except Exception as e:
            return None

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
                # Calculate Trend (Regression)
                trend = np.polyfit(range(len(vals)), vals, 1)[0]
                stats[col] = {"mean": round(vals.mean(), 2), "trend": round(trend, 4)}
                
                # Visuals
                plt.figure(figsize=(6, 4))
                sns.lineplot(data=vals, color='#074050', linewidth=2, marker='o')
                plt.title(f"Client Data Analysis: {col}")
                path = f"{col.replace(' ', '_')}_viz.png"
                plt.savefig(path, bbox_inches='tight')
                plt.close()
                charts.append(path)
        return stats, charts

class StratOS_Orchestrator:
    def __init__(self, kb, api_key):
        genai.configure(api_key=api_key)
        # Use 'models/gemini-1.5-flash' to be ultra-explicit
        self.model = genai.GenerativeModel('models/gemini-1.5-flash') 
        self.kb = kb

    def run_loop(self, problem, stats):
        context = self.kb.query(problem)
        prompt = (
            f"Context from Market Reports: {context}\n"
            f"Client Data Trends: {stats}\n"
            f"Problem: {problem}\n\n"
            "Role: McKinsey Senior Partner. Provide a high-level strategy using the Pyramid Principle. "
            "Lead with a 'Governing Thought' followed by 3 MECE strategic pillars."
        )
        try:
            return self.model.generate_content(prompt).text
        except Exception as e:
            return f"AI Error: {str(e)}"

class ReportEngine:
    def create_deck(self, summary, charts):
        prs = Presentation()
        # Slide 1: Executive Summary
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.shapes.title.text = "StratOS Executive Mandate"
        slide.shapes.placeholders[1].text = summary[:1000] # Cap text for slide
        
        # Slide 2+: Data Visuals
        for img in charts:
            slide = prs.slides.add_slide(prs.slide_layouts[6])
            slide.shapes.add_picture(img, Inches(0.5), Inches(1), width=Inches(9))
        
        path = "StratOS_Strategy_Deck.pptx"
        prs.save(path)
        return path
