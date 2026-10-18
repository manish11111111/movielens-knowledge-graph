
import os

import certifi
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from neo4j import GraphDatabase
from pyvis.network import Network

st.set_page_config(
    page_title="MovieLens Graph Explorer",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_dotenv()
os.environ.setdefault("SSL_CERT_FILE", certifi.where())

st.markdown("""
<style>
    .stApp {
        background: #0B1120;
        color: #E5E7EB;
    }

    [data-testid="stSidebar"] {
        background: #111827;
        border-right: 1px solid #263244;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }

    .hero {
        background: linear-gradient(120deg, #172033, #111827);
        border: 1px solid #293548;
        border-radius: 18px;
        padding: 26px 28px;
        margin-bottom: 24px;
    }

    .hero h1 {
        color: #F9FAFB;
        font-size: 2.15rem;
        margin: 0;
        letter-spacing: -1px;
    }

    .hero p {
        color: #9CA3AF;
        margin-top: 8px;
        margin-bottom: 0;
        font-size: 1rem;
    }

    .section-heading {
        color: #F9FAFB;
        font-size: 1.35rem;
        font-weight: 700;
        margin-top: 12px;
        margin-bottom: 6px;
    }

    .section-subtitle {
        color: #9CA3AF;
        font-size: 0.92rem;
        margin-bottom: 18px;
    }

    [data-testid="stMetric"] {
        background: #111827;
        border: 1px solid #293548;
        border-radius: 14px;
        padding: 18px 20px;
    }

    [data-testid="stMetricLabel"] {
        color: #9CA3AF;
    }

    [data-testid="stMetricValue"] {
        color: #F9FAFB;
    }

    div.stButton > button[kind="primary"],
    div.stFormSubmitButton > button[kind="primary"] {
        background: #F59E0B;
        color: #111827;
        border: none;
        font-weight: 700;
        border-radius: 9px;
        min-height: 42px;
    }

    div.stButton > button[kind="primary"]:hover,
    div.stFormSubmitButton > button[kind="primary"]:hover {
        background: #FBBF24;
        color: #111827;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid #293548;
        border-radius: 12px;
        overflow: hidden;
    }

    div[data-testid="stForm"] {
        background: #111827;
        border: 1px solid #293548;
        border-radius: 14px;
        padding: 20px;
    }

    hr {
        border-color: #293548;
    }

    .footer {
        color: #6B7280;
        text-align: center;
        font-size: 0.82rem;
        padding-top: 12px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>🎬 MovieLens Graph Explorer</h1>
    <p>Discover movies, explore genres, and visualize connections
    between movies and users.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🎬 MovieLens")
    st.caption("Knowledge Graph Explorer")
    st.divider()
    st.markdown("### Navigation")
    st.markdown("🔎 Movie Explorer")
    st.markdown("🕸️ Knowledge Graph")
    st.divider()
    st.markdown("### Graph Legend")
    st.markdown("🟡 Movie")
    st.markdown("🟢 Genre")
    st.markdown("🔵 User")
    st.divider()
    st.caption("Powered by Neo4j · Streamlit · Python")

if "movies" not in st.session_state:
    st.session_state["movies"] = None

if "show_connections" not in st.session_state:
    st.session_state["show_connections"] = False

if "selected_movie_id" not in st.session_state:
    st.session_state["selected_movie_id"] = None

if "search_text" not in st.session_state:
    st.session_state["search_text"] = ""

if "selected_genre" not in st.session_state:
    st.session_state["selected_genre"] = "All genres"


@st.cache_resource
def get_driver():
    uri = os.getenv("NEO4J_URI")
    username = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")

    if not all([uri, username, password]):
        raise ValueError(
            "Missing Neo4j credentials. Check your local .env file."
        )

    return GraphDatabase.driver(
        uri,
        auth=(username, password),
    )


def run_query(query, parameters=None):
    driver = get_driver()

    with driver.session() as session:
        result = session.run(query, parameters or {})
        return [record.data() for record in result]


def section_heading(title, subtitle=""):
    st.markdown(
        f'<div class="section-heading">{title}</div>',
        unsafe_allow_html=True,
    )

    if subtitle:
        st.markdown(
            f'<div class="section-subtitle">{subtitle}</div>',
            unsafe_allow_html=True,
        )


try:
    stats_result = run_query("""
        MATCH (m:Movie)
        WITH count(m) AS movies
        MATCH (u:User)
        WITH movies, count(u) AS users
        MATCH ()-[r:RATED]->()
        WITH movies, users, count(r) AS ratings
        MATCH (g:Genre)
        RETURN movies, users, ratings, count(g) AS genres
    """)

    if not stats_result:
        st.warning("No statistics returned from Neo4j.")
        st.stop()

    stats = stats_result[0]

    section_heading(
        "Dataset Overview",
        "A snapshot of your MovieLens knowledge graph.",
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("🎞️ Movies", f"{stats['movies']:,}")
    col2.metric("👥 Users", f"{stats['users']:,}")
    col3.metric("⭐ Ratings", f"{stats['ratings']:,}")
    col4.metric("🏷️ Genres", f"{stats['genres']:,}")

    st.divider()

    section_heading(
        "🔎 Movie Explorer",
        "Search the catalogue and filter movies by genre.",
    )

    genres_result = run_query("""
        MATCH (g:Genre)
        RETURN g.name AS genre
        ORDER BY genre
    """)

    genre_options = [
        row["genre"]
        for row in genres_result
        if row.get("genre")
    ]

    with st.form("movie_search"):
        search_text = st.text_input(
            "Movie title",
            value=st.session_state["search_text"],
            placeholder="Try Toy Story, Batman, or Matrix...",
        )

        selected_genre = st.selectbox(
            "Genre",
            ["All genres"] + genre_options,
            index=(
                ["All genres"] + genre_options
            ).index(st.session_state["selected_genre"])
            if st.session_state["selected_genre"]
            in ["All genres"] + genre_options
            else 0,
        )

        submitted = st.form_submit_button(
            "🔍 Search Movies",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        st.session_state["search_text"] = search_text
        st.session_state["selected_genre"] = selected_genre
        st.session_state["show_connections"] = False
        st.session_state["selected_movie_id"] = None

        st.session_state["movies"] = run_query("""
            MATCH (m:Movie)
            OPTIONAL MATCH (m)-[:IN_GENRE]->(g:Genre)
            WITH m, collect(DISTINCT g.name) AS genres
            WHERE toLower(m.title) CONTAINS toLower($title)
              AND (
                  $genre = 'All genres'
                  OR $genre IN genres
              )
            OPTIONAL MATCH (u:User)-[r:RATED]->(m)
            RETURN
                m.movieId AS movie_id,
                m.title AS title,
                genres,
                round(avg(r.rating) * 100) / 100.0 AS avg_rating,
                count(r) AS rating_count
            ORDER BY rating_count DESC, title
            LIMIT 100
        """, {
            "title": search_text.strip(),
            "genre": selected_genre,
        })

    movies = st.session_state["movies"]

    if movies is None:
        st.info("Search for a movie to get started.")

    elif not movies:
        st.warning(
            "No matching movies found. Try another title or genre."
        )

    else:
        section_heading(
            "Search Results",
            f"{len(movies)} matching movie(s) found.",
        )

        df = pd.DataFrame(movies)

        df["genres"] = df["genres"].apply(
            lambda items: ", ".join(
                item for item in (items or []) if item
            )
        )

        df["avg_rating"] = df["avg_rating"].apply(
            lambda value: (
                round(value, 2) if value is not None else "N/A"
            )
        )

        df = df.rename(columns={
            "movie_id": "Movie ID",
            "title": "Movie Title",
            "genres": "Genres",
            "avg_rating": "Avg Rating",
            "rating_count": "Ratings",
        })

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        section_heading(
            "🎥 Movie Details",
            "Choose a result to inspect its knowledge graph.",
        )

        movie_options = {
            f"{row['title']} (ID: {row['movie_id']})":
                row["movie_id"]
            for row in movies
        }

        option_labels = list(movie_options.keys())
        movie_ids = list(movie_options.values())
        current_id = st.session_state["selected_movie_id"]

        default_index = (
            movie_ids.index(current_id)
            if current_id in movie_ids
            else 0
        )

        chosen_movie = st.selectbox(
            "Select a movie",
            option_labels,
            index=default_index,
            key="movie_details",
        )

        if st.button(
            "🕸️ View Movie Connections",
            type="primary",
            use_container_width=True,
        ):
            st.session_state["selected_movie_id"] = (
                movie_options[chosen_movie]
            )
            st.session_state["show_connections"] = True

        if st.session_state["show_connections"]:
            movie_id = st.session_state["selected_movie_id"]

            details = run_query("""
                MATCH (m:Movie {movieId: $movie_id})
                OPTIONAL MATCH (m)-[:IN_GENRE]->(g:Genre)
                WITH m, collect(DISTINCT g.name) AS genres
                OPTIONAL MATCH (u:User)-[r:RATED]->(m)
                RETURN
                    m.title AS title,
                    genres,
                    round(avg(r.rating) * 100) / 100.0
                        AS avg_rating,
                    count(r) AS rating_count
            """, {"movie_id": movie_id})

            if details:
                detail = details[0]

                st.divider()
                section_heading(
                    "Selected Movie",
                    "Information retrieved from your Neo4j graph.",
                )

                detail1, detail2, detail3 = st.columns(3)

                detail1.metric(
                    "⭐ Average Rating",
                    (
                        f"{detail['avg_rating']:.2f} / 5"
                        if detail["avg_rating"] is not None
                        else "Not rated"
                    ),
                )

                detail2.metric(
                    "👥 Total Ratings",
                    f"{detail['rating_count']:,}",
                )

                detail3.metric(
                    "🏷️ Genres",
                    str(len(detail["genres"] or [])),
                )

                st.markdown(f"### {detail['title']}")

                genre_names = detail["genres"] or []

                if genre_names:
                    st.markdown(" ".join(
                        f"`{name}`" for name in genre_names
                    ))
                else:
                    st.caption("No genres listed for this movie.")

                graph_data = run_query("""
                    MATCH (m:Movie {movieId: $movie_id})
                    OPTIONAL MATCH (m)-[:IN_GENRE]->(g:Genre)
                    WITH m, collect(DISTINCT g) AS genres
                    OPTIONAL MATCH (u:User)-[r:RATED]->(m)
                    WITH m, genres,
                         collect(DISTINCT {
                             user_id: u.userId,
                             rating: r.rating
                         }) AS ratings
                    RETURN
                        m.movieId AS movie_id,
                        m.title AS title,
                        [g IN genres WHERE g IS NOT NULL |
                            {name: g.name}] AS genres,
                        [x IN ratings
                            WHERE x.user_id IS NOT NULL | x]
                            AS ratings
                """, {"movie_id": movie_id})

                if graph_data:
                    data = graph_data[0]

                    net = Network(
                        height="620px",
                        width="100%",
                        bgcolor="#0B1120",
                        font_color="#F9FAFB",
                        directed=True,
                        cdn_resources="in_line",
                    )

                    net.barnes_hut(
                        gravity=-25000,
                        central_gravity=0.3,
                        spring_length=170,
                        spring_strength=0.02,
                        damping=0.09,
                    )

                    movie_node = f"movie_{data['movie_id']}"

                    net.add_node(
                        movie_node,
                        label=data["title"],
                        title=f"Movie: {data['title']}",
                        color={
                            "background": "#F59E0B",
                            "border": "#FDE68A",
                            "highlight": {
                                "background": "#FBBF24",
                                "border": "#FFFFFF",
                            },
                        },
                        size=34,
                        shape="dot",
                        font={"size": 20, "face": "Arial"},
                    )

                    for genre in data["genres"]:
                        genre_name = genre["name"]
                        genre_node = f"genre_{genre_name}"

                        net.add_node(
                            genre_node,
                            label=genre_name,
                            title=f"Genre: {genre_name}",
                            color="#34D399",
                            size=23,
                            shape="diamond",
                            font={"size": 15},
                        )

                        net.add_edge(
                            movie_node,
                            genre_node,
                            label="IN_GENRE",
                            color="#34D399",
                            arrows="to",
                        )

                    for item in data["ratings"][:50]:
                        user_node = f"user_{item['user_id']}"

                        net.add_node(
                            user_node,
                            label=f"User {item['user_id']}",
                            title=f"Rating: {item['rating']}/5",
                            color="#60A5FA",
                            size=13,
                            shape="dot",
                            font={"size": 11},
                        )

                        net.add_edge(
                            user_node,
                            movie_node,
                            label=str(item["rating"]),
                            color="#52627A",
                            arrows="to",
                            font={"size": 10, "color": "#D1D5DB"},
                        )

                    section_heading(
                        "🕸️ Knowledge Graph",
                        "Drag nodes to explore. Hover over a node or edge "
                        "to inspect its information.",
                    )

                    components.html(
                        net.generate_html(),
                        height=650,
                        scrolling=True,
                    )

                    st.caption(
                        f"Graph shows 1 movie, "
                        f"{len(data['genres'])} genre connection(s), "
                        f"and up to {min(len(data['ratings']), 50)} "
                        f"user rating connection(s)."
                    )

                    with st.expander("About this visualization"):
                        st.write(
                            "Yellow nodes represent movies, green nodes "
                            "represent genres, and blue nodes represent "
                            "users. Edges show genre membership and user "
                            "ratings. The visualization limits user nodes "
                            "to 50 for readability."
                        )

                else:
                    st.info("No graph connections found for this movie.")

            else:
                st.warning("Movie details could not be found.")

except Exception as exc:
    st.error("Could not load the dashboard from Neo4j.")

    st.info(
        "Check your .env credentials, internet connection, "
        "Neo4j Aura status, and graph property names."
    )

    with st.expander("Technical details"):
        st.code(str(exc))

st.divider()

st.markdown(
    '<div class="footer">MovieLens Knowledge Graph · '
    'Python · Streamlit · Neo4j</div>',
    unsafe_allow_html=True,
)
