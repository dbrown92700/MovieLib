#!python3

import os
from imdb import Cinemagoer
from movie_sql import DataBase
from movie import Movie

if __name__ == '__main__':

    db = DataBase(server='127.0.0.1', user=os.getenv('DB_USER'), password=os.getenv('DB_PASS'), database='fred2')
    movie = Movie('The Matrix 1999.mkv', '/my/directory')
    movie.get_imdb()
    db.insert_movie(movie)

    if False:
        files = os.listdir('/media/db/Elements/Movies_TV/Movies/Tarantino')
        imdb = Cinemagoer()
        for file in files:
            if file[-4::] not in ['.mkv', '.avi', '.mp4']:
                continue
            for suf in ['.mkv', '.avi', '.mp4']:
                filename = file.removesuffix(suf)
            results = imdb.search_movie(filename)
            movie = imdb.get_movie(results[0].movieID)
            print(f'{filename:50} - {results[0]["title"]} {results[0]["year"]}')
            for x in ['rating', 'genres', 'plot']:
                print(movie[x])
            print('-' * 80)
