#!python3

import os
from movie_sql import DataBase
from movie import Movie
from files import Files
import logging

logger = logging.getLogger(__name__)
root_dir = '/media/db/Elements/Movies_TV/New Movies'
movie_extensions = ['mkv', 'mp4']

if __name__ == '__main__':
    logging.basicConfig(filename='myapp.log', level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    db = DataBase(server='127.0.0.1', user=os.getenv('DB_USER'), password=os.getenv('DB_PASS'),
                  database=os.getenv('MOVIE_DB'))
    files = Files(root_dir)
    delta = files.delta(db.files())
    for directory in delta['added']:
        for file in delta['added'][directory]:
            if os.path.islink(f'{directory}/{file}'):
                continue
            if file.split('.')[-1] in movie_extensions:
                movie = Movie(file, directory)
                try:
                    movie.get_imdb()
                    db.insert_movie(movie)
                except Exception as e:
                    logger.error(f'Movie Search Error: file:{directory}/{file}\n'
                                 f'   Error: {e}')
            else:
                print(f'Ignored file {directory}/{file}')

    # if False:
    #     files = os.listdir('/media/db/Elements/Movies_TV/Movies/Tarantino')
    #     imdb = Cinemagoer()
    #     for file in files:
    #         if file[-4::] not in ['.mkv', '.avi', '.mp4']:
    #             continue
    #         for suf in ['.mkv', '.avi', '.mp4']:
    #             filename = file.removesuffix(suf)
    #         results = imdb.search_movie(filename)
    #         movie = imdb.get_movie(results[0].movieID)
    #         print(f'{filename:50} - {results[0]["title"]} {results[0]["year"]}')
    #         for x in ['rating', 'genres', 'plot']:
    #             print(movie[x])
    #         print('-' * 80)
