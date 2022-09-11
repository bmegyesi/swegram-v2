import os
from .base import *

DEBUG = True
PRODUCTION = False
BETA = False

ALLOWED_HOSTS = ['127.0.0.1', '*']

STATIC_URL = '/static/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'swegram.db'),
    }
}


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'swegram-local',
    }
}

SESSION_COOKIE_AGE = 8 * 60 * 60
