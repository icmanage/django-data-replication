import re
from django.conf import settings
from django.test import TestCase
import mock
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

data_replication_app = apps.get_app_config('data_replication')
Example = apps.get_model('example', 'Example')


class MockResponse():
    status_code = 200
    json = Mock(return_value={'your': 'data'})

    def __init__(self, **kwargs):
        self.status_code = kwargs.get('status_code', self.status_code)


class MockSession():
    def request(self, url, data=None, json=None, **kwargs):
        print(url)
        if url == '{base_url}/services/search/jobs/{search_id}/results?output_mode=json':
            return MockResponse(status_code=204)

    def get(self, url, **kwargs):
        pass
        print(url)


mock_session = MockSession()


class TestSplunk(TestCase):
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

    # @patch('data_replication.backends.splunk.SplunkRequest.session', mock_session)
    def XXXtest_get_search_status(self):
        self.instance = SplunkRequest()
        result, status_code = self.instance.get_search_status(search_id='123')
        self.assertEqual(result, {'mock': 'data'})

    def XXXtest_missing_settings(self):
        # Test that ImproperlyConfiguredException is raised if required settings are missing
        with self.assertRaises(ImproperlyConfiguredException):
            SplunkRequest()

    def XXXtest_create_search(self):
        instance = SplunkRequest()
        mock_search = 'thing'
        instance.create_search(mock_search)
        self.assertEqual(instance.create_search(mock_search), mock_search)
