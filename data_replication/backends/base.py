# -*- coding: utf-8 -*-
"""base.py: Django """

import logging
import datetime
from collections import OrderedDict

from django.contrib.admin.options import get_content_type_for_model
from django.utils.timezone import now
from kombu.exceptions import OperationalError

__author__ = 'Steven Klass'
__date__ = '9/25/17 16:15'
__copyright__ = 'Copyright 2017 IC Manage. All rights reserved.'
__credits__ = ['Steven Klass', ]

log = logging.getLogger(__name__)

class ImproperlyConfiguredException(Exception):
    pass


def make_sure_mysql_usable():
    from django.db import connection, connections
    if connection.connection and not connection.is_usable():
        del connections._connections.default


class BaseReplicationCollector(object):
    model = None
    change_keys = []
    field_map = OrderedDict()
    search_quantifiers = None

    def __init__(self, reset=False, max_count=None, **kwargs):
        self.last_look = None
        self.locked = False
        self.query_time = None
        self.add_pks = []
        self.update_pks = []
        self.delete_pks = []
        self._accounted_pks = []
        self._queryset_pks = []
        self.skip_locks = True
        self.reset = reset
        self.output_file = None
        self.max_count = max_count
        self.use_subtasks = kwargs.get('use_subtasks', True)

        self.log_level = kwargs.get('log_level')
        if self.log_level:
            log.setLevel(self.log_level)

        if self.get_model() is None:
            raise AttributeError("You must provide a reference model by defining the attribute `model` or redefine `get_model()`")
        if not self.change_keys:
            raise AttributeError(
                "You must provide a a date to reference changes by setting the attribute `change_keys`")

    def get_model(self):
        return self.model

    def get_queryset(self):
        order = ['-%s' % x for x in self.change_keys]
        return self.get_model().objects.all().order_by(*order)

    @property
    def search_quantifier(self):
        data = ""
        if self.search_quantifiers:
            data = self.search_quantifier
        return data + " model={}".format(self.model._meta.model_name)

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
                del_pks = Replication.objects.filter(content_type=self.content_type, tracker=self.last_look)
                self._delete_items(list(del_pks.values_list('object_id', flat=True)))
                self.last_look.last_updated = prior_date
            self.last_look.state = 2
            self.last_look.save()
        self.locked = True

    def unlock(self):
        """Sets our last look and open the db"""
        self.last_look.state = 0
        if not self.reset and not self.max_count:
            self.last_look.last_updated = self.query_time
        else:
            from data_replication.models import Replication
            replications = Replication.objects.filter(content_type=self.content_type, tracker=self.last_look)
            try:
                self.last_look.last_updated = max(list(replications.values_list('last_updated', flat=True)))
            except ValueError:
                pass
        self.last_look.save()
        self.locked = False

    @property
    def accounted_pks(self):

        from data_replication.models import Replication

        if len(self._accounted_pks):
            return self._accounted_pks

        make_sure_mysql_usable()
        self._accounted_pks = Replication.objects.filter(
            tracker=self.last_look).values_list('object_id', flat=True)

        return self._accounted_pks

    @property
    def changed_queryset_pks(self):
        if len(self._queryset_pks):
            return self._queryset_pks

        self.query_time = now()

        make_sure_mysql_usable()
        kwargs = {'%s__gt' % k: self.last_look.last_updated for k in self.change_keys}
        self._queryset_pks = self.get_queryset().filter(**kwargs).values_list('pk', flat=True)

        return self._queryset_pks

    def get_actions(self):
        assert self.locked, "You need to lock the db first"

        if self.delete_pks or self.add_pks or self.update_pks:
            return self.add_pks, self.update_pks, self.delete_pks

        change_pks = self.changed_queryset_pks
        accounted_pks = self.accounted_pks

        make_sure_mysql_usable()
        self.delete_pks = list(set(accounted_pks) - set(list(self.get_queryset().values_list('pk', flat=True))))
        self.add_pks = list(set(change_pks) - set(accounted_pks))
        self.update_pks = list(set(accounted_pks).intersection(set(change_pks) - set(self.add_pks)))

        log.info("%s identified a potential of %d add actions, %d update actions and %d delete actions",
                 self.verbose_name, len(self.add_pks), len(self.update_pks), len(self.delete_pks))

        return (self.add_pks, self.update_pks, self.delete_pks)

    def analyze(self):

        try:
            self.lock()
        except RuntimeError as err:
            log.info("Unable to lock! - %r", err)
            return err

        log.debug("Analyzing %s replication of %s", self.last_look.get_replication_type_display(), self.verbose_name)
        (add_pks, update_pks, delete_pks) = self.get_actions()

        msg = "Analyzed %s replication of %s" % (
            self.last_look.get_replication_type_display(), self.verbose_name)

        delete_pks = update_pks + delete_pks
        delete_pks = delete_pks[:self.max_count] if self.max_count is not None else delete_pks
        if len(delete_pks):
            self._delete_items(delete_pks)
            msg += " deleted %d items" % len(delete_pks)

        add_pks = add_pks + update_pks
        add_pks = add_pks[:self.max_count] if self.max_count is not None else add_pks
        if len(add_pks):
            self._add_items(add_pks)
            msg += " added %d items" % len(add_pks)

        if self.max_count:
            log.info("%s reduced a max of %d add actions and %d delete actions",
                     self.verbose_name, len(add_pks), len(delete_pks))

        self.unlock()
        return msg

    def _delete_items(self, object_pks):
        from data_replication.models import Replication
        self.delete_items(object_pks)
        make_sure_mysql_usable()
        Replication.objects.filter(
            tracker=self.last_look,
            object_id__in=object_pks,
            content_type=self.content_type,).delete()

    def delete_items(self, object_pks):
        raise NotImplemented

    @property
    def task_name(self):
        raise NotImplemented

    def get_task_kwargs(self):
        return {}

    @classmethod
    def add_items(cls, chunk_ids):
        """Given a chuck of items get some information"""
        raise NotImplemented("You need to figure this out..")

    def _add_items(self, object_pks, chunk_size=1000):
        from data_replication.models import Replication
        bulk_inserts = []
        for item in self.get_queryset().filter(pk__in=object_pks).values_list('pk', *self.change_keys):
            item = list(item)
            pk = item.pop(0)
            last_updated = max(item)
            bulk_inserts.append(
                dict(content_type=self.content_type, tracker=self.last_look,
                     object_id=pk, defaults=dict(state=0, last_updated=last_updated)))
        if not len(bulk_inserts):
            return

        for replication_data in bulk_inserts:
            make_sure_mysql_usable()
            try:
                Replication.objects.get_or_create(**replication_data)
            except:
                log.error("Issue with creating %r".format(replication_data))

        log.debug("Added %d replication entries", len(bulk_inserts))

        def chunks(l, n):
            """Yield successive n-sized chunks from l."""
            for i in range(0, len(l), n):
                yield l[i:i + n]

        for count, chunk in (enumerate(chunks(object_pks, chunk_size))):
            kwargs = {
                'object_ids': chunk,
                'tracker_id': self.last_look.id,
                'content_type_id': self.content_type.id
            }

            kwargs.update(self.get_task_kwargs())

            if self.use_subtasks:
                try:
                    self.task_name.delay(**kwargs)
                except OperationalError as err:
                    log.error("Unable dispatch task %s - %s", self.task_name, err)
                    self.task_name(**kwargs)
            else:
                self.task_name(**kwargs)

