#!python
import os
from movie_sql import DataBase

if __name__ == '__main__':

    db = DataBase(server='127.0.0.1', user=os.getenv('DB_USER'), password=os.getenv('DB_PASS'), database='fred')
    if False:
        imdb = Cinemagoer()
        for m in ['The Matrix', 'Alien 1979', 'Shawshank Redemption', 'Clerks']:
            movie = imdb.search_movie(m)
            movie_detail = imdb.get_movie(movie[0].movieID)
            db.insert_movie('filename.mkv', movie_detail)
    movies = db.movie_list(rating=8)
    print(movies)
    db.close()

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
