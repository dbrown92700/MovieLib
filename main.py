#!python3

import os
from movie_sql import DataBase
from movie import Movie
from files import Files
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
root_dir = '/media/db/Elements/Movies_TV/New Movies'
logfile = '/home/db/PycharmProjects/MovieLib/movielib-app.log'
movie_extensions = ['mkv', 'mp4']

if __name__ == '__main__':
    t = datetime.now()
    try:
        os.rename(logfile, f'{logfile}.{t.year}-{t.month:02}-{t.day:02}')
    except FileNotFoundError:
        pass
    logging.basicConfig(filename='/home/db/PycharmProjects/MovieLib/movielib-app.log', level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    db = DataBase(server='127.0.0.1', user=os.getenv('DB_USER'), password=os.getenv('DB_PASS'),
                  database=os.getenv('MOVIE_DB'))
    files = Files(root_dir)
    delta = files.delta(db.files())
    logger.info('--------------------SCANNING FILES-------------')
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
                logger.info(f'Ignored file {directory}/{file}')
