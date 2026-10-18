
/*
MovieLens Knowledge Graph
Query 06: Collaborative Recommendations

Purpose:
Find movies rated highly by users who also rated
the target movie highly.
*/

MATCH (target:Movie {title: 'Toy Story (1995)'})
      <-[:RATED]-(u:User)-[r2:RATED]->(rec:Movie)
WHERE r2.rating >= 4
  AND rec <> target

WITH rec,
     count(DISTINCT u) AS sharedFans,
     avg(r2.rating) AS avgRating
WHERE sharedFans >= 5

RETURN rec.title AS RecommendedMovie,
       sharedFans,
       round(avgRating * 100) / 100 AS avgRating
ORDER BY sharedFans DESC, avgRating DESC
LIMIT 10;
