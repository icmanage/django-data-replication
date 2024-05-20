from collections import OrderedDict
from unittest import TestCase

import self
from django import test
from django.contrib.admin.options import get_content_type_for_model
from kombu.exceptions import OperationalError
import data_replication.backends.base as base
from django.db import connection, connections
from django.contrib.contenttypes.models import ContentType
from data_replication.models import Replication, ReplicationTracker
from data_replication.tests.factories import replication_tracker_factory, base_factory


class TestBase(test.TestCase):
    def test_base(self):
        ct = ContentType.objects.get_for_model(base.BaseReplicationCollector)
        self.base1 = ct.objects.create(model=None, change_keys=[], field_map=OrderedDict(), search_quantifiers=None)
        bf = base_factory()
        bf.objects.create(model=None, change_keys=[], field_map=OrderedDict(), search_quantifiers=None)

    def test_init(self, **kwargs):
        ct = ContentType.objects.get_for_model(base.BaseReplicationCollector)
        self.baseIn = ct.objects.create(self, last_look=None, reset=False, max_count=None, **kwargs)
        self.assertEqual(self.baseIn.last_look, None)

        #self.assertFalse(base.locked())
        #self.assertEqual(base.last_look(), None)
        pass

    def test_mysql_usable(self):
        self.assertEqual(connection.connection, connection.is_usable(), "Not working")

    def test_get_models(self):
        self.assertIn(base.BaseReplicationCollector.model, base.BaseReplicationCollector.model)

    #I'm not sure this is necessary, but i see the lock function shares a lot of similarities to replication_tracker
    def test_replicator_factory_lock(self, **kwargs):
        ct = ContentType.objects.get_for_model(ReplicationTracker)
        rt = replication_tracker_factory()
        self.assertEqual(ReplicationTracker.objects.count(), 1)
        rt = replication_tracker_factory(state=1)
        self.assertEqual(rt.state, 1)

    def test_delete_items(self, object_pks):
        self.assertEqual(NotImplemented, None)
        #self.assertIn(base.BaseReplicationCollector.delete_items, tracker=self.last_look, object_id__in=object_pks, content_type=self.content_type)
