from django.utils.timezone import now
from django import test
import logging
from pymongo.errors import ConnectionFailure, OperationFailure
from data_replication.models import ReplicationTracker

import data_replication.urls as urls


class UrlsTest(test.TestCase):

    def tasks_test(self):
        self.assertEqual(urls.__author__, "Steven Klass", "author is incorrect")
        self.assertEqual(urls.__date__, "9/21/17 07:56", "date is incorrect")
        self.assertEqual(urls.__copyright__, "Copyright 2017 IC Manage. All rights reserved.", "copyright incorrect")
        self.assertEqual(urls.__credits__, "Steven Klass", "credits is incorrect")
