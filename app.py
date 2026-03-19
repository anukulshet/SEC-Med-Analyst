import streamlit as st
import pandas as pd
import numpy as np
from src.graph import app

st.set_page_config(
    page_title="SEC-Med Risk Intelligence",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
    }
    .metric-card {
        background: #0f1117;
        border: 1px solid #2d2d3a;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
    }
    .risk-high   { color: #ff4b4b; font-weight: 700; font-size: 1.4rem; }
    .risk-medium { color: #ffd700; font-weight: 700; font-size: 1.4rem; }
    .risk-low    { color: #00c853; font-weight: 700; font-size: 1.4rem; }
    .risk-item {
        background: #161823;
        border-left: 3px solid #3a3aff;
        padding: 10px 14px;
        margin: 6px 0;
        border-radius: 0 6px 6px 0;
        font-size: 0.88rem;
        line-height: 1.5;
    }
    .headline-item {
        background: #161823;
        border-left: 3px solid #00bcd4;
        padding: 8px 12px;
        margin: 4px 0;
        border-radius: 0 6px 6px 0;
        font-size: 0.85rem;
    }
    .score-badge {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 3.5rem;
        font-weight: 600;
        line-height: 1;
    }
    .agent-step {
        display: inline-block;
        background: #1e1e2e;
        border: 1px solid #3a3aff;
        color: #a0a8ff;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.78rem;
        margin: 2px;
        font-family: 'IBM Plex Mono', monospace;
    }
</style>
""", unsafe_allow_html=True)

#Sidebar
    st.markdown("## 🕵️ SEC-Med Analyst")
    st.markdown("*Autonomous Due Diligence Pipeline*")
    st.divider()

    st.markdown("### Pipeline Agents")
    st.markdown('<span class="agent-step">1 · SEC Detective</span>', unsafe_allow_html=True)
    st.markdown('<span class="agent-step">2 · News Reporter</span>', unsafe_allow_html=True)
    st.markdown('<span class="agent-step">3 · Risk Calculator</span>', unsafe_allow_html=True)
    st.divider()

    st.markdown("### Run Analysis")
    ticker = st.text_input(
        "Company Ticker",
        value="PFE",
        placeholder="e.g. PFE, MRNA, JNJ, ABT",
        help="Enter any US-listed healthcare or pharma ticker"
    ).upper().strip()

    st.markdown("**Example tickers:**")
    col_a, col_b = st.columns(2)
    with col_a:
        for t in ["PFE", "MRNA", "JNJ"]:
            if st.button(t, key=f"btn_{t}", use_container_width=True):
                ticker = t
    with col_b:
        for t in ["ABT", "UNH", "CVS"]:
            if st.button(t, key=f"btn_{t}", use_container_width=True):
                ticker = t

    run_btn = st.button("▶ Run Risk Audit", type="primary", use_container_width=True)
    st.divider()
    st.caption("Data sources: SEC EDGAR (10-K filings) · Google News RSS")
    st.caption("No API keys required.")

#Main
st.markdown("# 🕵️ SEC-Med Risk Intelligence")
st.markdown("*Automated due diligence — real SEC filings · live news sentiment · quantitative risk scoring*")
st.divider()

if not run_btn:
    st.markdown("""
    ### How it works

    **Agent 1 — SEC Detective**
    Queries the SEC EDGAR database for the company's most recent 10-K annual filing.
    Extracts and scores risk factor sentences from the official Item 1A disclosure section.

    **Agent 2 — News Reporter**
    Fetches live news headlines via Google News RSS (no API key needed).
    Scores each headline using a financial/medical keyword sentiment lexicon.

    **Agent 3 — Risk Calculator**
    Combines SEC risk count and news sentiment into a composite danger score using NumPy:

    ```
    score = (1 - sentiment) × log(risk_count + 1) × 10
    ```

    Enter a ticker in the sidebar and click **Run Risk Audit** to begin.
    """)
else:
    # Run the LangGraph pipeline
    with st.spinner(f"Running 3-agent pipeline for **{ticker}**..."):
        try:
            results = app.invoke({"ticker": ticker})
        except Exception as e:
            st.error(f"Pipeline error: {e}")
            st.stop()

    company_name = results.get("company_name", ticker)
    sec_risks = results.get("sec_risks", [])
    news_headlines = results.get("news_headlines", [])
    news_sentiment = results.get("news_sentiment", 0.0)
    risk_score = results.get("final_risk_score", 0.0)
    risk_level = results.get("risk_level", "UNKNOWN")
    error = results.get("error", "")

    if error and not sec_risks:
        st.error(f"Error: {error}")
        st.stop()

    st.success(f"Analysis complete for **{company_name}** ({ticker})")

    #Top metrics
    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.metric("Company", company_name[:20] + ("…" if len(company_name) > 20 else ""))
    with m2:
        st.metric("SEC Risk Factors", len(sec_risks))
    with m3:
        sentiment_label = "Positive" if news_sentiment > 0.1 else "Negative" if news_sentiment < -0.1 else "Neutral"
        st.metric("News Sentiment", f"{news_sentiment:+.3f}", delta=sentiment_label)
    with m4:
        st.metric("Composite Risk Score", f"{risk_score:.1f} / 100")

    st.divider()

    #Risk score gauge
    gauge_col, detail_col = st.columns([1, 2])

    with gauge_col:
        st.markdown("#### Overall Risk Assessment")
        color_cls = "risk-high" if risk_score >= 70 else "risk-medium" if risk_score >= 40 else "risk-low"
        icon = "🔴" if risk_score >= 70 else "🟡" if risk_score >= 40 else "🟢"
        st.markdown(f"""
        <div class="metric-card">
            <div class="score-badge" style="color: {'#ff4b4b' if risk_score >= 70 else '#ffd700' if risk_score >= 40 else '#00c853'}">
                {risk_score:.1f}
            </div>
            <div style="color:#888; font-size:0.8rem; margin:4px 0">out of 100</div>
            <div class="{color_cls}">{icon} {risk_level}</div>
        </div>
        """, unsafe_allow_html=True)

        #Gauge bar
        st.markdown("<br>", unsafe_allow_html=True)
        pct = risk_score / 100
        bar_color = "#ff4b4b" if risk_score >= 70 else "#ffd700" if risk_score >= 40 else "#00c853"
        st.markdown(f"""
        <div style="background:#1e1e2e; border-radius:6px; height:12px; overflow:hidden;">
            <div style="width:{pct*100:.0f}%; background:{bar_color}; height:100%; border-radius:6px; transition:width 1s;"></div>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:0.7rem; color:#555; margin-top:2px;">
            <span>0 Low</span><span>50 Moderate</span><span>100 High</span>
        </div>
        """, unsafe_allow_html=True)

    with detail_col:
        st.markdown("#### Risk Score Breakdown")
        breakdown_df = pd.DataFrame({
            "Component": ["News Sentiment Penalty", "SEC Risk Factor Count", "Log Scaling Factor", "Composite Score"],
            "Value": [
                f"{1 - news_sentiment:.3f}",
                str(len(sec_risks)),
                f"{np.log1p(len(sec_risks)):.3f}",
                f"{risk_score:.2f} / 100"
            ],
            "Notes": [
                "Higher when news is negative",
                "Risk sentences extracted from 10-K",
                "Diminishing returns scaling",
                "Formula: (1−sentiment) × log(n+1) × 10"
            ]
        })
        st.dataframe(breakdown_df, hide_index=True, use_container_width=True)

    st.divider()

    #Two column findings
    left_col, right_col = st.columns(2)

    with left_col:
        st.markdown(f"### 🕵️ Detective Findings — SEC 10-K Risks")
        st.caption(f"{len(sec_risks)} risk factors extracted from official filing")
        if not sec_risks or (len(sec_risks) == 1 and "error" in sec_risks[0].lower()):
            st.warning(sec_risks[0] if sec_risks else "No risks extracted.")
        else:
            for i, risk in enumerate(sec_risks, 1):
                st.markdown(f'<div class="risk-item"><b>#{i}</b> {risk}</div>', unsafe_allow_html=True)

    with right_col:
        st.markdown("### 📰 Reporter Analysis — Live News")
        st.caption(f"{len(news_headlines)} headlines analyzed")

        if news_sentiment > 0.1:
            st.success(f"📈 Positive news sentiment detected ({news_sentiment:+.3f})")
        elif news_sentiment < -0.1:
            st.error(f"📉 Negative news sentiment detected ({news_sentiment:+.3f})")
        else:
            st.info(f"➡️ Neutral news sentiment ({news_sentiment:+.3f})")

        if news_headlines and "error" not in news_headlines[0].lower():
            for h in news_headlines:
                st.markdown(f'<div class="headline-item">📌 {h}</div>', unsafe_allow_html=True)
        else:
            st.warning("Could not fetch live news headlines.")

    st.divider()

    #Raw audit table
    st.markdown("### 📋 Full Audit Summary")
    audit_df = pd.DataFrame([{
        "Ticker": ticker,
        "Company": company_name,
        "SEC Risk Count": len(sec_risks),
        "News Sentiment": news_sentiment,
        "Composite Risk Score": risk_score,
        "Risk Level": risk_level,
        "CIK": results.get("cik", "N/A"),
    }])
    st.dataframe(audit_df, hide_index=True, use_container_width=True)

    if results.get("cik"):
        cik_clean = results["cik"].lstrip("0")
        st.markdown(f"🔗 [View {company_name} filings on SEC EDGAR](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik_clean}&type=10-K&dateb=&owner=include&count=10)")