
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

BATCH_SIZE = 5000


def import_ratings(tx, rows):
    tx.run("""
        UNWIND $rows AS row
        MERGE (u:User {userId: row.userId})
        WITH u, row
        MATCH (m:Movie {movieId: row.movieId})
        MERGE (u)-[r:RATED]->(m)
        SET r.rating = row.rating,
            r.timestamp = row.timestamp
    """, rows=rows)


def main():
    ratings = pd.read_csv("data/ratings.csv")

    rows = [
        {
            "userId": int(row.userId),
            "movieId": int(row.movieId),
            "rating": float(row.rating),
            "timestamp": int(row.timestamp)
        }
        for row in ratings.itertuples(index=False)
    ]

    with GraphDatabase.driver(
        URI, auth=(USERNAME, PASSWORD)
    ) as driver:
        driver.verify_connectivity()

        with driver.session() as session:
            session.run("""
                CREATE CONSTRAINT user_id IF NOT EXISTS
                FOR (u:User) REQUIRE u.userId IS UNIQUE
            """)

            for start in range(0, len(rows), BATCH_SIZE):
                batch = rows[start:start + BATCH_SIZE]
                session.execute_write(import_ratings, batch)
                print(f"Imported {min(start + len(batch), len(rows))}/{len(rows)} ratings")

            result = session.run("""
                MATCH (u:User)
                WITH count(u) AS users
                MATCH (:User)-[r:RATED]->(:Movie)
                RETURN users, count(r) AS ratings
            """).single()

            print("\nRatings import completed!")
            print(f"Users in graph: {result['users']}")
            print(f"Rating relationships: {result['ratings']}")


if __name__ == "__main__":
    main()
