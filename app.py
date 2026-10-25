import os

import certifi
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from neo4j import GraphDatabase
from pyvis.network import Network

st.set_page_config(
    page_title="MovieLens · Graph Explorer",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_dotenv()
os.environ.setdefault("SSL_CERT_FILE", certifi.where())

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {
    --bg-void: #08080c;
    --bg-base: #0d0d14;
    --bg-elevated: #13131d;
    --bg-card: #171722;
    --bg-card-hover: #1e1e2d;
    --bg-input: #1a1a26;
    --text-primary: #f5f5f7;
    --text-secondary: #a1a1b5;
    --text-tertiary: #6b6b85;
    --border-subtle: rgba(255,255,255,0.06);
    --border-default: rgba(255,255,255,0.10);
    --border-strong: rgba(255,255,255,0.16);
    --accent: #ff5c5c;
    --accent-glow: rgba(255,92,92,0.35);
    --accent-soft: rgba(255,92,92,0.12);
    --accent-2: #ffb347;
    --gold: #ffd93d;
    --gold-soft: rgba(255,217,61,0.12);
    --success: #34d399;
    --success-soft: rgba(52,211,153,0.12);
    --violet: #a78bfa;
    --violet-soft: rgba(167,139,250,0.12);
    --blue: #60a5fa;
    --blue-soft: rgba(96,165,250,0.12);
}

html, body, [class*="css"], .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--text-secondary);
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

.stApp {
    background: var(--bg-void);
    background-image:
        radial-gradient(ellipse 80% 50% at 50% -20%, rgba(255,92,92,0.10), transparent),
        radial-gradient(ellipse 60% 40% at 100% 0%, rgba(167,139,250,0.06), transparent);
}

header[data-testid="stHeader"] {
    background: transparent !important;
    z-index: 10 !important;
}

.block-container {
    padding-top: 1.2rem !important;
    padding-bottom: 4rem !important;
    max-width: 1400px;
}

#MainMenu, footer { visibility: hidden; }

::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb {
    background: var(--bg-card-hover);
    border-radius: 99px;
    border: 2px solid var(--bg-base);
}
::-webkit-scrollbar-thumb:hover { background: var(--text-tertiary); }

.hero-wrap {
    position: relative;
    border-radius: 24px;
    padding: 2.6rem 2.8rem 2.2rem;
    margin-bottom: 1.8rem;
    overflow: hidden;
    background: linear-gradient(135deg, #151520 0%, #0f0f1a 100%);
    border: 1px solid var(--border-subtle);
}

.hero-wrap::before {
    content: '';
    position: absolute;
    top: -50%; left: -10%;
    width: 600px; height: 600px;
    background: radial-gradient(circle, var(--accent-glow) 0%, transparent 60%);
    filter: blur(60px);
    pointer-events: none;
}

.hero-wrap::after {
    content: '';
    position: absolute;
    bottom: -60%; right: -5%;
    width: 500px; height: 500px;
    background: radial-gradient(circle, rgba(167,139,250,0.18) 0%, transparent 60%);
    filter: blur(70px);
    pointer-events: none;
}

.hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    background: var(--accent-soft);
    border: 1px solid rgba(255,92,92,0.25);
    color: var(--accent);
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    border-radius: 999px;
    padding: 0.4rem 0.95rem;
    margin-bottom: 1.2rem;
}

.hero-eyebrow .dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--accent);
    box-shadow: 0 0 8px var(--accent);
}

.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    color: var(--text-primary);
    font-size: 2.9rem;
    font-weight: 700;
    letter-spacing: -0.045em;
    line-height: 1.05;
    margin: 0 0 0.8rem 0;
}

