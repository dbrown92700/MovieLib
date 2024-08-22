#!python3

__author__ = "David Brown <dbrown92700@gmail.com>"
__contributors__ = []

import requests
from flask import Flask, request, render_template, redirect, session
from markupsafe import Markup
import os
from movie_sql import DataBase
import urllib.parse
from movie import Movie

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
    imdb_id = request.args.get('imdb_id') or ''
    genre = request.args.get('genre') or ''
    name = request.args.get('name') or ''
    page = int(request.args.get('page') or '1')
    rating = float(request.args.get('rating') or '-1.1')
    year = int(request.args.get('year') or '0')
    top250 = request.args.get('top250') or False
    watched = request.args.get('watched') or ''
    wants = request.args.get('wants') or ''
    pagesize = int(request.args.get('pagesize') or '10')
    sort = request.args.get('sort') or 'title'
    direction = request.args.get('direction') or 'ASC'

    try:
        db.user = session['user']
    except KeyError:
        session['user'] = db.user = 'none'

    movies, movie_count = db.movie_list(imdb_id=imdb_id, name=name, genre=genre, pagesize=pagesize, page=page,
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
           f'rating={rating}&top250={"True" if top250=="True" else ""}&sort={sort}&direction={direction}&'
           f'pagesize={pagesize}')
    pages = (f'<td width="350" align="center">Movies {(page-1) * pagesize + 1}-{min(page*pagesize, movie_count)} of '
             f'{movie_count} movies</td>\n'
             f'<td width="350" align="center">')
    if page == 1:
        pages += 'prev<<<'
    else:
        pages += f'<a href="{url}&page={page-1}">prev<<< </a>'
    pages += f' <b>Page {page}</b> '
    if movie_count > page*pagesize:
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
    new_user = request.args.get('new_user') or None
    if user:
        session['user'] = user
    if new_user:
        db.add_user(new_user)
        session['user'] = new_user

    return redirect('/')


@app.route('/edit')
def edit_entry():
    imdb_id = request.args.get('id')
    db = database()
    movie_db, movie_count = db.movie_list(imdb_id=imdb_id)
    movie_data = db.db_to_dict(movie_db)[0]
    page = f'<html><body>Filename: {movie_data["file"]}<br>\n' \
           f'<form action="/change_imdb">\n' \
           f'<input type="hidden" id="id" name="imdb_id" value="{imdb_id}">\n' \
           f'<input type="hidden" id="file" name="file" value="{movie_data["file"]}">\n' \
           f'<input type="hidden" id="dir" name="dir" value="{movie_data["directoryId"]}">\n' \
           f'<input type="text" name="new_id" value="{imdb_id}"><input type="submit" value="Change IMDB ID"></form>' \
           f'</html></body>'

    return Markup(page)


@app.route('/change_imdb')
def change_imdb():
    imdb_id = request.args.get('id')
    new_id = request.args.get('new_id')
    file = request.args.get('file')
    directory = request.args.get('dir')
    new_movie = Movie(filename=file, directory=directory)
    new_movie.get_imdb(imdb_id=int(new_id.lstrip('t')))
    db = database()
    result = db.insert_movie(new_movie)
    if result['status'] == 'duplicate':
        return Markup(f'<html>New IMDB ({new_id}) already exists in database. Entry not changed.<br>\n'
                      f'<a href="/">Movie List</a>\n</html>')
    else:
        db.delete(imdb_id=imdb_id)
        return redirect(f'/?imdb_id={new_id.lstrip("t")}')


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
        url = f'/get_imdb?db={file[0]}&file={urllib.parse.quote(file[1])}&dir={urllib.parse.quote(file[2])}'
        page += f'<a href="{url}">{file[0]}: {file[2]}/{file[1]}</a><br>\n'
    page += '</body></html>'

    return Markup(page)


@app.route('/get_imdb')
def get_imdb():
    db_num = request.args.get('db')
    file = request.args.get('file')
    dir = request.args.get('dir')
    page = f'<html><body>{db_num}<br>{file}<br>{dir}<br>\n' \
           f'<form action="/set_imdb">' \
           f'<input type="hidden" id="db" name="db" value="{db_num}">' \
           f'<input type="hidden" id="file" name="file" value="{file}">' \
           f'<input type="hidden" id="dir" name="dir" value="{dir}">' \
           f'<input type="text" name="imdb_id"><input type="submit" value="Set IMDB ID"></form>' \
           f'</html></body>'

    return Markup(page)


@app.route('/set_imdb')
def set_imdb():
    db = database()
    db_num = request.args.get('db')
    file = request.args.get('file')
    dir = request.args.get('dir')
    imdb_id = request.args.get('imdb_id').lstrip('t')
    movie = Movie(filename=file, directory=dir)
    movie.get_imdb(imdb_id=imdb_id.lstrip('t'))
    result = db.insert_movie(movie)
    if result['status'] == 'success':
        db.file_error_remove(int(db_num))
        return redirect('/errors')
    else:
        return Markup(result)


if __name__ == '__main__':
    app.run(host=server_ip, port=server_port, debug=True)
# [END gae_python38_app]
