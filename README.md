# Install

- Install mysql. 
> sudo apt install mysql-server
- Create a local user
> sudo mysql \
> CREATE USER 'username'@'localhost' IDENTIFIED BY 'the_secure_password'; \
> GRANT ALL PRIVILEGES ON *\*.** TO 'username'@'localhost';
- Add username and password to python virtual environment
> nano venv/bin/activate
- Add the following lines to the beginning of activate file
> export DB_USER='username' \
> export DB_PASS='the_secure_password'

