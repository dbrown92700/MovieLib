#!python3

__author__ = "David Brown <dbrown92700@gmail.com>"
__contributors__ = []

import requests
from flask import Flask, request, render_template, redirect, session
from markupsafe import Markup
import os
from movie_sql import DataBase

app = Flask(__name__)
app.secret_key = 'any random string'
app_url = os.environ.get('SCRIPT_NAME') or ''
server_ip = os.environ.get('SERVER_IP') or '127.0.0.1'
server_port = os.environ.get('SERVER_PORT') or '8111'
root_dir = os.getenv('MOVIE_ROOT')


def database():
    db = DataBase(server='0.0.0.0',
                  user=os.getenv('DB_USER'),
                  password=os.getenv('DB_PASS'),
                  database=os.getenv('MOVIE_DB'))
    return db


@app.route('/')
def list_movies():

    db = database()
    genre = request.args.get('genre') or ''
    name = request.args.get('name') or ''
    page = int(request.args.get('page') or '1')
    rating = float(request.args.get('rating') or '-1.1')
    year = int(request.args.get('year') or '0')
    top250 = request.args.get('top250') or False
    watched = request.args.get('watched') or ''
    wants = request.args.get('wants') or ''
    available = request.args.get('available') or ''
    pagesize = int(request.args.get('pagesize') or '10')
    sort = request.args.get('sort') or 'title'
    direction = request.args.get('direction') or 'ASC'

    try:
        db.user = session['user']
    except KeyError:
        session['user'] = db.user = 'none'

    movies, movie_count = db.movie_list(name=name, genre=genre, pagesize=pagesize, page=page,
                                        rating=rating, year=year, top250=top250,
                                        watched=watched, wants=wants,
                                        sort=sort, direction=direction)
    match_list = db.db_to_dict(movies)

    movie_table = ''
    for movie in match_list:
        movie_table += (f'<tr>\n'
                        f'<td width=200>'
                        f'<a href="https://imdb.com/title/tt{movie["imdb_id"]}/" target="_imdb">'
                        f'{movie["title"]}</a><br>\n'
                        f'{movie["year"]}\n'
                        f'<br><br><div align=center><a href="{app_url}/edit?id={movie["imdb_id"]}">Edit</a>'
                        f'</div></td>\n'
                        f'<td width=90 align=left><img src="{movie["coverUrl"]}" height=120 width=80></td>\n'
                        f'<td width=30>{movie["rating"]}</td>\n'
                        f'<td width=300 style="padding-right: 5px">\n'
                        f'<div style="height:120px;width:290px;overflow:auto;">'
                        f'{movie["plot"]}</td>\n<td width=120>')
        for g in movie["genres"]:
            movie_table += f'{g}<br>\n'

        watched_list = db.user_movie_list(movie_list='watched')
        wants_list = db.user_movie_list(movie_list='wants')
        if db.user != 'none':
            movie_table += f'<table>' \
                           f'<tr valign="middle"><td align="right">Watch:</td><td>' \
                           f'<img src="/static/{"yes" if movie["imdb_id"] in wants_list else "no"}.png" ' \
                           f'id="{movie["imdb_id"]}wants" onclick="toggle(\'{movie["imdb_id"]}\', \'wants\')" ' \
                           f'width="20" height="20"></td></tr>' \
                           f'<tr valign="middle"><td align="right">Watched:</td><td>' \
                           f'<img src="/static/{"yes" if movie["imdb_id"] in watched_list else "no"}.png" ' \
                           f'id="{movie["imdb_id"]}watched" onclick="toggle(\'{movie["imdb_id"]}\', \'watched\')" ' \
                           f'width="20" height="20"></td></tr></table>' \
                           f'</td></tr>\n'
        movie_table += (f'<tr><td style="border-bottom: 2px solid black;"></td>'
                        f'<td colspan="4" style="border-bottom: 2px solid black;">'
                        f'{movie["directoryId"].removeprefix(root_dir)}/{movie["file"]}</td></tr>\n')

    genre_menu = ''
    full_genre_list = list(db.genre_dict.keys()).copy()
    full_genre_list.sort()
    for genre_item in full_genre_list:
        selected = ''
        if genre == genre_item:
            selected = ' selected'
        genre_menu += f'<option value="{genre_item}"{selected}>{genre_item}</option>\n'

    top250_radio = f'<input type="radio" name="top250" value="True" {"checked" if top250=="True" else ""}>'

    url = (f'{app_url}/?name={"+".join(name)}&genre={genre}&watched={watched}&wants={wants}&'
           f'rating={rating}&top250={"True" if top250=="True" else ""}&sort={sort}&direction={direction}')
    pages = (f'<td width="350" align="center">Movies {(page-1) * pagesize + 1}-{min(page*pagesize, movie_count)} of '
             f'{movie_count} movies</td>\n'
             f'<td width="350" align="center">')
    if page == 1:
        pages += 'prev<<<'
    else:
        pages += f'<a href="{url}&page={page-1}">prev<<< </a>'
    pages += f' <b>Page {page}</b> '
    if movie_count > page*10:
        pages += f'<a href="{url}&page={page+1}"> >>>next</a></td>\n'
    else:
        pages += '>>>next</td>\n'

    db.close()
    return render_template('list_movies.html', genre_menu=Markup(genre_menu), name=' '.join(name), pages=Markup(pages),
                           movie_table=Markup(movie_table), app_url=app_url, top250_radio=Markup(top250_radio),
                           user=db.user)


