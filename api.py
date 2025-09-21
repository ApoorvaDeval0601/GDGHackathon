#API.PY.       # api.py
import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
 
# Import your custom modules
from database import DatabaseManager
from agents import ScoutAgent
from croagent import CROAgent
 
# --- Initialization ---
app = FastAPI()
db_manager = DatabaseManager("bolt://localhost:7687", "neo4j", "password")
scout_agent = ScoutAgent()
cro_agent = CROAgent()
 
# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    """Returns all nodes and relationships from Neo4j."""
    query = """
    MATCH (n:Institution)-[r:RELATIONSHIP]->(m:Institution)
    RETURN n, r, m
    UNION
    MATCH (n:Institution)
    WHERE NOT (n)-[:RELATIONSHIP]->()
    RETURN n, NULL AS r, NULL AS m
    """
    try:
        results = db_manager.execute_query(query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")
 
    nodes = []
    edges = []
    node_ids = set()
 
    for record in results:
        try:
            n = record["n"]
            r = record["r"]
            m = record["m"]
        except (KeyError, IndexError):
            continue
 
        nid = n.id
        if nid not in node_ids:
            nodes.append({"id": nid, "label": n.get("name")})
            node_ids.add(nid)
 
        if r is not None:
            start_id = r.start_node.id
            end_id = r.end_node.id
            rel_label = r.get("type")
 
            if end_id not in node_ids:
                m_label = m.get("name")
                nodes.append({"id": end_id, "label": m_label})
                node_ids.add(end_id)
 
            edges.append({
                "from": start_id,
                "to": end_id,
                "label": rel_label
            })
    return {"nodes": nodes, "edges": edges}
 
 
@app.get("/api/risk_alerts/{company}")
def risk_alerts(company: str):
    """Assess the company's risk based on latest news and market data."""
    # Assuming ticker is same as company for this example
    ticker = company
    latest_news = scout_agent.fetch_news(company)
    market_data = scout_agent.fetch_market_data(ticker)
 
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
    """Return Gemini-generated analysis of company condition."""
    # Assuming ticker is same as company for this example
    ticker = company
    latest_news = scout_agent.fetch_news(company)
    market_data = scout_agent.fetch_market_data(ticker)
 
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
    """Simulate a hypothetical scenario for a company."""
    scenario = request.scenario
    if not scenario:
        raise HTTPException(status_code=400, detail="Scenario description is required.")
    result = cro_agent.simulate_scenario(company, scenario)
    return {"company": company, "scenario": scenario, "simulation": result}