.hero-title .gradient {
    background: linear-gradient(135deg, #ff5c5c 0%, #ffb347 50%, #a78bfa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-sub {
    color: var(--text-secondary);
    font-size: 1.02rem;
    line-height: 1.6;
    max-width: 680px;
    margin: 0;
    font-weight: 400;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 1.8rem;
}

.stat-card {
    position: relative;
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 18px;
    padding: 1.4rem 1.5rem;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.stat-card:hover {
    border-color: var(--border-strong);
    background: var(--bg-card-hover);
    transform: translateY(-3px);
}

.stat-icon {
    width: 38px; height: 38px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.05rem;
    margin-bottom: 1rem;
}

.stat-icon.red { background: var(--accent-soft); border: 1px solid rgba(255,92,92,0.2); }
.stat-icon.blue { background: var(--blue-soft); border: 1px solid rgba(96,165,250,0.2); }
.stat-icon.gold { background: var(--gold-soft); border: 1px solid rgba(255,217,61,0.2); }
.stat-icon.success { background: var(--success-soft); border: 1px solid rgba(52,211,153,0.2); }

.stat-label {
    color: var(--text-tertiary);
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.4rem;
}

.stat-value {
    font-family: 'JetBrains Mono', monospace;
    color: var(--text-primary);
    font-size: 2rem;
    font-weight: 700;
    line-height: 1;
    letter-spacing: -0.02em;
    margin-bottom: 0.35rem;
}

.stat-sub { color: var(--text-tertiary); font-size: 0.78rem; }

.section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--text-primary);
    letter-spacing: -0.025em;
    margin: 2rem 0 0.5rem 0;
    display: flex;
    align-items: center;
    gap: 0.7rem;
}

.section-title .accent-line {
    width: 3px;
    height: 24px;
    background: linear-gradient(180deg, var(--accent), var(--accent-2));
    border-radius: 2px;
}

.section-desc {
    color: var(--text-tertiary);
    font-size: 0.92rem;
    line-height: 1.6;
    margin-bottom: 1.5rem;
}

div[data-testid="stForm"] {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 16px;
    padding: 1.4rem 1.5rem;
}

div[data-testid="stForm"] label {
    color: var(--text-secondary) !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em !important;
}

[data-baseweb="input"] > div,
[data-baseweb="select"] > div {
    background: var(--bg-input) !important;
    border-color: var(--border-default) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    font-size: 0.88rem !important;
}

[data-baseweb="input"] > div:hover,
[data-baseweb="select"] > div:hover {
    border-color: var(--border-strong) !important;
}

[data-baseweb="input"] input {
    color: var(--text-primary) !important;
}

[data-baseweb="select"] [role="listbox"] {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-default) !important;
}

[data-baseweb="popover"] {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-default) !important;
    border-radius: 10px !important;
}

