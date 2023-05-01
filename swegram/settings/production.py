import os
from .base import *

DEBUG = False
PRODUCTION = True
BETA = False

ALLOWED_HOSTS = ['stp.lingfil.uu.se', 'cl.lingfil.uu.se']

STATIC_ROOT = "/local/etc/httpd/html/static/swegram/"
STATIC_URL = '/static/swegram/'

DATABASES = {
    'default': {
        'ENGINE': "django.db.backends.postgresql_psycopg2",
        'NAME': "swegram",
        'HOST': "localhost",
        'PORT': "5432"
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'swegram_db_cache',
    }
}

SESSION_COOKIE_AGE = 8 * 60 * 60
