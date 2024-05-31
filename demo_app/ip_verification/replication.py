# -*- coding: utf-8 -*-
"""replication.py: Django ip_verification"""

from __future__ import unicode_literals
from __future__ import print_function

import logging

import datetime
import socket

import pytz

from data_replication.backends.mongo import MongoReplicator
from data_replication.backends.splunk import SplunkReplicator

from .models import TestResultLink, RegressionTagSummary, RegressionAnalytic

__author__ = 'Steven Klass'
__date__ = '9/25/17 16:14'
__copyright__ = 'Copyright 2011-2022 IC Manage Inc IC Manage.. All rights reserved.'
__credits__ = ['Steven Klass', ]

log = logging.getLogger(__name__)


class TestResultReplicatorMixin(object):
    model = TestResultLink
    change_keys = ['last_used']

    def __init__(self, **kwargs):
        self.summary_ids = []

        summary_ids = kwargs.pop('summary_ids', None)
        if summary_ids:
            self.summary_ids = summary_ids
        summary_id = kwargs.pop('summary_id', None)
        if summary_id:
            self.summary_ids.append(summary_id)

        super(TestResultReplicatorMixin, self).__init__(**kwargs)

    # P: question: we concluded that the bug was likely in the changed query set function,
    # but with the prints I put in, it does not even find/get the TestResultLinkQuerySet objects.
    # Would that not maybe mean the issue is under the get transaction?
    def get_queryset(self):
        incomplete_jobs = list(RegressionTagSummary.objects.incomplete_jobs().values_list('id', flat=True))
        if self.summary_ids:
            kw = {'summary_id__in': self.summary_ids}
        else:
            kw = {'summary_id__isnull': False, 'last_used__gte': datetime.datetime(2017, 1, 1)}
        return self.get_model().objects.filter(**kw).exclude(summary_id__in=incomplete_jobs).order_by('-id')

    @property
    def changed_queryset_pks(self):
        # We don't really look at the changed date for this
        from data_replication.models import Replication

        # P: Where getting this from?
        if len(self._queryset_pks):
            return self._queryset_pks

        # All of them
        # P: At this point when the data acquisition fails it already has no pk values
        model_pk_date_dict = dict(self.get_queryset().values_list('pk', 'last_used'))
        print('model pk dict:', model_pk_date_dict)

        # The ones we know about.

        # TODO It is somewhere in
        replication_pk_date_dict = dict(Replication.objects.filter(
            tracker=self.last_look, object_id__in=model_pk_date_dict.keys()
        ).values_list('object_id', 'last_updated'))
        # TODO Look more into this to see if the naive and timezone data is interfering causing error
        self.query_time = datetime.datetime(1970, 1, 1).replace(tzinfo=pytz.UTC)
        # P: here it is getting the replication data values
        for pk, _date in replication_pk_date_dict.items():
            # Same date ignore (P: ?)
            if model_pk_date_dict.get(pk) and model_pk_date_dict.get(pk) <= _date:
                model_pk_date_dict.pop(pk)
            if _date and _date > self.query_time:
                self.query_time = _date
        # TODO If I had to guess I think this might be bug causation.
        # This is where it is actually filtering in and out the data and updating it

        self._queryset_pks = self.get_queryset().filter(pk__in=model_pk_date_dict.keys()).values_list('pk', flat=True)
        print('query set pks:', self._queryset_pks)
        return self._queryset_pks
        # TODO Here most likely

    @property
    def accounted_pks(self):

        from data_replication.models import Replication

        if len(self._accounted_pks):
            return self._accounted_pks

        self._accounted_pks = Replication.objects.filter(
            tracker=self.last_look,
            object_id__in=self.get_queryset().values_list('pk', flat=True),
        ).values_list('object_id', flat=True)
        return self._accounted_pks

    @classmethod
    def add_items(cls, chunk_ids):
        log.info("Pulling JSON data for %d ids", len(chunk_ids))
        print('replication add_items:', "Pulling JSON data for %d ids", len(chunk_ids))
        return TestResultLink.objects.filter(id__in=chunk_ids).as_json(as_list=True)


class TestResultSplunkReplicator(TestResultReplicatorMixin, SplunkReplicator):
    source_type = "verification"
    source = "tcp://envision"
    host = socket.gethostname()


class TestResultMongoReplicator(TestResultReplicatorMixin, MongoReplicator):
    pass


class RegressionAnalyticSplunkReplicator(SplunkReplicator):
    source_type = "icm_verification_analytic"
    source = "tcp://envision"
    model = RegressionAnalytic
    change_keys = ['last_updated']

    @classmethod
    def add_items(cls, chunk_ids):
        log.info("Pulling JSON data for %d ids", len(chunk_ids))
        return RegressionAnalytic.objects.filter(id__in=chunk_ids).as_json(as_list=True)


class RegressionAnalyticMongoReplicator(MongoReplicator):
    model = RegressionAnalytic
    change_keys = ['last_updated']

    @classmethod
    def add_items(cls, chunk_ids):
        log.info("Pulling JSON data for %d ids", len(chunk_ids))
        return RegressionAnalytic.objects.filter(id__in=chunk_ids).as_json(as_list=True)
