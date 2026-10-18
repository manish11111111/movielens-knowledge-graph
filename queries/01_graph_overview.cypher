
/*
MovieLens Knowledge Graph
Query 01: Graph Overview

Purpose:
Summarize the number of nodes and relationships
stored in the Neo4j database.
*/

MATCH (n)
UNWIND labels(n) AS NodeType
WITH NodeType, count(*) AS Total
RETURN NodeType, Total
ORDER BY Total DESC;
