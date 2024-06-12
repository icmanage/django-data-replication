from django.contrib.auth import get_user_model
from django.test import TestCase

from django.contrib.contenttypes.models import ContentType
from data_replication.backends.base import BaseReplicationCollector
from data_replication.backends.mongo import MongoReplicator

User = get_user_model()


class TestBase(TestCase):

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

    def test_accounted_pks(self):
        pass

    def test_changed_queryset_pks(self):
        pass

    def test_get_actions(self):
        instance = TestMongoReplicatorExample()
        # self.assertIn("You need to lock the db first", instance.locked)
        self.assertFalse(instance.locked)

    def test_analyze(self):
        pass

    def XXXtest__delete_items(self, object_pks):
        pass

    def XXXtest_delete_items(self):
        instance = TestMongoReplicatorExample()
        with self.assertRaises(NotImplementedError):
            instance.delete_items([1, 2, 3])

    def XXXtest_task_name(self):
        instance = BaseReplicationCollector()
        with self.assertRaises(NotImplementedError):
            instance.delete_items([1, 2, 3])

    def XXXtest_get_task_kwargs(self):
        instance = BaseReplicationCollector()
        result = instance.get_task_kwargs()
        self.assertEqual(result, {})

    def XXXtest_add_items(self):
        instance = BaseReplicationCollector()
        with self.assertRaises(NotImplementedError):
            instance.delete_items([1, 2, 3])

    def XXXtest__add_items(self):
        pass

    def XXXtest_chunks(self):
        pass


class TestMongoReplicatorExample(MongoReplicator):
    model = User
    change_keys = ['last_used']
