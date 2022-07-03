# A minimalistic version of settings.py
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'swegram',
        'USER': 'postgres',
        'HOST': 'localhost',
        'PASSWORD': 'password',
        'PORT': '5432'
    }
}


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'unique_snowflake'
    }
}


INSTALLED_APPS = (
    'app',
)


SECRET_KEY = '*****'
