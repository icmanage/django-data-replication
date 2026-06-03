# -*- coding: utf-8 -*-
from __future__ import unicode_literals

__copyright__ = 'Copyright 2011-2026 IC Manage. All rights reserved.'

"""Tests for ReplicationTracker.get_replicator() discovery."""

import datetime

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.utils.timezone import now

from data_replication.models import ReplicationTracker
from example.models import Example
from example.replication import ExampleSplunkReplicator


def _tracker():
    return ReplicationTracker.objects.create(
        content_type=ContentType.objects.get_for_model(Example),
        replication_type=2,  # Splunk
        last_updated=now() - datetime.timedelta(days=3650),
        state=1,
    )


class GetReplicatorTests(TestCase):
    def test_discovers_single_replicator_for_content_type(self):
        # No replication_class_name + exactly one matching replicator.
        replicator = _tracker().get_replicator()
        self.assertIs(replicator, ExampleSplunkReplicator)

    def test_returns_instance_when_named(self):
        replicator = _tracker().get_replicator(
            replication_class_name='ExampleSplunkReplicator', use_subtasks=False)
        self.assertIsInstance(replicator, ExampleSplunkReplicator)
        self.assertFalse(replicator.use_subtasks)
