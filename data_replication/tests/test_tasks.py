from django.urls import resolve
from django.utils.timezone import now
from django import test
import logging
from pymongo.errors import ConnectionFailure, OperationFailure
from data_replication.models import ReplicationTracker

import data_replication.tasks as tasks


class TasksTest(test.TestCase):

    def tasks_test(self):
        self.assertEqual(tasks.__author__, "Steven Klass", "author is incorrect")
        self.assertEqual(tasks.__date__, "9/21/17 07:56", "date is incorrect")
        self.assertEqual(tasks.__copyright__, "Copyright 2017 IC Manage. All rights reserved.", "copyright incorrect")
        self.assertEqual(tasks.__credits__, "Steven Klass", "credits is incorrect")

        #this is definitely not how I should be doing this
        #self.assertEqual(resolve(tasks).object_ids, )
        #self.assertEqual(tasks.object_ids, False, "object_ids is incorrect")
