from imdb import Cinemagoer

movie_suffixes = ['mkv', 'mp4', 'avi']
imdb_detail = ['title', 'year', 'rating', 'plot', 'genres']


class Movie:

    def __init__(self, filename, directory):

        self.filename = filename
        self.directory = directory
        self.imdb_id = ''
        self.imdb_data = {}

    def get_imdb(self):
        imdb = Cinemagoer()
        search_name = self.filename
        for x in movie_suffixes:
            search_name = search_name.removesuffix(x)
        search_name = search_name.replace('_', ' ')
        movie = imdb.search_movie(search_name)
        self.imdb_id = movie[0].movieID
        movie_detail = imdb.get_movie(movie[0].movieID)
        for x in imdb_detail:
            self.imdb_data[x] = movie_detail[x]
        try:
            self.imdb_data['top250'] = movie_detail['top 250 rank']
        except KeyError:
            self.imdb_data['top250'] = 999
