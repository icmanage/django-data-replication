from django.apps import apps
from django.utils.timezone import now
from mock import patch, mock, MagicMock

from django.contrib.auth import get_user_model
from django.test import TestCase

from django.contrib.contenttypes.models import ContentType

from data_replication.backends.base import BaseReplicationCollector
from data_replication.backends.mongo import MongoReplicator
from data_replication.models import Replication, ReplicationTracker
from data_replication.tests.factories import replication_tracker_factory
from data_replication.tests.test_tasks import mock_session

User = get_user_model()
Example = apps.get_model('example', 'Example')


class TestBase(TestCase):

    def setUp(self):
        class MockB(BaseReplicationCollector):
            mock_instance = MagicMock()
            model = Example
            change_keys = ['foo']
            search_quantifiers = None,
            search_quantifier = "search_quantifier_value"
            self.skip_locks = True
            reset = True
            # self.last_look = None
            # last_look = ReplicationTracker.objects.get(
            #     content_type=BaseReplicationCollector.content_type,
            #     replication_type=mock_instance.replication_type
            # )
            # ftr = replication_tracker_factory()
            the_state = ReplicationTracker.state

        self.base_replication_collector = MockB

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

    def test_get_model(self, **kwargs):
        self.instance = TestMongoReplicatorExample()
        self.assertEqual(self.instance.get_model(), User)

    # TODO fix or remove
    def test_search_quantifier(self):
        instance = TestMongoReplicatorExample()
        caller = instance.search_quantifier
        self.assertEqual(caller, ' model=user')

    # P: This runs an infinite recursion error when search_quantifiers
    # is set to true. Is that a bug, or a problem with my testing?
    def XXXtest_search_quantifier_con(self):
        instance = TestMongoReplicatorExample()
        instance.search_quantifiers = True
        caller = instance.search_quantifier
        self.assertEqual(caller, ' model=user')

    def test_content_type(self):
        instance = TestMongoReplicatorExample()
        expected_content_type = ContentType.objects.get_for_model(User)
        actual_content_type = instance.content_type
        self.assertEqual(actual_content_type, expected_content_type)

    def test_verbose_name(self):
        instance = TestMongoReplicatorExample()
        pass

    def test_lock(self):
        instance = TestMongoReplicatorExample(state=0)
        instance.skip_locks = False
        instance.reset = True
        instance.lock()
        self.assertTrue(instance.reset)

    # TODO fix or remove
    def test_lock_oth(self):
        instance = self.base_replication_collector
        instance.skip_locks = False
        instance.reset = False
        instance.lock()
        self.assertFalse(instance.reset)

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
