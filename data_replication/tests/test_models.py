from django import test
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now

from data_replication import apps
from data_replication.models import ReplicationTracker
from data_replication.tests.factories import replication_tracker_factory
import data_replication.models as models


class DataReplicationTests(test.TestCase):
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
        # rt2 = ReplicationTracker.objects.create(state=10)
        # self.assertEqual(rt2.state, 1 or 2)
        #self.assertRaisesMessage(self, "Unable to find replication.py in app %s",  ReplicationTracker.content_type.app_label)
        #self.assertIsInstance(isinstance(models.module, ReplicationTracker))

    def test_get_replicator_mongo(self):
        rt = replication_tracker_factory(replication_type=1)
        replicator = rt.get_replicator()
        self.assertIn("TestResultMongoReplicator", str(replicator))

    def test_get_replicator_splunk(self):
        rt = replication_tracker_factory(replication_type=2)
        replicator = rt.get_replicator()
        self.assertIn("TestResultSplunkReplicator", str(replicator))

    def test_replication_combo(self):
        mt = replication_tracker_factory(replication_type=1)
        st = replication_tracker_factory(replication_type=2)
        #this isnt catching the error like intended from models line 62.
        gt = replication_tracker_factory(replication_type=2)
        st.get_replicator()
