#!python3

import os
from movie_sql import DataBase
from movie import Movie
from files import Files
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
root_dir = os.getenv('MOVIE_ROOT')
log_dir = os.getenv('LOG_DIR')
movie_extensions = ['mkv', 'mp4', 'm4v']

if __name__ == '__main__':
    t = datetime.now()
    logging.basicConfig(filename=f'{log_dir}/movielib-app.{t.year}-{t.month:02}.log', level=logging.INFO,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    db = DataBase(server='127.0.0.1', user=os.getenv('DB_USER'), password=os.getenv('DB_PASS'),
                  database=os.getenv('MOVIE_DB'))

    # Generate a list of file changes as delta
    files = Files(root_dir)
    if not files.dirs:
        logger.error('ERROR: Drive Not Detected.  Exiting scanner.')
        exit()
    delta = files.delta(db.files())

    # Scan through delta to determine what happened to each
    logger.info('--------------------SCANNING FILES-------------')
    file_errors = {}
    for file in delta:
        directory = delta[file]['dir']
        if delta[file]['action'] == 'added':
            if os.path.islink(f'{directory}/{file}'):
                logger.info(f'File Ignored: Link {directory}/{file}')
                continue
            if file.split('.')[-1] in movie_extensions:
                movie = Movie(file, directory)
                try:
                    movie.get_imdb()
                    db.insert_movie(movie)
                except Exception as e:
                    file_errors[file] = directory
                    logger.error(f'Movie Search Error: file:{directory}/{file}\n'
                                 f'   Error: {e}')
            else:
                logger.info(f'File Ignored: Not a movie extension {directory}/{file}')
        elif delta[file]['action'] == 'removed':
            db.delete(file=file)
            logger.info(f'File Deleted: Missing from drive {directory}/{file}')
        elif delta[file]['action'] == 'moved':
            db.update_dir(directory=directory, file=file)
            logger.info(f'File Moved: Database Updated {directory}/{file}')
        elif delta[file]['action'] == 'duplicate':
            logger.error(f'Duplicate File: {directory}/{file}')
            file_errors[file] = directory + '--DUPLICATE FILENAME-- '
    db.update_file_errors(file_errors)
