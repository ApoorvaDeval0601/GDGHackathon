# database.py
from neo4j import GraphDatabase

class DatabaseManager:
    """
    Manages the connection and all interactions with the Neo4j database.
    """
    def __init__(self, uri, user, password):
        # Establishes the connection to your running Neo4j instance
        self._driver = GraphDatabase.driver(uri, auth=(user, password))
        print("Database connection established.")

    def close(self):
        # Closes the connection when the application shuts down
        self._driver.close()

    def execute_query(self, query, parameters=None):
        # A helper function to run queries against the database
        with self._driver.session() as session:
            # Using write_transaction for queries that modify the database
            result = session.write_transaction(lambda tx: list(tx.run(query, parameters)))
            return result

    def create_institution_node(self, name: str):
        """
        Creates a new :Institution node if it doesn't already exist.
        The MERGE command is crucial as it prevents creating duplicate companies.
        """
        print(f"Database: Creating/merging node for {name}...")
        query = "MERGE (i:Institution {name: $name}) RETURN i"
        self.execute_query(query, {"name": name})

    def create_relationship_edge(self, source_name: str, target_name: str, relationship_type: str):
        """
        Finds two existing institution nodes and creates a directed relationship between them.
        """
        print(f"Database: Creating relationship: {source_name} -> {relationship_type} -> {target_name}")
        query = """
        MATCH (a:Institution {name: $source_name})
        MATCH (b:Institution {name: $target_name})
        MERGE (a)-[r:RELATIONSHIP {type: $relationship_type}]->(b)
        """
        self.execute_query(query, {
            "source_name": source_name,
            "target_name": target_name,
            "relationship_type": relationship_type
        })

# --- Independent Test Block ---
# This allows you to test your database code without needing the other agents.
if __name__ == '__main__':
    # Connect to the database you started with Docker
    db = DatabaseManager("bolt://localhost:7687", "neo4j", "password")

    print("\n--- Running Database Test ---")
    
    # Test 1: Create some nodes
    print("\nStep 1: Creating nodes...")
    db.create_institution_node("JPMorgan Chase")
    db.create_institution_node("Goldman Sachs")

    # Test 2: Create a relationship between them
    print("\nStep 2: Creating a relationship...")
    db.create_relationship_edge(
        source_name="JPMorgan Chase",
        target_name="Goldman Sachs",
        relationship_type="is a competitor to"
    )

    print("\n--- Test Complete ---")
    print("Check your Neo4j browser at http://localhost:7474 to see the results!")

    db.close()