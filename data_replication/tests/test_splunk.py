import re
from django.conf import settings
from django.test import TestCase
import mock
from django.utils.datetime_safe import datetime
from mock import Mock, patch
from data_replication.backends.base import ImproperlyConfiguredException
from data_replication.models import ReplicationTracker
import data_replication.backends.splunk as splunk
from data_replication.backends.splunk import SplunkAuthenticationException
from data_replication.backends.splunk import SplunkPostException
from data_replication.backends.splunk import SplunkRequest
from data_replication.backends.splunk import SplunkReplicator
from django.apps import apps

from data_replication.tasks import push_splunk_objects
from data_replication.tests.factories import replication_tracker_factory
from data_replication.tests.test_tasks import mock_session

data_replication_app = apps.get_app_config('data_replication')
Example = apps.get_model('example', 'Example')


class TestSplunk(TestCase):

    def setUp(self):
        class FooBar(SplunkRequest):
            model = Example
            change_keys = ['foo']
            object_pks = ['all', 'these', 'things', 'fart']

        self.splunk_request = FooBar

    def test_splunk_basics(self):
        self.assertEqual(splunk.__author__, "Steven Klass", "author is incorrect")
        self.assertEqual(splunk.__date__, "9/21/17 08:11", "date is incorrect")
        self.assertEqual(splunk.__copyright__, "Copyright 2017 IC Manage. All rights reserved.", "copyright incorrect")
        self.assertEqual(splunk.__credits__, ["Steven Klass"], "credits is incorrect")
        self.assertEqual(splunk.SPLUNK_PREFERRED_DATETIME, "%Y-%m-%d %H:%M:%S:%f")
        # self.assertEqual(splunk.INTS, re.compile(r"^-?[0-9]+$"))
        # self.assertEqual(splunk.NUMS, re.compile(r"^[+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?$"))

    def test_splunk_auth_exception(self):
        with self.assertRaises(SplunkAuthenticationException):
            raise SplunkAuthenticationException('hello')
        try:
            raise SplunkAuthenticationException('hello')
        except SplunkAuthenticationException as error:
            self.assertIn('hello', str(error))

    def test_splunk_post_exception(self):
        with self.assertRaises(SplunkPostException):
            raise SplunkPostException('hello')
        try:
            raise SplunkPostException('hello')
        except SplunkPostException as error:
            self.assertIn('hello', str(error))

    def test_delete_items(self):
        instance = self.splunk_request()
        instance.delete_items(object_pks=['fart'])

    @patch.object(SplunkRequest, 'connect')
    def test_get_search_status(self, mock_sleep):
        mock_session = Mock()
        mock_request = Mock()
        mock_request.status_code = 400
        mock_request.json.return_value = {'results': ['mocked_data']}
        mock_session.get.return_value = mock_request

        with patch.object(SplunkRequest, 'session', new=mock_session):
            search_instance = SplunkRequest()
            result, status_code = search_instance.get_search_status('mock_search_id')

            self.assertEqual(status_code, 400)
            self.assertEqual(result, {'results': ['mocked_data']})

    def XXXtest_missing_settings(self):
        # Test that ImproperlyConfiguredException is raised if required settings are missing
        with self.assertRaises(ImproperlyConfiguredException):
            SplunkRequest()

    def XXXtest_create_search(self):
        instance = SplunkRequest()
        mock_search = 'thing'
        instance.create_search(mock_search)
        self.assertEqual(instance.create_search(mock_search), mock_search)
