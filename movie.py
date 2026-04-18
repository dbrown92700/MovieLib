import re
from imdbinfo import search_title, get_movie, get_top250
import logging
logger = logging.getLogger(__name__)

movie_suffixes = ['.mkv', '.mp4', '.avi', 'm4v']
imdb_detail = ['title', 'year', 'rating', 'plot', 'genres', 'cover_url', 'duration']


class Movie:

    def __init__(self, filename: str, directory):

        self.filename = filename
        self.directory = directory
        self.imdb_id = ''
        self.imdb_data = {}

    def get_imdb(self, imdb_id=''):
        # If imdb_id is provided, movie detail will be pulled from that id
        # If it is not provided, this routine will search for a match based on the filename

        if imdb_id:
            self.imdb_id = imdb_id
            movie_detail = get_movie(self.imdb_id)
        else:
            search_name = self.filename
            year = ''
            for x in movie_suffixes:
                search_name = search_name.removesuffix(x)
            for regex in ['(.+)(\\(\\d{4}\\)$)', '(.+)(\\[\\d{4}\\]$)', '(.+)(\\d{4}$)']:
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
            search_results = search_title(f'{search_name} {year}')
            num = 0
            while True:
                if num == len(search_results.titles):
                    raise FileNotFoundError('No movie found with this search')
                self.imdb_id = search_results.titles[num].imdb_id
                movie_detail = get_movie(self.imdb_id)
                print(f"{movie_detail.title} {movie_detail.kind} {movie_detail.year}")
                if ((movie_detail.kind in ['movie', 'tv movie', 'video movie', 'tv mini series']) and
                        (str(movie_detail.year) == year)):
                    break
                else:
                    num += 1
        for x in imdb_detail:
            try:
                self.imdb_data[x] = getattr(movie_detail, x)
            except KeyError:
                self.imdb_data[x] = ''
        top = get_top250()
        try:
            self.imdb_data['top250'] = top[self.imdb_id]
        except KeyError:
            self.imdb_data['top250'] = 999
