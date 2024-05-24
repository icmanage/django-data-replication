# from unittest.mock import Mock

from django import test
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.utils.timezone import now

from data_replication import apps
from data_replication.management.commands import replicate
from data_replication.models import ReplicationTracker
from data_replication.tests.factories import replication_tracker_factory
import data_replication.models as models


class DataReplicationTests(TestCase):
    def test_tostring(self):
        ct = ContentType.objects.get_for_model(ReplicationTracker)
        obj = ReplicationTracker.objects.create(replication_type=1, state=1, last_updated=now(), content_type=ct)
        self.assertEqual(str(obj), "u'Mongo' replication of u'replication tracker'")

    def test_replicator_factory(self, **kwargs):
        ct = ContentType.objects.get_for_model(ReplicationTracker)
        rt = replication_tracker_factory()
        self.assertEqual(ReplicationTracker.objects.count(), 1)
        rt = replication_tracker_factory(state=1)
        self.assertEqual(rt.state, 1)
        with self.assertRaises(ImportError):
            self.assertIsInstance(not ct, ReplicationTracker)
        # rt2 = ReplicationTracker.objects.create(state=10)
        # self.assertEqual(rt2.state, 1 or 2)
        # self.assertIsInstance(isinstance(models.module, ReplicationTracker))

    def test_get_replicator_mongo(self):
        rt = replication_tracker_factory(replication_type=1)
        replicator = rt.get_replicator()
        self.assertIn("TestResultMongoReplicator", str(replicator))

    def test_get_replicator_splunk(self):
        rt = replication_tracker_factory(replication_type=2)
        replicator = rt.get_replicator()
        self.assertIn("TestResultSplunkReplicator", str(replicator))

    def test_replication_combo(self):
        self.mt = ContentType.objects.get_for_model(ReplicationTracker)
        obj = ReplicationTracker.objects.create(replication_type=1, content_type=self.mt)
        # self.mt = replicate.Command()
        # Mock the content_type attribute with a dummy object
        self.mt.content_type = MockClass()
        mock_options = [1, 2, 3]
        with self.assertRaises(IOError) as context:
            self.mt.get_replicator(mock_options)
        self.assertIn('replication module', str(context.exception))


class MockClass():
    app_label = 'app'
