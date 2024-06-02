CREATE TABLE genres
(
    genreId int NOT NULL AUTO_INCREMENT,
    genre nchar(50) NOT NULL,
    PRIMARY KEY (genreId)
);

CREATE TABLE movies
(
    movieId int NOT NULL AUTO_INCREMENT,
    name nchar(50) NOT NULL,
    PRIMARY KEY (movieId)
);

CREATE TABLE movie_genres
(
 movieId int NOT NULL,
 genreId int NOT NULL,
 INDEX (movieId),
 INDEX (genreId),
 FOREIGN KEY (movieId) REFERENCES movies (movieId),
 FOREIGN KEY (genreId) REFERENCES genres (genreId)
);

INSERT INTO movies (name) VALUES ('Rambo'), ('First Blood'), ('Citizen Kane');

INSERT INTO genres (genre) VALUES ('Drama'), ('Action'), ('War');

INSERT INTO movie_genres (movieId, genreId) VALUES (1,2), (2,2), (3,1), (1,3);

SELECT movies.movieId, movies.title, genres.genreId, genres.genre FROM movies
JOIN movie_genres ON (movie_genres.movieId = movies.movieId)
JOIN genres ON (genres.genreId = movie_genres.genreId)
WHERE genres.genre='Action';


SELECT movies.title, genres.genre FROM movies
JOIN movie_genres ON (movie_genres.movieId = movies.movieId)
JOIN genres ON (genres.genreId = movie_genres.genreId)
WHERE genres.genre='Sci-Fi';

SELECT movies.title, genres.genre FROM movies
JOIN movie_genres ON (movie_genres.movieId = movies.movieId)
JOIN genres ON (genres.genreId = movie_genres.genreId);

SELECT genres.genre
FROM movies
JOIN movie_genres ON (movie_genres.movieId = movies.movieId)
JOIN genres ON (genres.genreId = movie_genres.genreId)
WHERE movies.name='Rambo';

ALTER TABLE movies
ADD rating decimal(3,1);

DESCRIBE movies;

UPDATE movies SET rating=7.5 WHERE name='Rambo';

SELECT movies.title
FROM movies
JOIN movie_genres ON (movie_genres.movieId = movies.movieId)
JOIN genres ON (genres.genreId = movie_genres.genreId)
WHERE movies.movieID in (SELECT * FROM dave) AND
genres.genre='Action' AND movies.rating>7;

SELECT * FROM genres ORDER BY genre LIMIT 2 OFFSET 1;

SELECT COUNT(*) FROM genres WHERE genreId>1;


SELECT *
FROM movies
JOIN movie_genres ON (movie_genres.movieId = movies.movieId)
JOIN genres ON (genres.genreId = movie_genres.genreId)
WHERE movies.rating>7;


movies WHERE movieID NOT IN (SELECT * FROM dave_watched) and WHERE movieID NOT IN (SELECT * FROM dave_wants)