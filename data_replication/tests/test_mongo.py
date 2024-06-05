from unittest import TestCase

import objects
from django.contrib.contenttypes.models import ContentType
from django.urls import resolve
from django.utils.timezone import now
from django import test
import logging
from pymongo.errors import ConnectionFailure, OperationFailure
from data_replication.models import ReplicationTracker
from data_replication.tasks import push_mongo_objects
import data_replication.backends.mongo as mongo


class MongoTestCase(test.TestCase):

    def test_task_name(self):
        #ct = ContentType.objects.get_for_model(mongo.MongoRequest)
        #mtn = ct.all()
        #self.assertEqual(push_mongo_objects.task_name(), 'push_mongo_objects')
        pass

    def XXXtest_delete_items(self):
        #ct = ContentType.objects.get_for_model(mongo.MongoRequest)
        self.assertEqual(mongo.MongoReplicator(mongo), mongo.MongoRequest())
        pass

    def test_get_task_kwargs(self):
        pass
