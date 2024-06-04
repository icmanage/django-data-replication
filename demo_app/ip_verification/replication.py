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

    def get_queryset(self):
        incomplete_jobs = list(RegressionTagSummary.objects.incomplete_jobs().values_list('id', flat=True))
        if self.summary_ids:
            kw = {'summary_id__in': self.summary_ids}
        else:
            kw = {'summary_id__isnull': False, 'last_used__gte': datetime.datetime(2017, 1, 1)}

            queryset = self.get_model().objects.filter(**kw).exclude(summary_id__in=incomplete_jobs).order_by('-id')

        return self.get_model().objects.filter(**kw).exclude(summary_id__in=incomplete_jobs).order_by('-id')

    @property
    def changed_queryset_pks(self):
        from data_replication.models import Replication

        if len(self._queryset_pks):
            return self._queryset_pks

        model_pk_date_dict = dict(self.get_queryset().values_list('pk', 'last_used'))

        replication_pk_date_dict = dict(Replication.objects.filter(
            tracker=self.last_look, object_id__in=model_pk_date_dict.keys()
        ).values_list('object_id', 'last_updated'))
        self.query_time = datetime.datetime(1970, 1, 1).replace(tzinfo=pytz.UTC)
        for pk, _date in replication_pk_date_dict.items():
            # Same date ignore
            if model_pk_date_dict.get(pk) and model_pk_date_dict.get(pk) <= _date:
                model_pk_date_dict.pop(pk)
            if _date and _date > self.query_time:
                self.query_time = _date

        self._queryset_pks = self.get_queryset().filter(pk__in=model_pk_date_dict.keys()).values_list('pk', flat=True)
        return self._queryset_pks

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
