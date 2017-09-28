# -*- coding: utf-8 -*-
"""models.py: Django data_replication"""

from __future__ import unicode_literals
from __future__ import print_function

import importlib
import inspect
import logging

from django.apps import apps
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from data_replication.backends.base import BaseReplicationCollector
from data_replication.backends.mongo import MongoReplicator
from data_replication.backends.splunk import SplunkReplicator

__author__ = 'Steven Klass'
__date__ = '9/21/17 07:56'
__copyright__ = 'Copyright 2017 IC Manage. All rights reserved.'
__credits__ = ['Steven Klass', ]

log = logging.getLogger(__name__)

REPLICATION_TYPES = ((1, "Mongo"), (2, "Splunk"))


class ReplicationTracker(models.Model):
    """Tracks a general model processing"""
    replication_type = models.IntegerField(choices=REPLICATION_TYPES)
    content_type = models.ForeignKey(ContentType)
    state = models.SmallIntegerField(choices=[(1, 'Ready'), (2, 'In-Process')])
    last_updated = models.DateTimeField()

    def __unicode__(self):
        return "%r replication of %r" % (
            self.get_replication_type_display(), self.content_type.model_class()._meta.verbose_name)

    def get_replicator(self, **kwargs):

        app_config = apps.get_app_config(self.content_type.app_label)
        try:
            module = app_config.module.replication
        except AttributeError:
            try:
                module = importlib.import_module("{}.replication".format(self.content_type.app_label))
            except ImportError:
                raise ImportError("Unable to find replication.py in app %s" % self.content_type.app_label)

        target_module = SplunkReplicator if self.replication_type == 2 else MongoReplicator
        ignored_classes = [BaseReplicationCollector, SplunkReplicator, MongoReplicator]

        if module:
            for name in dir(module):
                Replcate = getattr(module, name)
                if inspect.isclass(Replcate) and Replcate not in ignored_classes and issubclass(Replcate, target_module):
                    log.debug("Using replicator - %r", Replcate)
                    return Replcate(**kwargs)

        raise IOError("Unable to identify replication module for %s" % self.content_type.app_label)



class Replication(models.Model):
    tracker = models.ForeignKey('ReplicationTracker')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey(ct_field="content_type", fk_field="object_id")

    state = models.IntegerField(choices=((0, "Not Replicated"), (1, "In Storage")))
    last_updated = models.DateTimeField()

    class Meta:
        unique_together = ('content_type', 'object_id', 'tracker')
        permissions = (('view_replication', "View Replication"),)


# This is to be included in the model data you want to push to the replication
#
# class ReplicationMixin(object):
#     def _get_replication_object(self, replication_type):
#         ctype = ContentType.objects.get_for_model(self.__class__)
#         try:
#             obj = Replication.objects.get(content_type__pk=ctype.id, object_id=self.id, replicaion_type=replication_type)
#         except Replication.DoesNotExist:
#             return None
#         return obj
#
#
# class MongoReplicationMixin(ReplicationMixin):
#
#     @property
#     def mongo_replication(self):
#         return self._get_replication_object(1)
#
#     @property
#     def in_mongo(self):
#         obj = self._get_replication_object(1)
#         return obj.state == 1 if obj else False
#
#     @property
#     def _should_replicate_mongo(self):
#         return getattr(self, 'should_replicate_mongo', True)
#
#
# class SplunkReplicationMixin(ReplicationMixin):
#
#     @property
#     def splunk_replication(self):
#         return self._get_replication_object(2)
#
#     @property
#     def in_splunk(self):
#         obj = self._get_replication_object(2)
#         return obj.state == 1 if obj else False
#
#     @property
#     def _should_replicate_mongo(self):
#         return getattr(self, 'should_replicate_splunk', True)
