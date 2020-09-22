from mealpaper.settings.base import *

DEBUG = True
THUMBNAIL_DEBUG = True

CLIENT_BASE_URL = 'http://mealpaper.codebnb.me'
BASE_URL = 'http://mealpaper.codebnb.me/'
ALLOWED_HOSTS = ['*', ]

BASE_PATH = "/var/www/subdomains/codebnb/mealpaper/public_html"

THIRD_PARTY_APPS += [
    'debug_toolbar',
    'django_extensions',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INSTALLED_APPS = INSTALLED_APPS + THIRD_PARTY_APPS + PROJECT_APPS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'mealpaper',
        'USER': 'mealpaper_db_manager',
        'PASSWORD': '123456ab',
        'HOST': '127.0.0.1',
        'PORT': '5432'
    }
}

