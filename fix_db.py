#!/usr/bin/env python

from movie_sql import DataBase
from imdb import Cinemagoer
import os
from datetime import datetime

db = DataBase(server='127.0.0.1', user=os.getenv('DB_USER'), password=os.getenv('DB_PASS'),
              database=os.getenv('MOVIE_DB'))
imdb = Cinemagoer()

movies = db.db_to_dict(db.movie_list(pagesize=0)[0])

fix = input(f'1. Run Time\n'
            f'2. Date Added\n'
            f'3. IMDB Rating\n'
            f'?: ')

for n, movie in enumerate(movies):

    print(f"{n:04} {movie['title']}")

    if fix == 3:
        # Update IMDB Rating
        imdb_data = imdb.get_movie(movie['imdb_id'])
        if imdb_data.data['rating'] != float(movie['rating']):
            print(f'   {movie["rating"]} --> {imdb_data.data["rating"]}')
            db.update_movie(movie['imdb_id'],'rating', imdb_data.data['rating'])
        else:
            print('   No Change')

    if fix == 2:
        #Fix Date
        date_added = int(os.path.getctime(f'{movie["directoryId"]}/{movie["file"]}'))
        if date_added != movie['dateAdded']:
            print(f"   {datetime.fromtimestamp(date_added)}")
            db.update_movie(movie['imdb_id'], 'dateAdded', date_added)

    if fix == 1:
        #  Update run_time
        if movie['runTime']:
            continue
        imdb_data = imdb.get_movie(movie['imdb_id'])
        try:
            run_time = int(imdb_data.data['runtimes'][0])
        except KeyError:
            run_time = 999
        db.update_movie(movie['imdb_id'], 'runTime', run_time)
        print(f'   {run_time}')

db.close()