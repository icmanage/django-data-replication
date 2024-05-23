from collections import OrderedDict

from django.test import TestCase
import data_replication.backends.base as base
from django.db import connection, connections
from django.contrib.contenttypes.models import ContentType
from data_replication.models import Replication, ReplicationTracker
from data_replication.backends.base import BaseReplicationCollector
from data_replication.backends.base import ImproperlyConfiguredException


class TestBase(TestCase):
    #not sure what is going on with this test failing
    def test_mysql_usable(self):
        connection.connection = None
        base.make_sure_mysql_usable()

    #breaking into chatGPT here.
    def test_default_values(self):
        instance = BaseReplicationCollector()
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

    #specific question I want to ask here:
    # How do you know to take those exact parameters into your argument? Reset, max_count, etc.
    def test_custom_values(self):
        instance = BaseReplicationCollector(reset=True, max_count=10, use_subtasks=False, log_level='DEBUG')
        self.assertTrue(instance.reset)
        self.assertEqual(instance.max_count, 10)
        self.assertFalse(instance.use_subtasks)
        self.assertEqual(instance.log_level, 'DEBUG')

    def test_missing_model_attribute(self):
        with self.assertRaises(AttributeError):
            # Test case where model is not provided
            BaseReplicationCollector()

    def test_missing_change_keys_attribute(self):
        with self.assertRaises(AttributeError):
            # Test case where change_keys are not provided
            class YourModelWithoutChangeKeys(BaseReplicationCollector):
                def get_model(self):
                    return BaseReplicationCollector

            YourModelWithoutChangeKeys()

    #confused about this
    def test_get_model(self, **kwargs):
        self.instance = BaseReplicationCollector()
        self.instance.model = ''
        self.assertEqual(self.instance.get_model(), '')
        return not None

    #ends here

    def test_get_queryset(self):
        pass

    def test_search_quantifier(self):
        pass

    def test_content_type(self):
        instance = BaseReplicationCollector()
        expected_content_type = ContentType.objects.get_for_model('BaseReplicationCollector')
        actual_content_type = self.instance.content_type()
        self.assertEqual(actual_content_type, expected_content_type)

    def test_verbose_name(self):
        instance = BaseReplicationCollector()

    def test_get_models(self):
        pass

    def test_accounted_pks(self):
        pass

    def test__delete_items(self, object_pks):
        pass

    def test_delete_items(self):
        instance = BaseReplicationCollector()
        object_pks = [1, 2, 3]
        with self.assertRaises(NotImplemented):
            instance.delete_items(object_pks)

    def test_task_name(self):
        instance = BaseReplicationCollector()
        self.assertRaises(instance.task_name, NotImplemented)