@app.route('/toggle')
def toggle():
    db = database()
    user = session['user']
    imdb_id = request.args.get('imdbId')
    db_list = request.args.get('db_list')
    db.user = user
    print(f'Toggle User: {db.user}')
    db.toggle_list_entry(imdb_id=imdb_id, movie_list=db_list)

    return Markup('ok')


@app.route('/set_user')
def set_user():
    db = database()
    user = request.args.get('user') or None
    new_user = request.args.get('new_user') or None\
    if user:
        session['user'] = user
    if new_user:
        db.add_user(new_user)
        session['user'] = new_user

    return redirect('/')


@app.route('/user')
def get_user():
    db = database()
    user_list = db.user_list()
    user_select = ''
    for u in user_list:
        user_select += f'<option value="{u}">{u}</option>\n'

    return render_template('user.html', user_list=Markup(user_select))


@app.route('/errors')
def file_errors():
    db = database()
    files = db.file_errors()
    page = '<html><body>\n'
    for file in files:
        page += f'{file[0]}: {file[2]}/{file[1]}<br>\n'
    page += '</body></html>'

    return Markup(page)


# @app.route('/search')
# def search():
#
#     return render_template('search.html', app_url=app_url)
#
#
# @app.route('/results')
# def search_result():
#
#     api_key = os.environ.get('IMDB_API_KEY')
#     search_text = request.args.get("search_text").replace('+', '%20')
#     results = json.loads(requests.get(f'https://imdb-api.com/en/API/Search/{api_key}/{search_text}').text)
#
#     if results['results'] is None:
#         return render_template('error.html', err=results, key=api_key, app_url=app_url)
#
#     expression = results["expression"]
#     movie_table = ''
#     for result in results['results']:
#         movie_table += f'<tr>\n \
#                 <td width=200><a href="https://imdb.com/title/{result["id"]}/" target="_imdb">{result["title"]}<br> \
#                 {result["description"]}</a></td>\n \
#                 <td width=100 align=left><static src="{result["image"]}" height=120 width=80></td>\n \
#                 <td width=50><a href="{app_url}/add?id={result["id"]}">Add</a></td>\n'
#
#     return render_template('search_result.html', expression=expression, movie_table=Markup(movie_table),
#                            app_url=app_url)
#
#
# @app.route('/add')
# def add_movie():
#
#     global movie_list
#     imdb_id = request.args.get("id")
#     api_key = os.environ.get('IMDB_API_KEY')
#
#     url = f'https://imdb-api.com/en/API/Title/{api_key}/{imdb_id}'
#     title = json.loads(requests.get(url).text)
#
#     genres = title['genres'].split(',')
#     genres = ':'.join([genres[x].lstrip(' ') for x in range(len(genres))])
#     new_movie = {'id': imdb_id, 'title': title['fullTitle'].replace(',', '~^'), 'image': title['image'],
#                  'rating': title['imDbRating'], 'plot': title['plot'].replace(',', '~^'), 'genres': genres,
#                  'watched': 'no', 'available': 'yes'}
#     # for value in new_movie:
#     #     new_movie[value] = new_movie[value].encode('utf-8')
#     #     print(new_movie[value])
#     found = False
#     for movie in movie_list:
#         if movie['id'] == new_movie['id']:
#             movie_list[movie_list.index(movie)] = new_movie
#             found = True
#             break
#         if float(new_movie['rating']) > float(movie['rating']):
#             movie_list.insert(movie_list.index(movie), new_movie)
#             found = True
#             break
#     if not found:
#         movie_list.append(new_movie)
#
#     write_movie_file()
#
#     return redirect(f'{app_url}/edit?id={imdb_id}')
#
#
# @app.route('/edit')
# def edit_movie():
#
#     global movie_list
#
#     imdb_id = request.args.get("id")
#     for movie in movie_list:
#         if movie['id'] == imdb_id:
#             break
#     movie_table = f'<tr>\n' \
#                   f'<td width=200><a href="https://imdb.com/title/{movie["id"]}/" target="_imdb">' \
#                   f'{movie["title"].replace("~^",",")}</a></td>\n' \
#                   f'<td width=90 align=left><static src="{movie["image"]}" height=120 width=80></td>\n' \
#                   f'<td width=30>{movie["rating"]}</td>\n' \
#                   f'<td width=300 style="border: 1px solid black;">\n' \
#                   f'<div style="height:120px;width:300px;overflow:auto;">{movie["plot"].replace("~^", ",")}</td>\n' \
#                   f'<td width=80>'
#     for this in movie["genres"].split(':'):
#         movie_table += f'{this}<br>\n'
#     movie_table += f'</td></tr></table>\n'
#
#     watched_radio = ''
#     for choice in ['yes', 'no']:
#         selected = ''
#         if choice == movie['watched']:
#             selected = 'checked'
#         watched_radio += f'<td width="50">{choice.title()} ' \
#                          f'<input type="radio" name="watched" value="{choice}" {selected}></td>'
#
#     available_radio = ''
#     for choice in ['yes', 'no']:
#         selected = ''
#         if choice == movie['available']:
#             selected = 'checked'
#         available_radio += f'<td>{choice.title()} ' \
#                            f'<input type="radio" name="available" value="{choice}" {selected}></td>'
#
#     return render_template('edit_movie.html', title=movie['title'], movie_table=Markup(movie_table),
#                            watched_radio=Markup(watched_radio), available_radio=Markup(available_radio),
#                            id=movie['id'], app_url=app_url)


# @app.route('/delete')
# def delete_movie():
#
#     global movie_list
#
#     imdb_id = request.args.get("id")
#     for movie in movie_list:
#         if movie['id'] == imdb_id:
#             list_index = movie_list.index(movie)
#             movie_list.pop(list_index)
#     write_movie_file()
#
#     return redirect(f'{app_url}/')


# @app.route('/save')
# def save_movie():
#
#     global movie_list
#
#     imdb_id = request.args.get("id")
#     watched = request.args.get("watched")
#     available = request.args.get("available")
#
#     for movie in movie_list:
#         if movie['id'] == imdb_id:
#             list_index = movie_list.index(movie)
#             movie_list[list_index]['watched'] = watched
#             movie_list[list_index]['available'] = available
#     write_movie_file()
#     return redirect(f'{app_url}/')


if __name__ == '__main__':
    app.run(host=server_ip, port=server_port, debug=True)
# [END gae_python38_app]
