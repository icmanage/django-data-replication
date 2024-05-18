from django import test
import datetime
from collections import OrderedDict
from django.contrib.admin.options import get_content_type_for_model
from kombu.exceptions import OperationalError
import data_replication.backends.base as base
from django.db import connection, connections


class TestBase(test.TestCase):
    def base_tests(self):
        self.assertEqual(base.locked(), False, "Not working")

    def test_mysql_usable(self):
        self.assertEqual(connection.connection, connection.is_usable(), "Not working")

    def test_get_models(self):
        self.assertIn(base.BaseReplicationCollector.model, base.BaseReplicationCollector.model)