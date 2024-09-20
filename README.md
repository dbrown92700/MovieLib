# Install

- Clone repo
> git clone https://github.com/dbrown92700/MovieLib
- In the MovieLib direectory created by the clone
  - create a virtual environment, activate it and install requirements
  > python -m venv venv\
  > source venv/bin/activate\
  > pip install -r requirements.txt
- Install apache2
> sudo apt install apache2
- Install mysql. 
> sudo apt install mysql-server
- Create a local mysql user
> sudo mysql \
> CREATE USER 'username'@'localhost' IDENTIFIED BY 'the_secure_password'; \
> GRANT ALL PRIVILEGES ON *\*.** TO 'username'@'localhost';
- Add username and password to python virtual environment
> nano venv/bin/activate
- Add the following lines to the beginning of activate file
  - DB_USER and DB_PASS are the mysql credentials
  - SERVER_IP and SERVER_PORT are for the webserver
  - MOVIE_ROOT is the root directory of the movie files
  - MOVIE_DB is the name of the database.  This can be any name changing it after one has been created will create a new database
  - SCRIPT_NAME is the app name used by Apache.  Use '' if it's at the root
> export DB_USER='username' \
> export DB_PASS='the_secure_password'\
> export SERVER_IP='127.0.0.1'\
> export SERVER_PORT='8111'\
> export MOVIE_ROOT='/home/db/MovieDirectory'\
> export MOVIE_DB='movieLib'\
> export SCRIPT_NAME=''
- Create a movie_server.wsgi file using the example and edit the environment variables appropriately
- Create an apache web directory and link appropriate files
> sudo mkdir /var/www/MovieLib\
> cd /var/www/MovieLib\
> sudo ln -s /home/db/Documents/MovieLib/movie_server.py movie_server.py\
> sudo ln -s /home/db/Documents/MovieLib/static static\
> sudo ln -s /home/db/Documents/MovieLib/templates templates
- Link the apache site file and enable the site
> 