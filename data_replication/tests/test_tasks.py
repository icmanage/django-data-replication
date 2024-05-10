from django.contrib.contenttypes.models import ContentType
from django.urls import resolve
from django.utils.timezone import now
from django import test
import logging
from pymongo.errors import ConnectionFailure, OperationFailure
from data_replication.models import ReplicationTracker

import data_replication.tasks as tasks
from data_replication.tests.factories import replication_tracker_factory, tasks_factory


class TasksTest(test.TestCase):

    def test_tasks(self):
        self.assertEqual(tasks.__author__, "Steven Klass", "author is incorrect")
        self.assertEqual(tasks.__date__, "9/26/17 10:12", "date is incorrect")
        self.assertEqual(tasks.__copyright__, "Copyright 2017 IC Manage. All rights reserved.", "copyright incorrect")
        self.assertEqual(tasks.__credits__, ["Steven Klass"], "credits is incorrect")

    def test_push_splunk_objects(self):
        ct = ContentType.objects.get_for_model(ReplicationTracker)
        rt = replication_tracker_factory()
        self.assertEqual(ReplicationTracker.objects.count(), 1)
        rt = replication_tracker_factory(state=1)
        self.assertEqual(rt.state, 1)

        #new stuff and error is here
        #tf = tasks_factory()
        #tf = tasks_factory(model_name='mode_name')
        #self.assertEqual(tf.model_name, 'model_name')
