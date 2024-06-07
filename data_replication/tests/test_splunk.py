from compiler.ast import obj
from unittest import TestCase

import objects
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now
from django import test
from pymongo.errors import ConnectionFailure, OperationFailure
from data_replication.models import ReplicationTracker
import data_replication.backends.splunk as splunk


class TestSplunk(TestCase):
    def test_splunk(self):
        self.assertEqual(splunk.__author__, "Steven Klass", "author is incorrect")
        self.assertEqual(splunk.__date__, "9/21/17 08:11", "date is incorrect")
        self.assertEqual(splunk.__copyright__, "Copyright 2017 IC Manage. All rights reserved.", "copyright incorrect")
        self.assertEqual(splunk.__credits__, ["Steven Klass"], "credits is incorrect")

    class TestSplunkAuthenticationException(TestCase):

