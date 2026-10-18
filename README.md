# MovieLens Knowledge Graph

A graph-based movie recommendation and data exploration application built with **Python, Neo4j Aura, Cypher, Streamlit, and PyVis**.

**Live Demo:** [Try the MovieLens Knowledge Graph](https://movielens-knowledge-graph.streamlit.app/)  
**GitHub Repository:** [movielens-knowledge-graph](https://github.com/manish11111111/movielens-knowledge-graph)

## About the Project

I built this project to explore how graph databases can represent relationships between users, movies, genres, ratings, and tags to support movie recommendations and data exploration.

Instead of storing everything as disconnected records, I modelled the data as connected nodes and relationships in Neo4j. This allows me to explore movie similarities, user rating patterns, and genre-level trends using Cypher queries.

The project uses the MovieLens dataset, Python data-import scripts, and a Neo4j Aura database. It also includes a Streamlit web interface for exploring the graph and inspecting movie information interactively.

## Features

- Import movies, genres, ratings, and tags into Neo4j.
- Explore movies through a Streamlit dashboard.
- Search for movies and inspect their details.
- Explore movie relationships through an interactive knowledge graph.
- Find movies that share genres with a selected movie.
- Explore baseline recommendations based on user rating patterns.
- Analyse movie ratings and genre popularity using Cypher.
- Run graph overview, relationship analysis, and data quality checks.

## Tech Stack

- **Python** — data import, processing, and application logic
- **Neo4j Aura** — cloud-hosted graph database
- **Cypher** — graph queries, analytics, and recommendation logic
- **Pandas** — CSV data handling
- **Streamlit** — interactive web application and dashboard
- **PyVis** — interactive graph visualisation
- **python-dotenv** — environment configuration
- **certifi** — trusted certificate bundle for secure connections

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

This model supports queries across movie genres, user ratings, and tags, making it possible to explore connections useful for recommendation and analytics tasks.

## Dataset

The imported graph contains the following nodes and relationships:

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
├── app.py
├── .gitignore
├── requirements.txt
└── README.md
```

*Note: This tree represents the main project files. Keep it aligned with the actual files and folders in the repository. The `.env` file is intentionally excluded because it contains private credentials.*

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/manish11111111/movielens-knowledge-graph.git
cd movielens-knowledge-graph
```

### 2. Create a virtual environment

On Windows, using Python 3.14:

```powershell
py -3.14 -m venv .venv
```

### 3. Install dependencies

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Make sure `requirements.txt` includes the dependencies used by the application, including `streamlit`, `pyvis`, `neo4j`, `pandas`, `python-dotenv`, and `certifi`.

### 4. Configure Neo4j

Create a `.env` file in the project root and add your own Neo4j Aura connection details:

```env
NEO4J_URI=your_neo4j_uri
NEO4J_USERNAME=your_neo4j_username
NEO4J_PASSWORD=your_neo4j_password
```

Use your own credentials and keep them private. **Never commit your `.env` file to GitHub.**

### 5. Import the dataset

Make sure the required CSV files are available in the `data/` directory and your Neo4j database is running.

Run the import scripts from the project root:

```powershell
.\.venv\Scripts\python.exe .\src\import_movies.py
.\.venv\Scripts\python.exe .\src\import_ratings.py
.\.venv\Scripts\python.exe .\src\import_tags.py
```

If the graph has already been imported, you can skip this step unless you need to reload the data.

### 6. Launch the Streamlit application

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Streamlit will provide a local URL in the terminal. Open that URL in your browser to use the application.

## Deployment

The application is available online through Streamlit Community Cloud and connects to a Neo4j Aura database.

- **Live application:** [movielens-knowledge-graph.streamlit.app](https://movielens-knowledge-graph.streamlit.app/)
- **Source code:** [GitHub repository](https://github.com/manish11111111/movielens-knowledge-graph)

Database credentials for the deployed application are configured through Streamlit Cloud secrets rather than committed to the repository.

## Example: Graph-Based Recommendations

The project includes Cypher queries demonstrating two baseline recommendation approaches.

**Genre-based recommendations:** Find movies that share genres with a selected movie, then use rating counts and average ratings to help rank the results.

**Collaborative recommendation exploration:** Identify movies rated highly by users who also rated a target movie highly.

For example, `Toy Story (1995)` can be used to explore genre overlap and connections through user ratings.

These approaches demonstrate graph-based recommendation logic; they are not intended to represent a fully trained or comprehensively evaluated recommendation model.

## What I Learned

Working on this project gave me practical experience with:

- Designing a graph data model.
- Loading and processing CSV data with Python.
- Connecting Python applications to Neo4j Aura.
- Writing Cypher queries for analytics and recommendations.
- Checking data quality after importing data.
- Building an interactive dashboard with Streamlit.
- Visualising relationships between users, movies, and genres using PyVis.
- Managing configuration through environment variables.
- Deploying a Python application to Streamlit Community Cloud.

## Limitations and Next Steps

The current recommendations use straightforward graph-query rules rather than a trained recommendation model with comprehensive offline evaluation.

Potential improvements include:

- Adding movie posters and richer movie metadata.
- Adding genre analytics charts and rating distribution visualisations.
- Improving recommendation scoring and ranking.
- Evaluating recommendations using metrics such as Precision@K and Recall@K.
- Adding more interactive graph exploration features.

## Dataset Credit

This project uses the [MovieLens dataset](https://grouplens.org/datasets/movielens/) provided by [GroupLens](https://grouplens.org/). Please refer to the original dataset page for dataset details and terms of use.
