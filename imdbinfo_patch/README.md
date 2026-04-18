The imdbinfo library lacks a way to lookup the top250 movies, but it does have a way to get past the AWS WAF that \
IMDB put in place.

I added a get_top250() method to it.  To use it:

- Replace these two files in the your site-packages directory.  If using venv, these will be under \
venv/lib/python3.xx/site-packages/imdbinfo
- For coding get_top250() returns a diction with imdbId as the keys and rank as values
> from imdbinfo import get_top250
> top = get_top250()