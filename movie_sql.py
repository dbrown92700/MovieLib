import mysql.connector
from movie import Movie
import logging
logger = logging.getLogger(__name__)


movie_table = ('(movieId nchar(20) NOT NULL,'
               ' file nchar(255) NOT NULL,'
               ' directoryId nchar(255) NOT NULL,'
               ' title nchar(255) NOT NULL,'
               ' year smallint,'
               ' rating decimal(3,1),'
               ' plot varchar(1000),'
               ' top250rank smallint,'
               ' coverUrl nchar(255),'
               ' PRIMARY KEY (movieId)'
               ')')
genre_table = ('(genreId smallint NOT NULL AUTO_INCREMENT,'
               ' genre nchar(50) NOT NULL,'
               ' PRIMARY KEY (genreId)'
               ')')
movie_genres = ('(movieId nchar(20) NOT NULL,'
                ' genreId smallint NOT NULL,'
                ' INDEX (movieId), INDEX (genreId),'
                ' FOREIGN KEY (movieId) REFERENCES movies (movieId),'
                ' FOREIGN KEY (genreId) REFERENCES genres (genreId)'
                ')')


class DataBase:

    def __init__(self, server: str, user: str, password: str, database: str):

        self.cnx = mysql.connector.connect(user=user, password=password, host=server)
        self.cursor = self.cnx.cursor()
        self.cursor.execute('SET autocommit=1;')
        try:
            self.cursor.execute(f'USE {database};')
        except mysql.connector.Error:
            self.cursor.execute(f'CREATE DATABASE {database};')
            logger.info(f'Created database {database}')
            self.cursor.execute(f'USE {database};')
            self.cursor.execute(f'CREATE TABLE movies {movie_table};')
            logger.info(f'Created table movies')
            self.cursor.execute(f'CREATE TABLE genres {genre_table};')
            logger.info(f'Created table genres')
            self.cursor.execute(f'CREATE TABLE movie_genres {movie_genres};')
            logger.info(f'Created table movie_genres')
        self.cursor.execute(f'SELECT * FROM genres;')
        genres = self.cursor.fetchall()
        self.genre_dict = {}
        for g in genres:
            self.genre_dict[g[1]] = g[0]

    def close(self):
        self.cnx.close()

    def add_genre(self, genre):

        self.cursor.execute(f'INSERT INTO genres (genre) VALUES ("{genre}");')
        self.cnx.commit()
        self.cursor.execute(f'SELECT genreId FROM genres WHERE genre="{genre}";')
        genre_id = self.cursor.fetchall()[0][0]
        self.genre_dict[genre] = genre_id

        return genre_id

    def insert_movie(self, movie: Movie):

        movie_search = self.movie_list(imdb_id=movie.imdb_id)[0]
        if movie_search:
            found_movie = self.db_to_dict(movie_search)[0]
            logger.info(f'Duplicate: File: {movie.directory}/{movie.filename}\n'
                        f'   Database: {found_movie["directoryId"]}/{found_movie["file"]}')
            return {'status': 'duplicate'}
        plot = movie.imdb_data['plot'][0].replace('"', "'")
        command = f'INSERT INTO movies (movieId, file, directoryId, title, year, rating, plot, top250rank, coverUrl) ' \
                  f'VALUES ("{movie.imdb_id}", "{movie.filename}", "{movie.directory}", ' \
                  f'"{movie.imdb_data["title"]}", "{movie.imdb_data["year"]}", "{movie.imdb_data["rating"]}", ' \
                  f'"{plot}", "{movie.imdb_data["top250"]}", "{movie.imdb_data["cover url"]}");'
        print(command)

        self.cursor.execute(command)
        self.cnx.commit()
        for genre in movie.imdb_data['genres']:
            if genre not in self.genre_dict:
                self.add_genre(genre)
            command = f'INSERT INTO movie_genres (movieId, genreId) VALUES ("{movie.imdb_id}", {self.genre_dict[genre]});'
            self.cursor.execute(command)
            self.cnx.commit()
        logger.info(f'Added to database: {movie.filename} : {movie.imdb_data["title"]}')

    def movie_list(self, imdb_id='', name='', genre='', rating=-1.1, year=0, top250=False, page=1, pagesize=10,
                   sort='title', direction='ASC'):
        # Returns a list of movies using the filters specified
        movie_filter = []
        if imdb_id:
            movie_filter.append(f'movies.movieId="{imdb_id}"')
        if name:
            movie_filter.append(f'movies.title LIKE "%{name}%"')
        if rating > 0:
            movie_filter.append(f'movies.rating>{rating}')
        if year > 0:
            movie_filter.append(f'movies.year={year}')
        if top250:
            movie_filter.append(f'movies.top250rank<300')
        if genre:
            movie_filter.append(f'genre="{genre}"')

        if genre:
            command = (f' FROM movies '
                       f'JOIN movie_genres ON(movie_genres.movieId = movies.movieId) '
                       f'JOIN genres ON(genres.genreId = movie_genres.genreId) '
                       f'WHERE {" AND ".join(movie_filter)}')
        elif movie_filter:
            command = f' FROM movies WHERE {" AND ".join(movie_filter)}'
        else:
            command = ' FROM movies'
        self.cursor.execute(f'SELECT * {command} ORDER BY {sort} {direction} LIMIT {pagesize} OFFSET {(page-1) * pagesize};')
        movies = self.cursor.fetchall()
        self.cursor.execute('SELECT COUNT(*)' + command)
        movie_count = self.cursor.fetchall()[0][0]

        return movies, movie_count

    def movie_genres(self, movie_id):
        # Returns a list of genres for a given movie ID

        self.cursor.execute(f'SELECT genreId FROM movie_genres WHERE movieId={movie_id};')
        genres = self.cursor.fetchall()
        genre_list = []
        for g in [x[0] for x in genres]:
            genre = list(self.genre_dict.keys())[list(self.genre_dict.values()).index(g)]
            genre_list.append(genre)

        return genre_list

    def files(self):

        files = {}
        self.cursor.execute(f'SELECT * FROM movies;')
        all_movies = self.db_to_dict(self.cursor.fetchall())
        for movie in all_movies:
            if movie['directoryId'] in files.keys():
                files[movie['directoryId']].append(movie['file'])
            else:
                files[movie['directoryId']] = [movie['file']]
        return files

    def db_to_dict(self, movie_list: list) -> list:
        dict_list = []
        for movie in movie_list:
            movie_dict = {
                'imdb_id': movie[0],
                'file': movie[1],
                'directoryId': movie[2],
                'title': movie[3],
                'year': movie[4],
                'rating': movie[5],
                'plot': movie[6],
                'top250rank': movie[7],
                'coverUrl': movie[8],
                'genres': self.movie_genres(movie[0])
            }
            dict_list.append(movie_dict)

        return dict_list
