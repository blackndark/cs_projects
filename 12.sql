SELECT title from movies
JOIN stars ON movies.id = stars.movie_id
JOIN people ON stars.person_id = people.id
WHERE TITLE IN (SELECT title from movies
JOIN stars ON movies.id = stars.movie_id
JOIN people ON stars.person_id = people.id
WHERE name = 'Johnny Depp')
AND name = 'Helena Bonham Carter'