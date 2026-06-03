# -*- coding: utf-8 -*-
from __future__ import unicode_literals

__copyright__ = 'Copyright 2011-2026 IC Manage. All rights reserved.'

"""Django 1.11 settings for the (never-shipped) demo project used to run the
data_replication test suite."""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'demo-only-not-secret'
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'data_replication',
    'example',
]

MIDDLEWARE = []
ROOT_URLCONF = 'demo_app.urls'
TEMPLATES = []
WSGI_APPLICATION = None

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
STATIC_URL = '/static/'

# data_replication connection settings (backends are mocked in tests; the host
# project normally supplies these, so they must exist for SplunkRequest init).
SPLUNK_HOST = 'localhost'
SPLUNK_SCHEME = 'https'
SPLUNK_PORT = '8089'
SPLUNK_USERNAME = 'admin'
SPLUNK_PASSWORD = 'password'
SPLUNK_APP = 'search'
MONGO_CONNECTION_URI = None
MONGO_DB_NAME = None
