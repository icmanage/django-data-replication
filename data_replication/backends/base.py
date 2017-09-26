# -*- coding: utf-8 -*-
"""base.py: Django """

from __future__ import unicode_literals
from __future__ import print_function

import logging
import datetime
from collections import OrderedDict

from django.contrib.admin.options import get_content_type_for_model
from django.utils.timezone import now


__author__ = 'Steven Klass'
__date__ = '9/25/17 16:15'
__copyright__ = 'Copyright 2017 IC Manage. All rights reserved.'
__credits__ = ['Steven Klass', ]

log = logging.getLogger(__name__)


class BaseReplicationCollector(object):
    model = None
    fields = ('pk',)
    change_keys = []
    field_map = OrderedDict()

    def __init__(self, reset=False, max_count=None):
        self.last_look = None
        self.locked = False
        self.query_time = None
        self.add_pks = []
        self.update_pks = []
        self.delete_pks = []
        self._accounted_pks = []
        self._queryset_pks = []
        self.splunk_ready = False
        self.skip_locks = True
        self.reset = reset
        self.output_file = None
        self.max_count = max_count

        if self.get_model() is None:
            raise AttributeError("You must provide a reference model by defining the attribute `model` or redefine `get_model()`")
        if not self.change_keys:
            raise AttributeError(
                "You must provide a a date to reference changes by setting the attribute `change_keys`")

    def get_model(self):
        return self.model

    def get_queryset(self, **kwargs):
        return self.get_model().objects.filter(**kwargs)

    @property
    def content_type(self):
        return get_content_type_for_model(self.get_model())

    @property
    def verbose_name(self):
        return self.get_model()._meta.verbose_name.title()

    def lock(self):
        from data_replication.models import Replication, ReplicationTracker

        prior_date = now() - datetime.timedelta(days=365 * 100)
        try:
            self.last_look = ReplicationTracker.objects.get(
                content_type=self.content_type,
                replication_type=self.replication_type)
        except ReplicationTracker.DoesNotExist:
            self.last_look = ReplicationTracker.objects.create(
                content_type=self.content_type,
                replication_type=self.replication_type,
                last_updated=prior_date, state=2)
        else:
            if self.last_look.state == 0:
                if not self.skip_locks:
                    raise RuntimeError("Already processing")
            if self.reset:
                log.warning("Resetting {}".format(self.verbose_name))
                Replication.objects.filter(content_type=self.content_type,
                                           replication_type=self.replication_type).delete()
                self.last_look.last_updated = prior_date
            self.last_look.state = 2
            self.last_look.save()
        self.locked = True

    def unlock(self):
        """Sets our last look and open the db"""
        self.last_look.state = 0
        self.last_look.last_updated = self.query_time
        self.last_look.save()
        self.locked = False

    @property
    def accounted_pks(self):

        from data_replication.models import Replication

        if len(self._accounted_pks):
            return self._accounted_pks

        self._accounted_pks = Replication.objects.filter(
            tracker=self.last_look).values_list('object_id', flat=True)

        return self._accounted_pks

    @property
    def changed_queryset_pks(self):
        if len(self._queryset_pks):
            return self._queryset_pks

        self.query_time = now()

        kwargs = {'%s__gt' % k: self.last_look.last_updated for k in self.change_keys}
        self._queryset_pks = self.get_queryset(**kwargs).values_list('pk', flat=True)

        return self._queryset_pks

    def get_actions(self):
        assert self.locked, "You need to lock the db first"

        if self.delete_pks or self.add_pks or self.update_pks:
            return self.add_pks, self.update_pks, self.delete_pks

        change_pks = self.changed_queryset_pks
        accounted_pks = self.accounted_pks

        self.delete_pks = list(set(accounted_pks) - set(list(self.get_queryset().values_list('pk', flat=True))))
        self.add_pks = list(set(change_pks) - set(accounted_pks))
        self.update_pks = list(set(accounted_pks).intersection(set(change_pks) - set(self.add_pks)))

        log.info("%s identified %d add actions, %d update actions and %d delete actions",
                 self.verbose_name, len(self.add_pks), len(self.update_pks), len(self.delete_pks))

        return (self.add_pks, self.update_pks, self.delete_pks)

    def analyze(self):

        try:
            self.lock()
        except RuntimeError as err:
            log.info("Unable to lock! - %r", err)
            return err

        log.debug("Getting actions")
        (add_pks, update_pks, delete_pks) = self.get_actions()

        delete_pks = update_pks + delete_pks
        delete_pks = delete_pks[:self.max_count] if self.max_count else delete_pks
        self._delete_items(delete_pks)

        add_pks = add_pks + update_pks
        add_pks = add_pks[:self.max_count] if self.max_count else add_pks
        self._add_items(add_pks)

        self.unlock()

    def _delete_items(self, object_pks):
        from data_replication.models import Replication
        self.delete_items(object_pks)
        Replication.objects.filter(
            tracker=self.last_look,
            object_id__in=object_pks,
            content_type=self.content_type,).delete()

    def delete_items(self, object_pks):
        raise NotImplemented

    def _add_items(self, object_pks):
        from data_replication.models import Replication
        self.add_items(object_pks)
        bulk_inserts = []
        for item in self.get_queryset(pk__in=object_pks).values_list('pk', *self.change_keys):
            item = list(item)
            pk = item.pop(0)
            last_updated = max(item)
            bulk_inserts.append(
                Replication(content_type=self.content_type, tracker=self.last_look,
                            object_id=pk, state=1, last_updated=last_updated))
        if len(bulk_inserts):
            Replication.objects.bulk_create(bulk_inserts)

    def add_items(self, object_pks):
        raise NotImplemented
