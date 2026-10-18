
/*
MovieLens Knowledge Graph
Query 07: Genre Analytics

Purpose:
Analyze movie counts, rating volume, and average
ratings for each genre.
*/

MATCH (m:Movie)-[:IN_GENRE]->(g:Genre)
OPTIONAL MATCH (m)<-[r:RATED]-(:User)

WITH g,
     count(DISTINCT m) AS movieCount,
     count(r) AS totalRatings,
     avg(r.rating) AS avgRating

RETURN g.name AS Genre,
       movieCount,
       totalRatings,
       round(avgRating * 100) / 100 AS avgRating
ORDER BY totalRatings DESC;
