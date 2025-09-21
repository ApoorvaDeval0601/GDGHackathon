# api.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import DatabaseManager
from croagent import CROAgent
from agents import ScoutAgent
from pydantic import BaseModel

# --- Initialization ---
app = FastAPI()
db_manager = DatabaseManager("bolt://localhost:7687", "neo4j", "password")
cro_agent = CROAgent()
scout_agent = ScoutAgent()

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Model for Scenario Simulation ---
class ScenarioRequest(BaseModel):
    scenario: str

# --- API Endpoints ---

@app.get("/api/graph_data")
def get_graph_data():
    """
    Returns all nodes and relationships from Neo4j.
    """
    query = "MATCH (n:Institution) OPTIONAL MATCH (n)-[r:RELATIONSHIP]->(m:Institution) RETURN n, r, m"
    results = db_manager.execute_query(query)

    nodes = []
    edges = []
    node_ids = set()

    for record in results:
        n = record["n"]
        if n.id not in node_ids:
            nodes.append({"id": n.id, "label": n.get("name")})
            node_ids.add(n.id)

        m = record["m"]
        r = record["r"]
        if m is not None and r is not None:
            if m.id not in node_ids:
                nodes.append({"id": m.id, "label": m.get("name")})
                node_ids.add(m.id)
            edges.append({"from": r.start_node.id, "to": r.end_node.id, "label": r.get("type")})

    return {"nodes": nodes, "edges": edges}


@app.get("/api/risk_alerts/{company}")
def risk_alerts(company: str):
    """
    Assess the company's risk based on latest news and market data.
    """
    latest_news = scout_agent.get_latest_news(company)
    market_data = scout_agent.get_market_data(company)

    if not latest_news and not market_data:
        raise HTTPException(status_code=404, detail="No data available for this company.")

    company_data = {
        "company_name": company,
        "news_articles": latest_news,
        "market_data": market_data
    }

    report = cro_agent.assess_risk(company_data)
    return {"company": company, "risk_report": report}


@app.get("/api/company_condition/{company}")
def company_condition(company: str):
    """
    Return Gemini-generated analysis of company condition.
    """
    latest_news = scout_agent.get_latest_news(company)
    market_data = scout_agent.get_market_data(company)

    if not latest_news and not market_data:
        raise HTTPException(status_code=404, detail="No data available for this company.")

    company_data = {
        "company_name": company,
        "news_articles": latest_news,
        "market_data": market_data
    }

    report = cro_agent.analyze_company_condition(company_data)
    return {"company": company, "report": report, "news": latest_news, "market_data": market_data}


@app.post("/api/simulate/{company}")
def simulate(company: str, request: ScenarioRequest):
    """
    Simulate a hypothetical scenario for a company.
    """
    scenario = request.scenario
    if not scenario:
        raise HTTPException(status_code=400, detail="Scenario description is required.")

    result = cro_agent.simulate_scenario(company, scenario)
    return {"company": company, "scenario": scenario, "simulation": result}
