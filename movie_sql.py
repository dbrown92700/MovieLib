import mysql.connector

movie_table = ('(movieId smallint NOT NULL AUTO_INCREMENT,'
               ' file nchar(255) NOT NULL,'
               ' title nchar(255) NOT NULL,'
               ' imdb_id nchar(20),'
               ' year smallint,'
               ' rating decimal(3,1),'
               ' plot varchar(1000),'
               ' top250rank smallint,'
               ' PRIMARY KEY (movieId)'
               ')')
genre_table = ('(genreId smallint NOT NULL AUTO_INCREMENT,'
               ' genre nchar(50) NOT NULL,'
               ' PRIMARY KEY (genreId)'
               ')')
movie_genres = ('('
                ' movieId smallint NOT NULL,'
                ' genreId smallint NOT NULL,'
                ' INDEX (movieId), INDEX (genreId),'
                ' FOREIGN KEY (movieId) REFERENCES movies (movieId),'
                ' FOREIGN KEY (genreId) REFERENCES genres (genreId)'
                ')')


class DataBase:

    def __init__(self, server: str, user: str, password: str, database: str):

        self.cnx = mysql.connector.connect(user=user, password=password, host=server)
        self.cursor = self.cnx.cursor()
        try:
            self.cursor.execute(f'USE {database};')
        except mysql.connector.Error:
            self.cursor.execute(f'CREATE DATABASE {database};')
            self.cursor.execute(f'CREATE TABLE movies {movie_table};')
            self.cursor.execute(f'CREATE TABLE genres {genre_table};')
            self.cursor.execute(f'CREATE TABLE movie_genres {movie_genres};')
            self.cursor.execute('USE movie_db')
        self.cursor.execute(f'SELECT * FROM genres')
        genres = self.cursor.fetchall()
        self.genre_list = {}
        for g in genres:
            self.genre_list[g[1]] = g[0]

    def close(self):
        self.cnx.close()

    def create_table(self, table: str):

        self.cursor.execute(f'CREATE TABLE {table}')

    def add_genre(self, genre):

        self.cursor.execute(f'INSERT INTO genres (genre) VALUES ({genre})')
        genre_id = self.cursor.execute(f'SELECT genreId FROM genres WHERE genre="{genre}"')
        self.genre_list[genre] = genre_id

        return genre_id

    def insert_movie(self, file, movie):

        try:
            top250 = f" {movie['top 250 rank']}"
        except KeyError:
            top250 = Null
        self.cursor.execute(f'INSERT INTO movies '
                            f'(file, title, imdb_id, year, rating, plot) '
                            f'VALUES ({file}, {movie["title"]}, {movie["imdbID"]}, {movie["year"]}, {movie["rating"]}, '
                            f'{movie["plot"][0]});')
        self.cursor.execute(f'SELECT movieId FROM movies WHERE file="{file}"')
        movie_id = self.cursor.fetchall()[0][0]
        for genre in movie['genres']:
            if genre not in self.genre_list:
                self.add_genre(genre)
            self.cursor.execute(f'INSERT INTO movie_genres '
                                f'(movieId, genreId)'
                                f'VALUES ({movie_id}, {self.genre_list[genre]});')

        return movie_id

    def movie_list(self, name: str, genre: str, rating: float, year: int, page: int, page_size: int):
        # Returns a list of movies using the filters specified
        movies = []
        count = 1
        movie_filter = []
        if name:
            movie_filter.append(f'title LIKE "%{title}%"')
        if rating:
            movie_filter.append(f'rating>{rating}')
        if year:
            movie_filter.append(f'year={year}')


        # SELECT * FROM movies
        # JOIN movie_genres ON(movie_genres.movieId = movies.movieId)
        # JOIN genres ON(genres.genreId = movie_genres.genreId)
        # WHERE movies.rating > 7;

        count = self.cursor.execute(f'SELECT COUNT(*) FROM movies WHERE {" AND ".join(movie_filter)};')
        if page:
            count = f'LIMIT {page_size} OFFSET {(page - 1)*page_size}'

        self.cursor.execute('')

        return movies, count

    def movie_genres(self, movie_id):
        # Returns a list of genres for a given movie ID

        self.cursor.execute(f'SELECT genreId FROM movie_genres WHERE movieId={movie_id};')
        genres = self.cursor.fetchall()
        genre_list = []
        for g in genres:
            genre_list.append(self.genre_list[g[0]])

        return genre_list
