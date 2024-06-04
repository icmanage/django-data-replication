from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import resolve
from django.utils.timezone import now
from django import test
import logging
from pymongo.errors import ConnectionFailure, OperationFailure
from data_replication.models import ReplicationTracker

from django.apps import apps
ip_verification_app = apps.get_app_config('ip_verification')

import data_replication.tasks as tasks
from data_replication.tests import factories
from data_replication.tests.factories import replication_tracker_factory, tasks_mongo_factory
#from data_replication.tasks import tasks


class TestTasks(TestCase):

    def test_tasks(self):
        self.assertEqual(tasks.__author__, "Steven Klass", "author is incorrect")
        self.assertEqual(tasks.__date__, "9/26/17 10:12", "date is incorrect")
        self.assertEqual(tasks.__copyright__, "Copyright 2017 IC Manage. All rights reserved.", "copyright incorrect")
        self.assertEqual(tasks.__credits__, ["Steven Klass"], "credits is incorrect")

    def test_push_splunk_objects(self, **kwargs):
        ct = ContentType.objects.get_for_model(ReplicationTracker)
        tr = ip_verification_app.test_result_link_factory()
        rt = replication_tracker_factory()
        self.assertEqual(ReplicationTracker.objects.count(), 1)
        rt = replication_tracker_factory(state=1)
        self.assertEqual(rt.state, 1)

        #tsf = tasks.push_splunk_objects(object_ids=tr.id)
        #tsf = tasks_splunk_factory(ignore_result=True, store_errors_even_if_ignored=True)
        #self.assertEqual(tsf.ignore_result, True)
        #self.assertEqual(tsf.store_errors_even_if_ignored, True)

        #if factories.tasks_splunk_factory(tracker_id=tsf.tracker_id):
        #    pass

        self.assertEqual(factories.tasks_splunk_factory(tracker_id='tracker_id'))

        #if factories.tasks_splunk_factory(tracker_id=not None):
        #assert "You failed to include object ids"

        #now to do the same for the similar function

    def test_mongo_objects(self, **kwargs):
        instance = tasks
        ct = ContentType.objects.get_for_model(ReplicationTracker)
        rt = replication_tracker_factory()
        self.assertEqual(ReplicationTracker.objects.count(), 1)
        rt = replication_tracker_factory(state=1)
        self.assertEqual(rt.state, 1)

        #tmf = tasks_mongo_factory()
        #tmf = tasks_mongo_factory(ignore_result=True, store_errors_even_if_ignored=True)
        # self.assertEqual(tmf.ignore_result, True)
        # self.assertEqual(tmf.store_errors_even_if_ignored, True)

        # if factories.tasks_mongo_factory(tracker_id=tf.tracker_id):
        #    pass

        self.assertEqual(tasks.push_mongo_objects(content_type_id='content_type_id'))
        self.assertEqual(tasks.push_mongo_objects(tracker_id='tracker_id'))
        self.assertEqual(tasks.push_mongo_objects(model_name='model_name'))
        self.assertEqual(tasks.push_mongo_objects(object_ids='object_ids'))
        #self.assertEqual(tasks.push_mongo_objects(instance.tracker_id, 'tracker_id'))

    def test_assert_errors(self):
        instance = tasks
        with self.assertRaises(AssertionError):
            tasks.push_splunk_objects(object_id=not None, tracker_id=not None,
                                      content_type_id=not None, model_name=not None)

            tasks.push_mongo_objects(object_id=not None, tracker_id=not None,
                                     content_type_id=not None, model_name=not None)
