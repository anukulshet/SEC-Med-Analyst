from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END

# Define the Shared Memory
class AgentState(TypedDict):
    ticker: str
    sec_risks: List[str]
    news_sentiment: float
    final_risk_score: float

# Node 1: The Detective
def detective_node(state: AgentState):
    print(f"--- 🕵️ DETECTIVE: Reading SEC Filing for {state['ticker']} ---")
    # Later, we will put the real SEC reading logic here.
    return {"sec_risks": ["FDA Approval Delay", "Manufacturing Risk"]}

# Node 2: The Reporter 
def reporter_node(state: AgentState):
    print(f"--- 📰 REPORTER: Searching medical news for {state['sec_risks']} ---")
    # Later, we will put the news search logic here.
    return {"news_sentiment": -0.5}

# Build the Graph (The "Tracks")
workflow = StateGraph(AgentState)

# Add our stations (Nodes)
workflow.add_node("detective", detective_node)
workflow.add_node("reporter", reporter_node)

# Connect the stations (Edges)
workflow.add_edge(START, "detective")
workflow.add_edge("detective", "reporter") 
workflow.add_edge("reporter", END)

app = workflow.compile()

if __name__ == "__main__":
    test_input = {"ticker": "PFE"}
    app.invoke(test_input)