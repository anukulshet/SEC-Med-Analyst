import streamlit as st
from src.graph import app # This imports your LangGraph Brain!
import pandas as pd

# UI Header
st.set_page_config(page_title="SEC-Med Analyst", layout="wide")
st.title("🕵️ SEC-Med Risk Intelligence")
st.markdown("Automated Due Diligence for Healthcare & Finance")

# Sidebar for User Input
with st.sidebar:
    st.header("Settings")
    ticker = st.text_input("Enter Company Ticker (e.g., PFE, MRNA):", value="PFE")
    run_btn = st.button("Run Risk Audit")

# Main Logic
if run_btn:
    st.info(f"Analyzing {ticker}...")
    
    results = app.invoke({"ticker": ticker})
    
    # Display the Logs
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🕵️ Detective Findings")
        for risk in results['sec_risks']:
            st.write(f"- {risk}")
            
    with col2:
        st.subheader("📰 Reporter Analysis")
        st.write(f"Sentiment Score: **{results['news_sentiment']}**")
        if results['news_sentiment'] < 0:
            st.error("Warning: Negative News Sentiment detected.")
        else:
            st.success("News sentiment is stable.")

    # Table
    st.divider()
    st.subheader("Audit Summary")
    df = pd.DataFrame([results])
    st.table(df)