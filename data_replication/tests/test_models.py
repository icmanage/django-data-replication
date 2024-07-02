# -*- coding: utf-8 -*-
from django.apps import apps
from django.test import TestCase

from data_replication.models import ReplicationTracker
from data_replication.tests.factories import replication_tracker_factory
from django.contrib.contenttypes.models import ContentType

Example = apps.get_model("example", "Example")
ManyExample = apps.get_model("example", "ManyExample")


class DataReplicationTests(TestCase):
    def setUp(self):
        self.ct = ContentType.objects.get_for_model(Example)

    def test_tostring(self):
        obj = replication_tracker_factory(Example, replication_type="mongo")
        self.assertEqual(str(obj), "'Mongo' replication of 'example'")

    def test_replicator_factory(self, **kwargs):
        rt = replication_tracker_factory(Example, replication_type="splunk", state=1)
        self.assertEqual(ReplicationTracker.objects.count(), 1)
        self.assertEqual(rt.state, 1)

    def test_get_replicator_mongo(self):
        rt = replication_tracker_factory(Example, replication_type=1)
        replicator = rt.get_replicator()
        self.assertIn("TestMongoReplicatorExample", str(replicator))

    def test_get_replicator_splunk(self):
        rt = replication_tracker_factory(Example, replication_type=2)
        replicator = rt.get_replicator()
        self.assertIn("TestSplunkReplicatorExample", str(replicator))

    def test_get_replicator_no_options(self):
        rt = replication_tracker_factory(ManyExample, replication_type=2)
        self.assertRaises(IOError, rt.get_replicator)

    def test_get_replicator_options(self):
        rt = replication_tracker_factory(ManyExample, replication_type=1)
        rt = replication_tracker_factory(ManyExample, replication_type=1)
        self.assertRaises(IOError, rt.get_replicator)
