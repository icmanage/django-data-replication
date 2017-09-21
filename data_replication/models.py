# -*- coding: utf-8 -*-
"""models.py: Django data_replication"""

from __future__ import unicode_literals
from __future__ import print_function

import logging

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

__author__ = 'Steven Klass'
__date__ = '9/21/17 07:56'
__copyright__ = 'Copyright 2017 IC Manage. All rights reserved.'
__credits__ = ['Steven Klass', ]

log = logging.getLogger(__name__)


class ReplicationType(models.Model):
    name = models.CharField(max_length=32)
    backend = models.CharField(max_length=128)


class Replication(models):

    replication_type = models.ForeignKey(ReplicationType)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey(ct_field="content_type", fk_field="object_id")

    state = models.IntegerField(choices=((0, "Not Replicated"), (1, "In Storage"), (2, "Removed")))
    last_updated = models.DateTimeField()

    class Meta:
        unique_together = ('content_type', 'object_id', 'replication_type')
        permissions = (('view_replication', "View Replication"),)


# This is to be included in the model data you want to push to the replication

class MongoReplicationMixin(object):

    @property
    def mongo_replication(self):
        ctype = ContentType.objects.get_for_model(self.__class__)
        try:
            obj = Replication.objects.get(content_type__pk=ctype.id, object_id=self.id, replicaion_type__name="mongo")
        except Replication.DoesNotExist:
            return None
        return obj

    @property
    def in_mongo(self):
        ctype = ContentType.objects.get_for_model(self.__class__)
        try:
            obj = Replication.objects.get(content_type__pk=ctype.id, object_id=self.id, replicaion_type__name="mongo")
        except Replication.DoesNotExist:
            return False
        return obj.state == 1

    @property
    def _should_replicate_mongo(self):
        return getattr(self, 'should_replicate_mongo', True)


class SplunkReplicationMixin(object):

    @property
    def splunk_replication(self):
        ctype = ContentType.objects.get_for_model(self.__class__)
        try:
            obj = Replication.objects.get(content_type__pk=ctype.id, object_id=self.id, replicaion_type__name="splunk")
        except Replication.DoesNotExist:
            return None
        return obj

    @property
    def in_splunk(self):
        ctype = ContentType.objects.get_for_model(self.__class__)
        try:
            obj = Replication.objects.get(content_type__pk=ctype.id, object_id=self.id, replicaion_type__name="splunk")
        except Replication.DoesNotExist:
            return False
        return obj.state == 1

    @property
    def _should_replicate_mongo(self):
        return getattr(self, 'should_replicate_splunk', True)
