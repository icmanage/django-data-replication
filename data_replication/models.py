# -*- coding: utf-8 -*-
"""models.py: Django data_replication"""

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
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    state = models.SmallIntegerField(choices=[(1, 'Ready'), (2, 'In-Process')])
    last_updated = models.DateTimeField()

    def __str__(self):
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

        replication_class_name = kwargs.get('replication_class_name')
        options = []
        if module:
            for name in dir(module):
                Replcate = getattr(module, name)
                if inspect.isclass(Replcate) and Replcate not in ignored_classes and issubclass(Replcate, target_module):
                    if ContentType.objects.get_for_model(Replcate.model) == self.content_type:
                        if replication_class_name is not None:
                            if replication_class_name == Replcate().__class__.__name__:
                                log.debug("Using matching replication with class name %s - %r", replication_class_name, Replcate)
                                return Replcate(**kwargs)
                        else:
                            options.append(Replcate)
        if len(options) == 1:
            return options[1]
        elif len(options) > 1:
            raise IOError("Unable to identify replication module for %s many found use replication_class_name %r" % self.content_type.app_label, options)
        raise IOError("Unable to identify replication module for %s" % self.content_type.app_label)



class Replication(models.Model):
    tracker = models.ForeignKey('ReplicationTracker', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
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
