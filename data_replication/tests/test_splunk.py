import re
from compiler.ast import obj

from django.test import TestCase

import objects
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now
from django import test
from pymongo.errors import ConnectionFailure, OperationFailure

from data_replication import tasks
from data_replication.backends.base import ImproperlyConfiguredException
from data_replication.models import ReplicationTracker
import data_replication.backends.splunk as splunk
from data_replication.backends.splunk import SplunkAuthenticationException
from data_replication.backends.splunk import SplunkPostException
from data_replication.backends.splunk import SplunkRequest
from data_replication.backends.splunk import SplunkReplicator


class TestSplunk(TestCase):
    def test_splunk(self):
        self.assertEqual(splunk.__author__, "Steven Klass", "author is incorrect")
        self.assertEqual(splunk.__date__, "9/21/17 08:11", "date is incorrect")
        self.assertEqual(splunk.__copyright__, "Copyright 2017 IC Manage. All rights reserved.", "copyright incorrect")
        self.assertEqual(splunk.__credits__, ["Steven Klass"], "credits is incorrect")
        self.assertEqual(splunk.SPLUNK_PREFERRED_DATETIME, "%Y-%m-%d %H:%M:%S:%f")
        # self.assertEqual(splunk.INTS, re.compile(r"^-?[0-9]+$"))
        # self.assertEqual(splunk.NUMS, re.compile(r"^[+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?$"))

    def test_splunk_auth_exception(self):
        with self.assertRaises(SplunkAuthenticationException):
            # I am confused here because I don't know what function to use or how to make a mock one
            tasks.push_splunk_objects()

    def test_splunk_post_exception(self):
        with self.assertRaises(SplunkAuthenticationException):
            # I am confused here because I don't know what function to use or how to make a mock one
            tasks.push_splunk_objects()


class TestSplunkRequest(TestCase):
    def test_init(self):
        pass

    def test_missing_settings(self):
        # Test that ImproperlyConfiguredException is raised if required settings are missing
        with self.assertRaises(ImproperlyConfiguredException):
            SplunkRequest()
