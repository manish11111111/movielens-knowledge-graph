import os
import tomllib
from pathlib import Path
from neo4j import GraphDatabase

def get_config():
    keys = ["NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD"]
    # 1. GitHub Actions / env variable
    if all(os.environ.get(k) for k in keys):
        return {k: os.environ[k] for k in keys}
    # 2. Local secrets.toml
    path = Path(".streamlit/secrets.toml")
    if path.exists():
        data = tomllib.loads(path.read_text())
        if all(k in data for k in keys):
            return {k: data[k] for k in keys}
    raise SystemExit("Credentials not found in env or .streamlit/secrets.toml")

cfg = get_config()
print("URI starts with:", cfg["NEO4J_URI"][:8])

with GraphDatabase.driver(cfg["NEO4J_URI"], auth=(cfg["NEO4J_USERNAME"], cfg["NEO4J_PASSWORD"])) as driver:
    driver.verify_connectivity()
    with driver.session() as session:
        count = session.run("MATCH (n) RETURN count(n) AS c").single()["c"]
        print(f"Neo4j is alive. Node count: {count}")