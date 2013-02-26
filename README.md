evedjango
=========

EVE API and Data Management for Django

$ git clone evedjango.git

$ virtualenv evedjango

$ cd evedjango

$ source bin/activate

(evedjango)$ pip install -r requirements.txt

(evedjango)$ cp settings.py evedjango

Edit evedjango/settings.py

(evedjango)$ python manage.py syncdb

(evedjango)$ python manage.py migrate
