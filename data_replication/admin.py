# -*- coding: utf-8 -*-
"""admin.py: Django """

import logging

from django.contrib import admin

from data_replication.models import ReplicationTracker

__author__ = 'Steven Klass'
__date__ = '9/25/17 15:09'
__copyright__ = 'Copyright 2017 IC Manage. All rights reserved.'
__credits__ = ['Steven Klass', ]

log = logging.getLogger(__name__)


class ReplicationTrackerAdmin(admin.ModelAdmin):
    pass

admin.site.register(ReplicationTracker, ReplicationTrackerAdmin)