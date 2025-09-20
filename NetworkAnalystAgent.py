# NetworkAnalystAgent.py (Corrected Version)

from database import DatabaseManager
import json

class NetworkAnalystAgent:
    """
    This agent takes the analysis from the AnalystAgent and uses the
    DatabaseManager to store the findings in the Neo4j database.
    """
    # This __init__ method now correctly accepts the db_manager object.
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def process_and_store(self, analysis_data: dict, main_company_name: str):
        """
        Processes the analysis JSON dictionary and stores nodes and relationships.
        """
        print(f"Network Analyst: Processing analysis for {main_company_name}")
        
        self.db.create_institution_node(main_company_name)

        relationships = analysis_data.get("relationships", [])
        if not relationships:
            print("Network Analyst: No new relationships to process.")
            return

        for rel in relationships:
            source = rel.get("source_entity")
            target = rel.get("target_entity")
            rel_type = rel.get("relationship_type")

            if not all([source, target, rel_type]):
                continue 

            self.db.create_institution_node(source)
            self.db.create_institution_node(target)
            self.db.create_relationship_edge(source, target, rel_type)