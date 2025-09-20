import json
from database import DatabaseManager

class NetworkAnalystAgent:
    """
    Takes the AI-enhanced analysis output, extracts institutions and relationships,
    and writes them into the Neo4j graph database.
    """
    def __init__(self, db_uri, db_user, db_password):
        self.db_manager = DatabaseManager(db_uri, db_user, db_password)

    def process_analysis(self, analysis_json_str: str):
        """
        Parses JSON string output from AnalystAgent and updates the graph.
        Expects keys 'institutions' and 'relationships' or similar in JSON.
        """
        try:
            data = json.loads(analysis_json_str)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return

        # Example structure ideas - adjust per your AnalystAgent output format
        institutions = data.get("institutions", [])
        relationships = data.get("company_relationships", [])

        # Create nodes for institutions
        for institution in institutions:
            name = institution.get("name")
            if name:
                self.db_manager.create_institution_node(name)

        # Create edges for relationships
        for rel in relationships:
            source = rel.get("source")
            target = rel.get("target")
            rel_type = rel.get("type")  # e.g. "invested_in", "acquired", "partnered_with"
            if source and target and rel_type:
                self.db_manager.create_relationship_edge(source, target, rel_type)

    def close(self):
        self.db_manager.close()


# --- Example usage ---
if __name__ == "__main__":
    # Setup connection to Neo4j (update credentials accordingly)
    db_uri = "bolt://localhost:7687"
    db_user = "neo4j"
    db_password = "password"

    network_agent = NetworkAnalystAgent(db_uri, db_user, db_password)

    # Example AI-generated JSON output, replace this with real output from AnalystAgent
    example_json = '''
    {
        "institutions": [
            {"name": "JPMorgan Chase"},
            {"name": "Goldman Sachs"}
        ],
        "company_relationships": [
            {"source": "JPMorgan Chase", "target": "Goldman Sachs", "type": "competitor"}
        ]
    }
    '''

    network_agent.process_analysis(example_json)

    print("Nodes and relationships added to Neo4j.")

    network_agent.close()