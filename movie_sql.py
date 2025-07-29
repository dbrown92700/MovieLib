import datetime

import mysql.connector
from movie import Movie
import os
import logging
logger = logging.getLogger(__name__)


# NOTES:
# os.path.getctime(path)  ... 1727875564.78
# datetime.fromtimestamp(epoch) = datetime.datetime(2017, 1, 22, 2, 47, 52) = 2017-01-22 02:47:52
# imdb.data['runtimes'][0] ... ['136']

movie_table = ('(movieId nchar(20) NOT NULL,'
               ' file nchar(255) NOT NULL,'
               ' directoryId nchar(255) NOT NULL,'
               ' title nchar(255) NOT NULL,'
               ' year smallint,'
               ' rating decimal(3,1),'
               ' plot varchar(1000),'
               ' top250rank smallint,'
               ' coverUrl nchar(255),'
               ' dateAdded int,'
               ' runTime smallint,'
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
file_error = ('(fileId smallint NOT NULL AUTO_INCREMENT,'
              ' file nchar(255),'
              ' directoryId nchar(255),'
              ' PRIMARY KEY (fileId)'
              ')')
series_table = ('(seriesId smallint NOT NULL AUTO_INCREMENT,'
                ' series nchar(50) NOT NULL,'
                ' PRIMARY KEY (seriesId)'
                ')')
movie_series = ('(movieId nchar(20) NOT NULL,'
                ' seriesId smallint NOT NULL,'
                ' INDEX (movieId), INDEX (seriesId),'
                ' FOREIGN KEY (movieId) REFERENCES movies (movieId),'
                ' FOREIGN KEY (seriesId) REFERENCES series (seriesId)'
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
            self.cursor.execute(f'CREATE TABLE series {series_table};')
            logger.info(f'Created table series')
            self.cursor.execute(f'CREATE TABLE movie_series {movie_series};')
            logger.info(f'Created table movie_series')
            self.cursor.execute(f'CREATE TABLE none_watched (movieID nchar(20) not NULL);')
            self.cursor.execute(f'CREATE TABLE none_wants (movieID nchar(20) not NULL);')
            self.cursor.execute(f'CREATE TABLE users (user nchar(32) not NULL);')
            self.cursor.execute(f'INSERT INTO users (user) VALUES ("none");')
            logger.info(f'Created tables users, none_watched and none_wants')
            self.cursor.execute(f'CREATE TABLE file_errors {file_error};')

        self.cursor.execute(f'SELECT * FROM genres;')
        self.user = 'none'
        genres = self.cursor.fetchall()
        self.genre_dict = {}
        for g in genres:
            self.genre_dict[g[1]] = g[0]

        self.cursor.execute(f'SELECT * FROM series;')
        self.user = 'none'
        series = self.cursor.fetchall()
        self.series_dict = {}
        for s in series:
            self.series_dict[s[1]] = s[0]

    def close(self):
        self.cnx.close()

    def delete(self, imdb_id='', file=''):

        if file and not imdb_id:
            self.cursor.execute(f'SELECT movieID FROM movies WHERE file="{file}";')
            imdb_id = self.cursor.fetchall()[0][0]
        self.cursor.execute(f'DELETE FROM movie_genres WHERE movieID="{imdb_id}";')
        self.cursor.execute(f'DELETE FROM movies WHERE movieID="{imdb_id}";')
        self.cnx.commit()
        logger.info(f'File Deleted: Removed {imdb_id} from database')

    def movie_list(self, imdb_id='', name='', genre='', rating=-1.1, year_min=0, year_max=0, top250=False, length=0,
                   page=1, pagesize=10, sort='title', direction='ASC', watched='', wants='', file='', series='',
                   plot=''):
        # Returns a list of movies using the filters specified and the count of movies in the form
        # ([(movie1),(movie2)], count)
        # if pagesize=0, it returns all entries

        movie_filter = []
        if imdb_id:
            movie_filter.append(f'movies.movieId="{imdb_id}"')
        if name:
            movie_filter.append(f'movies.title LIKE "%{name}%"')
        if plot:
            movie_filter.append(f'movies.plot LIKE "%{plot}%"')
        if rating > 0:
            movie_filter.append(f'movies.rating>={rating}')
        if year_min > 0:
            movie_filter.append(f'movies.year>={year_min}')
        if year_max > 0:
            movie_filter.append(f'movies.year<={year_max}')
        if length > 0:
            movie_filter.append(f'movies.runTime<={length}')
        if top250:
            movie_filter.append(f'movies.top250rank<900')
        if genre:
            movie_filter.append(f'genre="{genre}"')
        if series:
            movie_filter.append(f'series="{series}"')
        if watched:
            movie_filter.append(f'movies.movieID {"NOT " if watched=="no" else ""}IN (SELECT * FROM {self.user}_watched)')
        if wants:
            movie_filter.append(f'movies.movieID {"NOT " if wants=="no" else ""}IN (SELECT * FROM {self.user}_wants)')
        if file:
            movie_filter.append(f'file="{file}"')
        filter_text = ''
        if movie_filter:
            filter_text = f'WHERE {" AND ".join(movie_filter)}'

        join_text = ''
        if genre:
            join_text += (f'JOIN movie_genres ON (movie_genres.movieId = movies.movieId) '
                         f'JOIN genres ON (genres.genreId = movie_genres.genreId) ')
        if series:
            join_text += (f'JOIN movie_series ON (movie_series.movieId = movies.movieId) '
                         f'JOIN series ON (series.seriesId = movie_series.seriesId) ')
        if pagesize==0:
            limit = ''
        else:
            limit = f'LIMIT {pagesize} OFFSET {(page-1) * pagesize}'
        command = (f'SELECT movies.* FROM movies '
                   f'{join_text} '
                   f'{filter_text} '
                   f'ORDER BY movies.{sort} {direction}, movies.title ASC '
                   f'{limit};')
        print(command)
        self.cursor.execute(command)
        movies = self.cursor.fetchall()
        self.cursor.execute(f'SELECT COUNT(*) FROM movies '
                            f'{join_text} '
                            f'{filter_text};')
        movie_count = self.cursor.fetchall()[0][0]

        return movies, movie_count

    def insert_movie(self, movie: Movie):
        # inserts a movie into the database

        movie_search = self.movie_list(imdb_id=movie.imdb_id)[0]
        if movie_search:
            found_movie = self.db_to_dict(movie_search)[0]
            logger.info(f'Duplicate: File: {movie.directory}/{movie.filename}\n'
                        f'   Database: {found_movie["directoryId"]}/{found_movie["file"]}')
            return {'status': 'duplicate'}
        plot = movie.imdb_data['plot'][0].replace('"', "'")
        try:
            date_added = os.path.getmtime(f'{movie.directory}/{movie.filename}')
        except PermissionError:
            logger.error(f"File Permissions Error getting create time. Using Now: {movie.directory}/{movie.filename}")
            date_added = datetime.datetime.now().timestamp()
        command = (f'INSERT INTO movies (movieId, file, directoryId, title, year, rating, plot, top250rank, coverUrl, '
                   f'dateAdded, runTime) VALUES ("{movie.imdb_id}", "{movie.filename}", "{movie.directory}", '
                   f'"{movie.imdb_data["title"]}", "{movie.imdb_data["year"]}", "{movie.imdb_data["rating"]}", '
                   f'"{plot}", "{movie.imdb_data["top250"]}", "{movie.imdb_data["cover url"]}",'
                   f'"{int(date_added)}", "{movie.imdb_data["runtimes"][0]}");')
        self.cursor.execute(command)
        self.cnx.commit()
        self.genres_update(movie_id=movie.imdb_id, genres=movie.imdb_data['genres'])
        logger.info(f'File Added: {movie.filename} : {movie.imdb_data["title"]}')

        return {'status': 'success'}

    def db_to_dict(self, movie_list: list) -> list:
        # converts a database list of movies to a dictionary list of movies

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
                'dateAdded': movie[9],
                'runTime': movie[10],
                'genres': self.movie_genres(movie[0]),
                'series': self.movie_series(movie[0])
            }
            dict_list.append(movie_dict)

        return dict_list

    def add_user(self, username: str) -> bool:

        users = self.user_list()
        if username in users:
            return False
        watch_table = f'CREATE TABLE {username}_watched (movieID nchar(20) not NULL);'
        wants_table = f'CREATE TABLE {username}_wants (movieID nchar(20) not NULL);'
        self.cursor.execute(watch_table)
        logger.info(f'Created table {username}_watched')
        self.cursor.execute(wants_table)
        logger.info(f'Created table {username}_wants')
        self.user = username
        self.cursor.execute(f'INSERT INTO users (user) VALUES ("{username}");')

        return True

    def user_list(self) -> list:
        self.cursor.execute(f'SELECT * FROM users;')
        results = self.cursor.fetchall()

        return [x[0] for x in results]

    def select_user(self, username: str) -> bool:
        # changes the database user to username. returns False if user does not exist

        if username not in self.user_list():
            return False
        self.user = username
        return True

    def toggle_list_entry(self, imdb_id: str, movie_list='wants'):

        command = f'SELECT * FROM {self.user}_{movie_list} WHERE movieID="{imdb_id}";'
        self.cursor.execute(command)
        if self.cursor.fetchall():
            command = f'DELETE FROM {self.user}_{movie_list} WHERE movieID="{imdb_id}";'
        else:
            command = f'INSERT INTO {self.user}_{movie_list} (movieID) VALUES ("{imdb_id}");'
        self.cursor.execute(command)

    def user_movie_list(self, movie_list='wants'):

        self.cursor.execute(f'SELECT * FROM {self.user}_{movie_list};')
        movies = self.cursor.fetchall()

        return [m[0] for m in movies]

    def files(self) -> dict:
        # returns a dictionary in the format {directory1: [filename1, filename2], directory2: etc}

        files = {}
        self.cursor.execute(f'SELECT * FROM movies;')
        all_movies = self.db_to_dict(self.cursor.fetchall())
        for movie in all_movies:
            if movie['directoryId'] in files.keys():
                files[movie['directoryId']].append(movie['file'])
            else:
                files[movie['directoryId']] = [movie['file']]
        return files

    def update_dir(self, directory='', imdb_id='', file='', new_file=''):

        if file and not imdb_id:
            self.cursor.execute(f'SELECT movieID FROM movies WHERE file="{file}";')
            imdb_id = self.cursor.fetchall()[0][0]
        if directory:
            self.cursor.execute(f'UPDATE movies SET directoryId="{directory}" WHERE movieId="{imdb_id}";')
        if new_file:
            self.cursor.execute(f'UPDATE movies SET file="{new_file}" WHERE movieId="{imdb_id}";')
        logger.info(f'File Moved: {file} moved to directory {directory}')

    def file_errors(self):

        self.cursor.execute('SELECT * FROM file_errors;')
        errors = self.cursor.fetchall()

        return errors

    def update_file_errors(self, files: dict):

        self.cursor.execute('DELETE FROM file_errors;')
        self.cursor.execute('ALTER TABLE file_errors AUTO_INCREMENT = 1;')
        for file in files:
            self.cursor.execute(f'INSERT INTO file_errors (file, directoryId) '
                                f'values ("{file}", "{files[file]}");')

    def file_error_remove(self, file_num: int):

        self.cursor.execute(f'DELETE FROM file_errors WHERE fileId={file_num};')

    def update_movie(self, imdb_id, column, value):

        self.cursor.execute(f'UPDATE movies SET {column}="{value}" WHERE movieId="{imdb_id}";')

    def add_genre(self, genre) -> int:
        # adds a new genre to the genre table and returns its integer ID

        self.cursor.execute(f'INSERT INTO genres (genre) VALUES ("{genre}");')
        self.cnx.commit()
        self.cursor.execute(f'SELECT genreId FROM genres WHERE genre="{genre}";')
        genre_id = self.cursor.fetchall()[0][0]
        self.genre_dict[genre] = genre_id

        return genre_id

    def genres_update(self, movie_id, genres):
        in_db = self.movie_genres(movie_id=movie_id)
        for genre in genres:
            if genre not in self.genre_dict:
                self.add_genre(genre)
            if genre not in in_db:
                command = (f'INSERT INTO movie_genres (movieId, genreId) VALUES '
                           f'("{movie_id}", {self.genre_dict[genre]});')
                self.cursor.execute(command)
                self.cnx.commit()
        for genre in in_db:
            if genre not in genres:
                command = f'DELETE FROM movie_genres WHERE movieId={movie_id} AND genreId={self.genre_dict[genre]};'
                self.cursor.execute(command)
                self.cnx.commit()

    def movie_genres(self, movie_id):
        # Returns a list of genres for a given movie ID

        self.cursor.execute(f'SELECT genreId FROM movie_genres WHERE movieId={movie_id};')
        genres = self.cursor.fetchall()
        genre_list = []
        for g in [x[0] for x in genres]:
            genre = list(self.genre_dict.keys())[list(self.genre_dict.values()).index(g)]
            genre_list.append(genre)

        return genre_list

    def add_series(self, series) -> int:
        # adds a new series to the series table and returns its integer ID

        self.cursor.execute(f'INSERT INTO series (series) VALUES ("{series}");')
        self.cnx.commit()
        self.cursor.execute(f'SELECT seriesId FROM series WHERE series="{series}";')
        series_id = self.cursor.fetchall()[0][0]
        self.series_dict[series] = series_id

        return series_id

    def movie_series(self, movie_id):
        # Returns a list of series for a given movie ID

        self.cursor.execute(f'SELECT seriesId FROM movie_series WHERE movieId={movie_id};')
        series = self.cursor.fetchall()
        series_list = []
        for s in [x[0] for x in series]:
            ser = list(self.series_dict.keys())[list(self.series_dict.values()).index(s)]
            series_list.append(ser)

        return series_list

    def series_update(self, movie_id, series):
        in_db = self.movie_series(movie_id=movie_id)
        for ser in series:
            if ser not in self.series_dict:
                self.add_series(ser)
            if ser not in in_db:
                command = (f'INSERT INTO movie_series (movieId, seriesId) VALUES '
                           f'("{movie_id}", {self.series_dict[ser]});')
                self.cursor.execute(command)
                self.cnx.commit()
        for ser in in_db:
            if ser not in series:
                command = f'DELETE FROM movie_series WHERE movieId={movie_id} AND seriesId={self.series_dict[ser]};'
                self.cursor.execute(command)
                self.cnx.commit()