div.stButton > button[kind="primary"],
div.stFormSubmitButton > button[kind="primary"] {
    background: linear-gradient(135deg, #ff5c5c 0%, #ff7b4d 100%) !important;
    color: #ffffff !important;
    border: none !important;
    font-weight: 700 !important;
    font-size: 0.92rem !important;
    border-radius: 12px !important;
    min-height: 46px !important;
    box-shadow: 0 8px 32px -8px var(--accent-glow) !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

div.stButton > button[kind="primary"]:hover,
div.stFormSubmitButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 14px 44px -8px var(--accent-glow) !important;
}

div.stButton > button:not([kind="primary"]) {
    background: var(--bg-card) !important;
    color: var(--text-secondary) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
}

div.stButton > button:not([kind="primary"]):hover {
    background: var(--bg-card-hover) !important;
    color: var(--text-primary) !important;
    border-color: var(--border-default) !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid var(--border-subtle) !important;
    border-radius: 12px !important;
    overflow: hidden;
}

[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 12px !important;
    overflow: hidden;
}

[data-testid="stExpander"] summary {
    color: var(--text-secondary) !important;
    font-size: 0.86rem !important;
    font-weight: 500 !important;
}

[data-testid="stExpander"] summary:hover {
    color: var(--text-primary) !important;
}

[data-testid="stAlert"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 12px !important;
    color: var(--text-secondary) !important;
    font-size: 0.86rem !important;
}

[data-testid="stSidebar"] {
    background: var(--bg-base) !important;
    border-right: 1px solid var(--border-subtle) !important;
}

[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }

.side-brand {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding-bottom: 0.3rem;
}

.side-brand .logo {
    width: 36px; height: 36px;
    border-radius: 10px;
    background: linear-gradient(135deg, #ff5c5c, #ffb347);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    box-shadow: 0 4px 16px var(--accent-glow);
}

.side-brand .name {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.02em;
}

.side-brand .tag {
    font-size: 0.7rem;
    color: var(--text-tertiary);
    font-weight: 500;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-top: 2px;
}

.side-section {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--text-tertiary);
    margin: 1.1rem 0 0.5rem 0;
}

.nav-item {
    display: flex;
    align-items: center;
    gap: 0.55rem;
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 9px;
    padding: 0.55rem 0.75rem;
    font-size: 0.82rem;
    font-weight: 500;
    color: var(--text-secondary);
    margin-bottom: 0.4rem;
    transition: all 0.2s ease;
}

.nav-item.active {
    background: var(--accent-soft);
    border-color: rgba(255,92,92,0.3);
    color: var(--accent);
    font-weight: 600;
}

.legend-item {
    display: flex;
    align-items: center;
    gap: 0.55rem;
    font-size: 0.8rem;
    color: var(--text-secondary);
    padding: 0.35rem 0;
}

.legend-dot {
    width: 12px; height: 12px;
    border-radius: 50%;
    flex-shrink: 0;
}

.legend-dot.movie {
    background: #F59E0B;
    box-shadow: 0 0 10px rgba(245,158,11,0.6);
}

.legend-dot.genre {
    background: #34D399;
    border-radius: 3px;
    transform: rotate(45deg);
    box-shadow: 0 0 10px rgba(52,211,153,0.5);
}

.legend-dot.user {
    background: #60A5FA;
    box-shadow: 0 0 10px rgba(96,165,250,0.5);
}

[data-testid="stSidebar"] hr {
    border-color: var(--border-subtle) !important;
    margin: 0.9rem 0 !important;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    margin-bottom: 0;
}

[data-testid="stSidebarHeader"] {
    height: 2.2rem;
    min-height: 0;
    padding: 0.3rem 1rem 0 1rem;
}

.movie-panel {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 18px;
    padding: 1.6rem 1.8rem;
    margin: 1rem 0;
    position: relative;
}

.movie-panel::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    background: linear-gradient(180deg, var(--gold), var(--accent));
    border-radius: 3px 0 0 3px;
}

.movie-title-lg {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--text-primary);
    letter-spacing: -0.02em;
    margin: 0 0 1rem 0;
}

.detail-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-bottom: 1.2rem;
}

.detail-cell {
    background: var(--bg-input);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 0.9rem 1rem;
}

.detail-label {
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-tertiary);
    font-weight: 700;
    margin-bottom: 0.3rem;
}

.detail-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.01em;
}

.genre-tag {
    display: inline-block;
    font-size: 0.73rem;
    font-weight: 500;
    color: var(--success);
    background: var(--success-soft);
    border: 1px solid rgba(52,211,153,0.25);
    border-radius: 999px;
    padding: 0.22rem 0.7rem;
    margin: 0.2rem 0.25rem 0.2rem 0;
}

.app-footer {
    margin-top: 3rem;
    padding: 1.8rem 0 0;
    border-top: 1px solid var(--border-subtle);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 1rem;
    color: var(--text-tertiary);
    font-size: 0.78rem;
}

.app-footer .brand {
    display: flex;
    align-items: center;
    gap: 0.55rem;
    color: var(--text-secondary);
}

.app-footer .brand strong {
    color: var(--text-primary);
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
}

