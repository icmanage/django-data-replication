from django import test
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now

from data_replication import apps
from data_replication.models import ReplicationTracker


class DataReplicationTests(test.TestCase):
    def test_tostring(self):
        ct = ContentType.objects.get_for_model(ReplicationTracker)
        obj = ReplicationTracker.objects.create(replication_type=1, state=1, last_updated=now(), content_type=ct)
        self.assertEqual(str(obj), "u'Mongo' replication of u'replication tracker'")

    # def test_get_replicator(self, **kwargs):
    #     ct = ContentType.objects.get_for_model(ReplicationTracker)
    #     app_config = apps.get_app_config('data_replication')
    #     self.assertEqual(ReplicationTracker.objects.count(), 0)