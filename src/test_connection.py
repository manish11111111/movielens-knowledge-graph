
import os
os.environ["SSL_CERT_FILE"] = __import__("certifi").where()
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

if not all([URI, USERNAME, PASSWORD]):
    raise ValueError("Missing Neo4j credentials in .env file")

with GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
) as driver:
    driver.verify_connectivity()
    print("Connected to Neo4j Aura successfully!")

    with driver.session() as session:
        result = session.run("RETURN 'MovieLens KG is ready!' AS message")
        print(result.single()["message"])
