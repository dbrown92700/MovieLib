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
            f'4. IMDB Top 250\n'
            f'?: ')

try:
    fix = int(fix)
except ValueError:
    pass

top_dict = {}

if fix == 4:

    import requests
    from parsel import Selector
    import json

    # Download the IMDB Top 250 Page

    top_page = requests.get('https://www.imdb.com/chart/top/',
                            headers={
                                'User-Agent': f'Mozilla/5.0 (Windows NT 6.3; Win 64 ; x64) Apple WeKit /537.36(KHTML ,'
                                              f' like Gecko) Chrome/80.0.3987.162 Safari/537.36'})

    # Use xpath to pull JSON list of top 250 movies from page data

    sel = Selector(top_page.text)
    script_text = sel.xpath('//script[@type="application/ld+json"]/text()').getall()
    top_list = json.loads(script_text[0])['itemListElement']

    # Create a dictionary of the top 250 movies

    for n, x in enumerate(top_list):
        top_dict[x['item']['url'].removeprefix('https://www.imdb.com/title/tt').removesuffix('/')] = {
            'rank': n+1,
            'title': x['item']['name']
        }
        print(f"{n + 1}. {x['item']['url'].removeprefix('https://www.imdb.com/title/').removesuffix('/')} "
              f"{x['item']['name']}")

for n, movie in enumerate(movies):

    print(f"{n:04} {movie['imdb_id']} {movie['title']}")

    if fix == 4:

        # Update Top 250 ranking.  Set movies dropped from the list to 888

        if (movie['imdb_id'] not in top_dict.keys()) and (movie['top250rank'] < 251):
            print(f"     Old Top250 Rank: {movie['top250rank']:3}   New Top250 Rank: Dropped from Top 250\n")
            db.update_movie(movie['imdb_id'], 'top250rank', 888)
        if movie['imdb_id'] in top_dict.keys():
            print(f"     Old Top250 Rank: {movie['top250rank']:3}   New Top250 Rank: {top_dict[movie['imdb_id']]['rank']}\n")
            db.update_movie(movie['imdb_id'], 'top250rank', top_dict[movie['imdb_id']]['rank'])
            top_dict.pop(movie['imdb_id'])

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

if fix == 4:
    print(f"\n\nIMDB Top 250 movies not on server:\nTotal: {len(top_dict)}")
    for x in top_dict:
        print(f"{top_dict[x]['rank']:3}: {x:15} {top_dict[x]['title']}")