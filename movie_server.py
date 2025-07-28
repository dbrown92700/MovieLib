#!python3

__author__ = "David Brown <dbrown92700@gmail.com>"
__contributors__ = []

from datetime import datetime

from flask import Flask, request, render_template, redirect, session
from markupsafe import Markup
import os
from movie_sql import DataBase
import urllib.parse
from movie import Movie
from fix_db import top250list

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
    series = request.args.get('series') or ''
    name = request.args.get('name') or ''
    plot = request.args.get('plot') or ''
    page = int(request.args.get('page') or '1')
    rating = float(request.args.get('rating') or '-1.1')
    year_min = int(request.args.get('year_min') or '0')
    year_max = int(request.args.get('year_max') or '0')
    top250 = request.args.get('top250') or False
    length = int(request.args.get('length') or '0')
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
                                        rating=rating, year_min=year_min, year_max=year_max, top250=top250,
                                        plot=plot, length=length, series=series,
                                        watched=watched, wants=wants,
                                        sort=sort, direction=direction)
    match_list = db.db_to_dict(movies)

    movie_table = ''
    for movie in match_list:
        if movie['top250rank'] == 888:
            rank = '<br>OFF'
        elif movie['top250rank'] < 900:
            rank = f'<br>#{movie["top250rank"]}'
        else:
            rank = ''
        if movie['dateAdded']:
            da = datetime.fromtimestamp(movie['dateAdded'])
            date_added = f'{da.year}/{da.month}/{da.day}'
        else:
            date_added = 'UNK'
        run_time = 'UNK'
        if movie['runTime'] and movie['runTime'] < 999:
                run_time = f'{int(movie["runTime"] / 60)}:{movie["runTime"] % 60:02}'
        movie_table += (f'<tr>\n'
                        f'<td width=200>'
                        f'<a href="https://imdb.com/title/tt{movie["imdb_id"]}/" target="_imdb">'
                        f'{movie["title"]}</a><br>\n'
                        f'{movie["year"]}<br>\n')
        for s in movie["series"]:
            movie_table += f'<b>Series</b>: <a href="/?series={s}">{s}</a><br>\n'
        movie_table += (f'<b>Runtime</b>: {run_time}<br>\n'
                        f'<b>Added</b>: {date_added}\n'
                        f'<br><br><div align=center><a href="{app_url}/edit?id={movie["imdb_id"]}">Edit</a>'
                        f'</div></td>\n'
                        f'<td width=90 align=left><img src="{movie["coverUrl"]}" height=120 width=80></td>\n'
                        f'<td width=30>{movie["rating"]}{rank}</td>\n'
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
        movie_table += (f'<tr><td style="border-bottom: 2px solid black;" align="right"><b>Location:&nbsp</b></td>'
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

    series_menu = ''
    full_series_list = list(db.series_dict.keys()).copy()
    full_series_list.sort()
    for ser in full_series_list:
        selected = ''
        if series == ser:
            selected = ' selected'
        series_menu += f'<option value="{ser}"{selected}>{ser}</option>\n'

    top250_radio = f'<input type="radio" name="top250" value="True" {"checked" if top250=="True" else ""}>'

    url = (f'{app_url}/?name={name.replace(' ', '+')}&genre={genre}&watched={watched}&wants={wants}&'
           f'rating={rating if rating>0 else ""}&top250={"True" if top250=="True" else ""}&sort={sort}&'
           f'direction={direction}&pagesize={pagesize}&length={length if length>0 else ""}&'
           f'year_min={year_min if year_min>0 else ""}&year_max={year_max if year_max>0 else ""}')
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
    return render_template('list_movies.html', genre_menu=Markup(genre_menu), name=' '.join(name),
                           pages=Markup(pages), movie_table=Markup(movie_table), app_url=app_url,
                           series_menu=Markup(series_menu), top250_radio=Markup(top250_radio), user=db.user)


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
    page = (f'<html><body><br><h1>Filename: {movie_data["file"]}</h1><br><br>\n'
            f'<table>'
            f'<tr><form action="/change_imdb">'
            f'<td>'
            f'<input type="submit" value="Change IMDB ID"></td>\n'
            f'<td>'
            f'<input type="hidden" id="imdb_id" name="imdb_id" value="{imdb_id}">\n'
            f'<input type="hidden" id="file" name="file" value="{movie_data["file"]}">\n'
            f'<input type="hidden" id="dir" name="dir" value="{movie_data["directoryId"]}">\n'
            f'<input type="text" name="new_id" value="{imdb_id}"></td>'
            f'</form></tr>\n'
            f'<tr><form action="/delete?imdb_id={imdb_id}">\n'
            f'<td><input type="submit" value="Delete Entry"></td>'
            f'<td><input type="hidden"id="imdb_id" name="imdb_id" value="{imdb_id}"></td>\n'
            f'</form></tr>\n'
            f'<tr style="vertical-align:top;"><form action="/change_genres" method="post">\n'
            f'<td><input type="submit" value="Modify Genres"></td>\n'
            f'<td><input type="hidden" id="imdb_id" name="imdb_id" value="{imdb_id}">\n')

    genres = list(db.genre_dict.keys())
    genres.sort()
    for genre in genres:
        checked = ""
        if genre in db.movie_genres(imdb_id):
            checked = " checked"
        page += f'<input type="checkbox" id="{genre}" name="{genre}" value="{genre}"{checked}>{genre}<br>\n'
    page += (f'New Genre: <input id="New" name="New"><br>\n'
             f'</td></form></tr>\n'
             f'<tr style="vertical-align:top;"><form action="/change_series" method="post">\n'
             f'<td><input type="submit" value="Modify Series"></td>\n'
             f'<td><input type="hidden" id="imdb_id" name="imdb_id" value="{imdb_id}">\n')

    series = list(db.series_dict.keys())
    series.sort()
    for ser in series:
        checked = ""
        if ser in db.movie_series(imdb_id):
            checked = " checked"
        page += f'<input type="checkbox" id="{ser}" name="{ser}" value="{ser}"{checked}>{ser}<br>\n'

    page += (f'New Series: <input id="New" name="New"><br>\n'
             f'</td></form></tr></table>\n'
             f'</html></body>')

    return Markup(page)


@app.route('/change_imdb')
def change_imdb():
    imdb_id = request.args.get('imdb_id')
    new_id = request.args.get('new_id')
    file = request.args.get('file')
    directory = request.args.get('dir')
    new_movie = Movie(filename=file, directory=directory)
    new_movie.get_imdb(imdb_id=new_id.lstrip('t'))
    db = database()
    result = db.insert_movie(new_movie)
    if result['status'] == 'duplicate':
        return Markup(f'<html>New IMDB ({new_id}) already exists in database. Entry not changed.<br>\n'
                      f'<a href="/">Movie List</a>\n</html>')
    else:
        db.delete(imdb_id=imdb_id)
        return redirect(f'/?imdb_id={new_id.lstrip("t")}')

@app.route('/delete')
def delete_movie():
    db=database()
    imdb_id = request.args.get('imdb_id')
    db.delete(imdb_id=imdb_id)
    return redirect('/')

@app.route('/change_genres', methods=['POST'])
def change_genres():
    db = database()
    imdb_id = request.form.get('imdb_id')
    genres = list(dict(request.form).values())
    genres.remove(imdb_id)
    try:
        genres.remove('')
    except ValueError:
        genres = list(set(genres))
    db.genres_update(movie_id=imdb_id, genres=genres)

    return redirect(f'/?imdb_id={imdb_id}')

@app.route('/change_series', methods=['POST'])
def change_series():
    db = database()
    imdb_id = request.form.get('imdb_id')
    series = list(dict(request.form).values())
    series.remove(imdb_id)
    try:
        series.remove('')
    except ValueError:
        series = list(set(series))
    db.series_update(movie_id=imdb_id, series=series)

    return redirect(f'/?imdb_id={imdb_id}')

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


@app.route('/top250')
def top250():
    db = database()
    top250dict = top250list()
    top250table = ('<html><body>\n'
                   '<table style="border-collapse: collapse;">\n')
    for imdb_id in top250dict:
        movie = db.movie_list(imdb_id=imdb_id)
        if movie[1] == 0:
            result = "Not Found"
            color = "#ff9999"
            title = top250dict[imdb_id]['title']
        else:
            this_movie = db.db_to_dict(movie[0])[0]
            title = f"{this_movie['title']} [{this_movie['year']}]"
            if this_movie['top250rank'] == top250dict[imdb_id]['rank']:
                result = ""
                color = "#ccff66"
            else:
                result = (f"Moved from {'Unranked' if this_movie['top250rank'] > 250 else this_movie['top250rank']} "
                          f"to {top250dict[imdb_id]['rank']}")
                color = "#ffff99"
                db.update_movie(imdb_id=imdb_id, column='top250rank', value=top250dict[imdb_id]['rank'])
        top250table += (f"<tr style='border-collapse:collapse; background-color:{color};'>"
                        f"<td>{top250dict[imdb_id]['rank']} </td>"
                        f"<td> {title}</td>"
                        f"<td>{result}</td></tr>\n")
    db_top250 = db.db_to_dict(db.movie_list(top250=True, pagesize=0)[0])
    for movie in db_top250:
        imdb_id = movie['imdb_id']
        if imdb_id not in top250dict:
            top250table += (f"<tr style='background-color:#ff9966'>"
                            f"<td>{'' if movie['top250rank']==888 else movie['top250rank']} </td>"
                            f"<td> {movie['title']} [{movie['year']}]</td>"
                            f"<td>Dropped from Top 250</td></tr>\n")
            db.update_movie(imdb_id=imdb_id, column='top250rank', value=888)

    top250table += f'</table></body>'

    return Markup(top250table)

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
