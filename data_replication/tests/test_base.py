from django.apps import apps
from django.utils.timezone import now
from mock import patch, mock

from django.contrib.auth import get_user_model
from django.test import TestCase

from django.contrib.contenttypes.models import ContentType

from data_replication.backends.base import BaseReplicationCollector
from data_replication.backends.mongo import MongoReplicator
from data_replication.models import Replication
from data_replication.tests.factories import replication_tracker_factory
from data_replication.tests.test_tasks import mock_session

User = get_user_model()
Example = apps.get_model('example', 'Example')


class TestBase(TestCase):

    def setUp(self):
        class FooBar(BaseReplicationCollector):
            model = Example
            change_keys = ['foo']

        self.base_replication_collector = FooBar

    def test_default_values(self):
        instance = TestMongoReplicatorExample()
        self.assertIsNone(instance.last_look)
        self.assertFalse(instance.locked)
        self.assertIsNone(instance.query_time)
        self.assertEqual(instance.add_pks, [])
        self.assertEqual(instance.update_pks, [])
        self.assertEqual(instance.delete_pks, [])
        self.assertEqual(instance._accounted_pks, [])
        self.assertEqual(instance._queryset_pks, [])
        self.assertTrue(instance.skip_locks)
        self.assertIsNone(instance.output_file)
        self.assertIsNone(instance.max_count)
        self.assertTrue(instance.use_subtasks)
        self.assertIsNone(instance.log_level)

    # specific question I want to ask here:
    # How do you know to take those exact parameters into your argument? Reset, max_count, etc.
    def test_custom_values(self):
        instance = TestMongoReplicatorExample(reset=True, max_count=10, use_subtasks=False, log_level='DEBUG')
        self.assertTrue(instance.reset)
        self.assertEqual(instance.max_count, 10)
        self.assertFalse(instance.use_subtasks)
        self.assertEqual(instance.log_level, 'DEBUG')

    def test_missing_model_attribute(self):
        with self.assertRaises(AttributeError):
            # Test case where model is not provided
            BaseReplicationCollector()

    def test_missing_change_keys_attribute(self):
        class YourModelWithoutChangeKeys(BaseReplicationCollector):
            model = User
        with self.assertRaises(AttributeError):
            YourModelWithoutChangeKeys()

    # confused about this
    def test_get_model(self, **kwargs):
        self.instance = TestMongoReplicatorExample()
        self.assertEqual(self.instance.get_model(), User)

    def test_get_queryset(self):
        instance = TestMongoReplicatorExample()

    def test_search_quantifier(self):
        instance = TestMongoReplicatorExample()

    def test_content_type(self):
        instance = TestMongoReplicatorExample()
        expected_content_type = ContentType.objects.get_for_model(User)
        actual_content_type = instance.content_type
        self.assertEqual(actual_content_type, expected_content_type)

    def test_verbose_name(self):
        instance = TestMongoReplicatorExample()
        pass

    def test_lock(self):
        instance = TestMongoReplicatorExample()
        pass

    def test_unlock(self):
        instance = TestMongoReplicatorExample()
        self.assertEqual(instance.last_look, None)
        self.assertFalse(instance.locked)

    @mock.patch('data_replication.backends.splunk.SplunkRequest.session', mock_session)
    def test__delete_items(self):
        instance = self.base_replication_collector()
        self.assertRaises(NotImplementedError, instance.delete_items, object_pks=[1, 2, 3])

        rt = replication_tracker_factory(Example, 'splunk')
        oids = []
        for i in range(3):
            oids.append(Example.objects.create(name="test%d" % i).pk)

        Replication.objects.bulk_create([
            Replication(tracker=rt, object_id=x, content_type=ContentType.objects.get_for_model(Example),
                        state=1, last_updated=now()) for x in oids]
        )
        self.assertEqual(Replication.objects.count(), 3)
        replicator = rt.get_replicator()
        collector = replicator()
        collector.last_look = rt  # Why did I use the variable last look in lieu of tracker????
        collector._delete_items(oids)
        self.assertEqual(Replication.objects.count(), 0)

    def test_delete_items(self):
        instance = self.base_replication_collector()
        with self.assertRaises(NotImplementedError):
            instance.delete_items([1, 2, 3])

    def test_task_name(self):
        instance = self.base_replication_collector()
        with self.assertRaises(NotImplementedError):
            instance.task_name()

    def test_get_task_kwargs(self):
        instance = self.base_replication_collector()
        result = instance.get_task_kwargs()
        self.assertEqual(result, {})

    def test_add_items(self):
        instance = self.base_replication_collector()
        with self.assertRaises(NotImplementedError):
            instance.delete_items([1, 2, 3])



class TestMongoReplicatorExample(MongoReplicator):
    model = User
    change_keys = ['last_used']
