import re

from imdb import Cinemagoer
import logging
logger = logging.getLogger(__name__)

movie_suffixes = ['.mkv', '.mp4', '.avi', 'm4v']
imdb_detail = ['title', 'year', 'rating', 'plot', 'genres', 'cover url']


class Movie:

    def __init__(self, filename, directory):

        self.filename = filename
        self.directory = directory
        self.imdb_id = ''
        self.imdb_data = {}

    def get_imdb(self, imdb_id=''):
        # If imdb_id is provided, movie detail will be pulled from that id
        # If it is not provided, this routine will search for a match based on the filename

        imdb = Cinemagoer()
        if imdb_id:
            self.imdb_id = imdb_id
            movie_detail = imdb.get_movie(self.imdb_id)
        else:
            search_name = self.filename
            year = ''
            for x in movie_suffixes:
                search_name = search_name.removesuffix(x)
            for regex in ['(.+)(\(\d{4}\)$)', '(.+)(\[\d{4}\]$)', '(.+)(\d{4}$)']:
                try:
                    search_name, year = re.search(regex, search_name).groups()
                except AttributeError:
                    continue
            if not year:
                raise SyntaxError(f'{self.filename} format error. Cannot parse name and year.')
            else:
                year = re.search(r'\d{4}', year).group(0)
            for x in ['_', '.']:
                search_name = search_name.replace(x, ' ').rstrip(' ')
            movie = imdb.search_movie(f'{search_name} {year}')
            num = 0
            while True:
                if num == len(movie):
                    raise FileNotFoundError('No movie found with this search')
                self.imdb_id = movie[num].movieID
                movie_detail = imdb.get_movie(self.imdb_id)
                print(f"{movie_detail['title']} {movie_detail['kind']} {movie_detail['year']}")
                if ((movie_detail['kind'] in ['movie', 'tv movie', 'video movie']) and
                        (str(movie_detail['year']) == year)):
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
