
import os
import certifi
os.environ["SSL_CERT_FILE"] = certifi.where()

import pandas as pd
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")


def import_tags(tx, rows):
    tx.run("""
        UNWIND $rows AS row
        MERGE (u:User {userId: row.userId})
        MATCH (m:Movie {movieId: row.movieId})
        MERGE (u)-[t:TAGGED {tag: row.tag}]->(m)
        SET t.timestamp = row.timestamp
    """, rows=rows)


def main():
    tags = pd.read_csv("data/tags.csv")
    rows = [
        {
            "userId": int(row.userId),
            "movieId": int(row.movieId),
            "tag": str(row.tag),
            "timestamp": int(row.timestamp)
        }
        for row in tags.itertuples(index=False)
    ]

    with GraphDatabase.driver(
        URI, auth=(USERNAME, PASSWORD)
    ) as driver:
        driver.verify_connectivity()

        with driver.session() as session:
            for start in range(0, len(rows), 5000):
                batch = rows[start:start + 5000]
                session.execute_write(import_tags, batch)
                print(f"Imported {min(start + len(batch), len(rows))}/{len(rows)} tags")

            result = session.run("""
                MATCH ()-[t:TAGGED]->()
                RETURN count(t) AS total_tags
            """).single()

            print("\nTag import completed!")
            print(f"Tag relationships: {result['total_tags']}")


if __name__ == "__main__":
    main()
