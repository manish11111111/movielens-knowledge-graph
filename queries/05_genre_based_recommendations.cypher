
/*
MovieLens Knowledge Graph
Query 05: Genre-Based Recommendations

Purpose:
Recommend movies that share genres with a target movie.
Only movies with at least 20 ratings are included.
*/

MATCH (target:Movie {title: 'Toy Story (1995)'})
MATCH (target)-[:IN_GENRE]->(g:Genre)<-[:IN_GENRE]-(rec:Movie)
WHERE rec <> target

WITH rec, count(DISTINCT g) AS commonGenres

MATCH (:User)-[r:RATED]->(rec)
WITH rec, commonGenres,
     count(r) AS ratingCount,
     avg(r.rating) AS avgRating
WHERE ratingCount >= 20

RETURN rec.title AS RecommendedMovie,
       commonGenres,
       ratingCount,
       round(avgRating * 100) / 100 AS avgRating
ORDER BY commonGenres DESC,
         avgRating DESC,
         ratingCount DESC
LIMIT 10;
