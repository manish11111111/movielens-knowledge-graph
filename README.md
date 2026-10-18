# MovieLens Knowledge Graph

A graph-based movie recommendation and data exploration project built with Python and Neo4j.

**GitHub Repository:** [movielens-knowledge-graph](https://github.com/manish11111111/movielens-knowledge-graph)

## About the Project

I built this project to explore how graph databases can be used to connect movie data and find relationships that are useful for recommendations.

Instead of keeping movies, users, genres, ratings, and tags in separate tables, I modelled them as connected nodes and relationships in Neo4j. This makes it possible to explore movie similarities, user rating patterns, and genre-level trends using Cypher queries.

The project uses the MovieLens dataset and Python scripts to load the data into a Neo4j Aura database.

## What It Can Do

- Import movies, genres, ratings, and tags into Neo4j.
- Find movies that share genres with a selected movie.
- Explore recommendations based on users who rated the same movies highly.
- Analyse movie ratings and genre popularity.
- Check the graph for missing data and unexpected values.
- Explore relationships between users, movies, and genres with Cypher.

## Tech Stack

- **Python** — data import and processing
- **Neo4j Aura** — graph database
- **Cypher** — graph queries and recommendations
- **Pandas** — CSV data handling
- **python-dotenv** — environment configuration

## Graph Model

The graph contains three main types of nodes:

- `User`
- `Movie`
- `Genre`

They are connected through these relationships:

```text
(User)-[:RATED {rating, timestamp}]->(Movie)
(User)-[:TAGGED {tag, timestamp}]->(Movie)
(Movie)-[:IN_GENRE]->(Genre)
```

This structure lets me query both movie information and the connections between users and movies.

## Dataset

The imported dataset contains:

| Item | Count |
|---|---:|
| Movies | 9,742 |
| Users | 610 |
| Genres | 19 |
| Ratings | 100,836 |
| Tags | 3,683 |
| Movie–genre relationships | 22,050 |

These counts were checked against the data loaded into Neo4j.

## Project Structure

```text
MovieLens-Knowledge-Graph/
├── data/
│   ├── movies.csv
│   ├── ratings.csv
│   └── tags.csv
├── queries/
│   ├── 01_graph_overview.cypher
│   ├── 02_relationship_overview.cypher
│   ├── 03_data_quality_checks.cypher
│   ├── 04_rating_distribution.cypher
│   ├── 05_genre_based_recommendations.cypher
│   ├── 06_collaborative_recommendations.cypher
│   └── 07_genre_analytics.cypher
├── src/
│   ├── import_movies.py
│   ├── import_ratings.py
│   └── import_tags.py
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/manish11111111/movielens-knowledge-graph.git
cd movielens-knowledge-graph
```

### 2. Create a virtual environment

On Windows:

```powershell
py -3.14 -m venv .venv
```

### 3. Install the dependencies

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 4. Configure Neo4j

Create a `.env` file in the project root and add your own Neo4j Aura connection details:

```env
NEO4J_URI=your_neo4j_uri
NEO4J_USERNAME=your_neo4j_username
NEO4J_PASSWORD=your_neo4j_password
```

Keep your credentials private. The `.env` file should not be committed to GitHub.

### 5. Import the dataset

Run these commands from the project root:

```powershell
.\.venv\Scripts\python.exe .\src\import_movies.py
.\.venv\Scripts\python.exe .\src\import_ratings.py
.\.venv\Scripts\python.exe .\src\import_tags.py
```

Make sure the CSV files are present in the `data/` directory and your Neo4j database is available before running the scripts.

## Example: Genre-Based Recommendations

One of the queries uses *Toy Story (1995)* as the target movie and finds other movies that share its genres. It then considers rating counts and average ratings to rank the results.

Another query looks at movies rated highly by users who also rated *Toy Story (1995)* highly. These are baseline recommendation approaches intended to demonstrate how graph relationships can be used for recommendations.

The `.cypher` files in the `queries/` directory contain the queries for graph inspection, data quality checks, recommendations, and analytics.

## What I Learned

Working on this project gave me practical experience with:

- Designing a graph data model.
- Loading CSV data into Neo4j using Python.
- Writing Cypher queries to explore connected data.
- Checking data quality after an import.
- Building basic recommendation logic from genre overlap and user ratings.

## Limitations and Next Steps

The current recommendations use straightforward rules rather than a trained or evaluated recommendation model. The next improvements could include better scoring, more robust ranking, recommendation evaluation, and a visual interface for exploring the graph.

## Dataset Credit

This project uses the [MovieLens dataset](https://grouplens.org/datasets/movielens/) provided by GroupLens. Please refer to the original dataset page for its details and terms.