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
        # Use PersistentClient to avoid memory resets on Streamlit
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
            if file_object.name.endswith('.csv'):
                df = pd.read_csv(file_object)
            else:
                df = pd.read_excel(file_object)
            
            df.columns = df.columns.astype(str).str.strip()
            df = df.dropna(how='all', axis=0).dropna(how='all', axis=1)
            
            for col in df.columns:
                if df[col].dtype == 'object':
                    try:
                        # Clean currency/percentage symbols
                        df[col] = df[col].replace(r'[\$,%]', '', regex=True).astype(float)
                    except:
                        pass 
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

class StratOS_Orchestrator:
    def __init__(self, kb, api_key):
        genai.configure(api_key=api_key)
        self.kb = kb
        # We are moving the 2.5 Flash to the top because your account is cleared for it!
        self.model_stack = [
            'gemini-2.5-flash', 
            'models/gemini-2.5-flash',
            'gemini-1.5-flash', 
            'gemini-1.5-pro'
        ]

    def run_loop(self, problem, stats):
        context = self.kb.query(problem)
        
        prompt = (
            f"SYSTEM: Act as a McKinsey Senior Partner. Use the Pyramid Principle.\n"
            f"MARKET CONTEXT: {context}\n"
            f"QUANTITATIVE DATA: {stats}\n"
            f"CLIENT CHALLENGE: {problem}\n\n"
            "DELIVERABLE: Provide a Governing Thought followed by 3 MECE strategic pillars. "
            "Ensure the data trends are cited in your reasoning."
        )

        for model_name in self.model_stack:
            try:
                model = genai.GenerativeModel(model_name)
                # We add a tiny delay (1 second) to prevent hitting that 5 RPM limit too fast
                import time
                time.sleep(1) 
                
                response = model.generate_content(prompt)
                if response and response.text:
                    return response.text
            except Exception as e:
                print(f"⚠️ Failover: {model_name} failed. Error: {str(e)}")
                continue 
        
        return "CRITICAL ERROR: Strategy Engine unavailable. Please check API Key permissions or Quotas."

    def run_loop(self, problem, stats):
        """The 'Self-Healing' Logic Loop with Version Failover"""
        context = self.kb.query(problem)
        
        prompt = (
            f"SYSTEM: Act as a McKinsey Senior Partner. Use the Pyramid Principle.\n"
            f"MARKET CONTEXT: {context}\n"
            f"QUANTITATIVE DATA: {stats}\n"
            f"CLIENT CHALLENGE: {problem}\n\n"
            "DELIVERABLE: Provide a Governing Thought followed by 3 MECE strategic pillars. "
            "Ensure the data trends are cited in your reasoning."
        )

        for model_name in self.model_stack:
            try:
                # We try both naming conventions: standard and prefixed
                for name_variant in [model_name, f"models/{model_name}"]:
                    try:
                        model = genai.GenerativeModel(model_name=name_variant)
                        response = model.generate_content(prompt)
                        if response and response.text:
                            return response.text
                    except:
                        continue
            except Exception as e:
                print(f"⚠️ Failover: {model_name} failed. Error: {str(e)}")
                continue 
        
        return "CRITICAL ERROR: Strategy Engine unavailable. Please verify API Key or regional availability."

class ReportEngine:
    def create_deck(self, summary, charts):
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.shapes.title.text = "StratOS Executive Mandate"
        
        # Prevent overflow by truncating summary if necessary
        body_shape = slide.shapes.placeholders[1]
        body_shape.text = summary[:1500] 
        
        for img in charts:
            if os.path.exists(img):
                slide = prs.slides.add_slide(prs.slide_layouts[6])
                slide.shapes.add_picture(img, Inches(0.5), Inches(1), width=Inches(9))
        
        path = "StratOS_Strategy_Deck.pptx"
        prs.save(path)
        return path
