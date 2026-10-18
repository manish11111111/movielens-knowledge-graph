
/*
MovieLens Knowledge Graph
Query 02: Relationship Overview

Purpose:
Count each relationship type in the graph.
*/

MATCH ()-[r]->()
RETURN type(r) AS Relationship,
       count(*) AS Total
ORDER BY Total DESC;
