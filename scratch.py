import os
from imdb import Cinemagoer
from movie_sql import DataBase

db = DataBase(server='127.0.0.1', user=os.getenv('DB_USER'), password=os.getenv('DB_PASS'), database='fred')
i = Cinemagoer()
for m in ['The Enforcer']:
    movie = i.search_movie(m)
    movie_detail = i.get_movie(movie[0].movieID)
    db.insert_movie(f'{m}.mkv', movie_detail)

movies = db.movie_list(rating=8)
print(movies)
