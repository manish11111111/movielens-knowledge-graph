import os
import sys
import time
import tomllib
from pathlib import Path
from urllib.parse import urlparse

import requests
from neo4j import GraphDatabase

API = "https://api.neo4j.io"
KEYS = [
    "NEO4J_URI",
    "NEO4J_USERNAME",
    "NEO4J_PASSWORD",
    "AURA_CLIENT_ID",
    "AURA_CLIENT_SECRET",
]


def load_config():
    cfg = {}

    # 1. .streamlit/secrets.toml (local)
    p = Path(".streamlit/secrets.toml")
    if p.exists():
        data = tomllib.loads(p.read_text(encoding="utf-8"))
        cfg.update({k: str(data[k]) for k in KEYS if k in data})

    # 2. .env (local)
    p = Path(".env")
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip().strip('"').strip("'")
                if k in KEYS and v:
                    cfg[k] = v

    # 3. Environment variables (GitHub Actions), sabbhanda mathi
    for k in KEYS:
        if os.environ.get(k):
            cfg[k] = os.environ[k]

    missing = [k for k in KEYS if not cfg.get(k)]
    if missing:
        sys.exit(f"Missing config: {missing}")
    return cfg


cfg = load_config()
uri = cfg["NEO4J_URI"].strip()
user = cfg["NEO4J_USERNAME"].strip()
password = cfg["NEO4J_PASSWORD"].strip()
client_id = cfg["AURA_CLIENT_ID"].strip()
client_secret = cfg["AURA_CLIENT_SECRET"].strip()

instance_id = urlparse(uri).hostname.split(".")[0]
print("Instance ID:", instance_id)

# Aura API token
r = requests.post(
    f"{API}/oauth/token",
    auth=(client_id, client_secret),
    data={"grant_type": "client_credentials"},
    timeout=30,
)
r.raise_for_status()
headers = {"Authorization": f"Bearer {r.json()['access_token']}"}


def get_status():
    r = requests.get(f"{API}/v1/instances/{instance_id}", headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()["data"]["status"]


# Paused bhaye resume garne
status = get_status()
print("Current status:", status)

if status == "paused":
    r = requests.post(
        f"{API}/v1/instances/{instance_id}/resume", headers=headers, timeout=30
    )
    r.raise_for_status()
    print("Resume requested.")

# Running hune samma parkhane (max ~15 minute)
for _ in range(30):
    status = get_status()
    print("Status:", status)
    if status == "running":
        break
    time.sleep(30)
else:
    sys.exit("Instance did not reach 'running' in time.")

# Ping
with GraphDatabase.driver(uri, auth=(user, password)) as driver:
    driver.verify_connectivity()
    with driver.session() as session:
        count = session.run("MATCH (n) RETURN count(n) AS c").single()["c"]
        print(f"Neo4j is alive. Node count: {count}")