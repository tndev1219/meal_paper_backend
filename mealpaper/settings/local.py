# -*- coding: utf-8 -*-
from mealpaper.settings.base import *

DEBUG = True
THUMBNAIL_DEBUG = True

ALLOWED_HOSTS = ['*', ]

BASE_PATH = "/var/www/mealpaper/"

INSTALLED_APPS = INSTALLED_APPS + PROJECT_APPS + THIRD_PARTY_APPS

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
