# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function

import warnings

from django.conf.global_settings import LOGGING

from .settings import *

__author__ = 'Steven Klass'
__date__ = '5/15/21 8:15 AM'
__copyright__ = 'Copyright 2011-2022 IC Manage Inc. All rights reserved.'
__credits__ = ['Steven Klass', ]


class DisableMigrations(object):
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()

# Handle system warning as log messages
warnings.simplefilter('once')

for handler in LOGGING.get('handlers', []):
    LOGGING['handlers'][handler]['level'] = 'CRITICAL'
for logger in LOGGING.get('loggers', []):
    LOGGING['loggers'][logger]['level'] = 'CRITICAL'

DEFAULT_DB = {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}
if os.environ.get('TRAVIS') is not None:
    DEFAULT_DB = DATABASES['default']

DATABASES = {
    'default': DEFAULT_DB,
}

SILENCED_SYSTEM_CHECKS = ['django_mysql.E016']

CELERY_TASK_ALWAYS_EAGER = CELERY_TASK_EAGER_PROPAGATES = True
CELERYD_HIJACK_ROOT_LOGGER = True