# 🕵️ SEC-Med Risk Intelligence Agent
**An Autonomous Multi-Agent Pipeline for Healthcare & Financial Due Diligence**

## 🚀 The Problem
Analysts spend hundreds of hours cross-referencing corporate financial filings with public news to find "Risk Discrepancies." This project automates that entire research lifecycle.

## 🛠️ Tech Stack & Architecture
- **Orchestration:** LangGraph (Stateful Agent Workflows)
- **Data Engineering:** NumPy & Pandas (Quantitative Risk Scoring)
- **Persistence:** PostgreSQL & Docker (Relational Intelligence Storage)
- **Interface:** Streamlit (Real-time Research Dashboard)

## 🧠 How it Works
1. **The Detective (SEC Agent):** Extracts legal risk factors from official 10-K filings.
2. **The Reporter (News Agent):** Conducts real-time sentiment analysis on medical news.
3. **The Logic Engine:** Uses NumPy to calculate a "Risk Alignment Score" based on state data.
4. **The UI:** Visualizes findings and alerts users to negative sentiment discrepancies.

## ⚙️ Setup Instructions
1. Initialize Database: `docker compose up -d`
2. Activate Environment: `.venv\Scripts\activate`
3. Launch Dashboard: `python -m streamlit run app.py`