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

Download the latest eve.db (sqlite3 format) from [here](http://www.fuzzwork.co.uk/dump).  Current as of this writing is Retribution 1.1-84566

(evedjango)$ python manage.py eve_import_ccp_dump ccp_dump.db invTypes

(evedjango)$ python manage.py eve_import_ccp_dump ccp_dump.db mapSolarSystems

(evedjango)$ python manage.py eve_import_ccp_dump ccp_dump.db chrFactions
