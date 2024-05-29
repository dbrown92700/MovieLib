from imdb import Cinemagoer
import logging
logger = logging.getLogger(__name__)

movie_suffixes = ['mkv', 'mp4', 'avi']
imdb_detail = ['title', 'year', 'rating', 'plot', 'genres', 'cover url']

class Movie:

    def __init__(self, filename, directory):

        self.filename = filename
        self.directory = directory
        self.imdb_id = ''
        self.imdb_data = {}

    def get_imdb(self):
        imdb = Cinemagoer()
        print(self.filename)
        search_name = self.filename
        for x in movie_suffixes:
            search_name = search_name.removesuffix(x)
        for x in ['_', '.']:
            search_name = search_name.replace(x, ' ').rstrip(' ')
        print(search_name)
        movie = imdb.search_movie(search_name)
        num = 0
        while True:
            if num == len(movie):
                print('HERE')
                raise FileNotFoundError('No movie found with this search')
            self.imdb_id = movie[num].movieID
            movie_detail = imdb.get_movie(self.imdb_id)
            print(movie_detail['title'])
            print(movie_detail['kind'])
            if movie_detail['kind'] == 'movie':
                break
            else:
                num += 1
        for x in imdb_detail:
            try:
                self.imdb_data[x] = movie_detail[x]
            except KeyError:
                self.imdb_data[x] = ''
        try:
            self.imdb_data['top250'] = movie_detail['top 250 rank']
        except KeyError:
            self.imdb_data['top250'] = 999
