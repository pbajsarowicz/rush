"""
This is an example local_settings.py, which stores custom settings,
different from project ones, provided for purpose of development.

Create a your own local settings in the `rush/local_settings.py`,
with the same content as here.

Then, to run server with them, provide extra argument `--settings`, e.g.
./manage.py runserver --settings=rush.local_settings
"""

from rush.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
