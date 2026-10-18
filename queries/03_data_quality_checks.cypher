
/*
MovieLens Knowledge Graph
Query 03: Data Quality Checks

Purpose:
Identify missing data and inactive entities.
*/

CALL {
    MATCH (m:Movie)
    WHERE m.title IS NULL OR m.movieId IS NULL
    RETURN count(m) AS moviesMissingData
}

CALL {
    MATCH (u:User)
    WHERE u.userId IS NULL
    RETURN count(u) AS usersMissingId
}

CALL {
    MATCH (m:Movie)
    WHERE NOT (m)-[:IN_GENRE]->(:Genre)
    RETURN count(m) AS moviesWithoutGenres
}

CALL {
    MATCH (u:User)
    WHERE NOT (u)-[:RATED]->(:Movie)
      AND NOT (u)-[:TAGGED]->(:Movie)
    RETURN count(u) AS usersWithoutActivity
}

RETURN moviesMissingData,
       usersMissingId,
       moviesWithoutGenres,
       usersWithoutActivity;
