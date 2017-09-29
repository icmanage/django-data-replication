# -*- coding: utf-8 -*-
"""conf.py: Django """

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

from appconf import AppConf
from django.conf import settings


__author__ = 'Steven Klass'
__date__ = '9/26/17 10:28'
__copyright__ = 'Copyright 2011-2017 Pivotal Energy Solutions. All rights reserved.'
__credits__ = ['Steven Klass', ]


__all__ = ('settings', 'DataMigrationConf')


class DataMigrationConf(AppConf):
    """Settings for data replication."""

    SPLUNK_HOST = 'localhost'
    """
    The host for Splunk.

        SPLUNK_HOST = "splunk.com" 
    """

    SPLUNK_SCHEME = 'https'
    """
    Scheme used for connecting to splunk.

        SPLUNK_SCHEME = "http" 
    """

    SPLUNK_PORT = '8089'
    """
    Port used for connecting to splunk.

        SPLUNK_PORT = "8090" 
    """

    SPLUNK_USERNAME = 'admin'
    """
    User used for connecting to splunk.

        SPLUNK_USERNAME = "8090" 
    """

    SPLUNK_PASSWORD = 'password'
    """
    Password used for connecting to splunk.

        SPLUNK_PASSWORD = "8090" 
    """

    SPLUNK_APP = 'search'
    """
    App used for connecting to splunk.

        SPLUNK_APP = "foo" 
    """

    MONGO_CONNECTION_URI = None
    """A short cut in lieu of filling out all of the data.
    
    """

    MONGO_DB_NAME = None