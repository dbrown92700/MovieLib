Changes to imdb.com broke several elements of the movie parser.  See:

https://github.com/cinemagoer/cinemagoer/issues/537

I've fixed the necessary elements in the parser in the attached file. Replace the existing movieParser.py file in:

/venv/lib/Python3.xx/site-packages/imdb/parser/http

I've only fixed the specific elements needed. If additional elements are needed, the XPATH tester at https://scrapfly.io/web-scraping-tools/css-xpath-tester is very helpful.

Changes in Nov 2025 further broke.  Use the following command to install the latest repo and swap the movieParser.py files to fix top250 and runtimes.
> pip install git+https://github.com/cinemagoer/cinemagoer