.app-footer .tech {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.02em;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-wrap">
    <div class="hero-eyebrow">
        <span class="dot"></span>
        Neo4j Knowledge Graph
    </div>
    <h1 class="hero-title">
        Explore movies as a <span class="gradient">living graph</span>.
    </h1>
    <p class="hero-sub">
        Search titles, inspect genres and community ratings, then visualize how
        everything connects — all pulled live from your Neo4j database.
    </p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(
        '<div class="side-brand">'
        '<div class="logo">🎬</div>'
        '<div><div class="name">MovieLens</div>'
        '<div class="tag">Graph Explorer</div></div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.divider()

    st.markdown('<div class="side-section">Navigation</div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-item active">🔎 Movie Explorer</div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-item">🕸️ Knowledge Graph</div>', unsafe_allow_html=True)

    st.markdown('<div class="side-section">Graph Legend</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="legend-item"><span class="legend-dot movie"></span>Movie</div>'
        '<div class="legend-item"><span class="legend-dot genre"></span>Genre</div>'
        '<div class="legend-item"><span class="legend-dot user"></span>User</div>',
        unsafe_allow_html=True,
    )

    st.divider()
    st.caption("Powered by Neo4j · Streamlit · Python")


for key, default in [
    ("movies", None),
    ("show_connections", False),
    ("selected_movie_id", None),
    ("search_text", ""),
    ("selected_genre", "All genres"),
]:
    if key not in st.session_state:
        st.session_state[key] = default


@st.cache_resource(show_spinner=False)
def get_driver():
    uri = os.getenv("NEO4J_URI")
    username = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")

    if not all([uri, username, password]):
        raise ValueError("Missing Neo4j credentials. Check your local .env file.")

    return GraphDatabase.driver(uri, auth=(username, password))


def run_query(query, parameters=None):
    with get_driver().session() as session:
        result = session.run(query, parameters or {})
        return [record.data() for record in result]


def section_heading(title, subtitle=""):
    st.markdown(
        f'<div class="section-title"><span class="accent-line"></span>{title}</div>',
        unsafe_allow_html=True,
    )
    if subtitle:
        st.markdown(f'<div class="section-desc">{subtitle}</div>', unsafe_allow_html=True)


@st.cache_data(ttl=600, show_spinner=False)
def fetch_stats():
    result = run_query("""
        MATCH (m:Movie)
        WITH count(m) AS movies
        MATCH (u:User)
        WITH movies, count(u) AS users
        MATCH ()-[r:RATED]->()
        WITH movies, users, count(r) AS ratings
        MATCH (g:Genre)
        RETURN movies, users, ratings, count(g) AS genres
    """)
    return result[0] if result else None


@st.cache_data(ttl=600, show_spinner=False)
def fetch_genres():
    result = run_query("""
        MATCH (g:Genre)
        RETURN g.name AS genre
        ORDER BY genre
    """)
    return [row["genre"] for row in result if row.get("genre")]


@st.cache_data(ttl=300, show_spinner=False)
def search_movies(title, genre):
    return run_query("""
        MATCH (m:Movie)
        OPTIONAL MATCH (m)-[:IN_GENRE]->(g:Genre)
        WITH m, collect(DISTINCT g.name) AS genres
        WHERE toLower(m.title) CONTAINS toLower($title)
          AND ($genre = 'All genres' OR $genre IN genres)
        OPTIONAL MATCH (u:User)-[r:RATED]->(m)
        RETURN
            m.movieId AS movie_id,
            m.title AS title,
            genres,
            round(avg(r.rating) * 100) / 100.0 AS avg_rating,
            count(r) AS rating_count
        ORDER BY rating_count DESC, title
        LIMIT 100
    """, {"title": title.strip(), "genre": genre})


@st.cache_data(ttl=300, show_spinner=False)
def fetch_movie_details(movie_id):
    return run_query("""
        MATCH (m:Movie {movieId: $movie_id})
        OPTIONAL MATCH (m)-[:IN_GENRE]->(g:Genre)
        WITH m, collect(DISTINCT g.name) AS genres
        OPTIONAL MATCH (u:User)-[r:RATED]->(m)
        RETURN
            m.title AS title,
            genres,
            round(avg(r.rating) * 100) / 100.0 AS avg_rating,
            count(r) AS rating_count
    """, {"movie_id": movie_id})


@st.cache_data(ttl=300, show_spinner=False)
def fetch_graph_data(movie_id):
    return run_query("""
        MATCH (m:Movie {movieId: $movie_id})
        OPTIONAL MATCH (m)-[:IN_GENRE]->(g:Genre)
        WITH m, collect(DISTINCT g) AS genres
        OPTIONAL MATCH (u:User)-[r:RATED]->(m)
        WITH m, genres,
             collect(DISTINCT {user_id: u.userId, rating: r.rating}) AS ratings
        RETURN
            m.movieId AS movie_id,
            m.title AS title,
            [g IN genres WHERE g IS NOT NULL | {name: g.name}] AS genres,
            [x IN ratings WHERE x.user_id IS NOT NULL | x] AS ratings
    """, {"movie_id": movie_id})


try:
    with st.spinner("Connecting to Neo4j…"):
        stats = fetch_stats()

    if not stats:
        st.warning("No statistics returned from Neo4j.")
        st.stop()

    st.markdown(f"""
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-icon gold">🎞️</div>
            <div class="stat-label">Movies</div>
            <div class="stat-value">{stats['movies']:,}</div>
            <div class="stat-sub">in the catalog</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon blue">👥</div>
            <div class="stat-label">Users</div>
            <div class="stat-value">{stats['users']:,}</div>
            <div class="stat-sub">community viewers</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon red">⭐</div>
            <div class="stat-label">Ratings</div>
            <div class="stat-value">{stats['ratings']:,}</div>
            <div class="stat-sub">verified reviews</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon success">🏷️</div>
            <div class="stat-label">Genres</div>
            <div class="stat-value">{stats['genres']:,}</div>
            <div class="stat-sub">unique categories</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    section_heading(
        "🔎 Movie Explorer",
        "Search the catalogue and filter movies by genre.",
    )

    genre_options = fetch_genres()

    with st.form("movie_search"):
        search_text = st.text_input(
            "Movie title",
            value=st.session_state["search_text"],
            placeholder="Try Toy Story, Batman, or Matrix…",
        )

        full_options = ["All genres"] + genre_options
        current_genre = st.session_state["selected_genre"]
        default_idx = full_options.index(current_genre) if current_genre in full_options else 0

        selected_genre = st.selectbox("Genre", full_options, index=default_idx)

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
        st.session_state["movies"] = search_movies(search_text, selected_genre)

    movies = st.session_state["movies"]

    if movies is None:
        st.info("Search for a movie to get started.")

    elif not movies:
        st.warning("No matching movies found. Try another title or genre.")

    else:
        section_heading(
            "Search Results",
            f"{len(movies)} matching movie(s) found.",
        )

        df = pd.DataFrame(movies)
        df["genres"] = df["genres"].apply(
            lambda items: ", ".join(i for i in (items or []) if i)
        )
        df["avg_rating"] = df["avg_rating"].apply(
            lambda v: round(v, 2) if v is not None else "N/A"
        )
        df = df.rename(columns={
            "movie_id": "Movie ID",
            "title": "Movie Title",
            "genres": "Genres",
            "avg_rating": "Avg Rating",
            "rating_count": "Ratings",
        })

        st.dataframe(df, use_container_width=True, hide_index=True)

        section_heading(
            "🎥 Movie Details",
            "Choose a result to inspect its knowledge graph.",
        )

        movie_options = {
            f"{row['title']} (ID: {row['movie_id']})": row["movie_id"]
            for row in movies
        }
        option_labels = list(movie_options.keys())
        movie_ids = list(movie_options.values())
        current_id = st.session_state["selected_movie_id"]
        default_index = movie_ids.index(current_id) if current_id in movie_ids else 0

        chosen_movie = st.selectbox(
            "Select a movie",
            option_labels,
            index=default_index,
            key="movie_details",
        )

        if st.button("🕸️ View Movie Connections", type="primary", use_container_width=True):
            st.session_state["selected_movie_id"] = movie_options[chosen_movie]
            st.session_state["show_connections"] = True

        if st.session_state["show_connections"]:
            movie_id = st.session_state["selected_movie_id"]
            with st.spinner("Loading movie details and graph…"):
                details = fetch_movie_details(movie_id)
                graph_data = fetch_graph_data(movie_id)

            if details:
                detail = details[0]
                avg = (
                    f"{detail['avg_rating']:.2f} / 5"
                    if detail["avg_rating"] is not None
                    else "Not rated"
                )
                genre_names = detail["genres"] or []
                genre_tags = "".join(
                    f'<span class="genre-tag">{g}</span>' for g in genre_names
                ) or '<span style="color:var(--text-tertiary);font-size:0.85rem;">No genres listed</span>'

                st.markdown(f"""
                <div class="movie-panel">
                    <div class="movie-title-lg">{detail['title']}</div>
                    <div class="detail-grid">
                        <div class="detail-cell">
                            <div class="detail-label">Average Rating</div>
                            <div class="detail-value">{avg}</div>
                        </div>
                        <div class="detail-cell">
                            <div class="detail-label">Total Ratings</div>
                            <div class="detail-value">{detail['rating_count']:,}</div>
                        </div>
                        <div class="detail-cell">
                            <div class="detail-label">Genres</div>
                            <div class="detail-value">{len(genre_names)}</div>
                        </div>
                    </div>
                    <div>{genre_tags}</div>
                </div>
                """, unsafe_allow_html=True)

                if graph_data:
                    data = graph_data[0]

                    net = Network(
                        height="620px",
                        width="100%",
                        bgcolor="#08080c",
                        font_color="#f5f5f7",
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
                            "highlight": {"background": "#FBBF24", "border": "#FFFFFF"},
                        },
                        size=34,
                        shape="dot",
                        font={"size": 20, "face": "Inter", "color": "#f5f5f7"},
                    )

                    for genre in data["genres"]:
                        genre_name = genre["name"]
                        genre_node = f"genre_{genre_name}"
                        net.add_node(
                            genre_node,
                            label=genre_name,
                            title=f"Genre: {genre_name}",
                            color={
                                "background": "#34D399",
                                "border": "#6EE7B7",
                                "highlight": {"background": "#6EE7B7", "border": "#FFFFFF"},
                            },
                            size=23,
                            shape="diamond",
                            font={"size": 15, "face": "Inter", "color": "#f5f5f7"},
                        )
                        net.add_edge(movie_node, genre_node, label="IN_GENRE", color="#34D399", arrows="to")

                    for item in data["ratings"][:50]:
                        user_node = f"user_{item['user_id']}"
                        net.add_node(
                            user_node,
                            label=f"User {item['user_id']}",
                            title=f"Rating: {item['rating']}/5",
                            color={
                                "background": "#60A5FA",
                                "border": "#93C5FD",
                                "highlight": {"background": "#93C5FD", "border": "#FFFFFF"},
                            },
                            size=13,
                            shape="dot",
                            font={"size": 11, "face": "Inter", "color": "#f5f5f7"},
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
                        "Drag nodes to explore. Hover over a node or edge to inspect its information.",
                    )

                    components.html(net.generate_html(), height=650, scrolling=True)

                    st.caption(
                        f"Graph shows 1 movie, {len(data['genres'])} genre connection(s), "
                        f"and up to {min(len(data['ratings']), 50)} user rating connection(s)."
                    )

                    with st.expander("About this visualization"):
                        st.write(
                            "Yellow nodes represent movies, green diamonds represent genres, "
                            "and blue nodes represent users. Edges show genre membership and "
                            "user ratings. The visualization limits user nodes to 50 for readability."
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

st.markdown("""
<div class="app-footer">
    <div class="brand">
        <div class="stat-icon red" style="width:28px;height:28px;font-size:0.8rem;margin:0;">🎬</div>
        <span>MovieLens Knowledge Graph Explorer</span>
    </div>
    <div class="tech">Python · Streamlit · Neo4j</div>
</div>
""", unsafe_allow_html=True)