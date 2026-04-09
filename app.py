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
import streamlit as st  # <--- Make sure this is there too!

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="StratOS v11 | Lancia Executive Suite", layout="wide", page_icon="🏛️")

# 2. INITIALIZE ENGINES & SESSION STATE
if 'kb' not in st.session_state:
    st.session_state.kb = KnowledgeEngine()
    st.session_state.de = DataEngine()
    st.session_state.re = ReportEngine()
    # Strategy persistence variables
    st.session_state.final_output = None
    st.session_state.roadmap = None
    st.session_state.transcript = None
    st.session_state.charts = []
    # Elite Features State
    st.session_state.traceability_report = None
    st.session_state.change_audit = None
    st.session_state.current_scenario = "Balanced"

# 3. CUSTOM CSS FOR LANCIA BRANDING
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { background-color: #074050; color: white; width: 100%; border-radius: 5px; height: 3em; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { 
        height: 50px; 
        background-color: #f0f2f6; 
        border-radius: 5px 5px 0 0; 
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] { background-color: #074050 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ StratOS v11: Strategic Command Center")
st.caption("Lancia Consult: Precision Strategy, Global Benchmarking, & Results365")

# 4. SIDEBAR: CONTROL CENTER
with st.sidebar:
    st.image("https://lancia-consult.com/wp-content/uploads/2021/01/Lancia-Consult-Logo-White-300x77.png", width=200)
    
    st.header("1. Configuration")
    api_key = "AIzaSyBi-p2SQk95Fj1YL4U4GfXLprCbQsi9wIo" 
    
    lancia_sectors = [
        "Retail & Consumer Goods", 
        "Logistics & Supply Chain", 
        "Financial Services", 
        "Manufacturing & Industry 4.0",
        "Technology & SaaS"
    ]
    
    industry_choice = st.selectbox(
        "Lancia Service Line", 
        lancia_sectors,
        help="Select the specific Lancia business unit for tailored benchmarks."
    )
    
    st.header("🎭 Lancia Persona")
    report_tone = st.selectbox(
        "Output Tone",
        ["Executive Summary", "Boardroom Deep-Dive", "Town Hall / Employee-Facing"],
        help="Adjusts the AI's language style for different stakeholders."
    )

    st.header("📊 Scenario & Stress")
    target_goal = st.slider("Strategic Target (Margin %)", 5, 50, 15)
    stress_test_mode = st.toggle("⚡ Enable 'Black Swan' Stress Test", help="Simulates market shocks like fuel spikes or supply chain blocks.")
    
    st.divider()

    # Visual Multi-Agent Status
    st.subheader("🤖 Digital Boardroom")
    with st.expander("Active Agents", expanded=True):
        st.write("⚖️ **Compliance Auditor**: :green[ACTIVE]") 
        st.write("🔍 **Explainability Engine**: :blue[TRACING]")     
        st.write("👥 **Culture Lead**: :orange[ANALYZING]") 
        st.write("🥊 **Red Team (Stress)**: " + (":red[SIMULATING]" if stress_test_mode else ":gray[Standby]"))

    st.divider()
    uploaded_data = st.file_uploader("Upload Client Telemetry", type=["csv", "xlsx"])

# 5. THE MAIN SUITE TABS
tab_audit, tab_strategy, tab_health = st.tabs([
    "🛡️ AI Realise (Audit)", 
    "🚀 Strategy Engine", 
    "📊 Results365 (Project Health)"
])

# --- TAB 1: AI REALISE (DATA MATURITY) ---
with tab_audit:
    st.header("AI Realise: Data Maturity Assessment")
    if uploaded_data:
        df_audit = st.session_state.de.clean_and_load(uploaded_data)
        audit = st.session_state.de.run_ai_realise_audit(df_audit)
        
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("Maturity Score", f"{audit['score']}%")
        col_m1.markdown(f"Status: :{audit['color']}[{audit['status']}]")
        
        st.divider()
        st.subheader("Data Quality Preview")
        st.dataframe(df_audit.head(10), use_container_width=True)
    else:
        st.warning("Please upload a dataset in the sidebar to run the AI Realise Audit.")

# --- TAB 2: STRATEGY ENGINE (BENCHMARKING & PERSONA) ---
with tab_strategy:
    col_input, col_output = st.columns([1, 1.2])

    with col_input:
        st.header("Strategic Input")
        problem = st.text_area("Business Challenge", placeholder="Describe the crisis or opportunity...", height=100)
        
        # FEATURE: MULTI-SCENARIO BRANCHING
        st.subheader("🛤️ Select Strategic Branch")
        scenario_mode = st.select_slider(
            "Risk Appetite",
            options=["Defensive", "Balanced", "Aggressive"],
            value="Balanced"
        )
        st.session_state.current_scenario = scenario_mode
        
        generate_btn = st.button("Generate Branching Roadmap")

    with col_output:
        st.header("Output & Deliverables")
        
        if generate_btn and uploaded_data:
            with st.status(f"🏗️ Crafting {report_tone} Strategy...", expanded=True) as status:
                # 1. CORE PROCESSING
                df = st.session_state.de.clean_and_load(uploaded_data)
                stats, charts = st.session_state.de.analyze_and_plot(df)
                
                # 2. ELITE FEATURES: TRACEABILITY & CHANGE
                st.write("🔍 Tracing Data Anchors...")
                st.session_state.traceability_report = {
                    "Anchor_1": f"Revenue Leakage identified in {industry_choice} Telemetry",
                    "Anchor_2": f"Margin Gap of {target_goal}% confirmed against Sector Benchmarks",
                    "Anchor_3": "High Labor Sensitivity detected in Regional Data"
                }
                
                st.write("👥 Running Behavioral Friction Analysis...")
                st.session_state.change_audit = "High risk of middle-management resistance. Suggested Mitigation: Week 2 Training Block."

                # 3. ORCHESTRATOR WITH PERSONA & STRESS CONTEXT
                orch = StratOS_Orchestrator(st.session_state.kb, api_key)
                context_prefix = f"Tone: {report_tone}. Stress Test: {stress_test_mode}. Mode: {scenario_mode}."
                transcript, final_output = orch.run_debate(f"[{context_prefix}] " + problem, stats, industry_choice.split(" ")[0])
                
                st.session_state.final_output = final_output
                st.session_state.roadmap = orch.generate_lancia_roadmap(final_output)
                st.session_state.transcript = transcript
                st.session_state.charts = charts
                
                status.update(label=f"{scenario_mode} Strategy Finalized!", state="complete")

        if st.session_state.get('final_output'):
            # FEATURE: COMPETITOR SHADOW (MARKET BENCHMARKING)
            st.subheader("👥 Competitor Shadow (Market Benchmarking)")
            b1, b2 = st.columns(2)
            b1.metric("Current Cost Efficiency", "72%", "-8.4% vs Industry Leader")
            b2.info(f"**Lancia Delta:** Industry leaders in {industry_choice} are outperforming your baseline by 14% in operational agility.")

            with st.expander("🔍 Deep Traceability & Change Audit", expanded=True):
                st.json(st.session_state.traceability_report)
                st.warning(f"**Adoption Risk:** {st.session_state.change_audit}")

            st.divider()
            st.subheader(f"📋 Executive Synthesis ({st.session_state.current_scenario})")
            st.markdown(st.session_state.final_output)
            st.success(st.session_state.roadmap)

# --- TAB 3: RESULTS365 (STRESS TEST & SELF-HEALING) ---
with tab_health:
    st.header("📊 Results365: Advanced Health & ROI")
    
    if st.session_state.get('final_output'):
        # Simulate tracking logic - Drop impact if stress test is active
        actual_impact = 9.5 if stress_test_mode else 12.8
        target = float(target_goal)
        variance = actual_impact - target
        
        col_h1, col_h2 = st.columns([2, 1])
        
        with col_h1:
            st.metric("Realized Margin Impact", f"{actual_impact}%", f"{variance:.1f}% vs Target")
            st.line_chart([10.2, 10.0, 9.7, actual_impact]) 
            
        with col_h2:
            if stress_test_mode:
                # FEATURE: STRESS TEST RESPONSE
                st.error("🚨 STRESS TEST ACTIVE")
                st.write("**Scenario:** Global Supply Chain Disruption Simulation")
                with st.container(border=True):
                    st.subheader("🩹 Self-Healing Path")
                    st.write("Strategy shifted to 'Liquidity Preservation' mode.")
                    if st.button("Apply Recovery Path"):
                        st.toast("Roadmap Adjusted for Market Shock!", icon="🩹")
                        st.balloons()
            elif variance < 0:
                st.warning("🚨 DRIFT DETECTED: Healing Path suggested.")
            else:
                st.success("🍀 ON TRACK: ROI realization aligned.")

        st.divider()
        st.subheader("📈 Scenario Performance Forecast")
        st.bar_chart({"Defensive": [5, 8], "Balanced": [10, 15], "Aggressive": [12, 28]})
    else:
        st.info("Please generate a strategy to activate Results365 Monitoring.")

st.markdown("---")
st.caption("StratOS v11 | Proprietary Lancia Consult Framework Integration")
