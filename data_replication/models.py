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

REPLICATION_TYPES = ((1, "Mongo"), (2, "Splunk"))


class Replication(models.Model):
    replication_type = models.IntegerField(choices=REPLICATION_TYPES)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey(ct_field="content_type", fk_field="object_id")

    state = models.IntegerField(choices=((0, "Not Replicated"), (1, "In Storage"), (2, "Removed")))
    last_updated = models.DateTimeField()

    class Meta:
        unique_together = ('content_type', 'object_id', 'replication_type')
        permissions = (('view_replication', "View Replication"),)


# This is to be included in the model data you want to push to the replication

class ReplicationMixin(object):
    def _get_replication_object(self, replication_type):
        ctype = ContentType.objects.get_for_model(self.__class__)
        try:
            obj = Replication.objects.get(content_type__pk=ctype.id, object_id=self.id, replicaion_type=replication_type)
        except Replication.DoesNotExist:
            return None
        return obj


class MongoReplicationMixin(ReplicationMixin):

    @property
    def mongo_replication(self):
        return self._get_replication_object(1)

    @property
    def in_mongo(self):
        obj = self._get_replication_object(1)
        return obj.state == 1 if obj else False

    @property
    def _should_replicate_mongo(self):
        return getattr(self, 'should_replicate_mongo', True)


class SplunkReplicationMixin(ReplicationMixin):

    @property
    def splunk_replication(self):
        return self._get_replication_object(2)

    @property
    def in_splunk(self):
        obj = self._get_replication_object(2)
        return obj.state == 1 if obj else False

    @property
    def _should_replicate_mongo(self):
        return getattr(self, 'should_replicate_splunk', True)
