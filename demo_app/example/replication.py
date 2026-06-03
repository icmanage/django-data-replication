# -*- coding: utf-8 -*-
from __future__ import unicode_literals

__copyright__ = 'Copyright 2011-2026 IC Manage. All rights reserved.'

from data_replication.backends.mongo import MongoReplicator
from data_replication.backends.splunk import SplunkReplicator

from .models import Example


def _example_payload(chunk_ids):
    return [
        {'pk': obj.pk, 'name': obj.name}
        for obj in Example.objects.filter(pk__in=chunk_ids)
    ]


class ExampleSplunkReplicator(SplunkReplicator):
    """Splunk replicator for Example. get_replicator() resolves it
    unambiguously for replication_type=2 (the per-type filter excludes the
    Mongo one below)."""

    model = Example
    change_keys = ['last_updated']

    def delete_items(self, object_pks):
        pass

    @classmethod
    def add_items(cls, chunk_ids):
        return _example_payload(chunk_ids)


class ExampleMongoReplicator(MongoReplicator):
    """Mongo replicator for Example (replication_type=1)."""

    model = Example
    change_keys = ['last_updated']

    def delete_items(self, object_pks):
        pass

    @classmethod
    def add_items(cls, chunk_ids):
        return _example_payload(chunk_ids)
