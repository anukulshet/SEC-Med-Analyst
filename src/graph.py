import requests
import numpy as np
from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END

#Shared State
class AgentState(TypedDict):
    ticker: str
    cik: str
    company_name: str
    sec_risks: List[str]
    sec_risk_raw: str
    news_sentiment: float
    news_headlines: List[str]
    final_risk_score: float
    risk_level: str
    error: str

HEADERS = {"User-Agent": "SEC-Med-Analyst research@secmedanalyst.com"}


def get_cik_for_ticker(ticker: str):
    url = "https://www.sec.gov/files/company_tickers.json"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    ticker_upper = ticker.upper().strip()
    for entry in data.values():
        if entry["ticker"].upper() == ticker_upper:
            cik = str(entry["cik_str"]).zfill(10)
            return cik, entry["title"]
    raise ValueError(f"Ticker '{ticker}' not found in SEC database.")

#Node 1: SEC Detective
def detective_node(state: AgentState) -> dict:
    print(f"Detective: Fetching SEC 10-K for {state['ticker']}...")
    try:
        cik, company_name = get_cik_for_ticker(state["ticker"])
        sub_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        sub = requests.get(sub_url, headers=HEADERS, timeout=15).json()

        filings = sub["filings"]["recent"]
        forms = filings["form"]
        acc_nums = filings["accessionNumber"]
        primary_docs = filings["primaryDocument"]

        ten_k_index = next(
            (i for i, f in enumerate(forms) if f in ("10-K", "10-K/A")), None
        )
        if ten_k_index is None:
            return {
                "cik": cik, "company_name": company_name,
                "sec_risks": ["No 10-K filing found for this company."],
                "sec_risk_raw": "", "error": "No 10-K found",
            }

        acc_num = acc_nums[ten_k_index].replace("-", "")
        primary_doc = primary_docs[ten_k_index]
        doc_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_num}/{primary_doc}"
        doc_text = requests.get(doc_url, headers=HEADERS, timeout=30).text
        risks = _extract_risk_factors(doc_text, state["ticker"])

        return {
            "cik": cik, "company_name": company_name,
            "sec_risks": risks[:12], "sec_risk_raw": " ".join(risks), "error": "",
        }
    except ValueError as e:
        return {"cik": "", "company_name": state["ticker"], "sec_risks": [str(e)], "sec_risk_raw": "", "error": str(e)}
    except Exception as e:
        return {"cik": "", "company_name": state["ticker"], "sec_risks": [f"SEC fetch error: {type(e).__name__}: {e}"], "sec_risk_raw": "", "error": str(e)}

def _extract_risk_factors(html_text: str, ticker: str) -> List[str]:
    import re
    clean = re.sub(r"<[^>]+>", " ", html_text)
    clean = re.sub(r"&[a-zA-Z]+;", " ", clean)
    clean = re.sub(r"\s+", " ", clean).strip()

    start = -1
    for pat in [r"Item\s*1A[\.\s]*Risk\s*Factor", r"ITEM\s*1A[\.\s]*RISK\s*FACTOR"]:
        m = re.search(pat, clean, re.IGNORECASE)
        if m:
            start = m.start()
            break

    if start == -1:
        return _keyword_risk_scan(clean, ticker)

    end_match = re.search(r"Item\s*[12][B-Z]?[\.\s]", clean[start + 100:], re.IGNORECASE)
    end = start + 100 + end_match.start() if end_match else start + 15000
    return _keyword_risk_scan(clean[start:end], ticker)

