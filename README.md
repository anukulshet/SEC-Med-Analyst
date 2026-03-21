# SEC-Med Risk Intelligence Agent

An autonomous multi-agent pipeline for healthcare and financial due diligence.
Live Dashboard: [https://sec-med-analyst.streamlit.app](https://sec-med-analyst.streamlit.app)

## The Problem

Analysts spend hundreds of hours cross-referencing corporate financial filings with public news to identify risk discrepancies. This project automates that entire research process.

## Tech Stack

- **Orchestration:** LangGraph for stateful agent workflows
- **Data Engineering:** NumPy and Pandas for quantitative risk scoring
- **Persistence:** PostgreSQL and Docker for relational storage
- **Interface:** Streamlit for the real-time research dashboard

## How it Works

1. **SEC Detective** fetches legal risk factors from the company's most recent 10-K filing on SEC EDGAR.
2. **News Reporter** pulls live headlines from Google News and scores sentiment using a financial keyword lexicon.
3. **Risk Calculator** combines both signals into a composite risk score using the formula: `(1 - sentiment) x log(risk_count + 1) x 10`
4. Results are displayed in a dashboard with a risk gauge, score breakdown and raw audit table.


## Setup

1. Start the database: `docker compose up -d`
2. Activate the environment: `.venv\Scripts\activate`
3. Launch the app: `python -m streamlit run app.py`
