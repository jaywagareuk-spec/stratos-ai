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

    # --- NEW FEATURE: SENSITIVITY CURVE (The Math) ---
    def generate_sensitivity(self, target_gain):
        """Calculates and plots a trade-off curve for margin improvement"""
        x = np.linspace(0, target_gain * 1.5, 20)
        # Strategic Formula: Efficiency to Margin Mapping
        y = 15 + (x * 0.82) 
        
        plt.figure(figsize=(8, 4))
        plt.plot(x, y, color='#074050', linewidth=3, label="Profit Trajectory")
        plt.axvline(target_gain, color='#d9534f', linestyle='--', label=f"Target: {target_goal}%")
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

    # --- NEW FEATURE: MULTI-AGENT DEBATE (The Consensus Engine) ---
    def run_debate(self, problem, stats, industry):
        """Forces 3 personas to argue for a MECE strategy before synthesis"""
        agents = {
            "The Visionary (Growth)": "Prioritize market capture and high-velocity expansion.",
            "The Conservator (Risk)": "Prioritize cash flow preservation and risk mitigation.",
            "The Operationalist (Execution)": "Prioritize scalability and process optimization."
        }
        
        transcript = ""
        context = self.kb.query(problem)
        
        for name, persona in agents.items():
            prompt = (f"ROLE: {name}. {persona}\n"
                      f"INDUSTRY: {industry}\n"
                      f"CLIENT DATA: {stats}\n"
                      f"CONTEXT: {context}\n"
                      f"TASK: Propose a 2-sentence solution for: {problem}")
            response = self.call_gemini(prompt)
            transcript += f"**{name}**: {response}\n\n"
        
        # Synthesis Pass
        synthesis_prompt = (f"Synthesize this expert debate into a unified 3-pillar strategy for {industry}:\n\n"
                            f"{transcript}\n\n"
                            "Deliverable: Pyramid Principle format (Governing Thought + 3 Pillars).")
        
        final_mandate = self.call_gemini(synthesis_prompt)
        return transcript, final_mandate

    def run_loop(self, problem, stats, industry="Retail"):
        """Main entry point for basic orchestration"""
        benchmarks = self.get_benchmarks(industry)
        context = self.kb.query(problem)
        
        prompt = (
            f"SYSTEM: Act as a McKinsey Senior Partner.\n"
            f"INDUSTRY BENCHMARKS: {benchmarks}\n"
            f"MARKET CONTEXT: {context}\n"
            f"QUANTITATIVE DATA: {stats}\n"
            f"CHALLENGE: {problem}\n\n"
            "Provide a Governing Thought and 3 MECE strategic pillars."
        )
        return self.call_gemini(prompt)

    def run_red_team_audit(self, strategy):
        audit_prompt = (
            f"ACT AS: A cynical Private Equity Auditor.\n"
            f"TASK: Find 3 failure points in this strategy: {strategy}\n"
            "DELIVERABLE: Failure points + mitigation advice."
        )
        return self.call_gemini(audit_prompt)

    def get_benchmarks(self, industry):
        data = {
            "Retail": "Avg Margin: 25%, Ad-to-Revenue Ratio: 8%, Shipping Cap: 12%",
            "SaaS": "Avg Margin: 70%, LTV/CAC Ratio: 3x, Churn Cap: 5%",
            "Manufacturing": "Avg Margin: 15%, Inventory Turnover: 6x, Logistics Cap: 20%"
        }
        return data.get(industry, "Standard Mid-Market KPIs")

    def call_gemini(self, prompt):
        for model_name in self.model_stack:
            try:
                model = genai.GenerativeModel(model_name)
                time.sleep(1) 
                response = model.generate_content(prompt)
                if response and response.text:
                    return response.text
            except Exception as e:
                continue
        return "CRITICAL ERROR: Strategy Engine unavailable."

class ReportEngine:
    def create_deck(self, summary, charts):
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.shapes.title.text = "StratOS Executive Mandate"
        
        body_shape = slide.shapes.placeholders[1]
        body_shape.text = summary[:1500] 
        
        for img in charts:
            if os.path.exists(img):
                slide = prs.slides.add_slide(prs.slide_layouts[6])
                slide.shapes.add_picture(img, Inches(0.5), Inches(1), width=Inches(9))
        
        path = "StratOS_Strategy_Deck.pptx"
        prs.save(path)
        return path
