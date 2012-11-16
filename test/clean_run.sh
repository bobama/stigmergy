#!/bin/bash

# drop old database files
cd ../database
rm *.sqlite

# drop user and manager keys.
# restore manager keys from archive.
cd ../crypto
find . -name \*.gpg* -exec rm {} \;
tar xvzf manager_keys.tar.gz

# drop intermediate application files
cd ../app
find . -name \*.pyc -exec rm {} \;
find . -name \*.po -exec rm {} \;
rm -rf static/*

# generate intermediate application files
python manage.py collectstatic --noinput
python manage.py makemessages --locale=en
python manage.py makemessages --locale=de

# generate empty database
python manage.py syncdb --noinput

# run application
# python -m trace --trace manage.py runserver --noreload 
python manage.py runserver 
