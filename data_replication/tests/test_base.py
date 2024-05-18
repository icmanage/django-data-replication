from collections import OrderedDict
from unittest import TestCase

import self
from django import test
from django.contrib.admin.options import get_content_type_for_model
from kombu.exceptions import OperationalError
import data_replication.backends.base as base
from django.db import connection, connections
from django.contrib.contenttypes.models import ContentType


class TestBase(test.TestCase):
    def test_base(self):
        ct = ContentType.objects.get_for_model(base.BaseReplicationCollector)
        #self.assertEqual(base.locked(), False)

    def test_init(self):
        ct = ContentType.objects.get_for_model(base.BaseReplicationCollector)
        obj = base.BaseReplicationCollector.objects.create(model=1, change_keys=[], field_map=OrderedDict(),
                                                           search_quantifiers=None)
        #self.assertFalse(base.locked())
        #self.assertEqual(base.last_look(), None)
        pass

    def test_mysql_usable(self):
        self.assertEqual(connection.connection, connection.is_usable(), "Not working")

    def test_get_models(self):
        self.assertIn(base.BaseReplicationCollector.model, base.BaseReplicationCollector.model)

    def test_delete_items(self, object_pks):
        self.assertEqual(NotImplemented, None)
