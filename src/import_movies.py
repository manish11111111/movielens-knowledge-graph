
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

DATA_DIR = "data"
BATCH_SIZE = 1000


def import_movies(tx, rows):
    tx.run("""
        UNWIND $rows AS row
        MERGE (m:Movie {movieId: row.movieId})
        SET m.title = row.title,
            m.genres = row.genres
    """, rows=rows)


def import_genres(tx, rows):
    tx.run("""
        UNWIND $rows AS row
        MATCH (m:Movie {movieId: row.movieId})
        MERGE (g:Genre {name: row.genre})
        MERGE (m)-[:IN_GENRE]->(g)
    """, rows=rows)


def batches(items, size):
    for start in range(0, len(items), size):
        yield items[start:start + size]


def main():
    movies = pd.read_csv(f"{DATA_DIR}/movies.csv")

    movie_rows = []
    genre_rows = []

    for row in movies.itertuples(index=False):
        movie_id = int(row.movieId)
        title = str(row.title)
        genres = str(row.genres).split("|")

        movie_rows.append({
            "movieId": movie_id,
            "title": title,
            "genres": genres
        })

        for genre in genres:
            if genre != "(no genres listed)":
                genre_rows.append({
                    "movieId": movie_id,
                    "genre": genre
                })

    with GraphDatabase.driver(
        URI, auth=(USERNAME, PASSWORD)
    ) as driver:
        driver.verify_connectivity()

        with driver.session() as session:
            session.run("""
                CREATE CONSTRAINT movie_id IF NOT EXISTS
                FOR (m:Movie) REQUIRE m.movieId IS UNIQUE
            """)
            session.run("""
                CREATE CONSTRAINT genre_name IF NOT EXISTS
                FOR (g:Genre) REQUIRE g.name IS UNIQUE
            """)

            for batch in batches(movie_rows, BATCH_SIZE):
                session.execute_write(import_movies, batch)

            for batch in batches(genre_rows, BATCH_SIZE):
                session.execute_write(import_genres, batch)

            result = session.run("""
                MATCH (m:Movie)
                RETURN count(m) AS movies
            """)
            movie_count = result.single()["movies"]

            result = session.run("""
                MATCH (g:Genre)
                RETURN count(g) AS genres
            """)
            genre_count = result.single()["genres"]

            print("Movie import completed!")
            print(f"Movies in graph: {movie_count}")
            print(f"Genres in graph: {genre_count}")


if __name__ == "__main__":
    main()
