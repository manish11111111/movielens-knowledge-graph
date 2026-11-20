import os
import sys
import time
from urllib.parse import urlparse

import requests
from neo4j import GraphDatabase

API = "https://api.neo4j.io"

uri = os.environ["NEO4J_URI"]
user = os.environ["NEO4J_USERNAME"]
password = os.environ["NEO4J_PASSWORD"]
client_id = os.environ["AURA_CLIENT_ID"]
client_secret = os.environ["AURA_CLIENT_SECRET"]

instance_id = urlparse(uri).hostname.split(".")[0]
print("Instance ID:", instance_id)

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

status = get_status()
print("Current status:", status)

if status == "paused":
    r = requests.post(f"{API}/v1/instances/{instance_id}/resume", headers=headers, timeout=30)
    r.raise_for_status()
    print("Resume requested.")

for _ in range(30):
    status = get_status()
    print("Status:", status)
    if status == "running":
        break
    time.sleep(30)
else:
    sys.exit("Instance did not reach 'running' in time.")

with GraphDatabase.driver(uri, auth=(user, password)) as driver:
    driver.verify_connectivity()
    with driver.session() as session:
        count = session.run("MATCH (n) RETURN count(n) AS c").single()["c"]
        print(f"Neo4j is alive. Node count: {count}")