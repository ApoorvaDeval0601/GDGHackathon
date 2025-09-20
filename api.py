# api.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import DatabaseManager

# --- Initialization ---
app = FastAPI()
db_manager = DatabaseManager("bolt://localhost:7687", "neo4j", "password")

# --- Middleware ---
# This is important security code that allows your frontend (which will run
# in a browser) to make requests to this backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# --- API Endpoint ---
@app.get("/api/graph_data")
def get_graph_data():
    """
    This endpoint queries the Neo4j database and returns all nodes and
    relationships in a format that is easy for a frontend to visualize.
    """
    # This Cypher query gets all nodes and their relationships.
    # OPTIONAL MATCH is used to include nodes that may not have relationships yet.
    query = "MATCH (n:Institution) OPTIONAL MATCH (n)-[r:RELATIONSHIP]->(m:Institution) RETURN n, r, m"
    results = db_manager.execute_query(query)

    nodes = []
    edges = []
    node_ids = set() # Use a set to avoid adding duplicate nodes

    for record in results:
        # Process the source node (n)
        n = record["n"]
        if n.id not in node_ids:
            nodes.append({"id": n.id, "label": n.get("name")})
            node_ids.add(n.id)

        # Process the target node (m) and the relationship (r) if they exist
        m = record["m"]
        r = record["r"]
        if m is not None and r is not None:
            if m.id not in node_ids:
                nodes.append({"id": m.id, "label": m.get("name")})
                node_ids.add(m.id)
            
            # Add the relationship
            edges.append({
                "from": r.start_node.id, 
                "to": r.end_node.id, 
                "label": r.get("type")
            })

    return {"nodes": nodes, "edges": edges}