def _keyword_risk_scan(text: str, ticker: str) -> List[str]:
    import re
    RISK_KEYWORDS = [
        "risk", "may not", "could result", "uncertainty", "competition",
        "failure", "adverse", "decline", "unable", "loss", "litigation",
        "regulatory", "FDA", "approval", "patent", "expire", "subject to",
        "cannot guarantee", "no assurance", "significant", "material",
        "dependent", "volatility", "cybersecurity", "data breach",
        "supply chain", "shortage", "recall", "clinical trial",
    ]
    sentences = re.split(r"(?<=[.!?])\s+", text)
    scored = []
    for sent in sentences:
        sent = sent.strip()
        if len(sent) < 40 or len(sent) > 400:
            continue
        score = sum(1 for kw in RISK_KEYWORDS if kw.lower() in sent.lower())
        if score >= 2:
            clean_sent = re.sub(r"\s+", " ", sent).strip()
            if len(clean_sent) > 220:
                clean_sent = clean_sent[:217] + "..."
            scored.append((score, clean_sent))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = [s for _, s in scored[:15]]
    if not results:
        results = [f"Risk factors not extractable for {ticker} from this filing. Review the full 10-K on SEC EDGAR."]
    return results

#Node 2: News Reporter
def reporter_node(state: AgentState) -> dict:
    print(f"Reporter: Analyzing news for {state['ticker']}...")
    try:
        headlines = _fetch_rss_headlines(state["ticker"], state.get("company_name", ""))
        sentiment = _score_sentiment(headlines)
        return {"news_headlines": headlines[:10], "news_sentiment": round(sentiment, 4)}
    except Exception as e:
        return {"news_headlines": [f"News fetch error: {e}"], "news_sentiment": 0.0}

def _fetch_rss_headlines(ticker: str, company_name: str) -> List[str]:
    import xml.etree.ElementTree as ET
    queries = [ticker]
    if company_name:
        queries.append(company_name.split()[0])
    headlines = []
    for q in queries:
        try:
            url = f"https://news.google.com/rss/search?q={q}+stock&hl=en-US&gl=US&ceid=US:en"
            resp = requests.get(url, timeout=10, headers=HEADERS)
            root = ET.fromstring(resp.text)
            for item in root.iter("item"):
                title = item.findtext("title", "")
                if title and len(title) > 10:
                    headlines.append(title)
            if len(headlines) >= 15:
                break
        except Exception:
            continue
    return list(dict.fromkeys(headlines))

def _score_sentiment(headlines: List[str]) -> float:
    POSITIVE = ["surge", "beat", "approve", "approved", "breakthrough", "profit",
        "growth", "gain", "rally", "upgrade", "exceed", "record", "success",
        "positive", "strong", "rise", "soar", "launch", "partnership", "deal",
        "win", "expand", "recovery", "boost", "bullish"]
    NEGATIVE = ["fall", "drop", "miss", "decline", "recall", "lawsuit", "warning",
        "risk", "loss", "down", "plunge", "cut", "concern", "fail", "reject",
        "investigation", "fine", "penalty", "fraud", "delay", "adverse",
        "withdraw", "downgrade", "crash", "layoff", "halt", "suspend", "probe"]
    if not headlines:
        return 0.0
    scores = []
    for h in headlines:
        h_lower = h.lower()
        pos = sum(1 for w in POSITIVE if w in h_lower)
        neg = sum(1 for w in NEGATIVE if w in h_lower)
        total = pos + neg
        scores.append((pos - neg) / total if total > 0 else 0.0)
    return float(np.mean(scores)) if scores else 0.0

#Node 3: Risk Calculator
def calculator_node(state: AgentState) -> dict:
    print("Calculator: Computing composite risk score...")
    risk_count = len([r for r in state.get("sec_risks", []) if len(r) > 20])
    sentiment = state.get("news_sentiment", 0.0)
    raw = (1 - sentiment) * np.log1p(risk_count) * 10
    score = float(np.clip(np.round(raw, 2), 0, 100))
    if score >= 70:
        level = "HIGH RISK"
    elif score >= 40:
        level = "MODERATE RISK"
    else:
        level = "LOW RISK"
    return {"final_risk_score": score, "risk_level": level}

#Build LangGraph
workflow = StateGraph(AgentState)
workflow.add_node("detective", detective_node)
workflow.add_node("reporter", reporter_node)
workflow.add_node("calculator", calculator_node)
workflow.add_edge(START, "detective")
workflow.add_edge("detective", "reporter")
workflow.add_edge("reporter", "calculator")
workflow.add_edge("calculator", END)
app = workflow.compile()