# -*- coding: utf-8 -*-
from mealpaper.settings.base import *

DEBUG = True
THUMBNAIL_DEBUG = True

BASE_URL = 'https://'
CLIENT_BASE_URL = 'https://'
ALLOWED_HOSTS = ['*', ]

BASE_PATH = "/var/www/mealpaper/api"
PRODUCTION_BASE_URL = 'https://'
API_BASE_URL = 'https://'

INSTALLED_APPS = INSTALLED_APPS + THIRD_PARTY_APPS + PROJECT_APPS

FILE_UPLOAD_PERMISSIONS = 0o777

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'mealpaper',
        'USER': 'mealpaper_db_user',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '5432'
    }
}
